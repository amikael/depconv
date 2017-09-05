import sys, LIBopts
from collections.abc import Sequence

def chop(line):
    if line[-1] == '\n':
        line = line[0:-1]
    return line

[ ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC, DEPSL, DEPSR, GAIF, EDGE, INV ] = range(0,15)

class CoNLLrec(Sequence):
    def __init__(self, L = None):
        self.reversed = False
        if L == None:
            #   [ ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC]
            L = [ 0 , '-',  '-',   '-',  '-',  '-',   0,    '-',    [],   '-' ]
        if len(L)-1 == MISC:
            #   [DEPSL, DEPSR, GAIF, EDGE, INV ]):
            L = L + [[],    [],    '',  ''   , ''  ]
        self.L = L
    def __len__(self):
        return len(self.L)
    def __getitem__(self, i):
        return self.L[i]
    def __setitem__(self, i, value):
        self.L[i] = value
    def print_plain(self):
        print('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t'.
              format(*self[ID:(MISC+1)]+[self[DEPSL],self[DEPSR],self[GAIF]]))
    def print_conll(self,opts):
        if opts.to == "latex":
            return
        if not opts.drop:
            print('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.
                  format(*self[ID:(MISC+1)]))
        else:
            print('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.
                  format(*self[ID:(FORM+1)]+["_","_","_","_","_",self[DEPREL],"_",self[MISC]]))

class CoNLLio:
    def __init__(self):
        self.n        = 0
        self.recs     = [[0,0,0,CoNLLrec()]]
        self.lines    = []
        self.running  = 0
    def __len__(self):
        return len(self.recs)
    def __getitem__(self, i):
        return self.recs[i]
    def __setitem__(self, i, value):
        self.recs[i] = value

    def read_conll(self, opts):
        self.reversed = False
        # assume that recs,comments,mwlines and running are initialized
        for line in sys.stdin:
            self.running = self.running + 1
            if line[0] == '#':
                self.lines.append([self.running,line])
            else:
                record = chop(line).split('\t')
                if '-' in record[0]:
                    #[a,b] = record[0].split('-')
                    self.lines.append([self.running,line])
                elif '.' in record[0]:
                    #[a,b] = record[0].split('.')
                    self.lines.append([self.running,line])
                else:
                    if len(record) < 2: # sentence end      
                        return
                    self.n = self.n + 1
                    self.recs.append([self.running,int(record[ID]),int(record[ID]),CoNLLrec(record)])
        if len(self) == 1:
            raise EOFError
        else: 
            raise BrokenPipeError

    def print_plain(self,opts):
        for i in range(0,self.n+1):
            self[i][3].print_plain()

    def print_conll(self,opts):
        # we merge records and other lines in the original order
        ls = [ r for [r,l]     in self.lines ] + [self.running]
        rs = [ r for [r,a,b,l] in self.recs  ] + [self.running]
        li = ri = 0
        while ls != rs:
            if ls[0] < rs[0]:
                if opts.to == "latex":
                    print("% ", self.lines[li][1], end="")
                else:
                    print(self.lines[li][1], end="")
                li = li + 1
                ls = ls[1:]
            else:
                if ri > 0:
                    self[ri][3].print_conll(opts)
                ri = ri + 1
                rs = rs[1:]
        print()

        
