from Tree import Tree

# TODO: should I replace rendering of tree.label to str(tree.label)??

##################
# Class Methods
##################
ROOT_LABEL = "ROOT"


class TreeTransformer:
    """
    Abstract base class for different Tree transformation classes.
    """
    @classmethod
    def transform_tree(cls, tree):
        raise NotImplementedError()


class FunctionNodeStripper(TreeTransformer):

    @classmethod
    def transform_tree(cls, tree):
        transformed_label = tree.label
        cut_idx = transformed_label.find('-')
        cut_idx2 = transformed_label.find('=')
        if cut_idx2 > 0 and (cut_idx2 < cut_idx or cut_idx == -1):
            cut_idx = cut_idx2
        cut_idx2 = transformed_label.find('^')
        if cut_idx2 > 0 and (cut_idx2 < cut_idx or cut_idx == -1):
            cut_idx = cut_idx2
        cut_idx2 = transformed_label.find(':')
        if cut_idx2 > 0 and (cut_idx2 < cut_idx or cut_idx == -1):
            cut_idx = cut_idx2

        if cut_idx > 0 and not tree.is_leaf():
            transformed_label = transformed_label[:cut_idx]
        if tree.is_leaf():
            return Tree(transformed_label)

        transformed_children = []
        for child in tree.children:
            transformed_children.append(FunctionNodeStripper.transform_tree(child))

        return Tree(transformed_label, transformed_children)


class EmptyNodeStripper(TreeTransformer):

    @classmethod
    def transform_tree(cls, tree):
        label = tree.label
        if label == "-NONE-":
            return None
        if tree.is_leaf():
            return Tree(label)
        children = tree.children
        transformed_children = []
        for child in children:
            transformed_child = EmptyNodeStripper.transform_tree(child)
            if transformed_child is not None:
                transformed_children.append(transformed_child)
        if len(transformed_children) == 0:
            return None
        return Tree(label, transformed_children)


class XOverXRemover(TreeTransformer):

    @classmethod
    def transform_tree(cls, tree):
        label = tree.label
        children = tree.children
        while len(children) == 1 and not children[0].is_leaf() \
                and label == children[0].label:
            children = children[0].children
        transformed_children = []
        for child in children:
            transformed_children.append(XOverXRemover.transform_tree(child))
        return Tree(label, transformed_children)


class StandardTreeNormalizer(TreeTransformer):

    @classmethod
    def transform_tree(cls, tree):
        tree = FunctionNodeStripper.transform_tree(tree)
        tree = EmptyNodeStripper.transform_tree(tree)
        tree = XOverXRemover.transform_tree(tree)
        return tree


class TreeReader:
    """
    Abstract base class for tree readers.
    NOTE: Does not implement read_root_tree()
    NOTE: self.ff is an open file object for reading a file
    """

    def __iter__(self):
        return self

    def next(self):
        if self.next_tree is None:
            raise StopIteration
        else:
            tree = self.next_tree
            self.next_tree = self.read_root_tree()
            return tree

    # Java version of iterable...
    """
    def has_next(self):
        return self.next_tree is not None

    def next(self):
        if not self.has_next():
            raise LookupError("No more trees!")
        tree = self.next_tree
        self.next_tree = self.read_root_tree()
        return tree
    """

    def read_root_tree(self):
        raise NotImplementedError()

    def peek(self):
        ch = self.ff.read(1)  # read a byte
        self.ff.seek(-1, 1)   # move back one byte
        return ch

    def read_label(self):
        self.read_whitespace()
        return self.read_text()

    def read_leaf(self):
        label = self.read_text()
        return Tree(label)

    def read_text(self):
        s = []
        ch = self.ff.read(1)
        while not TreeReader.is_whitespace(ch) and \
                not TreeReader.is_left_paren(ch) and \
                not TreeReader.is_right_paren(ch):
            s.append(ch)
            ch = self.ff.read(1)
        self.ff.seek(-1, 1)
        return ''.join(s)

    def read_left_paren(self):
        self.read_whitespace()
        ch = self.ff.read(1)
        if not TreeReader.is_left_paren(ch):
            raise ValueError("Format error reading tree. Character %d." % \
                    (self.ff.tell() - 1))

    def read_right_paren(self):
        self.read_whitespace()
        ch = self.ff.read(1)
        if not TreeReader.is_right_paren(ch):
            import ipdb; ipdb.set_trace()
            raise ValueError("Format error reading tree. (filename: %s)" % self.ff.name)

    def read_whitespace(self):
        ch = self.ff.read(1)
        while TreeReader.is_whitespace(ch):
            ch = self.ff.read(1)
        self.ff.seek(-1, 1)

    @classmethod
    def is_whitespace(cls, ch):
        return ch == ' ' or ch == '\t' or ch == '\f' or ch == '\r' or ch == '\n'

    @classmethod
    def is_left_paren(cls, ch):
        return ch == '('

    @classmethod
    def is_right_paren(cls, ch):
        return ch == ')'

    @classmethod
    def is_semicolon(cls, ch):
        return ch == ';'

    def remove(self):
        return NotImplementedError()


