from ling.Tree import Tree
import ling.Trees as Trees




class TreeAnnotations:
    """
    This class is created basically for two reasons:
     -> binarizing a given tree using 'binarize_tree' function
     -> applying Markov Vectorization using 'annotate_tree' function
    """

    @classmethod
    def annotate_tree(cls, unannotated_tree):
        """
        Currently, the only annotation done is a lossless binarization
        """

        # TODO: change the annotation from a lossless binarization to a
        # finite-order markov process (try at least 1st and 2nd order)
        # mark nodes with the label of their parent nodes, giving a second
        # order vertical markov process

        return TreeAnnotations.binarize_tree(unannotated_tree)


    @classmethod
    def binarize_tree(cls, tree):
        label = tree.label
        if tree.is_leaf():
            return Tree(label)
        if len(tree.children) == 1:
            return Tree(label, [TreeAnnotations.binarize_tree(tree.children[0])])

        intermediate_label = "@%s->" % label
        intermediate_tree = TreeAnnotations.binarize_tree_helper(
                tree, 0, intermediate_label)
        return Tree(label, intermediate_tree.children)


    @classmethod
    def binarize_tree_helper(cls, tree, num_children_generated,
            intermediate_label):
        left_tree = tree.children[num_children_generated]
        children = []
        children.append(TreeAnnotations.binarize_tree(left_tree))
        if num_children_generated < len(tree.children) - 1:
            right_tree = TreeAnnotations.binarize_tree_helper(
                    tree, num_children_generated + 1,
                    intermediate_label + "_" + left_tree.label)
            children.append(right_tree)
        return Tree(intermediate_label, children)


    @classmethod
    def at_filter(cls, string):
        if string.startswith('@'):
            return True
        else:
            return False


    @classmethod
    def unannotate_tree(cls, annotated_tree):
        """
        Remove intermediate nodes (labels beginning with "@")
        Remove all material on node labels which follow their base
        symbol (cuts at the leftmost -, ^, or : character)
        Examples: a node with label @NP->DT_JJ will be spliced out,
        and a node with label NP^S will be reduced to NP
        """
        debinarized_tree = Trees.splice_nodes(annotated_tree,
                TreeAnnotations.at_filter)
        unannotated_tree = Trees.FunctionNodeStripper.transform_tree(
                debinarized_tree)
        return unannotated_tree




if __name__ == "__main__":
    from read import *
    base_path = '../data/parser/miniTest'
    train_trees = read_trees(base_path, 1, 3)
    # binarized_trees = [TreeAnnotations.binarize_tree(t) for t in train_trees]
    # print Trees.PennTreeRenderer.render(binarized_trees[0])
    test_tree = read_trees(base_path, 4, 4)
    print Trees.PennTreeRenderer.render(test_tree[0])
    binarized_tree = TreeAnnotations.binarize_tree(test_tree[0])
    print Trees.PennTreeRenderer.render(binarized_tree)
    unbinarized_tree = TreeAnnotations.unannotate_tree(binarized_tree)
    print Trees.PennTreeRenderer.render(unbinarized_tree)
