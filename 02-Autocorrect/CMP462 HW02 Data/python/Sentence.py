from Datum import Datum


class Sentence:
  """Contains a list of Datums."""

  def __init__(self, sentence=[]):
    if(type(sentence) == type([])):
      self.data = list(sentence) 
    else:
      self.data = list(sentence.data)
  
  def getErrorSentence(self):
    """Returns a list of strings with the sentence containing all errors."""
    errorSentence = []
    for datum in self.data:
      if datum.hasError():
        errorSentence.append(datum.error)
      else:
        errorSentence.append(datum.word)
    return errorSentence

  def getCorrectSentence(self):
    """Returns a list of strings with the sentence containing all corrections."""
    correctSentence = []
    for datum in self.data:
      if datum.hasError():
        correctSentence.append(datum.word)
      else:
        correctSentence.append(datum.word)
    return correctSentence

  def isCorrection(self, candidate):
    """Checks if a list of strings is a correction of this sentence."""
    if len(self.data) != len(candidate):
      return False
    for i in range(len(self.data)):
      if candidate[i] != self.data[i].word:
        return False
    return True

  def getErrorIndex(self):
    for i in range(0, len(self.data)):
      if self.data[i].hasError():
        return i
    return -1

  def len(self):
    return len(self.data)

  def get(self, i):
    return self.data[i]

  def put(self, i, val):
    self.data[i] = val

  def cleanSentence(self):
    """Returns a new sentence with all datum's having error removed."""
    sentence = Sentence()
    for datum in self.data:
      clean = datum.fixError()
      sentence.append(clean)
    return sentence

  def isEmpty(self):
    return len(self.data) == 0

  def append(self, item):
    self.data.append(item)

  def __len__(self):
    return len(self.data)

  def __str__(self):
    str_list = []
    for datum in self.data:
      str_list.append(str(datum))
    return ' '.join(str_list)

"""
Here, i'm going to explain every method of the Sentence() class:

- Sentence() class takes a list of Datums like so;
  >>> from Datum import Datum
  >>>
  >>> lst = [Datum("i"), Datum("love", "lov"), Datum("girls")]
  >>> s = Sentence(lst)
  >>> print s
  i love (lov) girls
  >>>
  >>> # The following are some simple methods:
  >>> print len(s)
  3
  >>> print s.get(1)
  love (lov)
  >>> s.put(1, Datum('hate'))
  >>> print s
  i hate girls
  >>> print s.isEmpty()
  False
  >>> s.append("sooo much")
  >>> print s
  i love (lov) girls sooo much
  >>> print len(s)
  4


- Sentence().data: is a list of list of Datums, so;
  >>> for d in s.data:
  ...    print d
  i
  love (lov)
  girls

- getErrorSentence(): this method returns the Error of the word if exists. So;
  >>> s.getErrorSentence()
  ['i', 'lov', 'girls']

- getCorrectSentence(): this method returns the right word. So;
  >>> s.getCorrectSentence()
  ['i', 'love', 'girls']

- cleanSentence(): this method returns the right word but as a sentence. so;
  >>> print s.cleanSentence()
  i love girls

- isCorrection(): this method takes a list of strings and it iterates every word in the list and compare it with
  the Datum instances in the 'data' variable. So;
  >>> s.isCorrection(["i", "love", "girls"])
  True
  >>> s.isCorrection(["i", "lov", "girls"])
  False
  >>> s.isCorrection(["i", "lov", "Girls"])
  False

- getErrorIndex(): this method returns the index of the wrong word in the sentence and returns -1 if 
  there is no error. So;
  >>> s.getErrorIndex()
  1

"""
if __name__ == "__main__":
  lst = [Datum("i"), Datum("love", "lov"), Datum("girls")]
  s = Sentence(lst)
  s.put(0, Datum('I'))
  print s.isCorrection(["I", "love", "girls"])