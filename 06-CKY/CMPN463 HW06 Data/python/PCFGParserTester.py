import copy
from optparse import OptionParser
from collections import defaultdict

from ling.Tree import Tree
import ling.Trees as Trees

from read import *
from lexicon import Lexicon
from rules import *
from grammar import Grammar
from tree_annotations import TreeAnnotations



class Parser:
    #This class is used as an abstract class. In other words, it's used as a blueprint for other classes.

    def train(self, train_trees):
        pass

    def get_best_parse(self, sentence):
        """
        Should return a Tree
        """
        pass


class PCFGParser(Parser):

    def train(self, train_trees):
        self.lexicon = Lexicon(train_trees)
        binarized_train_trees = [TreeAnnotations.binarize_tree(t) for t in train_trees]
        self.grammar = Grammar(binarized_train_trees)
        self.parsing_triangle= defaultdict(set)


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
        return [(rule.parent, rule.score) for rule in self.parsing_triangle[row, col]]


    def get_cell_pairs(self, row, level):
        """
        It takes the cell row and level number, and it returns the possible cell tags that could the given cell
        could come from. For example, for first level (level=1), the cell at (0,1) come from the either (0,0)
        or (1,1). Another example, the cell (0,2) at level=2 could come from either ((0,0), (1,2)) or ((0,1), (2,2))
        """
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
        n = len(sentence)

        # ------------------------- (Level 0) -------------------------
        # --------------- Initializing Parsing Traingle ---------------

        possible_tags = self.lexicon.tag_counter.keys()
        for i, word in enumerate(sentence):
            for tag in possible_tags:
                if self.lexicon.word_to_tag_counters[word][tag] != 0:
                    unary_rule = UnaryRule(tag, word)
                    unary_rule.score = self.lexicon.score_tagging(word, tag)
                    # unary_rule.origin = (i,i)
                    # unary_rule.des = (i,i)
                    self.parsing_triangle[(i, i)].add(unary_rule)
        # self.print_parsing_traingle()
        # print '\n\n'

        # ------------- End Initializing Parsing Traingle -------------
        # ------------------ Expanding First Cells --------------------
        key = None
        while(key != 0):
            key = 0
            for row, col in sorted(self.parsing_triangle.keys()):
                tags_scores = self.get_cell_tags(row, col)
                for tag, score in tags_scores:
                    rules = self.grammar.get_unary_rules_by_child(tag)
                    for rule in rules:
                        if rule not in self.parsing_triangle[(row, col)]:
                            key += 1
                            tmp_rule = copy.copy(rule)
                            tmp_rule.score = score * rule.score
                            # print row, col
                            tmp_rule.origin = (row, col)
                            tmp_rule.des = (row, col)
                            self.parsing_triangle[(row, col)].add(tmp_rule)
                          
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
                key = None
                while(key != 0):
                    key = 0
                    tags_scores = self.get_cell_tags(row, col)
                    tags = [t[0] for t in tags_scores]
                    for tag, score in tags_scores: 
                        rules = self.grammar.get_unary_rules_by_child(tag)
                        for rule in rules:
                            if rule.parent in tags:
                                old_rules = [ r for r in self.parsing_triangle[row, col] if r.parent == rule.parent ]
                                for old_rule in old_rules:
                                    if rule.score*score > old_rule.score:
                                        key += 1
                                        self.parsing_triangle[row, col].discard(old_rule)
                                        new_rule = copy.copy(rule)
                                        new_rule.score = score * rule.score
                                        self.parsing_triangle[row, col].add(new_rule)
                # ----------- End Findin Better Unary Rules -----------
                # ----------------- Expanding  Cells ------------------
                key = None
                t = row, col
                while(key != 0):
                    key = 0
                    tags_scores = self.get_cell_tags(row, col)
                    for tag, score in tags_scores:
                        rules = self.grammar.get_unary_rules_by_child(tag)
                        for rule in rules:
                            if rule not in self.parsing_triangle[t]:
                                key += 1
                                tmp_rule = copy.copy(rule)
                                tmp_rule.score = score * rule.score
                                tmp_rule.origin = (row, col)
                                tmp_rule.des = (row, col)
                                self.parsing_triangle[t].add(tmp_rule)
                # ---------------- End Expanding  Cells ---------------
            level += 1

        # ----------------------- Building Tree -----------------------
        """
        The following four methods are defined to build the tree, and they are:
          -> search_rule.
          -> build_branch.
          -> build.
          -> build_tree.
        """
        return self.build_tree(n)
    


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
            print str(rule)
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
        no_levels = sen_length-1
        cell = (0, no_levels)
        starting_cell = (0, no_levels)
        starting_rule = self.search_rule(starting_cell, 'S')
        tree = self.build(starting_rule)
        if render:
            print Trees.PennTreeRenderer.render(tree)
        tree = TreeAnnotations.unannotate_tree(tree)
        
        return tree




