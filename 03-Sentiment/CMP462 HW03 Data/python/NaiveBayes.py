# NLP Programming Assignment #3
# NaiveBayes
# 2012

#
# The area for you to implement is marked with TODO!
# Generally, you should not need to touch things *not* marked TODO
#
# Remember that when you submit your code, it is not run from the command line
# and your main() will *not* be run. To be safest, restrict your changes to
# addExample() and classify() and anything you further invoke from there.
#

from collections import Counter
import os
import math

class NaiveBayes:
  class Example:
    """Represents a document with a label. klass is 'pos' or 'neg' by convention.
       words is a list of strings.
    """
    def __init__(self):
      self.klass = ''
      self.words = []

  class TrainSplit:
    """Represents a set of training/testing data. self.train is a list of Examples, as is self.test.
    """
    def __init__(self):
      self.train = []
      self.test = []

  def __init__(self):
    """NaiveBayes initialization"""
    self.FILTER_STOP_WORDS = False
    self.BOOLEAN = False
    self.stopList = set(self.readFile('../data/english.stop'))
    self.numFolds = 10
    #The following two Counter objects are used to save the words in the positive reviews 
    #and the negative ones respectively
    self.posDict = Counter()
    self.negDict = Counter()


  #############################################################################
  # TODO TODO TODO TODO TODO

  def addExample(self, klass, words):
    """
     * TODO
     * Train your model on an example document with label klass ('pos' or 'neg') and
     * words, a list of strings.
     * You should store whatever data structures you use for your classifier
     * in the NaiveBayes class.
     * Returns nothing
    """
    if self.BOOLEAN:
      for w in set(words):
        if klass == 'pos':
          self.posDict[w] += 1
        elif klass == 'neg':
          self.negDict[w] += 1
    else:
      for w in words:
        if klass == 'pos':
          self.posDict[w] += 1
        elif klass == 'neg':
          self.negDict[w] += 1


  def classify(self, words):
    """ TODO
      'words' is a list of words to classify. Return 'pos' or 'neg' classification.
    """
    V = len(set(self.posDict.keys() + self.negDict.keys()))
    posLen = sum(self.posDict.values())
    negLen = sum(self.negDict.values())
    
    #We used 0.5, because we are using 10 fold out of 1000 positive reviews which will be 900 for train and 100 for test. 
    #And the same with negative reviews. 
    #So, we have 900 positive reviews and 900 negative reviews which makes the probability of positive reviews is 0.5 of the 
    #whole corpus. And the same happens with negative reviews
    posScore, negScore = math.log(0.5), math.log(0.5)

    for w in words:
      posScore += math.log( (self.posDict[w]+1.) / (posLen + V) )
      negScore += math.log( (self.negDict[w]+1.) / (negLen + V) )

    # print posScore, negScore
    if posScore > negScore:
      return 'pos'
    else:
      return 'neg'

  def filterStopWords(self, words):
    """
    * TODO
    * Filters stop words found in self.stopList.
    """
    output = []
    for i in words:
      if i in self.stopList or i.strip() == '':
        pass
      else:
        output.append(i)

    return output

  # TODO TODO TODO TODO TODO
  #############################################################################
  def readFile(self, fileName):
    """
     * Code for reading a file.  you probably don't want to modify anything here,
     * unless you don't like the way we segment files.
    """
    contents = []
    f = open(fileName)
    for line in f:
      contents.append(line)
    f.close()
    result = self.segmentWords('\n'.join(contents))
    return result

  def segmentWords(self, s):
    """
     * Splits lines on whitespace for file reading
    """
    return s.split()

  def trainSplit(self, trainDir):
    """Takes in a trainDir, returns one TrainSplit with train set."""
    split = self.TrainSplit()
    posTrainFileNames = os.listdir('%s/pos/' % trainDir)
    negTrainFileNames = os.listdir('%s/neg/' % trainDir)
    for fileName in posTrainFileNames:
      example = self.Example()
      example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
      example.klass = 'pos'
      split.train.append(example)
    for fileName in negTrainFileNames:
      example = self.Example()
      example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
      example.klass = 'neg'
      split.train.append(example)
    return split

  def train(self, split):
    for example in split.train:
      words = example.words
      if self.FILTER_STOP_WORDS:
        words =  self.filterStopWords(words)
      self.addExample(example.klass, words)

  def buildSplits(self):
    """Builds the splits for training/testing"""
    trainData = []
    testData = []
    splits = []
    trainDir = '../data/imdb1'
    print '[INFO]\tPerforming %d-fold cross-validation on data set:\t%s' % (self.numFolds, trainDir)

    posTrainFileNames = os.listdir('%s/pos/' % trainDir)
    negTrainFileNames = os.listdir('%s/neg/' % trainDir)
    for fold in range(0, self.numFolds):
      split = self.TrainSplit()
      for fileName in posTrainFileNames:
        example = self.Example()
        example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
        example.klass = 'pos'
        if fileName[2] == str(fold):
          split.test.append(example)
        else:
          split.train.append(example)
      for fileName in negTrainFileNames:
        example = self.Example()
        example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
        example.klass = 'neg'
        if fileName[2] == str(fold):
          split.test.append(example)
        else:
          split.train.append(example)
      splits.append(split)
    return splits


