class Constituent:

    def __init__(self, label, start, end):
        self.label = label
        self.start = start
        self.end = end

    def __eq__(self, o):
        if self is o:
            return True

        if not isinstance(o, Constituent):
            return False

        if (self.end != o.end):
            return False
        if (self.start != o.start):
            return False
        if (self.label != o.label):
            return False

        return True

    def __hash__(self):
        result = hash(self.label)
        result = 29 * result + self.start
        result = 29 * result + self.end
        return result
