#!/bin/bash

#################################################################################
## Script that takes as input a file and overwrites it as sorted and prints it
## on the terminal
#################################################################################

sort $1 -o $1
cat $1
