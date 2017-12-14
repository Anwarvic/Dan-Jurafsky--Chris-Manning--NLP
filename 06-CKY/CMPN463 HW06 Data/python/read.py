import pennParser.EnglishPennTreebankParseEvaluator as EnglishPennTreebankParseEvaluator
import iob.PennTreebankReader as PennTreebankReader
import iob.MASCTreebankReader as MASCTreebankReader
import ling.Trees as Trees
from tree_annotations import TreeAnnotations


def test_parser(parser, test_trees):
    evaluator = EnglishPennTreebankParseEvaluator.LabeledConstituentEval(
            ["ROOT"], set(["''", "``", ".", ":", ","]))
    for test_tree in test_trees:
        test_sentence = test_tree.get_yield()
        binarized_test_tree = TreeAnnotations.binarize_tree(test_tree)
        print "Binarized Gold:\n%s" % Trees.PennTreeRenderer.render(binarized_test_tree)
        print "Gold:\n%s" % Trees.PennTreeRenderer.render(test_tree)
        if len(test_sentence) > 20:
            continue
        guessed_tree = parser.get_best_parse(test_sentence)
        print "Guess:\n%s" % Trees.PennTreeRenderer.render(guessed_tree)
        # print "Gold:\n%s" % Trees.PennTreeRenderer.render(test_tree)
        evaluator.evaluate(guessed_tree, test_tree)
    print ""
    return evaluator.display(True)


def read_trees(base_path, low=None, high=None):
    trees = PennTreebankReader.read_trees(base_path, low, high)
    return [Trees.StandardTreeNormalizer.transform_tree(tree) for tree in trees]


def read_masc_trees(base_path, low=None, high=None):
    print "Reading MASC from %s" % base_path
    trees = MASCTreebankReader.read_trees(base_path, low, high)
    return [Trees.StandardTreeNormalizer.transform_tree(tree) for tree in trees]


def display(trees, num=0):
    assert num >= 0 and num < len(trees)
    return Trees.PennTreeRenderer.render(trees[num])



if __name__ == "__main__":
    base_path = '../data/parser/miniTest'

    # reading files from 1 till 3
    train_trees = read_trees(base_path, 1, 3)
    print display(train_trees, 0)
