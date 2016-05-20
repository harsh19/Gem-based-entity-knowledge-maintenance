import config
import string
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer

class Preprocess:
  wordnet_lemmatizer = ""
  stemmer = ""
  global_english_stopwords = ""
  
  def __init__(self):
    self.data = []
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
    