class BioIETreeReader(TreeReader):

    def __init__(self, ff):
        self.ff = ff
        self.next_tree = self.read_root_tree()

    def read_root_tree(self):
        try:
            while True:
                self.read_comments_and_whitespace()
                if not TreeReader.is_left_paren(self.peek()):
                    return None
                self.ff.read(1)
                string = self.read_text()
                if string == "SENT":
                    break
                elif string == "SEC":
                    self.read_tree(False)
                else:
                    return None
            # Collections.singletonList(readTree(false)) ??
            return Tree(ROOT_LABEL, [self.read_tree(False)])
        except IOError:
            raise Exception("Error reading tree: %s\n" % self.ff.name)

    def read_tree(self, matchparen):
        if matchparen:
            self.read_left_paren()
        label = self.read_colonized_label()
        children = self.read_children()
        self.read_right_paren()
        return Tree(label, children)

    def read_colonized_label(self):
        self.read_whitespace()
        ret = self.read_text()
        i = ret.find(':')
        if i == -1:
            return ret
        else:
            return ret[:i]

    def read_children(self):
        self.read_whitespace()
        if not TreeReader.is_left_paren(self.peek()):
            return [self.read_leaf()] # Collections.singletonList(readLeaf())
        else:
            return self.read_child_list()

    def read_child_list(self):
        children = []
        self.read_whitespace()
        while not TreeReader.is_right_paren(self.peek()):
            children.append(self.read_tree(True))
            self.read_whitespace()
        return children

    def read_comments_and_whitespace(self):
        while True:
            self.read_whitespace()
            if not TreeReader.is_semicolon(self.peek()):
                return
            ch = self.ff.read(1)
            while not ch == '\n':
                ch = self.ff.read(1)


class PennTreeReader(TreeReader):

    def __init__(self, ff):
        self.ff = ff
        self.next_tree = self.read_root_tree()

    def read_root_tree(self):
        try:
            self.read_whitespace()
            if not TreeReader.is_left_paren(self.peek()):
                return None
            return self.read_tree(True)
        except IOError:
            raise Exception("Error reading tree: %s\n" % self.ff.name)

    def read_tree(self, is_root):
        self.read_left_paren()
        label = self.read_label()
        if len(label) == 0 and is_root:
            label = ROOT_LABEL
        children = self.read_children()
        self.read_right_paren()
        return Tree(label, children)

    def read_children(self):
        self.read_whitespace()
        if not TreeReader.is_left_paren(self.peek()):
            return [self.read_leaf()] # Collections.singletonList
        return self.read_child_list()

    def read_child_list(self):
        children = []
        self.read_whitespace()
        while not TreeReader.is_right_paren(self.peek()):
            children.append(self.read_tree(False))
            self.read_whitespace()
        return children


class GENIATreeReader(TreeReader):

    def __init__(self, ff):
        self.ff = ff
        self.next_tree = self.read_root_tree()

    def read_root_tree(self):
        try:
            self.read_whitespace()
            if not TreeReader.is_left_paren(self.peek()):
                return None
            return Tree(ROOT_LABEL, [self.read_tree(False)])
        except IOError:
            raise Exception("Error reading tree: %s\n" % self.ff.name)

    def read_tree(self, is_root):
        self.read_left_paren()
        label = self.read_label()
        if len(label) == 0 and is_root:
            label = ROOT_LABEL
        children = self.read_children()
        self.read_right_paren()
        return Tree(label, children)

    def read_children(self):
        children = []
        self.read_whitespace()
        while not TreeReader.is_right_paren(self.peek()):
            if TreeReader.is_left_paren(self.peek()):
                children.append(self.read_tree(False))
            else:
                ret = self.read_slash_label()
                if ret is not None:
                    children.append(ret)
            self.read_whitespace()
        return children

    def read_slash_label(self):
        label = self.read_text()
        i = label.rfind('/')
        if i == -1:
            return None
        while i > 0 and label[i-1] == '\\':
            i = label.rfind('/', 0, i-1)
        child_label = label[:i].replace('\\\\\\/', '\\/')
        return Tree(label[i+1:], [Tree(child_label)])


