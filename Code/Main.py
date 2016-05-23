#!/usr/bin/python

import sys, getopt
from gemExpansionPulp import GemExpansion
import config

usage = "python Main.py -s <seedFile> -i <inputFile> [-h] [-m] [-o <outputFile>] [--alpha <alphaValue>] [--context <left|center|right>]"

def main(argv):
  inputFile = 'data.txt'
  outputFile = ''
  halfBudget = False
  useMMR = False
  seedFile = ''
  print argv
  try:
    opts, args = getopt.getopt(argv,"hmi:o:s:",["ifile=","ofile=","alpha=","context="])
  except getopt.GetoptError:
    print 'Usage:', usage
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      halfBudget = True
    elif opt== '-m':
      useMMR = True
    elif opt== '--alpha':
      config.alpha = arg
    elif opt in ("-i", "--ifile"):
      inputFile = arg
      config.dataFileSrc = arg
    elif opt in ("-o", "--ofile"):
      outputFile = arg
      config.outputFile = outputFile
    elif opt == '-s':
      seedFile = arg
      config.seedFile = seedFile
    elif opt == 'context':
      if arg=='left':
        config.context_opt = context_opts[1]
      elif arg == 'center':
        config.context_opt = context_opts[0]
      elif arg == 'right':
        config.context_opt = context_opts[2]
      else:
        print "ERROR: Wrong argument value for 'context': Argument value has to be 'left','right', or 'center'"
        sys.exit(2)
        
  print 'Input file is ', inputFile
  print 'Output file is ', outputFile
  print 'MMR is set to ', useMMR
  print 'halfBudget is set to ', halfBudget
  
  config.halfBudget = halfBudget
  config.useMMR = useMMR
  
  if seedFile=='':
    print "seedFile has to be provided"
    sys.exit(2)
  if inputFile=='':
    print "input file path has to be provided"
    sys.exit(2)
    
  gem_expansion = GemExpansion()
  gem_expansion.main()


if __name__ == "__main__":
   main(sys.argv[1:])

  