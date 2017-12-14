import os
import sys

from NumberRangeFileFilter import NumberRangeFileFilter
import ling.Trees as Trees


class TreeCollection:
    """
    Collection of Trees.
    """

    def __init__(self, path, low_filenum, high_filenum):
        self.file_filter = NumberRangeFileFilter(
                ".mrg", low_filenum, high_filenum, True)
        self.files = self.get_files_under(path)
        self.trees = self.get_trees()
        self.index = 0


    def __iter__(self):
        return self


    def next(self):
        if self.index < len(self.trees):
            tree = self.trees[self.index]
            self.index += 1
            return tree
        else:
            raise StopIteration


    def get_files_under(self, path):
        files = []
        self.add_files_under(path, files)
        return files


    def add_files_under(self, root, files):
        #if not filter(root, self.file_filter.accept):
        if not self.file_filter.accept_sequential(root):
            return

        if os.path.isfile(root):
            files.append(root)
            return

        if os.path.isdir(root):
            children = os.listdir(root)
            for child in children:
                self.add_files_under(os.path.join(root, child), files)


    def get_trees(self):
        trees = []
        for i, tree_file in enumerate(self.files):
            if (i + 1) % 100 == 0:
                print "Tree %d" % (i + 1)
            ff = open(tree_file, 'rb')
            for tree in Trees.PennTreeReader(ff):
                trees.append(tree)
            ff.close()
        return trees


def read_trees(path, low_filenum=None, high_filenum=None):
    if low_filenum is None:
        low_filenum = 0
    if high_filenum is None:
        high_filenum = float('inf')
    return TreeCollection(path, low_filenum, high_filenum)


if __name__ == '__main__':
    trees = read_trees(sys.argv[1])
    none_trees = []
    for tree in trees:
        tree = Trees.StandardTreeNormalizer.transform_tree(tree)
        print Trees.PennTreeRenderer.render(tree)
