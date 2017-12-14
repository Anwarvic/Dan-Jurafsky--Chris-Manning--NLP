import re
from EditModel import *

class Datum:
  word = '' # the correct word
  error = '' # the error word (if any)

  def __init__(self):
    self.word = ''
    self.error = ''

  def __init__(self, word, error=''):
    self.word = word
    self.error = error

  def fixError(self):
    return Datum(self.word, '')

  def hasError(self):
    if self.error:
      return True
    else:
      return False

  def isValidTest(self):
    """Returns true if the error is within edit distance one and contains no numerics/punctuation."""
    if not self.hasError():
      return False
    distance = dameraulevenshtein(self.word, self.error) 
    if(distance > 1):
      return False
    regex = '.*[^a-zA-Z].*'
    if re.match(regex, self.word) or re.match(regex, self.error):
      return False
    return True

  def __str__(self):
    """Format: word (error)?"""
    rep = self.word 
    if self.hasError():
      rep = rep + " (" + self.error + ")"
    return rep

