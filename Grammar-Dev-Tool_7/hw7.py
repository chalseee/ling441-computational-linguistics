#Chalse Okorom-Achuonye
#LING 441 - Homework 7
from nltk import CFG, ChartParser, tokenize, tree

class GDev (object):
    def __init__(self, n):
        self.name = n

    def load_grammar(self):
        file = open(str(self.name + '.cfg')).read()
        self.grammar = CFG.fromstring(file)
        
    def reload(self):
        self.load_grammar()
        self.parser = ChartParser(self.grammar)  

    def load_sents(self):
        #using a textfile instead of a .sents? won't let me make a .sents file?
        file = open(str(self.name + '.sents'))
        self.sents = []
        for line in file:
            if line[0] == '*':
                self.sents.append((False, line.strip()[1:]))
            else:
                self.sents.append((True, line.strip()))     
    
    def parses(self, sentence):
        words = tokenize.word_tokenize(sentence)
        try:
            return list(self.parser.parse(words))[0]
        except:
            return None  
        
    def regress(self):
        for s in self.sents: 
            prediction = type(self.parses(s[1])) == tree.Tree
            #print(self.parses(s[1]))
            if prediction != s[0]:
                if s[0] == False:
                    print ("!!" + " " + "*" + s[1])
                else:
                    print ("!!" + " " + " " + s[1])
            else:
                if s[0] == False:
                    print ("  " + " " + "*" + s[1])
                else:
                    print ("  " + " " + " " +  s[1])
                    
    def __call__(self):
        self.reload()
        self.regress()
            

gd = GDev('g2')
gd.load_grammar()
gd.load_sents()
gd.reload()
gd.regress()
#test-- is my grammar remotely ok?