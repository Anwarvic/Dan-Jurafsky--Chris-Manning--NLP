

class BinaryRule():
    """
    A binary grammar rule with score representing its probability.
    """

    def __init__(self, parent, left_child, right_child):
        self.parent = parent
        self.left_child = left_child
        self.right_child = right_child
        self.score = 0.0
        #I added these two member variables to help me in Turning the Parsing Traingle into a tree
        self.origin = ( (None,None), (None,None) )
        self.des = (None,None) #for destination


    def __str__(self):
        if self.origin != ( (None,None), (None,None) ) or self.des != (None, None):
            origin_left = self.origin[0]
            origin_right = self.origin[1]
            return "(%s) -> (%s) (%s) %%%s FROM:(%d,%d)(%d,%d) TO:(%d,%d)\n" \
                % (self.parent, self.left_child, self.right_child, self.score, \
                    origin_left[0], origin_left[1], origin_right[0], origin_right[1], self.des[0], self.des[1])
                
        return "(%s) -> (%s) (%s) %%%s\n" % (self.parent, self.left_child, self.right_child, self.score)


    def __hash__(self):
        result = hash(self.parent)
        result = 29 * result + hash(self.left_child)
        result = 29 * result + hash(self.right_child)
        return result


    def __eq__(self, o):
        if self is o:
            return True

        if not isinstance(o, BinaryRule):
            return False

        if (self.left_child != o.left_child):
            return False
        if (self.right_child != o.right_child):
            return False
        if (self.parent != o.parent):
            return False
        return True


class UnaryRule():
    """
    A unary grammar rule with score representing its probability.
    """

    def __init__(self, parent, child):
        self.parent = parent
        self.child = child
        self.score = 0.0
        #I added these two member variables to help me in Turning the Parsing Traingle into a tree
        self.origin = (None,None)
        self.des = (None,None) #for destination


    def __str__(self):
        if self.origin != (None, None) or self.des != (None, None):
            return "(%s) -> (%s) %%%s FROM:(%s,%s) TO:(%s,%s)\n" \
                        % (self.parent, self.child, self.score, self.origin[0], self.origin[1], self.des[0], self.des[1])
        return "(%s) -> (%s) %%%s\n" % (self.parent, self.child, self.score)


    def __hash__(self):
        result = hash(self.parent)
        result = 29 * result + hash(self.child)
        return result


    def __eq__(self, o):
        if self is o:
            return True

        if not isinstance(o, UnaryRule):
            return False

        if (self.child != o.child):
            return False
        if (self.parent != o.parent):
            return False
        return True


if __name__ == "__main__":
    rule = UnaryRule('parent', 'child')
    print isinstance(rule, BinaryRule)
    rule.origin = (0,0)
    rule.des = (1,1)
    print str(rule)

    print hash(rule)