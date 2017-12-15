import nltk, random, os, sys
from nltk import Model, Valuation, Assignment, Expression
from nltk.featstruct import unify, TYPE
from nltk.grammar import FeatureGrammar, FeatStructNonterminal
from nltk.tree import Tree
from nltk.parse.featurechart import FeatureChartParser


#--  Grammar  ------------------------------------------------------------------

class Grammar (object):

    def __init__ (self, name):
        self.__name = name
        self.__parser = None
        self.__grammar = None
        self.__sents = None
        self.__labels = None
        self.__domain = None
        self.__model = None
        self.__assignment = None
        self.__trans = None

        self.__current_index = None
        self.__current_sent = None
        self.__current_trees = None

        self.reload()


    def grammar (self):
        return self.__grammar

    def sents (self):
        for i in range(len(self.__sents)):
            self.sent(i, markcurrent=True)

    def _save (self):
        save_sents(self.__sents, self.__labels, '%s.sents' % self.__name)


    #--  Loading  ----------------------------------------------

    def reload (self):
        self._load_grammar()
        self._load_sents()
        self._load_model()
        self._load_trans()

    def _load_grammar (self):
        gfn = '%s.fcfg' % self.__name
        if not os.path.exists(gfn):
            print('ERROR: Grammar file not found: %s' % gfn)
        else:
            try:
                self.__parser = load_parser(gfn)
                self.__grammar = self.__parser.grammar()
            except Exception as e:
                print('ERROR: Unable to load grammar %s' % gfn)
                print(e)

    def _load_sents (self):
        sfn = '%s.sents' % self.__name
        if not os.path.exists(sfn):
            print('ERROR: Sentences file not found: %s' % sfn)
        else:
            try:
                (self.__sents, self.__labels) = load_sents(sfn)
                if self.__sents:
                    if self.__current_index is None:
                        self.__current_index = 0
                    self.__current_sent = self.__sents[self.__current_index]
            except Exception as e:
                print('ERROR: Unable to load sentences %s' % sfn)
                print(e)
        
    def _load_model (self):
        dfn = '%s.domain' % self.__name
        if os.path.exists(dfn):
            self.__domain = load_domain(dfn)

        mfn = '%s.model' % self.__name
        if os.path.exists(mfn):
            if self.__domain:
                try:
                    self.__assignment = Assignment(self.__domain)
                    self.__model = load_model(self.__domain, mfn)
                except Exception as e:
                    print('ERROR: Unable to load model file %s' % mfn)
                    print(e)
            else:
                print('ERROR: Cannot load %s: no domain file %s' % (mfn, dfn))

    def _load_trans (self):
        tfn = '%s.trans' % self.__name
        if os.path.exists(tfn):
            self.__trans = []
            for (lno, line) in enumerate(open(tfn)):
                line = line.rstrip()
                i = line.find(' ')
                if i < 0:
                    print('ERROR: missing sent number: %s line %d' % (tfn, lno))
                    return
                ns = line[:i]
                if not ns.isdigit():
                    print('ERROR: missing sent number: %s line %d' % (tfn, lno))
                    return
                n = int(ns)
                if n != lno:
                    print('ERROR: nonsequential sent number: %s line %d' % (tfn, lno))
                    return
                self.__trans.append(Expression.fromstring(line[i+1:]))


    #--  This sent  --------------------------------------------

    def get_sent (self, s):
        if s is None:
            return self.__current_sent
        elif isinstance(s, int):
            return self.__sents[s]
        elif isinstance(s, list):
            return s
        elif isinstance(s, str):
            return s.split()
        else:
            raise Exception('Not a sentence: %s' % s)

    def get_index (self, i=None):
        if i is None:
            if self.__current_index is None:
                raise Exception('No current sentence')
            return self.__current_index
        elif isinstance(i, int):
            return i
        else:
            raise Exception('Not a sentence index: %s' % i)

    def sent (self, i=None, markcurrent=False):
        i = self.get_index(i)
        sent = ' '.join(self.__sents[i])
        if markcurrent:
            if i == self.__current_index: c = ' =>'
            else: c = '   '
        else:
            c = ''
        print('%s%3d %2s %s' % (c, i, self.__labels[i], sent))

    def get_label (self, i=None):
        i = self.get_index(i)
        return self.__labels[i]

    def set_label (self, i, label=None):
        if label is None:
            label = i
            i = self.get_index()
        self.__labels[i] = label
        self._save()

    def goto (self, s):
        if isinstance(s, int):
            n = len(self.__sents)
            while s >= n: s -= n
            while s < 0: s += n
            self.__current_index = s
            self.__current_sent = self.__sents[s]
        else:
            self.__current_index = None
            self.__current_sent = self.get_sent(s)
        self.sent()

    def next (self):
        if self.__current_index is None:
            raise Exception('No current index')
        self.goto(self.__current_index + 1)

    def prev (self):
        if self.__current_index is None:
            raise Exception('No current index')
        self.goto(self.__current_index - 1)


    #--  Current trees  ----------------------------------------

    def get_tree (self, i=0):
        if self.__current_trees is None:
            raise Exception('No current trees')
        return self.__current_trees[i]

    def tree (self, i=0):
        if self.__current_trees is None:
            raise Exception('No current trees')
        print('Number of trees: %d.  Tree %d:' % \
            (len(self.__current_trees), i))
        print(self.__current_trees[i])

    def trees (self):
        if self.__current_trees is None:
            raise Exception('No current trees')
        print('Number of trees: %d' % len(self.__current_trees))
        for i in range(len(self.__current_trees)):
            print()
            print('Tree %d' % i)
            print(self.__current_trees[i])


    #--  Parse/predict  ----------------------------------------

    def get_parses (self, s=None):
        sent = self.get_sent(s)
        return list(self.__parser.parse(sent))

    def parse (self, s=None):
        sent = self.get_sent(s)
        self.__current_trees = list(self.__parser.parse(sent))
        self.trees()

    def get_pred (self, s=None):
        sent = self.get_sent(s)
        p = self.__parser
        try:
            next(p.parse(sent))
            return 'OK'
        except:
            return '*'

    def get_preds (self):
        return [self.get_pred(sent) for sent in self.__sents]

    def pred (self, s=None):
        if self.__current_index is not None:
            i = self.__current_index
            sent = self.__sents[i]
            pred = self.get_pred(sent)
            label = self.__labels[i]
            print('%3d %2s (%2s) %s' % (i, pred, label, ' '.join(sent)))
        else:
            sent = self.get_sent(s)
            print(self.get_pred(sent), sent)

    def preds (self):
        for i in range(len(self.__sents)):
            sent = self.__sents[i]
            pred = self.get_pred(sent)
            label = self.__labels[i]
            print('%3d %2s (%2s) %s' % (i, pred, label, ' '.join(sent)))

    def errors (self):
        preds = self.get_preds()
        i = 0
        for sent, lab, plab in zip(self.__sents, self.__labels, preds):
            if i == self.__current_index: c = ' =>'
            else: c = '   '
            if lab != plab:
                print('%s%3d %2s (%2s) %s' % (c, i, plab, lab, ' '.join(sent)))
            i += 1

        
    #--  Chart  ------------------------------------------------

    def chart (self):
        if self.__current_sent is None:
            raise Exception('No current sentence')
        sent = self.__current_sent
        c = self.__parser.chart_parse(sent)
        d = {}
        for e in c:
            if e.is_complete() and e.rhs() and e.length() > 0:
                if e.span() in d: d[e.span()].append(e)
                else: d[e.span()] = [e]
        for span in sorted(d):
            print(' '.join(sent[span[0]:span[1]]))
            for e in d[span]:
                print('   ', repr(e.lhs()), '->', end=' ')
                for cat in e.rhs(): print(repr(cat), end=' ')
                print()

    #--  Scoring  ----------------------------------------------

    def score (self):
        acc, sens, spec = compare_labels(self.__labels, self.get_preds())
        print('Accuracy:   ', acc)
        print('Sensitivity:', sens)
        print('Specificity:', spec)


    #--  Vocabulary  -------------------------------------------

    def gvocab (self):
        v = set()
        for r in self.__grammar.productions():
            for y in r.rhs():
                if isinstance(y, str):
                    v.add(y)
        return v

    def svocab (self):
        v = set()
        for sent in self.__sents:
            for w in sent:
                v.add(w)
        return v

    def unknown_words (self):
        gvocab = self.gvocab()
        svocab = self.svocab()
        diff = svocab - gvocab
        if diff:
            for w in sorted(diff):
                print(w)

    def unused_words (self):
        gvocab = self.gvocab()
        svocab = self.svocab()
        diff = gvocab - svocab
        if diff:
            for w in sorted(diff):
                print(w)

    def get_parts (self):
        v = set()
        for r in self.__grammar.productions():
            z = r.rhs()
            if len(z) == 1 and isinstance(z[0], str):
                x = r.lhs()
                if isinstance(x, FeatStructNonterminal):
                    x = x[TYPE]
                v.add(x)
        return v

    def parts (self):
        for p in sorted(self.get_parts()):
            print(p)


    #--  Generate  ---------------------------------------------

    def gen (self, n=1):
        self.__current_trees = []
        for i in range(n):
            t = self.gentree()
            self.__current_trees.append(t)
            print('%3d %s' % (i, ' '.join(frontier(t))))

    def gentree (self, ntries=100):
        for i in range(ntries):
            try:
                return self.generate_from(self.__grammar.start())
            except Failure:
                pass
        raise Exception("Too many failures")

    def iter_expansions (self, x):
        for r in self.__grammar.productions(lhs=x):
            bindings = {}
            x1 = unify(x, r.lhs(), bindings, rename_vars=False)
            if x1:
                yield (r, x1, bindings)

    def expansions (self, x):
        return list(self.iter_expansions(x))

    def generate_from (self, x):
        options = self.expansions(x)
        if not options:
            raise Failure
        (r, x, bindings) = random.choice(options)
        children = []
        for y in r.rhs():
            if isinstance(y, str):
                children.append(y)
            else:
                y = y.substitute_bindings(bindings)
                child = self.generate_from(y)
                children.append(child)
                # just to update the bindings
                if not unify(y, child.label(), bindings, rename_vars=False):
                    raise Exception("This can't happen")
        x = x.substitute_bindings(bindings).rename_variables()
        return Tree(x, children)
        

    #--  Keep  -------------------------------------------------

    def keep (self, s, label='OK'):
        if isinstance(s, int):
            sent = frontier(self.__current_trees[s])
        elif isinstance(s, list):
            sent = s
        elif isinstance(s, str):
            sent = s.split()
        else:
            raise Exception('Not a sentence: %s' % s)
        self.__sents.append(sent)
        self.__labels.append(label)
        self._save()


    #--  Semantics  --------------------------------------------

    def get_sem (self, i=None):
        i = self.get_index(i)

        if self.__trans:
            tgt_expr = self.__trans[i]
            star = '*'
        else:
            tgt_expr = None
            star = '??'

        try:
            trees = list(self.get_parses(i))
        except Exception as e:
            trees = None
            tree = '<PARSE ERROR: %s>' % e
            yield (0, tree, tgt_expr, None, star, None)

        if trees:
            for (j, tree) in enumerate(trees):
                value = None
                try:
                    label = tree.label()
                    expr = label.get('v')
                    if tgt_expr:
                        if expr != tgt_expr: star = '*'
                        else: star = ' '
                    err = False
                except Exception as e:
                    expr = '<FEATURE ERROR: %s>' % e
                    if tgt_expr: star = '*'
                    err = True

                if not err:
                    if expr:
                        if self.__model is not None:
                            try:
                                value = self.__model.satisfy(expr, self.__assignment)
                            except Exception as e:
                                value = '<MODEL ERROR: %s>' % e

                yield (j, tree, tgt_expr, expr, star, value)

    def sem (self, i=None):
        for (j, tree, tgt_expr, expr, star, value) in self.get_sem(i):
            print('[%d]' % j)
            print(tree)
            if tgt_expr is not None:
                print('Target: ', tgt_expr)
            print('Trans:', star, expr)
            print('Value:  ', value)

    def sems (self):
        for i in range(len(self.__sents)):
            sems = list(self.get_sem(i))
            if len(sems) == 0:
                print('[%d]' % i, '(no parse)')
            else:
                for (j, tree, tgt_expr, expr, star, value) in sems:
                    if expr is None: expr = '(no translation)'
                    if value is None: value = '(no value)'
                    print('[%d]' % i, j, star, expr, value)

    def sem_results (self):
        for i in range(len(self.__sents)):
            tgt = self.__trans[i]
            sems = list(self.get_sem(i))
            if len(sems) == 0:
                unique = False
                trans = None
                value = None
            else:
                unique = (len(sems) == 1)
                trans = sems[0][3]
                value = sems[0][5]
            yield (tgt, trans, value, unique)


    #--  Interactive  ------------------------------------------

    def run (self):
        while True:
            try:
                line = input('G> ')
                com = line.strip()
                if len(com) == 0: continue
                elif com == 'q': break
                elif com == 's': self.sent()
                elif com == 'ss': self.sents()
                elif com == 'n': self.next()
                elif com == 'b': self.prev()
                elif com.isdigit(): self.goto(int(com))
                elif com == 'p': self.parse()
                elif com == 'c': self.chart()
                elif com == 'e': self.errors()
                elif com == 'sc': self.score()
                elif com == 'r': self.reload()
                elif com == 'unk': self.unknown_words()
                elif com == 'unt': self.unused_words()
                elif com == 'pos': self.parts()
                elif com == 'gen': self.gen(10)
                elif com == 'tt': self.trees()
                elif com.startswith('t'):
                    i = com[1:]
                    if not i.isdigit():
                        print('Expected a digit:', i)
                    else:
                        self.tree(int(i))
                elif com.startswith('k'):
                    i = com[1:]
                    if not i.isdigit():
                        print('Expected a digit:', i)
                    else:
                        self.keep(int(i))
                elif com.startswith('*'):
                    i = com[1:]
                    if not i.isdigit():
                        print('Expected a digit:', i)
                    else:
                        self.keep(int(i), label='*')
                elif com == 'sem': self.sem()
                elif com == 'sems': self.sems()
                else:
                    print('Unrecognized command:', com)
                
            except EOFError:
                break
            except Exception as e:
                print('ERR:', type(e), e)


