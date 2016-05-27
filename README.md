# Gem-based-entity-knowledge-maintenance
Implementation of Taneva, B., &amp; Weikum, G. (2013, October). Gem-based entity-knowledge maintenance. CIKM 2013

Usage: <br>
-> Go to ./Code <br>
-> python Main.py -s <seedFile> -i <inputFile> [-h] [-m] [-o <outputFile>] [--alpha <alphaValue>] [--context <left|center|right>] <br>

s: Compulsory parameter <br>
&lt seedFile &gt : Path of seed file. If there are m inputs, there will be 2*m lines. For each input, first line contains the seed text, which is a list of space separated words. Second line contains budget, which is a positive integer <br>
<br>

i: Compulsory parameter <br>
&lt inputFile &gt : Path of data file. Contains the repository of text <br>
<br>

m: To ensure diversity among text portions (gems), MMR (Maximal Marginal Relevance) based idea is used. Firstly, gems are extracted for twice the required budget. Thereafter, relevance score of a gem is made equal to the Jaccard similarity of gem with the seed text. Overlap among gems is also calculated based on Jaccard similarity. Finally, MMR is employed to select a subset of extracted gems. <br>
<br>

alpha: Higher alpha translates to preference of selection of contiguos words - which may be desirable to capture novel information related to seed text between two sections highly related to seed text as per standard text similarity measures. <br>
<br>

context: It is eitone of following: 'left', 'center', or 'right'. 'Left' means context of a word is determined by a set of words to the left of the word in question in sentences. Analogous meaning for 'center' and 'right' <br>
<br>


python Main.py -i ../../data.txt -s ../seed.txt -m
 
 
