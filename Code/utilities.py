import config
import string
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords

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
    