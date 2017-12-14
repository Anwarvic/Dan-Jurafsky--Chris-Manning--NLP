class SpellingResult:
  numCorrect = 0
  numTotal = 0

  def __init__(self):
    self.numCorrect = 0
    self.numTotal = 0

  def __init__(self, correct, total):
    self.numCorrect = correct
    self.numTotal = total
  
  def getAccuracy(self):
    if self.numTotal == 0:
      return 0.0
    else:
      return float(self.numCorrect) / self.numTotal

  def __str__(self):
    return 'correct: %d total: %d accuracy: %f' % (self.numCorrect, self.numTotal, self.getAccuracy())
