from Datum import Datum
from Sentence import Sentence

class HolbrookCorpus:
  corpus = [] # list of sentences

  def __init__(self, filename=None):
    if filename:
      self.read_holbrook(filename)
    else:
      self.corpus = []

  def processLine(self, line):
   line = line.strip()
   line = line.lower() 
   line = line.replace('"','') 
   line = line.replace(',', '')
   line = line.replace('.','') 
   line = line.replace('!','') 
   line = line.replace("'",'') 
   line = line.replace(":",'') 
   line = line.replace(";",'') 
   if line == '':
     return None
   processed_tokens = Sentence() 
   processed_tokens.append(Datum("<s>")) #start symbol
   tokens = line.split()
   i = 0
   while i < len(tokens):
     token = tokens[i]
     if token == '<err':
       targ = tokens[i+1]
       targ_splits = targ.split('=')
       correct_token = targ_splits[1][:-1] # chop off the trailing '>'
       correct_token_splits = correct_token.split()
       if len(correct_token_splits) > 2: # targ with multiple words
         #print 'targ with multiple words: "%s"' % targ
         for correct_word in correct_token_splits:
           processed_tokens.append(Datum(correct_word))
       elif tokens[i+3] != '</err>':
         processed_tokens.append(Datum(correct_token))
       else:
         incorrect_token = tokens[i+2]
         processed_tokens.append(Datum(correct_token, incorrect_token))    
       i += tokens[i:].index('</err>') + 1 # update index
     else: # regular word
       processed_tokens.append(Datum(token))
       i += 1
   processed_tokens.append(Datum("</s>"))
   return processed_tokens
  
  def read_holbrook(self, filename):
    """Read in holbrook data, returns a list (sentence) of list(words) of lists(alternatives).
       The first item in each word list is the correct word."""
    f = open(filename)
    self.corpus = []
    for line in f:
      sentence = self.processLine(line)      
      if sentence:
        self.corpus.append(sentence)
  
  
  def generateTestCases(self):  
    """Returns a list of sentences with exactly 1 elligible spelling error"""
    testCases = [] # list of Sentences
    for sentence in self.corpus:
      cleanSentence = sentence.cleanSentence()
      for i in range(0, len(sentence)):
        datum_i = sentence.get(i)
        if datum_i.hasError() and datum_i.isValidTest():
          testSentence = Sentence(cleanSentence)
          testSentence.put(i, datum_i)
          testCases.append(testSentence)
    return testCases

  
  def slurpString(self, contents):
    """Reads a clean corpus from string instead of file. Used for submission."""
    lines = contents.split('\n')
    self.corpus = []
    for line in lines:
      sentence = self.processLine(line)
      if sentence:
        self.corpus.append(sentence)

  def __str__(self):
    str_list = []
    for sentence in self.corpus:
      str_list.append(str(sentence))
    return '\n'.join(str_list)   





if __name__ == "__main__":
  h = HolbrookCorpus('../data/holbrook-tagged-dev.dat')
  print h.generateTestCases()[0]