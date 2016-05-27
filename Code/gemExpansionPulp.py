'''
'''
import os
from pulp import *
import config
from collections import Counter
import string
import math
import json
import scipy.stats as scipy_stats
import scipy.optimize as sco
from utilities import Preprocess

class GemExpansion:

  preprocess = None
  
  def __init__(self):
    self.preprocess = Preprocess()
  
  ################################################
  #CONTEXT = surrounding words within a window
  def getContext(self,surroundingTokens):
      ret = {}
      ctr = 0
      for i,token in enumerate(surroundingTokens):
          if token not in self.preprocess.global_english_stopwords:
              if token not in ret:
                  ret[token] = 0
              ret[token] += 1
              ctr += 1
      ctr = ctr*1.0
      return { k:(1.0*ret[k])/ctr for k in ret}
  
  ##############################################
  
  def getRelatednessScore(self,contextp, contextq):
      # kl distance from p to q 
      # expected difference b/w logs of p and q pdfs, under probability law p
      defaultValue = 0.01
      tokenSet = list( set(contextp.keys()) | set(contextq.keys()) )
      pk = []
      qk = []
      for token in tokenSet:
          if token in contextp:
              pk.append(contextp[token] + defaultValue)
          else:
              pk.append(defaultValue)
          if token in contextq:
              qk.append(contextq[token] + defaultValue)
          else:
              qk.append(defaultValue)
      return 1.0*scipy_stats.entropy(pk, qk)
  
  
  ##############################################
  
  def getSeedText(self,txt):
      return txt.lower().split(' ')
  
  def getAllText(self):
      data = (' '.join(open(config.dataFileSrc,'r').readlines())).replace('\n',' ')
      data = data.split(' ')
      data = [token.lower() for token in data]
      return data
      
  ##############################################
  
  def getSelection(self,relatednessScore, alpha, budget):
      print "----"
      m = len(relatednessScore)
      x = []
      for i in range(0,m):
          x.append(LpVariable("x"+str(i), 0, 1, cat='Binary'))
      for i in range(0,m-1):
          x.append(LpVariable("y"+str(i), 0, 1, cat='Binary'))
  
      # defines the problem
      prob = LpProblem("problem", LpMaximize)    
      
      # defines the constraints
      for i in range(0,m-1):
          prob += x[i+m]-x[i] <= 0
          prob += x[i+m]-x[i+1] <= 0
          prob += x[i]+x[i+1]-x[i+m] <= 1
      prob += lpSum(x[0:m])==budget
      
      # defines the objective function to maximize
      tmp1 = [x[i]*relatednessScore[i] for i in range(0,m)]
      tmp2 = [x[i]*alpha for i in range(m,2*m-1)]
      tmp1.extend(tmp2)
      #print tmp1
      prob += lpSum(tmp1) 
       
      # solve the problem
      status = prob.solve(GLPK(msg=0))
      
      #Check sum
      print "m= ",m
      tmp1 = [value(x[i])*relatednessScore[i] for i in range(0,m)]
      tmp2 = [value(x[i])*alpha for i in range(m,2*m-1)]
      tmp1.extend(tmp2)
      print sum(tmp1)
      
      print value(x[0])
      print value(x[1])
      print LpStatus[status]
      print status
      selection = [value(x[i]) for i in range(0,2*m-1)]
      return selection
      
  
  ##############################################
  
  def getGems(self,selectedWords):
    gems = []
    i = 0
    lim = len(selectedWords)
    while i<lim:
      cur = selectedWords[i]
      i+=1
      startGemIdx = i
      while i<lim:
        prev = cur
        cur = selectedWords[i]
        i+=1
        if cur == (prev+1):
          continue
        else:
          i = i-1
          break
      endGemIdx = i
      gems.append([startGemIdx,endGemIdx])
    return gems
    
  
  def maxSimilarity(self,i,list_of_j,simScores):
    ret = 0.0
    for j in list_of_j:
        ret = max(ret, simScores[i][j])
    return ret
  
  def getMMRGems(self,gems, seedText, relatednessScore, allText, budget):
    lambd = 0.5
    m = len(gems)
    relScores = [0.0]*m
    simScores = []
    for i in range(m):
      simScores.append([0.0]*m)
    
    gemTextAll = []
    for i,gem in enumerate(gems):
      st = gem[0]
      en = gem[1]
      gemText = allText[st:en+1]
      gemTextAll.append(gemText)
      relScores[i] = self.preprocess.getSimilarity(gemText, seedText)
      simScores[i][i]=1.0
    for i,gemText in enumerate(gemTextAll):
      simScores[i][i]=1.0
      for j in range(i):
        simScores[i][j] = self.preprocess.getSimilarity(gemText, seedText)
        simScores[i][j] = simScores[j][i]
        print "getNextSummary"

    #MMR
    chosen = []
    chosen_mark = [0]*m
    ignore_mark = [0]*m
    current_words = 0
    counter = 0
    scores = [0.0]*m
    max_score_val = -999
    selection = -1
    word_lim = budget
    while current_words<=word_lim and  counter<m:
        #Calculate scores
        selection = -1
        max_score_val = -9999
        for i in range(0,m):
            if chosen_mark[i]==1:
                continue
            if ( len(gemTextAll[i]) + current_words)>word_lim:
                ignore_mark[i] = 1
                counter+=1
                continue
            max_sim = self.maxSimilarity(i,chosen,simScores)
            scores[i] = lambd*relScores[i] - (1.0-lambd)*max_sim
            if scores[i] > max_score_val:
                max_score_val = scores[i]
                selection = i
        if selection == -1:
            print "Warning: ... "
        #print "selection ",selection
        else:
            chosen_mark[selection] = 1
            ignore_mark[selection] = 1
            chosen.append(selection)
            current_words += len(gemTextAll[i])
            counter+=1
    return chosen
          
      
  
  ##############################################
  
  def main(self,mmr=False):
      k = 5
      mm=21
      
      #Read all text
      seedTexts = open(config.seedFile,"r").readlines()
      allText = self.getAllText()
      lengthAllText = len(allText)
      tokensContext = [] #[0]*lengthAllText
      relatednessScore = [] #[0]*lengthAllText
      print "Length of text corpus (no. of words) = ",len(allText)
      for i,token in enumerate(allText):
        tokensContext.append( self.getContext( allText[max(0,i-k):min(lengthAllText,i+k+1)] ) )
        if i==400:
            break
      i = 0
      lim = len(seedTexts)
      if lim%2 != 0:
        print "ERROR: Wrong format for seed.txt"
        sys.exit(2)
      fw = open(config.outputFile,"w")
      while i<lim:
        print " Processing seed text no. ",i+1
        seedText = seedTexts[i].replace('\n','')
        print "seedText = ",seedText
        i+=1
        try:
          budget = int(seedTexts[i].replace('\n',''))
        except:
          print "ERROR while processing seedTexts.txt : Terminating..."
          sys.exit(2)
        print "budget = ",budget
        i+=1
        #try:
        seedText = self.getSeedText(seedText)
        seedTextContext = self.getContext(seedText)
        relatednessScore = [] #[0]*lengthAllText
        for j in range(len(allText)):
          relatednessScore.append( self.getRelatednessScore( tokensContext[j], seedTextContext ) )
          if j==400:
              break
        if mmr == False:
          selection = self.getSelection( relatednessScore = relatednessScore, alpha = config.alpha, budget = budget )
        else:
          selection = self.getSelection( relatednessScore = relatednessScore, alpha = config.alpha, budget = 2*budget )
        m = len(relatednessScore)
        sel = [i for i,val in enumerate(selection) if (val==1 and i<m)]
        t = []
        for seli in sel:
          t.append(allText[seli])
        print t
        
        if mmr==True:
          gems = self.getGems(sel)
          chosen = self.getMMRGems(gems, seedText, relatednessScore, allText, budget)
          print chosen
          print len(chosen)
          fw.write(str(t))
          fw.write("-------------------------------\n")
        else:
          fw.write(str(t))
          fw.write("-------------------------------\n")
        #except:
        #  print "ERROR: Skipping this seedtext..."  
      fw.close()
