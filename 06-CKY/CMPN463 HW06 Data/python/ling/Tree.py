from Constituent import Constituent

class Tree:

    # TODO: deepCopy() ?

    def __init__(self, label, children = []):
        """
        The constructor.
        """
        self.label = label
        self.children = children

    def is_leaf(self):
        """
        Returns true at the word (leaf) level of a tree.
        """
        return len(self.children) == 0

    def is_preterminal(self):
        """
        Returns true level of non-terminals which are directly above
        single words (leaves).
        """
        return len(self.children) == 1 and self.children[0].is_leaf()

    def is_phrasal(self):
        return not (self.is_leaf() and self.is_preterminal)

    def _append_yield(self, leaf_labels):
        if self.is_leaf():
            leaf_labels.append(self.label)
            return
        for child in self.children:
            child._append_yield(leaf_labels)

    def get_yield(self):
        """
        Returns a list of words at the leaves of this tree gotten by
        traversing from left to right.
        """
        leaf_labels = []
        self._append_yield(leaf_labels)
        return leaf_labels

    def _append_preterminal_yield(self, preterm_yield):
        if self.is_preterminal():
            preterm_yield.append(self.label)
            return
        for child in self.children:
            child._append_preterminal_yield(preterm_yield)

    def get_preterminal_yield(self):
        """
        Returns a list of the preterminals gotten by traversing from left
        to right.  This is effectively an POS tagging for the words that
        tree represents.
        """
        preterm_yield = []
        self._append_preterminal_yield(preterm_yield)
        return preterm_yield

    def _traversal_helper(self, traversal, pre_order):
        if pre_order:
            traversal.append(self)
        for child in self.children:
            child._traversal_helper(traversal, pre_order)
        if not pre_order:
            traversal.append(self)

    def get_preorder_traversal(self):
        """
        Returns a list of the node values gotten by traversing in this
        order: root, left subtree, right subtree.
        """
        traversal = []
        self._traversal_helper(traversal, True)
        return traversal

    def get_postorder_traversal(self):
        """
        Returns a list of the node values gotten by traversing in this
        order: left subtree, right subtree, root.
        """
        traversal = []
        self._traversal_helper(traversal, False)
        return traversal

    def _set_words_helper(self, words, word_num):
        if self.is_leaf():
            self.label = words[word_num]
            return word_num + 1
        else:
            for child in self.children:
                word_num = child._set_words_helper(words, word_num)
            return word_num

    def set_words(self, words):
        """
        Set the words at the leaves of a tree to the words from the list.
        """
        self._set_words_helper(words, 0)

    def to_subtree_list(self):
        return self.get_preorder_traversal()

    def _to_constituent_helper(self, start, constituents):
        if self.is_leaf() or self.is_preterminal():
            return 1
        span = 0
        for child in self.children:
            span += child._to_constituent_helper(start + span, constituents)
        constituents.append(Constituent(self.label, start, start + span))
        return span

    def to_constituent_list(self):
        """
        Creates a list of all constituents in this tree.  A constituent
        is just a non-terminal label and that non-terminal covers in the
        tree.
        """
        constituent_list = []
        self._to_constituent_helper(0, constituent_list)
        return constituent_list

    def _to_string(self, s):
        if not self.is_leaf():
            s.append('(')
        s.append(self.label)
        if not self.is_leaf():
            for child in self.children:
                s.append(' ')
                child._to_string(s)
            s.append(')')

    def __unicode__(self):
        s = []
        self._to_string(s)
        return ''.join(s)

    def __str__(self):
        return unicode(self).encode('utf-8')
