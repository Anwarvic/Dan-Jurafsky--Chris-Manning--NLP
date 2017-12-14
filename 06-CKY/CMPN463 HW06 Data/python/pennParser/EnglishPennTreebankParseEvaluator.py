from ling.Constituent import Constituent
from ling.Tree import Tree
import ling.Trees as Trees

"""
Evaluates precision and recall for English Penn Treebank parse
trees.  NOTE: Unlike the standard evaluation, multiplicity over
each span is ignored.  Also, punctuation is NOT currently deleted
properly (approximate hack), and other normalizations (like AVDP ~
PRT) are NOT done.
"""

class AbstractEval:

    def __init__(self):
        self.string = ""
        self.exact = 0
        self.total = 0
        self.correct_events = 0
        self.guessed_events = 0
        self.gold_events = 0

    def evaluate(self, guess, gold):
        """
        Evaluates precision and recall by calling makeObjects() to make a
        set of structures for guess Tree and gold Tree, and compares them
        with each other.
        """
        guessed_set = self.make_objects(guess)
        gold_set = self.make_objects(gold)
        gold_set = self.make_objects(gold)
        correct_set = set()
        correct_set.update(gold_set)
        correct_set.intersection_update(guessed_set)

        self.correct_events += len(correct_set)
        self.guessed_events += len(guessed_set)
        self.gold_events += len(gold_set)

        current_exact = 0
        if len(correct_set) == len(guessed_set) and \
                len(correct_set) == len(gold_set):
            self.exact += 1
            current_exact = 1
        self.total += 1

        return self.display_prf(self.string + " [Current] ", len(correct_set),
                len(guessed_set), len(gold_set), current_exact, 1)


    def display_prf(self, pre_str, correct, guessed, gold, exact, total):

        precision = correct / float(guessed) if guessed > 0 else 1.0
        recall = correct / float(gold) if gold > 0 else 1.0
        f1 = 2.0 / (1.0 / precision + 1.0 / recall) \
                if precision > 0.0 and recall > 0.0 else 0.0
        exact_match = exact / float(total)

        print "%s   P: %5.2f   R: %5.2f   F1: %5.2f   EX: %5.2f" % \
                (pre_str, 100.0 * precision, 100.0 * recall, 100.0 * f1,
                        100.0 * exact_match)
        return 100.0 * f1

    def display(self, verbose):
        return self.display_prf(self.string + " [Average] ", self.correct_events,
                self.guessed_events, self.gold_events, self.exact,
                self.total)

class LabeledConstituent:

    def __init__(self, label, start, end):
        self.label = label
        self.start = start
        self.end = end

    def __eq__(self, o):
        if self is o:     # tests if they are the same exact object
            return True
        if not isinstance(o, LabeledConstituent):
            return False
        if self.end != o.end or self.start != o.start or \
                self.label != o.label:
            return False
        return True

    def __hash__(self):
        # For comparison (with sets)
        result = hash(self.label)
        result = 29 * result + self.start
        result = 29 * result + self.end
        return result

    def __unicode__(self):
        return "%s[%d,%d]" % (self.label, self.start, self.end)

    def __str__(self):
        return unicode(self).encode('utf-8')


class LabeledConstituentEval(AbstractEval):

    def __init__(self, labels_to_ignore, punctuation_tags):
        AbstractEval.__init__(self)
        #super(LabeledConstituentEval, self).__init__()
        self.labels_to_ignore = set(labels_to_ignore)
        self.punctuation_tags = set(punctuation_tags)

    def strip_leaves(self, tree):
        if tree.is_leaf():
            return None
        if tree.is_preterminal():
            return Tree(tree.label)
        children = []
        for child in tree.children:
            children.append(self.strip_leaves(child))
        return Tree(tree.label, children)

    def make_objects(self, tree):
        no_leaf_tree = self.strip_leaves(tree)
        aset = set()
        self.add_constituents(no_leaf_tree, aset, 0)
        return aset

    def add_constituents(self, tree, aset, start):
        if tree.is_leaf():
            if tree.label in self.punctuation_tags:
                return 0
            else:
                return 1
        end = start
        for child in tree.children:
            child_span = self.add_constituents(child, aset, end)
            end += child_span
        label = tree.label
        if label not in self.labels_to_ignore:
            aset.add(LabeledConstituent(label, start, end))
        return end - start

if __name__ == '__main__':
    import StringIO

    gold_string = "(ROOT (S (NP (DT the) (NN can)) (VP (VBD fell))))"
    gold_io = StringIO.StringIO()
    gold_io.write(gold_string)
    gold_io.seek(0)
    gold_tree = Trees.PennTreeReader(gold_io).next()

    guess_string = "(ROOT (S (NP (DT the)) (VP (MB can) (VP (VBD fell)))))"
    guess_io = StringIO.StringIO()
    guess_io.write(guess_string)
    guess_io.seek(0)
    guess_tree = Trees.PennTreeReader(guess_io).next()

    evaluator = LabeledConstituentEval(["ROOT"], set())
    evaluator.evaluate(guess_tree, gold_tree)
    evaluator.display(True)
