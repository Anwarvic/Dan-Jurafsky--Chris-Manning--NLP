from collections import Counter
import math

class LaplaceUnigramLanguageModel:

  def __init__(self, corpus):
    """Initialize your data structures in the constructor."""
    # TODO your code here
    self.total = 0
    self.LaplaceUnigramCounts = Counter()
    self.train(corpus)

  def train(self, corpus):
    """ Takes a corpus and trains your language model. 
        Compute any counts or other corpus statistics in this function.
    """  
    # TODO your code here
    for sentence in corpus.corpus:
        for datum in sentence.data:
            self.LaplaceUnigramCounts[datum.word] += 1
            self.total += 1
  
  def score(self, sentence):
    """ Takes a list of strings as argument and returns the log-probability of the 
        sentence using your language model. Use whatever data you computed in train() here.
    """
    # TODO your code here
    score = 0.0
    for token in sentence:
      count = self.LaplaceUnigramCounts[token]
      score += math.log(count+1)
      score -= math.log(self.total)
    return score
    
