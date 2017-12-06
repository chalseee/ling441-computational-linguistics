#Chalse Okorom-Achuonye
#Homework 8 - LING 441

from nltk import ProbabilisticTree as Tree
from nltk import Nonterminal as NT
from nltk import PCFG


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
        new_node =  Node(cat, i, j)
        if self.get(cat, i, j) == None:
            self.xijtab[cat, i, j] = new_node
            if (j in self.jtab):
                self.jtab[j].append(new_node)
            else:
                self.jtab[j] = []
                self.jtab[j].append(new_node)
        return new_node

    def get (self, cat, i, j):
        return self.xijtab.get((cat, i, j))

    def ending_at (self, j):
        # Return value: a list of Nodes
        try:
            return self.jtab[j]
        except:
            return []


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
        cat = rule.lhs()
        node = self.chart.intern(cat, i, j)
        
        if type(children) == type(str()):
            new_logprob = rule.logprob()
        else:
            for x in range(len(children)):
                new_logprob = rule.logprob()
                if (type(children[x])) == type(str()):
                    r = self.grammar.productions(rhs=children[x])
                    for y in r:
                        new_logprob += y.logprob()
                else:
                    for c in children[x]:
                        if type(c) == type(list()):
                            c = c[0]
                        r = self.grammar.productions(rhs=c)
                        for y in r:
                            new_logprob += y.logprob()
            
        if (node.tree==None) or (new_logprob > node.tree.logprob()):
            if type(children) == type(str()):
                children = [children]
            node.tree = Tree(cat, children, logprob=new_logprob)
        
        if self.new_nodes==None:
           self.new_nodes = []
           self.new_nodes.append(node)
        else:
           self.new_nodes.append(node)
                
        if self.trace:
            print('new', node)
        else:
            print('old', node)
            
                
    def shift (self, j):
        # No return value
        # Side effect: calls create_node
        w = self.words[j-1]
        rule = self.grammar.productions(rhs=w)[0]
        self.create_node(rule, w, j-1, j)

    def extend_edges (self, node):
        # No return value
        # Side effect: calls create_node
        for p in self.chart.jtab[node.i]:
            if(p.j == node.i):
                rule = self.grammar.productions(rhs=p.cat)
                for r in rule:
                    if r.rhs()[1] == node.cat:
                        self.create_node(r, [p.tree, node.tree], p.i, node.j)
            
    def choose_node (self):
        # Returns a Node or None
        # Side effect: may delete a node from new_nodes
        i = 0
        for k in self.new_nodes:
            if k.i > i:
                i = k.i            
        result = self.new_nodes[i]
        del self.new_nodes[i]
        return result

    def run (self):
        # No return value
        # Side effect: calls shift, choose_node, extend_edges
        ptr = 0
        while True:
            if ptr == (len(self.words) - 1):
                break
            else:
                if self.new_nodes != []:
                    self.extend_edges(self.choose_node())
                else:
                    ptr += 1
                    self.shift(ptr)
                
    def __call__ (self, words):
        # Return value: a Tree or None
        # Side effect: calls reset, run
        pass
    

g = PCFG.fromstring(open('g2n.pcfg').read())
r = g.productions(lhs=NT('Det'))[0]
t = Tree(r.lhs(), r.rhs(), logprob=r.logprob())

node = Node(r.lhs(), 0, 1)

chart = Chart()
chart.xijtab[NT('Det'), 0, 1] = node
node = chart.intern(NT('Det'), 0, 1)
chart.intern(NT('V'), 0, 1)

parser = Parser(g)
parser.chart.intern(NT('NP'), 0, 1)
parser.reset("the cat".split())

parser.trace = True
parser.create_node(r, ['the'], 0, 1)

parser.shift(2)
node = parser.new_nodes[1]
parser.extend_edges(node)

parser.reset('Mary walked the cat in the park'.split())
parser.run()