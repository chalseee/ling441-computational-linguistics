#Chalse Okorom
#LING 441 - Homework 6

from math import log10
from hmm import example_model, Node, print_graph

#1
class Tagger (object):
	def __init__(self, hmm_model):
		self.model = hmm_model
	
	def reset(self, list_of_words):
		self.words = list_of_words
		self.nodes = []


#2
	def new_node(self, i, word, pos, prev_nodes):
		return Node(self.nodes[i].index, i, word, pos, prev_nodes)

	def build_graph(self):
		left_boundary = Node(0, -1, None, None, [])
		graph = []
		for w in self.words: #how to get words??
			graph.append(self.model.parts(w))
		
tagger = Tagger(example_model)
tagger.build_graph()
print_graph(tagger.nodes)
			
