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
        return self.xijtab[cat, i, j]

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
        rule = self.grammar.productions(rhs=w)
        for r in rule:
            self.create_node(r, w, j-1, j)

    def extend_edges (self, node):
        # No return value
        # Side effect: calls create_node
        for p in self.new_nodes:
            if(p.j == node.i):
                rule = self.grammar.productions(rhs=p.cat)
                for r in rule:
                    if r.rhs()[1] == node.cat:
                        self.create_node(r, [p.tree, node.tree], p.i, node.j)
            
    def choose_node (self):
        # Returns a Node or None
        # Side effect: may delete a node from new_nodes
        if self.new_nodes == [] or self.new_nodes == None:
            return None
        
        i = 0
        for idx, node in enumerate(self.new_nodes):
            if node.i > i:
                i = idx
        chosen_node = self.new_nodes[i]
        del self.new_nodes[i]
        return chosen_node

    def run (self):
        # No return value
        # Side effect: calls shift, choose_node, extend_edges
        ptr = 0
        while True:
            if (ptr == len(self.words)):
                break
            
            if self.new_nodes != []:
                nd = self.choose_node()
                self.extend_edges(nd) 
            else:
                ptr+=1
                self.shift(ptr)

    def __call__ (self, words):
        # Return value: a Tree or None
        # Side effect: calls reset, run
        self.reset(words)
        self.run()
    
        for node in self.new_nodes:
            if node.cat == 'S':
                return node.tree    

g = PCFG.fromstring(open('g2n.pcfg').read())
parser = Parser(g)
parser.trace = True
parser.reset('Mary walked the cat in the park'.split())
parser.run()