from collections import defaultdict, Counter
import pickle


class Lexicon:
    """
    Simple default implementation of a lexicon, which scores word,
    tag pairs with a smoothed estimate of P(tag|word)/P(tag).
    NOTE:
    All the tags here are Terminal tags. In other words, you can find tags like ('N', 'P', 'V', ...) here,
    but Non-terminal tags like ('NP', 'PP', ...) won't be here.

    Instance variables:
      -> word_to_tag_counters: 
         like so {'crabs': {'N': 1.0}, 'claws': {'N': 2.0}, ...}
      
      -> total_tokens:  
         it's the total counts of tags in whole corpus
      
      -> total_word_types:
         it's the summation of the tags of each tree. So, assume the corpus has 3 trees in it, and 
         each tree has 3 tags. Then, the total_word_types will be 9
         
      -> tag_counter: 
         it's the count of every tag like so {'P': 2.0, 'V': 3.0, 'N': 8.0, ...}
      
      -> word_counter:
         it's the count of every word like so {'crabs': 1.0, 'people': 1.0, ...}
      
      -> type_to_tag_counter:
         it's the count of words that have been assigned to a specific tag. 
         So, {'P': 1.0, 'V': 2.0, 'N': 5.0}) means that 'N' has been assigned to 5 different words, 
         and 'V' has been assigned to 2 different words.

      -> word_to_tag_counters:
         it's the count of a certain tag being assigned to a certain word. For example
         word_to_tag_counters['claws']['N']=2.0 means that the tag 'N' has been assigned to the word
         'claws' twice
    """

    def __init__(self):
        """
        Builds a lexicon from the observed tags in a list of training
        trees.
        """
        self.total_tokens = 0.0
        self.total_word_types = 0.0
        self.word_to_tag_counters = defaultdict(Counter)
        self.tag_counter = defaultdict(float)
        self.word_counter = defaultdict(float)
        self.type_to_tag_counter = defaultdict(float)


    def train(self, train_trees):
        for train_tree in train_trees:
            words = train_tree.get_yield() #returns only the words of the tree
            tags = train_tree.get_preterminal_yield() # returns only the terminal tags of the tree
            # print words, tags
            for word, tag in zip(words, tags):

                self.tally_tagging(word, tag)


    def tally_tagging(self, word, tag):
        if not self.is_known(word):
            self.total_word_types += 1
            self.type_to_tag_counter[tag] += 1
        self.total_tokens += 1
        self.tag_counter[tag] += 1
        self.word_counter[word] += 1
        self.word_to_tag_counters[word][tag] += 1


    def get_all_tags(self):
        return self.tag_counter.keys()


    def is_known(self, word):
        return word in self.word_counter


    def score_tagging(self, word, tag):
        """
        Simple default implementation of a lexicon, which scores word,
        tag pairs with a smoothed estimate of P(tag|word)/P(tag).
        """
        p_tag = float(self.tag_counter[tag]) / self.total_tokens
        c_word = float(self.word_counter[word])
        c_tag_and_word = float(self.word_to_tag_counters[word][tag])
        if c_word < 10:
            c_word += 1
            c_tag_and_word += float(self.type_to_tag_counter[tag]) / self.total_word_types
        p_word = (1.0 + c_word) / (self.total_tokens + self.total_word_types)
        p_tag_given_word = c_tag_and_word / c_word
        return p_tag_given_word / p_tag * p_word


    def read_lexicon(self, pickle_file):
      with open("lexicon.pickle", "r") as fin:
        lst = pickle.load(fin)
      
      self.total_tokens = lst[0]
      self.total_word_types = lst[1]
      self.word_to_tag_counters = lst[2]
      self.tag_counter = lst[3]
      self.word_counter = lst[4]
      self.type_to_tag_counter = lst[5]






def print_dictionary(d):
  #Helps with understanding these motherf***ing dictionaries.
  for k, v in d.iteritems():
    if type(v) == defaultdict:
      for k2, v2 in v.iteritems():
        print k, k2, v2
    else:
      print k, v


if __name__ == "__main__":
    from read import *
    base_path = '../data/parser/miniTest'

    train_trees = read_trees(base_path, 1, 3)
    l = Lexicon()
    l.train(train_trees)
    print l.tag_counter.keys()
    print l.score_tagging("cats", "N")
    print l.score_tagging("claws", "N")
    print l.score_tagging("walls", "N")
    # print print_dictionary(l.word_to_tag_counters)

    # print l.total_tokens #13
    # print l.total_word_types #8