def main():
  nB = NaiveBayes()
  splits = nB.buildSplits()

  for _ in range(2):
    for _ in range(2):
      #FILTER_STOP_WORDS and BOOLEAN is False by default
      if nB.FILTER_STOP_WORDS:
        if nB.BOOLEAN:
          print "[INFO]\tTraining Boolean classifier with filtering STOP WORDS:"
        else:
          print "[INFO]\tTraining classifier with filtering STOP WORDS:"
      else:
        if nB.BOOLEAN:
          print "[INFO]\tTraining Boolean classifier without filtering STOP WORDS:"
        else:
          print "[INFO]\tTraining classifier without filtering STOP WORDS:"

      avgAccuracy = 0.0
      fold = 0
      for split in splits:
        classifier = NaiveBayes()
        accuracy = 0.0
        for example in split.train:
          words = example.words
          if nB.FILTER_STOP_WORDS:
            words =  classifier.filterStopWords(words)
          classifier.addExample(example.klass, words)

        for example in split.test:
          words = example.words
          if nB.FILTER_STOP_WORDS:
            words =  classifier.filterStopWords(words)
          guess = classifier.classify(words)
          if example.klass == guess:
            accuracy += 1.0

        accuracy = accuracy / len(split.test)
        avgAccuracy += accuracy
        print '\t[INFO]\tFold %d Accuracy: %f' % (fold, accuracy)
        fold += 1
      avgAccuracy = avgAccuracy / fold
      print '\t[INFO]\tAccuracy: %f' % avgAccuracy
      nB.FILTER_STOP_WORDS = True
    nB.BOOLEAN = True
    nB.FILTER_STOP_WORDS = False

if __name__ == "__main__":
    main()
"""
The output would be:
[INFO]  Performing 10-fold cross-validation on data set:  ../data/imdb1
[INFO]  Training classifier without filtering STOP WORDS:
  [INFO]  Fold 0 Accuracy: 0.765000
  [INFO]  Fold 1 Accuracy: 0.850000
  [INFO]  Fold 2 Accuracy: 0.835000
  [INFO]  Fold 3 Accuracy: 0.825000
  [INFO]  Fold 4 Accuracy: 0.815000
  [INFO]  Fold 5 Accuracy: 0.820000
  [INFO]  Fold 6 Accuracy: 0.835000
  [INFO]  Fold 7 Accuracy: 0.825000
  [INFO]  Fold 8 Accuracy: 0.755000
  [INFO]  Fold 9 Accuracy: 0.840000
  [INFO]  Accuracy: 0.816500
[INFO]  Training classifier with filtering STOP WORDS:
  [INFO]  Fold 0 Accuracy: 0.760000
  [INFO]  Fold 1 Accuracy: 0.825000
  [INFO]  Fold 2 Accuracy: 0.825000
  [INFO]  Fold 3 Accuracy: 0.830000
  [INFO]  Fold 4 Accuracy: 0.800000
  [INFO]  Fold 5 Accuracy: 0.830000
  [INFO]  Fold 6 Accuracy: 0.830000
  [INFO]  Fold 7 Accuracy: 0.835000
  [INFO]  Fold 8 Accuracy: 0.755000
  [INFO]  Fold 9 Accuracy: 0.820000
  [INFO]  Accuracy: 0.811000
[INFO]  Training Boolean classifier without filtering STOP WORDS:
  [INFO]  Fold 0 Accuracy: 0.765000
  [INFO]  Fold 1 Accuracy: 0.850000
  [INFO]  Fold 2 Accuracy: 0.835000
  [INFO]  Fold 3 Accuracy: 0.825000
  [INFO]  Fold 4 Accuracy: 0.815000
  [INFO]  Fold 5 Accuracy: 0.820000
  [INFO]  Fold 6 Accuracy: 0.835000
  [INFO]  Fold 7 Accuracy: 0.825000
  [INFO]  Fold 8 Accuracy: 0.755000
  [INFO]  Fold 9 Accuracy: 0.840000
  [INFO]  Accuracy: 0.816500
[INFO]  Training Boolean classifier with filtering STOP WORDS:
  [INFO]  Fold 0 Accuracy: 0.760000
  [INFO]  Fold 1 Accuracy: 0.825000
  [INFO]  Fold 2 Accuracy: 0.825000
  [INFO]  Fold 3 Accuracy: 0.830000
  [INFO]  Fold 4 Accuracy: 0.800000
  [INFO]  Fold 5 Accuracy: 0.830000
  [INFO]  Fold 6 Accuracy: 0.830000
  [INFO]  Fold 7 Accuracy: 0.835000
  [INFO]  Fold 8 Accuracy: 0.755000
  [INFO]  Fold 9 Accuracy: 0.820000
  [INFO]  Accuracy: 0.811000

"""