class BaselineParser(Parser):

    def train(self, train_trees):
        self.lexicon = Lexicon(train_trees)
        self.known_parses = {}
        self.span_to_categories = {}
        for train_tree in train_trees:
            tags = train_tree.get_preterminal_yield()
            tags = tuple(tags)  # because lists are not hashable, but tuples are
            if tags not in self.known_parses:
                self.known_parses[tags] = {}
            if train_tree not in self.known_parses[tags]:
                self.known_parses[tags][train_tree] = 1
            else:
                self.known_parses[tags][train_tree] += 1
            self.tally_spans(train_tree, 0)


    def get_best_parse(self, sentence):
        tags = self.get_baseline_tagging(sentence)
        tags = tuple(tags)
        if tags in self.known_parses:
            return self.get_best_known_parse(tags, sentence)
        else:
            return self.build_right_branch_parse(sentence, list(tags))


    def build_right_branch_parse(self, words, tags):
        cur_position = len(words) - 1
        right_branch_tree = self.build_tag_tree(words, tags, cur_position)
        while cur_position > 0:
            cur_position -= 1
            right_branch_tree = self.merge(
                    self.build_tag_tree(words, tags, cur_position),
                    right_branch_tree)
        right_branch_tree = self.add_root(right_branch_tree)
        return right_branch_tree


    def merge(self, left_tree, right_tree):
        span = len(left_tree.get_yield()) + len(right_tree.get_yield())
        maxval = max(self.span_to_categories[span].values())
        for key in self.span_to_categories[span]:
            if self.span_to_categories[span][key] == maxval:
                most_freq_label = key
                break
        return Tree(most_freq_label, [left_tree, right_tree])


    def add_root(self, tree):
        return Tree("ROOT", [tree])


    def build_tag_tree(self, words, tags, cur_position):
        leaf_tree = Tree(words[cur_position])
        tag_tree = Tree(tags[cur_position], [leaf_tree])
        return tag_tree


    def get_best_known_parse(self, tags, sentence):
        maxval = max(self.known_parses[tags].values())
        for key in self.known_parses[tags]:
            if self.known_parses[tags][key] == maxval:
                parse = key
                break
        parse = copy.deepcopy(parse)
        parse.set_words(sentence)
        return parse


    def get_baseline_tagging(self, sentence):
        tags = [self.get_best_tag(word) for word in sentence]
        return tags


    def get_best_tag(self, word):
        best_score = 0
        best_tag = None
        for tag in self.lexicon.get_all_tags():
            score = self.lexicon.score_tagging(word, tag)
            if best_tag is None or score > best_score:
                best_score = score
                best_tag = tag
        return best_tag


    def tally_spans(self, tree, start):
        if tree.is_leaf() or tree.is_preterminal():
            return 1
        end = start
        for child in tree.children:
            child_span = self.tally_spans(child, end)
            end += child_span
        category = tree.label
        if category != "ROOT":
            if end-start not in self.span_to_categories:
                self.span_to_categories[end-start] = {}
            if category not in self.span_to_categories[end-start]:
                self.span_to_categories[end-start][category] = 1
            else:
                self.span_to_categories[end-start][category] += 1
        return end - start








MAX_LENGTH = 20
if __name__ == '__main__':
    opt_parser = OptionParser()
    opt_parser.add_option("--path", dest="path", default="../data/")
    # TODO: Choose the dataset here: "masc" or "miniTest"
    opt_parser.add_option("--data", dest="data", default = "masc")
    # TODO: Choose the parser here: "BaselineParser" or "PCFGParser"
    opt_parser.add_option("--parser", dest="parser", default="PCFGParser")
    opt_parser.add_option("--maxLength", dest="max_length", default="20")
    opt_parser.add_option("--testData", dest="test_data", default="")

    (options, args) = opt_parser.parse_args()
    options = vars(options)

    print "PCFGParserTest options:"
    for opt in options:
        print "  %-12s: %s" % (opt, options[opt])
    print ""
    MAX_LENGTH = int(options['max_length'])

    parser = globals()[options['parser']]()
    print "Using parser: %s" % parser.__class__.__name__

    base_path = options['path']
    pre_base_path = base_path
    data_set = options['data']
    if not base_path.endswith('/'):
        base_path += '/'

    print "Data will be loaded from: %s" % base_path

    train_trees = []
    validation_trees = []
    test_trees = []

    if data_set == 'miniTest':
        base_path += 'parser/%s' % data_set

        # training data: first 3 of 4 datums
        print "Loading training trees..."
        train_trees = read_trees(base_path, 1, 3)
        print "done."

        # test data: last of 4 datums
        print "Loading test trees..."
        test_trees = read_trees(base_path, 4, 4)
        print "done."

    if data_set == "masc":
        base_path += "parser/"

        # training data: MASC train
        print "Loading MASC training trees... from: %smasc/train" % base_path
        train_trees.extend(read_masc_trees("%smasc/train" % base_path, 0, 38))
        print "done."
        print "Train trees size: %d" % len(train_trees)
        print "First train tree: %s" % Trees.PennTreeRenderer.render(train_trees[0])
        print "Last train tree: %s" % Trees.PennTreeRenderer.render(train_trees[-1])

        # test data: MASC devtest
        print "Loading MASC test trees..."
        test_trees.extend(read_masc_trees("%smasc/devtest" % base_path, 0, 11))
        #test_trees.extend(read_masc_trees("%smasc/blindtest" % base_path, 0, 8))
        print "done."
        print "Test trees size: %d" % len(test_trees)
        print "First test tree: %s" % Trees.PennTreeRenderer.render(test_trees[0])
        print "Last test tree: %s" % Trees.PennTreeRenderer.render(test_trees[-1])


    if data_set not in ["miniTest", "masc"]:
        raise Exception("Bad data set: %s: use miniTest or masc." % data_set)

    print ""
    print "Training parser..."
    parser.train(train_trees)

    print "Testing parser"
    test_parser(parser, test_trees)