#--  Parser  -------------------------------------------------------------------

def load_parser (fn):
    return FeatureChartParser(FeatureGrammar.fromstring(open(fn).read()))


#--  Trees  --------------------------------------------------------------------

def iter_frontier (tree):
    if isinstance(tree, str):
        yield tree
    else:
        for child in tree:
            for leaf in iter_frontier(child):
                yield leaf

def frontier (tree):
    return list(iter_frontier(tree))

def frontier_string (tree):
    return ' '.join(frontier(tree))


#--  Sentences  ----------------------------------------------------------------


def load_sents (fn):
    labsents = list(iter_labeled_sents(fn))
    sents = [s for (s,l) in labsents]
    labels = [l for (s,l) in labsents]
    return (sents, labels)

def iter_labeled_sents (fn):
    for (i, line) in enumerate(open(fn)):
        line = line.strip()
        label = 'OK'
        if line.startswith('*'):
            label = '*'
            line = line[1:]
        yield (line.split(), label)

def save_sents (sents, labels, fn):
    if len(sents) != len(labels):
        raise Exception('Numbers of sents and labels do not match')
    f = open(fn, 'w')
    for i in range(len(sents)):
        if labels[i] == 'OK': s = ''
        else: s = '*'
        f.write('%s%s\n' % (s, ' '.join(sents[i])))
    f.close()


