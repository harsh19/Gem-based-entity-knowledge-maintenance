import config
import string
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import nltk

class Preprocess:
  wordnet_lemmatizer = ""
  stemmer = ""
  global_english_stopwords = []
  
  def __init__(self):
    self.excluded_characters = set(string.punctuation)
    if config.do_lemmatize:
        self.wordnet_lemmatizer =  WordNetLemmatizer()
    if config.do_stemming:
        self.stemmer = PorterStemmer() 
    self.global_english_stopwords = stopwords.words('english')
  
  ############################################
  # Utility functions
      
  def getLemmatized(self,word):
      return self.wordnet_lemmatizer.lemmatize(word)
      
  def getStemmed(self,word):
      return self.stemmer.stem(word)
  
  def ascii_only(self,s):
      ret = ""
      for ch in s:
          if ord(ch)<=128:
              ret =  ret + ch
      return ret
  
  def removePuntuation(self,s):
      return ''.join([ch for ch in s if ch not in excluded_characters])
  
  def getBigrams(self,words_list):
      m = len(words_list)
      i=0
      bigrams = []
      while i<m-1:
          bigrams.append(words_list[i] + " " + words_list[i+1])
          i = i+1
      return bigrams
      
  def getTrigrams(self,words_list):
      m = len(words_list)
      i = 0
      trigrams = []
      while i<m-2:
          trigrams.append(words_list[i] + " " + words_list[i+1] + " " + words_list[i+2])    
          i = i+1
      return trigrams
      
  def getTokens(self, s):
      s_tokens = nltk.word_tokenize(s)
      s_tokens = [preProcess(token) for token in s_tokens]
      s_tokens = [str(token) for token in s_tokens if len(token)>0]
      return s_tokens
      
  ########################################
  
  # using jaccard copefficient after removing stopwords
  def getSimilarity(self,s1,s2):
      cmn = 0
      ln1 = 0
      ln2 = 0
      s1 = set([w for w in s1 if w not in self.global_english_stopwords])
      s2 = set([w for w in s1 if w not in self.global_english_stopwords])
      num = 1+1.0*len(s1 & s2)
      den = 1+1.0*len(s1 | s2)
      return num/den
      
      

      
      
  
  
    