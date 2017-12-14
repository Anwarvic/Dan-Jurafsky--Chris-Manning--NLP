import os

import ling.Trees as Trees

class NumberRangeFileFilter:
    """
    Class to use as filter for files (by file number).
    """
    def __init__(self, extension, low_filenum, high_filenum, recurse):
        self.i = -1
        self.high_filenum = high_filenum
        self.low_filenum = low_filenum
        self.extension = extension
        self.recurse = recurse


    def accept(self, pathname):
        if os.path.isdir(pathname):
            return self.recurse
        name = os.path.basename(pathname)
        if not name.endswith(self.extension):
            return False
        last_num_index = self.get_last_number_index(name)
        if last_num_index == -1:
            return False
        num_end_loc = last_num_index + 1
        num_start_loc = self.get_last_non_number_index(name, last_num_index) + 1
        file_num = int(name[num_start_loc:num_end_loc])
        if file_num >= self.low_filenum and file_num <= self.high_filenum:
            return True
        return False


    def accept_sequential(self, pathname):
        if os.path.isdir(pathname):
            return self.recurse
        name = os.path.basename(pathname)
        if not name.endswith(self.extension):
            return False
        self.i += 1
        return self.i >= self.low_filenum and self.i <= self.high_filenum


    def get_last_number_index(self, name):
        index = len(name) - 1
        while index >= 0 and not name[index].isdigit():
            index -= 1
        if index < -1:
            return -1
        return index


    def get_last_non_number_index(self, name, last_number_index):
        index = last_number_index - 1
        while index >= 0 and name[index].isdigit():
            index -= 1
        if index < -1:
            return -1
        return index
