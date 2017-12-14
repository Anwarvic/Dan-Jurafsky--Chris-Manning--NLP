from lexicon import Lexicon
from PCFGParserTester import Parser
from tree_annotations import TreeAnnotations
from grammar import Grammar
from collections import defaultdict
from rules import *
import copy
from ling.Tree import Tree

#####
import pickle



class PCFGParser(Parser):

    def __init__(self):
        self.lexicon = Lexicon()
        self.grammar = Grammar()
        self.parsing_triangle= defaultdict(set)
        self.cell_capacity = 3 #represents the maximum capacity of a cell inside the Parsing Tree


    def write_par(self, train_trees, grammar_file, lexicon_file):
        self.train(train_trees)
        #write Grammar
        lst = []
        lst.append(self.grammar.unary_rules_by_child)
        lst.append(self.grammar.binary_rules_by_left_child)
        lst.append(self.grammar.binary_rules_by_right_child)
        with file(grammar_file, "w") as fout:
            pickle.dump(lst, fout)

        #write Lexicon
        lst = []
        lst.append(self.lexicon.total_tokens)
        lst.append(self.lexicon.total_word_types)
        lst.append(self.lexicon.word_to_tag_counters)
        lst.append(self.lexicon.tag_counter)
        lst.append(self.lexicon.word_counter)
        lst.append(self.lexicon.type_to_tag_counter)
        with file(lexicon_file, "w") as fout:
            pickle.dump(lst, fout)


    def read(self, grammar_file, lexicon_file):
        self.lexicon.read_lexicon(lexicon_file)
        self.grammar.read_grammar(grammar_file)


    def train(self, train_trees):
        self.lexicon.train(train_trees)
        binarized_train_trees = [TreeAnnotations.binarize_tree(t) for t in train_trees]
        self.grammar.train(binarized_train_trees)
        

    def print_parsing_traingle(self):
        """
        This function is used to pring the Parsing Traingle. It's very important for debugging, except that
        you can delete it.
        """
        for t, rules in sorted(self.parsing_triangle.iteritems()):
            for rule in rules:
                print t, str(rule),


    def get_cell_tags(self, row, col):
        #returns the 'tag'  and 'score' of the cell at 'row' and 'col'
        return [(rule.parent, rule.score) for rule in \
            sorted(self.parsing_triangle[row, col], key=lambda rule:rule.score, reverse = True)]\
            [:self.cell_capacity]


    def get_cell_pairs(self, row, level):
        result = []
        col = row+level
        for i in range(level):
            _tuple = ((row, row+i), (row+i+1, col))
            result.append( _tuple )
        assert len(result) == level
        return result


    def get_best_parse(self, sentence):
        """
        Should return a Tree.
        'sentence' is a list of strings (words) that form a sentence.
        """
        print " ".join(sentence)
        n = len(sentence)

        # ------------------------- (Level 0) -------------------------
        # --------------- Initializing Parsing Traingle ---------------

        possible_tags = self.lexicon.tag_counter.keys()
        for i, word in enumerate(sentence):
            for tag in possible_tags:
                if self.lexicon.word_to_tag_counters[word][tag] != 0:
                    unary_rule = UnaryRule(tag, word)
                    unary_rule.score = self.lexicon.score_tagging(word, tag)
                    self.parsing_triangle[(i, i)].add(unary_rule)

        self.print_parsing_traingle()
        print "\n\n"
        # ------------- End Initializing Parsing Traingle -------------
        # ------------------ Expanding First Cells --------------------
        key = None
        while(key != 0):
            key = 0
            for row, col in sorted(self.parsing_triangle.keys()):
                tags_scores = self.get_cell_tags(row, col)
                for tag, score in tags_scores:
                    rules = self.grammar.get_unary_rules_by_child(tag)
                    rules = sorted(rules, key=lambda rule:rule.score, reverse=True)[:self.cell_capacity]
                    print tag, len(rules)
                    for rule in rules:
                        if rule not in self.parsing_triangle[(row, col)]:
                            key += 1
                            tmp_rule = copy.copy(rule)
                            tmp_rule.score = score * rule.score
                            tmp_rule.origin = (row, col)
                            tmp_rule.des = (row, col)
                            self.parsing_triangle[(row, col)].add(tmp_rule)


                # self.print_parsing_traingle()
                # print "\n"
            # break
        print "Finished Level 0"
        # ---------------- End Expanding First Cells ------------------

        # self.print_parsing_traingle()
        
        # ----------------------- (Level 1...n) -----------------------
        # ------------------- Filling Other Cells ---------------------
        level = 1
        while(level != n):
            for row in range(n-level):
                col = row+level
                cell_pairs = self.get_cell_pairs(row, level)
                for cell_pair in cell_pairs:
                    first_tags_scores = self.get_cell_tags(cell_pair[0][0], cell_pair[0][1])
                    second_tags_scores = self.get_cell_tags(cell_pair[1][0], cell_pair[1][1])
                    for tag1, score1 in first_tags_scores:
                        rules1 = self.grammar.get_binary_rules_by_left_child(tag1)
                        for tag2, score2 in second_tags_scores:
                            rules2 = self.grammar.get_binary_rules_by_right_child(tag2)
                            common_rules = set(rules1).intersection(set(rules2))
                            for rule in common_rules:
                                tmp_rule = copy.copy(rule)
                                tmp_rule.score = score1 * score2 * rule.score
                                tmp_rule.origin = cell_pair
                                tmp_rule.des = (row, col)
                                self.parsing_triangle[row, col].add(tmp_rule)
                # ------------- Findin Better Unary Rules -------------
                #I think this part needs more debugging
                # key = None
                # while(key != 0):
                #     key = 0
                #     tags_scores = self.get_cell_tags(row, col)
                #     tags = [t[0] for t in tags_scores]
                #     for tag, score in tags_scores: 
                #         rules = self.grammar.get_unary_rules_by_child(tag)
                #         for rule in rules:
                #             if rule.parent in tags:
                #                 old_rules = [ r for r in self.parsing_triangle[row, col] if r.parent == rule.parent ]
                #                 for old_rule in old_rules:
                #                     if rule.score*score > old_rule.score:
                #                         key += 1
                #                         self.parsing_triangle[row, col].discard(old_rule)
                #                         new_rule = copy.copy(rule)
                #                         new_rule.score = score * rule.score
                #                         self.parsing_triangle[row, col].add(new_rule)
                # ----------- End Finding Better Unary Rules ----------
                # ----------------- Expanding  Cells ------------------
                key = None
                while(key != 0):
                    key = 0
                    tags_scores = self.get_cell_tags(row, col)
                    for tag, score in tags_scores:
                        rules = self.grammar.get_unary_rules_by_child(tag)
                        for rule in sorted(rules, key=lambda rule:rule.score, reverse=True):
                            if rule not in self.parsing_triangle[row, col]:
                                key += 1
                                tmp_rule = copy.copy(rule)
                                tmp_rule.score = score * rule.score
                                tmp_rule.origin = (row, col)
                                tmp_rule.des = (row, col)
                                self.parsing_triangle[row, col].add(tmp_rule)
                # ---------------- End Expanding  Cells ---------------
                # print ""
                # self.print_parsing_traingle()
            level += 1
            # break
        print "Finished Parsing traingle"

        self.print_parsing_traingle()
        print "\n\n"
        # ----------------------- Building Tree -----------------------
        """
        The following four methods are defined to build the tree, and they are:
          -> search_rule.
          -> build_branch.
          -> build.
          -> build_tree.
        """
        print len(self.parsing_triangle[0, 3])
        for rule in self.parsing_triangle[0, 3]:
            print str(rule)
        return self.build_tree(n, render=1)
    


    def search_rule(self, cell, tag):
        row, col = cell
        for rule in self.parsing_triangle[row, col]:
            if rule.parent == tag:
                return rule
            

    def build_branch(self, rule):
        if isinstance(rule, UnaryRule):
            return Tree(rule.parent, [Tree(rule.child)])
        elif isinstance(rule, BinaryRule):
            return Tree(rule.parent, [Tree(rule.left_child), Tree(rule.right_child)])


    def build(self, rule):
        origin = rule.origin
        if origin == (None, None):
            return self.build_branch(rule)
        else:
            if isinstance(rule, UnaryRule):
                # print str(rule)
                tag = rule.child
                next_rule = self.search_rule(origin, tag)
                return Tree(rule.parent, [self.build(next_rule)])
            
            elif isinstance(rule, BinaryRule):
                # print str(rule)
                left_origin, right_origin = origin[0], origin[1]
                left_tag, right_tag = rule.left_child, rule.right_child
                
                next_left_rule = self.search_rule(left_origin, left_tag)
                next_right_rule = self.search_rule(right_origin, right_tag)
                
                return Tree(rule.parent, [self.build(next_left_rule), self.build(next_right_rule)])


    def build_tree(self, sen_length, render=0):
        # print "It's Here"
        no_levels = sen_length-1
        cell = (0, no_levels)
        starting_cell = (0, no_levels)
        rule = self.search_rule(starting_cell, 'ROOT')
        starting_rule = self.search_rule(rule.origin, rule.child)
        tree = self.build(starting_rule)
        if render:
            print Trees.PennTreeRenderer.render(tree)
        tree = TreeAnnotations.unannotate_tree(tree)
        
        return tree














    









if __name__ == "__main__":
    from read import *
    base_path = '../data/parser/'
    parser = PCFGParser()
    TEST = False
    
    # ----------------------- FOR minitest dataset -----------------------
    if TEST:
        train_trees = read_trees(base_path+'miniTest', 1, 3)
        parser.train(train_trees)
        test_trees = read_trees(base_path, 4, 4)
        test_parser(parser, test_trees) 
        # rules = parser.parsing_triangle[0,0]
        # for rule in sorted(rules, key=lambda rule:rule.score, reverse = True)[:self.cell_capacity]:
        #     print rule


    # ----------------------- FOR MASC dataset -----------------------
    else:
        train_trees, test_trees = [], []
        # train_trees.extend(read_masc_trees("%smasc/train" % base_path, 0, 38))
        test_trees.extend(read_masc_trees("%smasc/devtest" % base_path, 0, 11))
        # parser.write_par(train_trees, "grammar.pickle", "lexicon.pickle")
        parser.read("grammar.pickle", "lexicon.pickle")
        # print unicode(parser.grammar)
        # parser.train(train_trees)
        test_parser(parser, [test_trees[0]])
        
    
