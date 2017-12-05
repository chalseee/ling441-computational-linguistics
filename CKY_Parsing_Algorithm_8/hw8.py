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
            return None


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
        
        if node.tree == None:
            if self.new_nodes == None:
                self.new_nodes = []
            self.new_nodes.append(node)
            
        if len(children)==1 and type(children[0])==type(' '):
            new_logprob = rule.logprob()
            #print('len1 child')
        else:
            #print('lemgthy child')
            new_logprob = rule.logprob() #add correct ish here      
            for c in [children]:
                r = self.grammar.productions(rhs=c)[0]
                new_logprob += r.logprob()
            
        if (new_logprob > rule.logprob()) or node.tree==None:
            node.tree = Tree(cat, [children], logprob=new_logprob) #test if correct vars are used
                
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
                print('extend_edges():', p)
                rule = self.grammar.productions(rhs=p.cat)[0]
                try:
                    self.create_node(rule, [p.tree, node.tree], p.i, node.j)
                except:
                    return
            
    def choose_node (self):
        # Returns a Node or None
        # Side effect: may delete a node from new_nodes
        i = 0
        for k in self.new_nodes:
            if k.i > i:
                i = k.i            #should be right, fix after extend_edges() is correct
        del self.new_nodes[i]
        return self.new_nodes

    def run (self):
        # No return value
        # Side effect: calls shift, choose_node, extend_edges
        pass

    def __call__ (self, words):
        # Return value: a Tree or None
        # Side effect: calls reset, run
        self.reset()
        self.run()
    

g = PCFG.fromstring(open('g2n.pcfg').read())

r = g.productions(lhs=NT('Det'))[0]

t = Tree(r.lhs(), r.rhs(), logprob=r.logprob())

node = Node(r.lhs(), 0, 1)

chart = Chart()
chart.intern(NT('Det'), 0, 1)
chart.intern(NT('V'), 0, 1)
chart.intern(NT('VP'), 1, 3)

node = chart.intern(NT('Det'), 0, 1)

chart.ending_at(1)
chart.ending_at(2)

parser = Parser(g)

parser.trace = True
parser.create_node(r, ['the'], 0, 1)

parser.reset('the cat'.split())
parser.shift(1)
parser.new_nodes[0].tree

parser.shift(2)
node = parser.new_nodes[1]
parser.extend_edges(node)
print(parser.new_nodes[-1].tree)