#--  Models  -------------------------------------------------------------------

def load_domain (fn):
    d = set()
    for line in open(fn):
        for word in line.split():
            d.add(word)
    return d


class Tokenizer (object):

    def __init__ (self, fn):
        self.fn = fn
        self.stream = open(fn)
        self.lno = 0
        self.line = None
        self.offset = 0
    
    def __iter__ (self): return self

    def __next__ (self):
        while True:
            if self.line is None or self.offset >= len(self.line):
                if self.stream is None:
                    raise StopIteration
                self.line = next(self.stream)
                self.lno += 1
                self.offset = 0
            c = self.line[self.offset]
            if c in '{}(),':
                self.offset += 1
                return (c, c, self.lno)
            elif (c == '=' 
                  and self.offset+1 < len(self.line)
                  and self.line[self.offset+1] == '>'):
                self.offset += 2
                return ('=>', '=>', self.lno)
            elif c.isspace():
                self.offset += 1
            elif c.isalnum():
                for j in range(self.offset+1, len(self.line)):
                    if not self.line[j].isalnum():
                        break
                s = self.line[self.offset:j]
                self.offset = j
                return ('word', s, self.lno)
            else:
                raise Exception('Bad character %s: %s line %d' % (c, self.fn, self.lno))


def load_model (dom, fn):
    tokens = Tokenizer(fn)
    pairs = []
    try:
        while True:
            (t, s, lno) = next(tokens)
            if t != 'word':
                raise Exception('Expecting a word, got %s: %s line %d' % (s, fn, lno))
            name = s
            (t, s, lno) = next(tokens)
            if t != '=>':
                raise Exception('Expecting =>, got %s: %s line %d' % (s, fn, lno))
            (t, s, lno) = next(tokens)
            if t == 'word':
                pairs.append((name, s))
            elif t == '{':
                (t, s, lno) = next(tokens)
                if t == 'word':
                    value = read_set(s, tokens, fn)
                elif t == '}':
                    value = set()
                elif t == '(':
                    value = read_relation(tokens, fn)
                else:
                    raise Exception('Expecting word or (, got %s: %s line %d' % (s, fn, lno))
                pairs.append((name, value))
            else:
                raise Exception('Expecting word or {, got %s: %s line %d' % (s, fn, lno))
    except StopIteration:
        return Model(dom, Valuation(pairs))


