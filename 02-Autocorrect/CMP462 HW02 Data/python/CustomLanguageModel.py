from LaplaceBigramLanguageModel import *
from collections import Counter, defaultdict
import math


class CustomLanguageModel:
  def __init__(self, corpus):
    """Initialize your data structures in the constructor."""
    # TODO your code here
    model = LaplaceBigramLanguageModel(corpus)
    self.UnigramCounts = model.LaplaceUnigramCounts
    self.total = model.total
    self.BigramCounts = model.LaplaceBigramCounts
    self.BeforeCounts = defaultdict(set)
    self.AfterCounts = defaultdict(set)
    self.train()

  def group_i_words(self, sentence, i):
    output = []
    cart = ""

    for j in range(len(sentence)):
        k = j
        while (k < j+i and k < len(sentence)):
            if type(sentence[k]) == str:
                cart += sentence[k] + ' '
            else:
                cart += sentence[k].word + ' '
            k += 1
        output.append(cart.strip())
        cart = ""
        j -= (i-1)
    return output[:-(i-1)]

  def train(self):
    """ Takes a corpus and trains your language model. 
        Compute any counts or other corpus statistics in this function.
    """  
    # TODO your code here
    for key in self.BigramCounts.keys():
      first_word, second_word = key.split(' ')
      self.AfterCounts[first_word].add(second_word)
      self.BeforeCounts[second_word].add(first_word)
    


  def score(self, sentence):
    """ Takes a list of strings as argument and returns the log-probability of the 
        sentence using your language model. Use whatever data you computed in train() here.
    """
    # TODO your code here
    score = 0.0
    d = 0.75
    lst = self.group_i_words(sentence, 2)
    for token in lst:
      first_word, second_word = token.split(' ')
      count1 = self.BigramCounts[token]
      count2 = self.UnigramCounts[first_word]
      _lambda = d/(count2+1.)*len(self.AfterCounts[first_word])
      if count1 == 0:
        d = 0.9
      p_continuation =  float(len(self.BeforeCounts[second_word]))/self.total
      first_term = ( (count1-d)/(count2+1.) )
      if first_term == 0:
        score += (_lambda*p_continuation)
      else:
        score += first_term + (_lambda*p_continuation)
    return score

    
