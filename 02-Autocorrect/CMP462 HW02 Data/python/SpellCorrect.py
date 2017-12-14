import math
from Datum import Datum
from Sentence import Sentence
from HolbrookCorpus import HolbrookCorpus
from UniformLanguageModel import UniformLanguageModel
from StupidBackoffLanguageModel import StupidBackoffLanguageModel
from LaplaceUnigramLanguageModel import LaplaceUnigramLanguageModel
from GoodTuringUnigram import GoodTuringUnigramLanguageModel
from LaplaceBigramLanguageModel import LaplaceBigramLanguageModel
from CustomLanguageModel import CustomLanguageModel
from SpellingResult import SpellingResult
from EditModel import EditModel
import re, collections

# Modified version of Peter Norvig's spelling corrector
"""Spelling Corrector.

Copyright 2007 Peter Norvig. 
Open source code under MIT license: http://www.opensource.org/licenses/mit-license.php
"""



class SpellCorrect:
  """Holds edit model, language model, corpus. trains"""
  

  def __init__(self, lm, corpus):
    """initializes the language model."""
    self.languageModel = lm
    self.editModel = EditModel('../data/count_1edit.txt', corpus)


  def evaluate(self, corpus):  
    """Tests this speller on a corpus, returns a SpellingResult"""
    numCorrect = 0
    numTotal = 0
    testData = corpus.generateTestCases()
    for sentence in testData:
      if sentence.isEmpty():
        continue
      errorSentence = sentence.getErrorSentence()
      hypothesis = self.correctSentence(errorSentence)
      if sentence.isCorrection(hypothesis):
        numCorrect += 1
      numTotal += 1
    return SpellingResult(numCorrect, numTotal)

  def correctSentence(self, sentence):
    """Takes a list of words, returns a corrected list of words."""
    if len(sentence) == 0:
      return []
    argmax_i = 0
    argmax_w = sentence[0]
    maxscore = float('-inf')
    maxlm = float('-inf')
    maxedit = float('-inf')

    # skip start and end tokens
    for i in range(1, len(sentence) - 1):
      word = sentence[i]
      editProbs = self.editModel.editProbabilities(word)
      for alternative, editscore in editProbs.iteritems():
        if alternative == word:
          continue
        sentence[i] = alternative
        lmscore = self.languageModel.score(sentence)
        if editscore != 0:
          editscore = math.log(editscore)
        else:
          editscore = float('-inf')
        score = lmscore + editscore
        if score >= maxscore:
          maxscore = score
          maxlm = lmscore
          maxedit = editscore
          argmax_i = i
          argmax_w = alternative

      sentence[i] = word # restores sentence to original state before moving on
    argmax = list(sentence) # copy it
    argmax[argmax_i] = argmax_w # correct it
    return argmax


  def correctCorpus(self, corpus): 
    """Corrects a whole corpus, returns a JSON representation of the output."""
    string_list = [] # we will join these with commas,  bookended with []
    sentences = corpus.corpus
    for sentence in sentences:
      uncorrected = sentence.getErrorSentence()
      corrected = self.correctSentence(uncorrected) # List<String>
      word_list = '["%s"]' % '","'.join(corrected)
      string_list.append(word_list)
    output = '[%s]' % ','.join(string_list)
    return output


    
def main():
  """Trains all of the language models and tests them on the dev data. Change devPath if you
     wish to do things like test on the training data."""
  trainPath = '../data/holbrook-tagged-train.dat'
  trainingCorpus = HolbrookCorpus(trainPath)

  devPath = '../data/holbrook-tagged-dev.dat'
  devCorpus = HolbrookCorpus(devPath)

  print 'Uniform Language Model: '
  uniformLM = UniformLanguageModel(trainingCorpus)
  uniformSpell = SpellCorrect(uniformLM, trainingCorpus)
  uniformOutcome = uniformSpell.evaluate(devCorpus) 
  print str(uniformOutcome), '\n'

  print 'Laplace Unigram Language Model: ' 
  laplaceUnigramLM = LaplaceUnigramLanguageModel(trainingCorpus)
  laplaceUnigramSpell = SpellCorrect(laplaceUnigramLM, trainingCorpus)
  laplaceUnigramOutcome = laplaceUnigramSpell.evaluate(devCorpus)
  print str(laplaceUnigramOutcome), '\n'

  #It has (accuracy: 0.012739) because of the small corpus (I think ^_^)
  print 'Good-Turing Unigram Language Model: '
  GoodTuringLM = GoodTuringUnigramLanguageModel(trainingCorpus)
  GoodTuringSpell = SpellCorrect(GoodTuringLM, trainingCorpus)
  GoodTuringOutcome = GoodTuringSpell.evaluate(devCorpus)
  print str(GoodTuringOutcome), '\n'

  #This model takes some time, about (70) seconds
  print 'Laplace Bigram Language Model: '
  laplaceBigramLM = LaplaceBigramLanguageModel(trainingCorpus)
  laplaceBigramSpell = SpellCorrect(laplaceBigramLM, trainingCorpus)
  laplaceBigramOutcome = laplaceBigramSpell.evaluate(devCorpus)
  print str(laplaceBigramOutcome), '\n'

  #This model takes some time, about (70) seconds
  print 'Stupid Backoff Language Model: '  
  sbLM = StupidBackoffLanguageModel(trainingCorpus)
  sbSpell = SpellCorrect(sbLM, trainingCorpus)
  sbOutcome = sbSpell.evaluate(devCorpus)
  print str(sbOutcome), '\n'

  #This model takes some time, about (70) seconds
  print 'Custom Language Model: '
  customLM = CustomLanguageModel(trainingCorpus)
  customSpell = SpellCorrect(customLM, trainingCorpus)
  customOutcome = customSpell.evaluate(devCorpus)
  print str(customOutcome), '\n'

if __name__ == "__main__":
    main()

"""
The output would be:
Uniform Language Model: 
correct: 31 total: 471 accuracy: 0.065817 

Laplace Unigram Language Model: 
correct: 52 total: 471 accuracy: 0.110403 

Good-Turing Unigram Language Model: 
correct: 6 total: 471 accuracy: 0.012739 

Laplace Bigram Language Model: 
correct: 61 total: 471 accuracy: 0.129512 

Stupid Backoff Language Model: 
correct: 87 total: 471 accuracy: 0.184713 

Custom Language Model: 
correct: 114 total: 471 accuracy: 0.242038 

"""