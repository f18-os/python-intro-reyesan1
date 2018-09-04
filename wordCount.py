#! /usr/bin/env python3

###########################################################################################
## Python program that takes in as input two files, an input and output file. 
## Functionality includes:
##   - Keeps track of the total the number of times each word occurs in the input text file
##   - Excludes white space and punctuation
##   - Is case-insensitive
##   - Prints out to the output file (overwriting if it exists) the list of words sorted in 
##     descending order with their respective totals separated by a space, one word per line
############################################################################################

import sys        # command line arguments
import re         # regular expression tools
import os         # checking if file exists
import subprocess # executing program
from subprocess import  Popen # to call script with arguments

# Set input and output files
if len(sys.argv) is not 3:
    print("Correct usage: wordCount.py <input text file> <output text file>")
    exit()

# Input file
textFname = sys.argv[1]

# Output file
outputFname = sys.argv[2]

# Make sure text files exist
if not os.path.exists(textFname):
    print ("text file input %s doesn't exist! Exiting" % textFname)
    exit()

# Make sure output file exists
if not os.path.exists(outputFname):
    print ("output file %s doesn't exist! Exiting" % outputFname)
    exit()

# Dictionary to count
count1 = {}

# Reading text file
with open(textFname, 'r') as inputFile:
    for line in inputFile:
        # Get rid of newline characters
        line = line.strip()
        # Split line on whitespace and punctuation
        word = re.split("\.|,|[ \t]|:|;|-|--|['\"]", line)
        for w in word:
            if w == '':
                continue
            elif w.lower() in count1.keys():
                count1[w.lower()]+=1
            else:
                count1[w.lower()]=1

# Writing list of words with respective totals separated by a space
with open(outputFname, 'w') as outputFile:
    for i in count1:
        outputFile.write("%s %s\n" % (i, count1[i]))

# Using script to sort file and print the results on the terminal
Process=Popen('./sort.sh %s' % (outputFname), shell=True)
