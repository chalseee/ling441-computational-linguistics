#Chalse Okorom
#LING 441 - Homework 6

from math import log10
from hmm import example_model, print_graph, Node

#1
class Tagger (object):
	def __init__(self, hmm_model):
		self.model = hmm_model
	
	def reset(self, list_of_words):
		self.words = list_of_words
		self.nodes = []

#2
	def new_node(self, i, word, pos, prev_nodes):
		index = len(self.nodes)
		nd = Node(index, i, word, pos, prev_nodes)
		self.nodes.append(nd)
		return nd

	def build_graph(self):
			left_boundary = Node(0, -1, None, None, [])
			self.nodes.append(left_boundary)
			
			ind = 1
			prev_nodes = [left_boundary]
			for idx, w in enumerate(self.words):
				count = 0
				for pos in self.model.parts(w):
					self.nodes.append(Node(ind, idx, w, pos, prev_nodes))
					ind += 1
					count += 1
				
				prev_nodes = self.nodes[-count:]
					
			right_boundary = Node(ind, len(self.words), None, None, prev_nodes)
			self.nodes.append(right_boundary)
					
#3
	def edge_score(self, prv, nxt):
		#up to prev node - previous path score + emission cost
		result = prv.score + self.model.ecost(prv.pos, prv.word)

		#find transmission cost
		next_score = self.model.tcost(prv.pos, nxt.pos)
		if (next_score < 1):
			result += next_score
		return result
	
	def score_node(self, node):
		tmp = 10000
		for nd in node.prev_nodes:
			score = self.edge_score(nd, node)
			if (score and (tmp > score)):
				tmp = self.edge_score(nd, node)
				node.best_prev = nd
		return tmp

	def score_graph(self):
		self.nodes[0].score = 0
		valid_nodes = self.nodes[1:]

		for nd in valid_nodes:
			nd.score = self.score_node(nd)

#4
	def unwind(self):
		current_node = self.nodes[len(self.nodes) - 1] #right boundary node
		results = []
		while (current_node != self.nodes[1]):
			current_node = current_node.best_prev
			results.append(current_node.pos)
		return list(reversed(results))

#5
	def __call__(self, list_of_words): #Error on some model + sentence combinations					
		pos = self.unwind()
		return list(zip(list_of_words, pos))


#Tests
print("#1 tests: ")
tagger = Tagger(example_model)
print(tagger.model.tprob(None, 'NNS'))
tagger.reset(['dogs', 'bark', 'often'])
print(tagger.words, '\n')

print('\n#2 tests: ')
tagger.build_graph()
print_graph(tagger.nodes)

print('\n\n', '#3 tests: ')
(n1, n2, n3) = tagger.nodes[1:4]
n1.score = .1
n2.score = .9
print('edge_score(n1,n3) =',tagger.edge_score(n1, n3))
print('edge_score(n2,n3) =', tagger.edge_score(n2,n3))
print('\nscore_node(n3) =', tagger.score_node(n3))
print('n3.best_prev =', n3.best_prev)
tagger.score_graph()
print('tagger.score_graph():')
print_graph(tagger.nodes)
 

print ('\n\n', "#4 tests")
print(tagger.unwind())

print('\n\n', "#5 tests")
print(tagger.__call__(['dogs', 'bark', 'often']))
print(tagger(['dogs', 'bark', 'often']))

print('\nNode new: ', tagger.new_node(3, 'often', 'RB', tagger.nodes))

