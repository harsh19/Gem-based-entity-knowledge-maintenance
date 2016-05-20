'''
'''
import os
from pulp import *
import config

from nltk.corpus import stopwords
from collections import Counter
import string
import math
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
import json
import scipy.stats as scipy_stats
import scipy.optimize as sco

############################################
excluded_characters = set(string.punctuation)
if config.do_lemmatize:
    wordnet_lemmatizer =  WordNetLemmatizer()
if config.do_stemming:
    stemmer = PorterStemmer() 
global_english_stopwords = []

############################################
# Utility functions

def loadInit():
    global global_english_stopwords
    global_english_stopwords = stopwords.words('english')
    
def getLemmatized(word):
    return wordnet_lemmatizer.lemmatize(word)
    
def getStemmed(word):
    return stemmer.stem(word)

def ascii_only(s):
    ret = ""
    for ch in s:
        if ord(ch)<=128:
            ret =  ret + ch
    return ret

def removePuntuation(s):
    return ''.join([ch for ch in s if ch not in excluded_characters])

def getBigrams(words_list):
    m = len(words_list)
    i=0
    bigrams = []
    while i<m-1:
        bigrams.append(words_list[i] + " " + words_list[i+1])
        i = i+1
    return bigrams
    
def getTrigrams(words_list):
    m = len(words_list)
    i = 0
    trigrams = []
    while i<m-2:
        trigrams.append(words_list[i] + " " + words_list[i+1] + " " + words_list[i+2])    
        i = i+1
    return trigrams
    
################################################
#CONTEXT
def getContext(surroundingTokens):
    global global_english_stopwords
    ret = {}
    ctr = 0
    for i,token in enumerate(surroundingTokens):
        if token not in global_english_stopwords:
            if token not in ret:
                ret[token] = 0
            ret[token] += 1
            ctr += 1
    ctr = ctr*1.0
    return { k:(1.0*ret[k])/ctr for k in ret}

##############################################

def getRelatednessScore(contextp, contextq):
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
    '''print pk
    print qk
    print scipy_stats.entropy(pk, qk)
    print ""
    '''
    return 1.0*scipy_stats.entropy(pk, qk)


##############################################

def getSeedText():
    return "price Pricing of cloud and licenses license".lower().split(' ')

def getAllText():
    data = (' '.join(open(config.dataFileSrc,'r').readlines())).replace('\n',' ')
    data = data.split(' ')
    data = [token.lower() for token in data]
    return data

def getSelection(relatednessScore, alpha, budget):
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
    print tmp1
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

def main():

    loadInit()
    k = 5
    
    seedText = getSeedText()
    seedTextContext = getContext(seedText)
    
    allText = getAllText()
    lengthAllText = len(allText)
    tokensContext = [] #[0]*lengthAllText
    relatednessScore = [] #[0]*lengthAllText
    print len(allText)
    for i,token in enumerate(allText):
      tokensContext.append( getContext( allText[max(0,i-k):min(lengthAllText,i+k+1)] ) )
      relatednessScore.append( getRelatednessScore( tokensContext[i], seedTextContext ) )
      if i==2500:
          break
    mm=21
    ##print relatednessScore[0:mm]
    selection = getSelection( relatednessScore = relatednessScore, alpha = 1.5, budget = 150 )
    '''resText = [allText[i] for i,v in enumerate(selection) if v==1 and i<10]
    print ' '.join(resText)
    print allText[0:10]
    print selection
    print config.alpha
    '''
    m = len(relatednessScore)
    #print selection[0:m]
    ##print selection[0:mm]
    ##print selection[mm:2*mm-1]
    sel = [i for i,val in enumerate(selection) if (val==1 and i<m)]
    ##print sel
    ##sel2 = [i for i,val in enumerate(selection) if (val==1 and i>=m)]
    ##print sel2
    
    t = []
    for seli in sel:
      t.append(allText[seli])
    print t
main()