from LaplaceUnigramLanguageModel import LaplaceUnigramLanguageModel
import copy, math

class GoodTuringUnigramLanguageModel:
  def __init__(self, corpus):
    """Initialize your data structures in the constructor."""
    # TODO your code here
    model = LaplaceUnigramLanguageModel(corpus)
    self.Unicounts = model.LaplaceUnigramCounts
    self.newCounts = copy.copy(self.Unicounts)
    self.N = model.total
    self.N_1 = self.Unicounts.values().count(1)
    self.train()

  def train(self):
    """ Takes a corpus and trains your language model. 
        Compute any counts or other corpus statistics in this function.
    """  
    # TODO your code here
    for key in self.Unicounts:
        c = self.Unicounts[key]
        N_c_inc = self.Unicounts.values().count(c+1)
        if N_c_inc != 0:
            N_c = self.Unicounts.values().count(c)
            self.newCounts[key] = ((c+1.)*N_c_inc/N_c)


  def score(self, sentence):
    """ Takes a list of strings as argument and returns the log-probability of the 
        sentence using your language model. Use whatever data you computed in train() here.
    """
    # TODO your code here
    score = 0.0
    for token in sentence:
      count = self.newCounts[token]
      if count == 0:
        count = float(self.N_1)
      score += math.log(count)
      score -= math.log(self.N)
    return score

    
