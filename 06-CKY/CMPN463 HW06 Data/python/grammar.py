from collections import defaultdict
from rules import *
from tree_annotations import TreeAnnotations
import pickle


class Grammar:
    """
    Simple implementation of a PCFG grammar, offering the ability to
    look up rules by their child symbols. Rule probability estimates
    are just relative frequency estimates off of training trees.
    
    Instance variables:
      -> binary_rules_by_left_child:


      -> binary_rules_by_right_child:


      -> unary_rules_by_child
    """

    def __init__(self):
        self.unary_rules_by_child = defaultdict(list)
        self.binary_rules_by_left_child = defaultdict(list)
        self.binary_rules_by_right_child = defaultdict(list)


    def train(self, train_trees):
        #CAUTION: it Takes binarized trees as an input
        unary_rule_counter = defaultdict(lambda: 0)
        binary_rule_counter = defaultdict(lambda: 0)
        symbol_counter = defaultdict(lambda: 0)

        for train_tree in train_trees:
            self.tally_tree(train_tree, symbol_counter, unary_rule_counter, binary_rule_counter)
        for unary_rule in unary_rule_counter:
            unary_prob = float(unary_rule_counter[unary_rule]) / symbol_counter[unary_rule.parent]
            unary_rule.score = unary_prob
            self.add_unary(unary_rule)
        for binary_rule in binary_rule_counter:
            binary_prob = float(binary_rule_counter[binary_rule]) / symbol_counter[binary_rule.parent]
            binary_rule.score = binary_prob
            self.add_binary(binary_rule)


    def __unicode__(self):
        rule_strings = []
        for left_child in self.binary_rules_by_left_child:
            for binary_rule in self.get_binary_rules_by_left_child(left_child):
                rule_strings.append(str(binary_rule))
        for child in self.unary_rules_by_child:
            for unary_rule in self.get_unary_rules_by_child(child):
                rule_strings.append(str(unary_rule))
        return "%s" % "".join(rule_strings)


    def add_binary(self, binary_rule):
        self.binary_rules_by_left_child[binary_rule.left_child].append(binary_rule)
        self.binary_rules_by_right_child[binary_rule.right_child].append(binary_rule)


    def add_unary(self, unary_rule):
        self.unary_rules_by_child[unary_rule.child].append(unary_rule)


    def get_binary_rules_by_left_child(self, left_child):
        return self.binary_rules_by_left_child[left_child]


    def get_binary_rules_by_right_child(self, right_child):
        return self.binary_rules_by_right_child[right_child]


    def get_unary_rules_by_child(self, child):
        return self.unary_rules_by_child[child]


    def tally_tree(self, tree, symbol_counter, unary_rule_counter, binary_rule_counter):
        if tree.is_leaf():
            return
        if tree.is_preterminal():
            return
        if len(tree.children) == 1:
            unary_rule = self.make_unary_rule(tree)
            symbol_counter[tree.label] += 1
            unary_rule_counter[unary_rule] += 1
        if len(tree.children) == 2:
            binary_rule = self.make_binary_rule(tree)
            symbol_counter[tree.label] += 1
            binary_rule_counter[binary_rule] += 1
        if len(tree.children) < 1 or len(tree.children) > 2:
            raise Exception("Attempted to construct a Grammar with " \
                    + "an illegal tree (most likely not binarized): " + str(tree))
        for child in tree.children:
            self.tally_tree(child, symbol_counter, unary_rule_counter, binary_rule_counter)


    def make_unary_rule(self, tree):
        return UnaryRule(tree.label, tree.children[0].label)


    def make_binary_rule(self, tree):
        return BinaryRule(tree.label, tree.children[0].label, tree.children[1].label)


    def read_grammar(self, grammar_file):
        with open(grammar_file, "r") as fin:
            lst = pickle.load(fin)
        self.unary_rules_by_child = lst[0]
        self.binary_rules_by_left_child = lst[1]
        self.binary_rules_by_right_child = lst[2]



if __name__ == "__main__":
    from read import *
    base_path = '../data/parser/miniTest'

    train_trees = read_trees(base_path, 1, 3)
    binarized_trees = [TreeAnnotations.binarize_tree(t) for t in train_trees]
    g = Grammar()
    g.train(binarized_trees)
    print unicode(g)
    # ------------- Unary Rule ---------------
    print len(g.unary_rules_by_child['NP'])
    rule = g.unary_rules_by_child['NP'][1]
    print str(rule)
    # print rule.parent
    # print rule.child

    # ------------- Binary Rule (Left) ---------------
    # print len(g.binary_rules_by_left_child['P'])
    # rule1 = g.binary_rules_by_left_child['P'][0]
    # print str(rule1)
    # print rule1.left_child
    # print rule1.right_child
    # print rule1.score

    # ------------- Binary Rule (right) ---------------
    # print len(g.binary_rules_by_right_child['@PP->_P'])
    # rule2 = g.binary_rules_by_right_child['@PP->_P'][0]
    # print str(rule2)
    # print rule2.left_child
    # print rule2.right_child
    # print rule2.score

    # print rule1 == rule2
    
    
