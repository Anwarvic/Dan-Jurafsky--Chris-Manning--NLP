from LaplaceUnigramLanguageModel import LaplaceUnigramLanguageModel
from LaplaceBigramLanguageModel import *
from collections import Counter
import math



class StupidBackoffLanguageModel:
  def __init__(self, corpus):
    """Initialize your data structures in the constructor."""
    # TODO your code here
    unigramModel = LaplaceUnigramLanguageModel(corpus)
    self.total = unigramModel.total
    bigramModel = LaplaceBigramLanguageModel(corpus)
    self.UnigramCounts = unigramModel.LaplaceUnigramCounts
    self.BigramCounts = bigramModel.LaplaceBigramCounts
    

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

  def score(self, sentence):
    """ Takes a list of strings as argument and returns the log-probability of the 
        sentence using your language model. Use whatever data you computed in train() here.
    """
    # TODO your code here
    score = 0.0
    lst = self.group_i_words(sentence, 2)
    for token in lst:
      first_word = token.split(' ')[0]
      count_bigram = self.BigramCounts[token]
      if count_bigram > 0:
        count_unigram = self.UnigramCounts[first_word]
        score += math.log(count_bigram)
        score += math.log(0.4)
        score -= math.log(count_unigram)
        
      else:
        second_word = token.split(' ')[1]
        count_unigram = self.UnigramCounts[second_word]
        score += math.log(count_unigram+1)
        score += math.log(0.4)
        score -= math.log(self.total)

    return  score