class PennTreeRenderer:
    """
    Renderer for pretty-printing trees according to the Penn Treebank indenting
    guidelines (mutliline).  Adapted from code originally written by Dan Klein
    and modified by Chris Manning.
    """
    @classmethod
    def render(cls, tree):
        s = []
        PennTreeRenderer.render_tree(tree, 0, False, False, False, True, s)
        s.append('\n')
        return ''.join(s)

    @classmethod
    def render_tree(cls, tree, indent, parent_label_null, first_sibling, \
            left_sibling_preterminal, top_level, s):
        # Condition for staying on same line in Penn Treebank
        suppress_indent = parent_label_null or \
                (first_sibling and tree.is_preterminal()) or \
                (left_sibling_preterminal and tree.is_preterminal() and \
                (tree.label is None or not tree.label.startswith('CC')))
        if suppress_indent:
            s.append(' ')
        else:
            if not top_level:
                s.append('\n')
            for i in range(indent):
                s.append('  ')
        if tree.is_leaf() or tree.is_preterminal():
            PennTreeRenderer.render_flat(tree, s)
            return
        s.append('(')
        s.append(tree.label)
        # TODO: tree.label is None or str(tree.label) is None...
        PennTreeRenderer.render_children(tree.children, indent + 1,
                tree.label is None, s)
        s.append(')')

    @classmethod
    def render_flat(cls, tree, s):
        if tree.is_leaf():
            s.append(tree.label)
            return
        s.append('(')
        s.append(tree.label)
        s.append(' ')
        s.append(tree.children[0].label)
        s.append(')')

    @classmethod
    def render_children(cls, children, indent, parent_label_null, s):
        first_sibling = True
        left_sib_is_preterm = True
        for child in children:
            PennTreeRenderer.render_tree(child, indent, parent_label_null,
                    first_sibling, left_sib_is_preterm, False, s)
            left_sib_is_preterm = child.is_preterminal()
            if child.label is not None and child.label.startswith('CC'):
                left_sib_is_preterm = False
            first_sibling = False


def splice_nodes(tree, filter_func):
    root_list = splice_nodes_helper(tree, filter_func)
    if len(root_list) > 1:
        raise Exception("splice_nodes: no unique root after splicing")
    if len(root_list) < 1:
        return None
    return root_list[0]


def splice_nodes_helper(tree, filter_func):
    spliced_children = []
    for child in tree.children:
        spliced_child_list = splice_nodes_helper(child, filter_func)
        spliced_children.extend(spliced_child_list)
    if filter_func(tree.label):
        return spliced_children
    return [Tree(tree.label, spliced_children)]


def prune_nodes(tree, filt):
    """
    Prunes out all nodes which match the provided filter (and nodes
    which dominate only pruned nodes).
    """
    return prune_nodes_helper(tree, filt)


def prune_nodes_helper(tree, filt):
    if filt.accept(tree.label):
        return None
    pruned_children = []
    for child in tree.children:
        pruned_child = prune_nodes_helper(child, filt)
        if pruned_child is not None:
            pruned_children.append(pruned_child)
    if len(pruned_children) == 0 and not tree.is_leaf():
        return None
    return Tree(label, pruned_children)


if __name__ == '__main__':
    import StringIO
    test_string = "((S (NP (DT the) (JJ quick) (JJ brown) (NN fox)) " + \
            "(VP (VBD jumped) (PP (IN over) (NP (DT the) (JJ lazy) " + \
            "(NN dog)))) (. .)))"
    o = StringIO.StringIO()
    o.write(test_string)
    o.seek(0)
    reader = PennTreeReader(o)
    tree = reader.next()
    print PennTreeRenderer.render(tree)
    print tree
