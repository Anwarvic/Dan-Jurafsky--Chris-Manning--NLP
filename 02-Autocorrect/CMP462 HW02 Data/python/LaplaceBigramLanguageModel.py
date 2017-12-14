from LaplaceUnigramLanguageModel import LaplaceUnigramLanguageModel
from collections import Counter
import math
class LaplaceBigramLanguageModel:

  def __init__(self, corpus):
    """Initialize your data structures in the constructor."""
    # TODO your code here
    uniModel = LaplaceUnigramLanguageModel(corpus)
    self.LaplaceUnigramCounts = uniModel.LaplaceUnigramCounts
    self.LaplaceBigramCounts = Counter()
    #The 'total' varaible is totally useless in this file, but i'm going
    #to use it in other files.
    self.total = uniModel.total
    self.train(corpus)

  def train(self, corpus):
    """ Takes a corpus and trains your language model. 
        Compute any counts or other corpus statistics in this function.
    """  
    # TODO your code here
    for sentence in corpus.corpus:
        temp = ""
        i = 0
        for datum in sentence.data:
            temp += datum.word
            i += 1
            temp += ' ' 
            if i ==2:
                self.LaplaceBigramCounts[temp.strip()] += 1
                temp = datum.word + ' '
                i = 1

  def group_i_words(self, sentence, i):
    """
    This function takes two arguments:
      - a sentece as a list
      - integer "i" which represents the number of words you want to group
    And it returns a list containing the word grouped out of that sentence putting every "i" words with each other. 
    So;
    >>> print example
    ['<s>', 'my', 'mum', 'goes', 'out', 'sometimes', '</s>']
    >>> print group_i_words(example, 2)
    ['<s> my', 'my mum', 'mum goes', 'goes out', 'out sometimes', 'sometimes </s>']
    >>> print group_i_words(test, 3)
    ['<s> my mum', 'my mum goes', 'mum goes out', 'goes out sometimes', 'out sometimes </s>']
    """
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
    V = 0.0
    for token in sentence:
      if self.LaplaceUnigramCounts[token] == 0:
        V += 1.0
    
    lst = self.group_i_words(sentence, 2)
    for token in lst:
      first_word = token.split(' ')[0]
      count1 = self.LaplaceBigramCounts[token]
      count2 = self.LaplaceUnigramCounts[first_word]
      score += math.log(count1+1.)
      score -= math.log(count2+V)
    return score
