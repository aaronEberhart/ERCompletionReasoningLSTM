# PySynGenReas

## predicateTest.py

This file is simply a series of checks to confirm that the proper exceptions are raised for malformed predicate usage.

## reasonerTest.py

This is a simple Python ER syntax generator and reasoner with room for potential expansion in the future. Has complex logging built in for analysis, so it's not very fast, but it can describe its behavior quite well. There is a plain random generator, as well as a sequential random generator that creates semi-predictable structured patterns with randomness alongside.

## datasetGenerators.py

This file contains code to generate data for use in the LSTM. If desired, the code from this file can be imported so that it can output directly to functions in main.py, though this is generally time consuming and using the saved .npz files is much faster.

## main.py

This file builds a prediction model of the reasoner with an LSTM. It can be run from a python IDE or in the terminal. Output will be saved to a folder in the same directory as main.py, depending on which options are chosen.

This is the manual for the command line options:

usage: main.py [-h] [-e EPOCHS] [-l LEARNINGRATE] [-s] [-m] [-c CROSS]
               [-t TRAINFILE] [-v EVALFILE] [-p PERTURB]

optional arguments:

  -h, --help            show this help message and exit
  
  -e EPOCHS, --epochs EPOCHS
                        number of epochs for each system
                        
  -l LEARNINGRATE, --learningRate LEARNINGRATE
                        learning rate of each system
                        
  -s, --snomed          use SNOMED dataset
  
  -m, --mix             use test set from different souce than train
  -c CROSS, --cross CROSS
                        cross validation k
                        
  -t TRAINFILE, --trainfile TRAINFILE
                        training log file to save to
                        
  -v EVALFILE, --evalfile EVALFILE
                        eval log file to save to
                        
  -p PERTURB, --perturb PERTURB
                        disturb each kb for comparison