def read_set (elt, tokens, fn):
    value = set([elt])
    try:
        while True:
            (t, s, lno) = next(tokens)
            if t == '}':
                return value
            elif t != ',':
                raise Exception('Expecting comma or }, got %s: %s line %d' % (s, fn, lno))
            (t, s, lno) = next(tokens)
            if t == 'word':
                value.add(s)
            else:
                raise Exception('Expecting word, got %s: %s line %d' % (s, fn, lno))
    except StopIteration:
        raise Exception('Expecting word or }, got end of file: %s' % (s, fn))


def read_relation (tokens, fn):
    value = set()
    try:
        while True:
            (t, s, lno) = next(tokens)
            if t == 'word':
                first = s
            else:
                raise Exception('Expecting word, got %s: %s line %d' % (s, fn, lno))
            (t, s, lno) = next(tokens)
            if t != ',':
                raise Exception('Expecting comma, got %s: %s line %d' % (s, fn, lno))
            (t, s, lno) = next(tokens)
            if t == 'word':
                second = s
            else:
                raise Exception('Expecting word, got %s: %s line %d' % (s, fn, lno))
            (t, s, lno) = next(tokens)
            if t != ')':
                raise Exception('Expecting ), got %s: %s line %d' % (s, fn, lno))
            value.add((first, second))

            (t, s, lno) = next(tokens)
            if t == '}':
                return value
            elif t == ',':
                (t, s, lno) = next(tokens)                
                if t != '(':
                    raise Exception('Expecting (, got %s: %s line %d' % (s, fn, lno))
            else:
                raise Exception('Expecting } or comma, got %s: %s line %d' % (s, fn, lno))
    except StopIteration:
        raise Exception('Premature end of file: %s' % fn)
            

#--  Utilities  ----------------------------------------------------------------

def compare_labels (labels, pred):
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    for l, p in zip(labels, pred):
        if l == 'OK':
            if p == 'OK': tp += 1
            else: fn += 1
        else:
            if p == 'OK': fp += 1
            else: tn += 1
    ok = tp + fn
    bad = tn + fp
    n = ok + bad
    acc = (tp + tn)/float(n)
    if ok > 0: sens = tp/float(ok)
    else: sens = 1.0
    if bad > 0: spec = tn/float(bad)
    else: spec = 1.0
    return (acc, sens, spec)


class Failure (Exception):
    pass


#--  Main  ---------------------------------------------------------------------

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        print('** Usage: grammar')
        sys.exit(1)
    Grammar(args[0]).run()
