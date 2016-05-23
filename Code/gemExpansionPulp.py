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
  
  def main(self):
      k = 5
      mm=21
      seedTexts = open(config.seedFile,"r").readlines()
      allText = self.getAllText()
      lengthAllText = len(allText)
      tokensContext = [] #[0]*lengthAllText
      relatednessScore = [] #[0]*lengthAllText
      print len(allText)
      for i,token in enumerate(allText):
        tokensContext.append( self.getContext( allText[max(0,i-k):min(lengthAllText,i+k+1)] ) )
        if i==2500:
            break
      i = 0
      lim = len(seedTexts)
      if lim%2 != 0:
        print "ERROR: Wrong format for seed.txt"
        sys.exit(2)
      fw = open(config.outputFile,"w")
      print " ::::::::::::::::::::::::::::::::: "
      while i<lim:
        print " i = .... ",i
        seedText = seedTexts[i].replace('\n','')
        print "seedText  ",seedText
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
        for j,token in enumerate(allText):
          relatednessScore.append( self.getRelatednessScore( tokensContext[j], seedTextContext ) )
          if j==2500:
              break
        selection = self.getSelection( relatednessScore = relatednessScore, alpha = config.alpha, budget = budget )
        m = len(relatednessScore)
        sel = [i for i,val in enumerate(selection) if (val==1 and i<m)]
        t = []
        for seli in sel:
          t.append(allText[seli])
        print t
        #fw.write(t)
        #fw.write("-------------------------------\n")
        #except:
        #  print "ERROR: Skipping this seedtext..."
      fw.close()
