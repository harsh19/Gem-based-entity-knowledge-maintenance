
#------------------------------------------------------------------------------------------------------------------------------------------
do_remove_punctuation = True
do_remove_stopwords = True
do_lemmatize = True
do_stemming = True
include_bigrams = False
include_trigrams = False
cnt_threshhold = 4 # token should occur in at least these many documents

context_opts = ['contextBothSideDoc','contextLeft','contextRight']
context_opt = context_opts[0]
alpha = 10.0
useMMR = False
halfBudget = False

dataFileSrc = "data.txt"
seedFile = "seed.txt"
outputFile = "output.txt"
#------------------------------------------------------------------------------------------------------------------------------------------