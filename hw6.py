#Chalse Okorom
#LING 441 Homework 6

import sys
from math import log10
from hmm import example_model, Node, print_graph

print(sys.version)

#1
class Tagger (object):
	def __init__(self, hmm_model):
		self.model = hmm_model
	
	def reset(list_of_words):
		self.words = list_of_words
		self.nodes = []


#2
def new_node(i, word, pos, prev_nodes): #is index right? put at end of list
	return Node(tagger.nodes[i].index, i, word, pos, prev_nodes)
	
def build_graph():
	pass

	
#3
def edge_score(node_a, node_b):
	pass

def score_node(node):
	pass

def score_graph():
	pass
	

#4
def unwind():
	pass
	

#5
#tagger.__call__(list)