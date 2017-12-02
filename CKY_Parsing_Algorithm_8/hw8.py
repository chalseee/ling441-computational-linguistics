
from nltk import ProbabilisticTree as Tree


class Node (object):

    def __init__ (self, cat, i, j):
        self.cat = cat
        self.i = i
        self.j = j
        self.tree = None

    def __repr__ (self):
        return '%s(%d,%d)' % (self.cat, self.i, self.j)


class Chart (object):

    def __init__ (self):
        self.xijtab = {}
        self.jtab = {}

    def reset (self):
        self.xijtab.clear()
        self.jtab.clear()

    def intern (self, cat, i, j):
        # Side effect: install new Node in xijtab and jtab if necessary
        # Return value: a Node 

    def get (self, cat, i, j):
        return self.xijtab.get((cat, i, j))

    def ending_at (self, j):
        # Return value: a list of Nodes


class Parser (object):

    def __init__ (self, grammar):
        self.grammar = grammar
        self.chart = Chart()
        self.words = None
        self.new_nodes = None
        self.trace = False

    def reset (self, words):
        self.words = words
        self.chart.reset()
        self.new_nodes = []

    def create_node (self, rule, children, i, j):
        # No return value
        # Side effect: calls the chart's intern method
        # Side effect: if the node already exists, may set its tree member
        # Side effect: may append a node to new_nodes

    def shift (self, j):
        # No return value
        # Side effect: calls create_node

    def extend_edges (self, node):
        # No return value
        # Side effect: calls create_node

    def choose_node (self):
        # Returns a Node or None
        # Side effect: may delete a node from new_nodes

    def run (self):
        # No return value
        # Side effect: calls shift, choose_node, extend_edges

    def __call__ (self, words):
        # Return value: a Tree or None
        # Side effect: calls reset, run
