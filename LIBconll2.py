
import sys, LIBopts
from LIBconll1 import *
from collections.abc import Sequence

Lopen   = ["<","<!","<!","❰"]
Lclose  = ["\\","\\!","\\!","】"]
Ropen   = ["/","/!","/!","【"]
Rclose  = [">",">!",">!","❱"]

Lwopen  = ["<","<","<","<"]
Rwclose = [">",">",">",">"]
Lwclose = ["\\","","\\0",""]
Rwopen  = ["/","","/0",""]

def reverse(list):
    return list[::-1]
   
class CoNLL(CoNLLio):

    def viz(self):
        print("\\begin{dependency}[theme = simple, edge style=-]")
        print("\\begin{deptext}[column sep=1em]")
        for i in range(1, self.n+1):
            if i > 1:
                print("\\&",end="")
            print("{}".format(self[i][3][FORM]),end="")
        print("\\\\\\end{deptext}")
        for i in range(1, self.n+1):
            if self[i][3][HEAD] != '_':
                print("\\depedge\\{{{}}}{{{}}}{{}}".format(i,self[i][3][HEAD]))
        print("\\end{dependency}")
        
    def root(self):
        return self[0][3][DEPSR][-1]

    def undoreverseheads(self):
        for i in range(0,self.n+1):
            self[i][3][DEPSR] = []
            self[i][3][DEPSL] = []
        self.reversed = False
        
    def reverseheads(self):
        if self.reversed:
            return
        self.reversed = True
        # uses HEAD to build DEPSL and DEPSR
        for i in range(1,self.n+1): # we skip the root (0) that cannot have a head
            if self[i][3][HEAD] != '_':
                h = int(self[i][3][HEAD])
                if i < h:
                    self[h][3][DEPSL].append(i)
                else:
                    self[h][3][DEPSR].append(i)

    def normalize_dbrackets(self,code):
        # We have a code word that has correct word boundaries but is not necessarily otherwise balanced:
        # 
        #  1) word does not have a head -- LEAVE UNLINKED (unlikely to happen)
        #            / {} I {} > have / {} no < {} \ > head ==>
        #            / {} I {} > have / {} no < {} \ > head
        #
        #  2) word has more than 1 head -- PICK the first (unlikely to happen)
        #            / {} I {} > > have / {} no < {} \ > head ==>
        #            / {} I {} >   have / {} no < {} \ > head
        #
        #  3) a dependent of a word is missing -- REMOVE the dependency bracket / or \:
        #            / {} I < {} \ > have / / {} no < {} \ > head ==>
        #            / {} I < {} \ > have /   {} no < {} \ > head 
        # 
        #  4) the head is missing -- REMOVE head links < and > that are not matched
        #            / {} I < {} \ have < / {} no < {} \ > head ==>
        #            / {} I < {} \ have   / {} no < {} \ > head ==>
        #
        # taxonomy of errors in bracketed trees => article?
        # necessary for making the converter complete
        code2 = ""
        new   = True
        for i in range(0,len(code)):
            if code[i] == '{':
                code2 = code2 + code[i]
                new = True
            elif new:
                code2 = code2 + code[i]
                if code[i] in "<>":
                    new = False
            elif code[i] not in "<>":
                code2 = code2 + code[i]
        code = code2
        # remove extra \\-symbols and >-symbols on empty stacks
        [stack,buff,code] = [[],code,""]
        while len(buff) > 0:
            [c,buff] = [buff[0],buff[1:]]
            if c == "/":
                [stack,code] = [ [c] + stack, code + "/" ]
            elif c == "<":
                [stack,code] = [ [c] + stack, code + "<" ]
            elif c == ">" and stack != [] and stack[0] == '/':
                [stack,code] = [ stack[1:], code + ">" ]
            elif c == "\\" and stack != [] and stack[0] == '<':
                [stack,code] = [ stack[1:], code + "\\" ]
            elif c == "\\":
                continue
            elif c == ">":
                continue
            else:
                code  = code + c
        # remove extra / and > symbols
        [stack,buff,code] = [[],code,""]
        while len(buff) > 0:
            [c,buff] = [buff[-1],buff[:-1]]
            if c == "\\":
                [stack,code] = [ [c] + stack, "\\"+code ]
            elif c == ">":
                [stack,code] = [ [c] + stack, ">" +code ]
            elif c == "<" and stack != [] and stack[0] == '\\':
                [stack,code] = [ stack[1:], "<" + code ]
            elif c == "/" and stack != [] and stack[0] == '>':
                [stack,code] = [ stack[1:], "/"+code ]
            elif c == "/":
                continue
            elif c == "<":
                continue
            else:
                code  = c+code
        return code
        
    def normalize_cbrackets(self,code):
        return code

    # Decodes headed constituent bracketing
    def decode_cbrackets(self):
        # create a code string for the tree
        code = ""
        for i in range(1,self.n+1):
            code = code + self[i][3][MISC]
        # fix errors:
        code = self.normalize_cbrackets(code)
        # now read the code string in both directions and compute heads
        stack = [0]
        [j,buff] = [0,code]
        while len(buff) > 0:
            [c,buff] = [buff[0],buff[1:]]
            if c == "(":
                stack = [-1] + stack
            elif c == ")":
                stack = stack[1:]
            else:
                stack[0] = j = j+1
                if stack[1] != -1:
                    self[j][3][HEAD] = stack[1]
        [j,buff] = [self.n+1,code]
        while len(buff) > 0:
            [c,buff] = [buff[-1],buff[:-1]]
            if c == ")":
                stack = [-1] + stack
            elif c == "(":
                stack = stack[1:]
            else:
                stack[0] = j = j-1
                if stack[1] != -1:
                    self[j][3][HEAD] = stack[1]

    # Decodes balanced dependency bracketing
    def decode_dbrackets(self):
        # create a code string for the tree
        code = "/"
        for i in range(1,self.n+1):
            code = code + "{}" + self[i][3][MISC]
            self[i][3][MISC] = '_'
        # fix errors:
        code = self.normalize_dbrackets(code)
        # use the dec algorithm of YJGR 2017 to decode the code string
        i = 0
        stack = []
        while len(code) > 0:
            c = code[0]
            code = code[1:]
            if c == "/" or c == "<":
                stack = [i] + stack
            elif c == ">" or c == "\\":
                j = stack[0]
                stack = stack[1:]
                if c == ">":
#                    print("{} gets head {}".format(i,j))
                    self[i][3][HEAD] = j
                else:
#                    print("{} gets head {}".format(j,i))
                    self[j][3][HEAD] = i
            elif c == "{":
                i = i+1
            
    # Separates dependency relation from the brackets
    def extract_deprel(self):
        for i in range(1,self.n+1):
            misc   = self[i][3][MISC]
            deprel = ""
            bracks = ""
            while misc != "":
                if misc[0] in "/><\\()[]":
                    bracks = bracks + misc[0]
                else:
                    deprel = deprel + misc[0]
                misc = misc[1:]
            self[i][3][DEPREL] = deprel
            self[i][3][MISC]   = bracks

    # Encodes the dependency relation and the links
    def init_news(self,opts):
        for i in range(1,self.n+1):
            if opts.labeled:
                init = self[i][3][DEPREL]
            else:
                init = self[i][3][FORM]
            if opts.to == "oflazer":
                self[i][3][EDGE] = "*"
            if opts.to == "gibson":
                self[i][3][MISC] = init
            else: # gaifman, ylijyra, ylijyra2,
                self[i][3][EDGE] = init


    def finalize(self,opts):
        for i in range(1,len(self)):
            if opts.to in ["oflazer","ylijyra","ylijyra2"]:
                self[i][3][MISC] = self[i][3][EDGE]
            elif opts.to == "gaifman":
                self[i][3][MISC] = self[i][3][GAIF]
            else:
                self[i][3][MISC] = self[i][3][MISC]
            self[i][3][HEAD] = "_"
            if opts.labeled:
                self[i][3][DEPREL] = "_"

    def _to_gi(self,opts):
        for i in range(1,len(self)):
            if self[i][3][HEAD] == 0:
                self[i][3][MISC] = "0" + self[i][3][MISC]
            else:
                self[i][3][MISC] = str(int(self[i][3][HEAD]) - int(self[i][3][ID])) + self[i][3][MISC]
        
    def _to_ga(self,lstack,h,rstack):
        # the method: - recursion is indicated with brackets
        #             - the brackets are placed before the leftmost and after the rightmost sibling
        if self[h][3][DEPSL] != []:                                     # if left dependents
            self._to_ga(lstack + "(", self[h][3][DEPSL][0],"")      # recurse to the leftmost
        else:                                                        # the left recursion ends here
            self[h][3][GAIF] = lstack + "(" + self[h][3][GAIF]            
        for d in self[h][3][DEPSL][1:] + self[h][3][DEPSR][:-1]:           # center recursion
           self._to_ga("",d,"")                                  # needs no brackets
           
        if self[h][3][DEPSR] != []:                                     # if right dependents
            self._to_ga("",self[h][3][DEPSR][-1],")" + rstack)      # recurse to the rightmost
        else:                                                        # the right recursion ends here
            self[h][3][GAIF] = self[h][3][GAIF] + ")" + rstack             

    def _to_of(self,opts,h):
        for d in self[h][3][DEPSL]:
            if opts.labeled:
                self[d][3][EDGE] = self[d][3][DEPREL]
                self[h][3][EDGE] = self[d][3][DEPREL].upper() + "." + self[h][3][EDGE]
            else:
                self[d][3][EDGE] = self[d][3][EDGE] + "d"
                self[h][3][EDGE] = "H" + self[h][3][EDGE]
            self._to_of(opts,d)
        for d in reverse(self[h][3][DEPSR]):
            if opts.labeled:
                self[h][3][EDGE] = self[h][3][EDGE] + "." + self[d][3][DEPREL].upper()
                self[d][3][EDGE] = self[d][3][DEPREL]
            else:
                self[h][3][EDGE] = self[h][3][EDGE] + "H"
                self[d][3][EDGE] = "d" + self[d][3][EDGE]
            self._to_of(opts,d)
            
    def _to_yj(self,h,prev,mode):
        for d in self[h][3][DEPSL]:
            if d == self[h][3][DEPSL][0] and prev != -1: # outermost
                self[d][3][EDGE] = self[d][3][EDGE]  + " " + Lopen[mode]  
                self[h][3][EDGE] = Lclose[mode] + " " + self[h][3][EDGE]
                self._to_yj(d,1,mode)
            else:
                self[d][3][EDGE] = self[d][3][EDGE] + " " + Lwopen[mode]
                self[h][3][EDGE] = Lwclose[mode] + " " + self[h][3][EDGE]
                self._to_yj(d,0,mode)
        for d in self[h][3][DEPSR]:
            if d == self[h][3][DEPSR][-1] and prev != 1: # outermost
                self[h][3][EDGE] = self[h][3][EDGE] + " " + Ropen[mode]  
                self[d][3][EDGE] = Rclose[mode] + " " + self[d][3][EDGE]   
                self._to_yj(d,-1,mode)
            else:
                self[h][3][EDGE] = self[h][3][EDGE] + " " + Rwopen[mode]  
                self[d][3][EDGE] = Rwclose[mode] + " " + self[d][3][EDGE]   
                self._to_yj(d,0,mode)
                    
    def yj_code(self,mode):
        code =  Ropen[mode]
        for i in range(1,self.n+1):
            code = code + " " + self[i][3][MISC]
        return code

    def code_depth(self,mode):
        code      = self.yj_code(mode).split(" ")
        height    = -1
        maxheight = -1
        residual  = ""
        for c in code:
            if c in [Lopen[mode],Ropen[mode]]:
                height = height + 1
            elif c in [Lclose[mode],Rclose[mode]]:
                height = height - 1
            if height > maxheight:
                maxheight = height
        return maxheight
        
    # EXTRACTING LABELS
    def labels_of(self,opts):
        self.extract_deprel()
    def labels_gi(self,opts):
        return
    def labels_ga(self,opts):
        self.extract_deprel()
        # add asterisk to each line
        for i in range(1,self.n+1):
            m = self[i][3][MISC]
            if m == "":
                self[i][3][MISC] = "*"
            elif m[0] == ")":
                self[i][3][MISC] = "*" + m
            else:
                tail = ( m+")" ).index(")")
                self[i][3][MISC] = m[0:tail] + "*" + m[tail:]
    def labels_yj(self,opts):
        self.extract_deprel()

    # DECODING LINKS
    def from_of(self,opts):
        # convert d and H to >< and /\\
        for i in range(1,self.n+1):
            ast  = False
            misc = self[i][3][MISC]
            misc2= ""
            for j in range(0,len(misc)):
                if misc[j] == '*':
                    ast = True
                elif misc[j] == 'd':
                    if ast:
                        misc2 = misc2 + '<'
                    else:
                        misc2 = misc2 + '>'
                elif ast:
                    misc2 = misc2 + '/'
                else:
                    misc2 = misc2 + '\\'
            self[i][3][MISC] = misc2
        self.decode_dbrackets()
    def from_gi(self,opts):
        for i in range(1,len(self)):
            if self[i][3][MISC] == 0:
                self[i][3][HEAD] = 0
            elif self[i][3][MISC] != "_":
                self[i][3][HEAD] = int(self[i][3][ID]) + int(self[i][3][MISC])
            self[i][3][MISC] = "_"
    def from_ga(self,opts):
        self.decode_cbrackets()
        for i in range(1,len(self)):
            self[i][3][MISC] = "_"
    def from_yj(self,opts):
        self.decode_dbrackets()
            
    def extract_labels(self, opts):
        if opts.labeled:
            if opts.fr == "gaifman":
                self.labels_ga(opts)
            elif opts.fr == "oflazer":
                self.labels_of(opts)
            elif opts.fr == "gibson":
                self.labels_gi(opts)
            elif opts.fr == "ylijyra":
                self.labels_yj(opts)
            elif opts.fr != "conll":
                print("unspecified output format\n", file=sys.stderr)

    def convert_from(self, opts):
        self.extract_labels(opts)
        if opts.fr == "gaifman":
            self.from_ga(opts)
        elif opts.fr == "oflazer":
            self.from_of(opts)
        elif opts.fr == "gibson":
            self.from_gi(opts)
        elif opts.fr == "ylijyra":
            self.from_yj(opts)
        elif opts.fr != "conll":
            print("unspecified input format\n", file=sys.stderr)

    def convert_to(self, opts):
        self.reverseheads()
        self.init_news(opts)
        if opts.to == "gaifman":
            self._to_ga("",self.root(),"")
        elif opts.to == "oflazer":
            self._to_of(opts,0)
        elif opts.to == "gibson":
            self._to_gi()
        elif opts.to == "ylijyra":
            self._to_yj(0,-1,0)
        elif opts.to == "ylijyra2":
            self._to_yj(0,-1,1)
        elif opts.to == "latex":
            self.viz()
        elif opts.to != "conll":
            print("unspecified output format\n", file=sys.stderr)
            return
        self.finalize(opts)
            
    def test_projective(self):
        for j in range(1,self.n+1):
            i = int(self[j][3][HEAD])
            h = int(self[i][3][HEAD])
            if (h < j) and (i < h):
                return False
            if (h > j) and (i > h):
                return False
        for j in range(1,self.n):
            for i in range(j+1,self.n+1):
                h = int(self[j][3][HEAD])
                if h > j:
                    edge1 = [j,h]
                else:
                    edge1 = [h,j]
                k = int(self[i][3][HEAD])
                if k > i:
                    edge2 = [i,k]
                else:
                    edge2 = [k,i]
                if edge1[0] < edge2[0] and edge2[0] < edge1[1] and edge1[1] < edge2[1] :
                    return False
                if edge2[0] < edge1[0] and edge1[0] < edge2[1] and edge2[1] < edge1[1] :
                    return False
        return True

    def _projectivise(self, opts):
        for j in range(1,self.n+1):
            i = int(self[j][3][HEAD])
            h = int(self[i][3][HEAD])
            if (h < j) and (i < h):
                self[j][3][HEAD] = h
                return
            elif (h > j) and (i > h): 
                self[j][3][HEAD] = h
                return
        for j in range(1,self.n):
            for i in range(j+1,self.n+1):
                h = int(self[j][3][HEAD])
                k = int(self[i][3][HEAD])
                if h > j:
                    edge1 = [j,h] # Aa
                else:
                    edge1 = [h,j]
                if k > i:
                    edge2 = [i,k] # Bb
                else:
                    edge2 = [k,i]
                if edge1[0] < edge2[0] and edge2[0] < edge1[1] and edge1[1] < edge2[1] :
                    if h == 0 or int(self[h][3][HEAD]) == 0:   # if h is root, it cannot be lifted; instead lift edge2
                        self[i][3][HEAD] = self[k][3][HEAD]
#                        print("{} {} -- lifting word {} to depend from {}".format(edge1,edge2,i,self[i][3][HEAD]))
                    else:        # principle: lift the first, i.e. i
                        self[j][3][HEAD] = self[h][3][HEAD]
#                        print("{} {} ++ lifting word {} to depend from {}".format(edge1,edge2,j,self[j][3][HEAD]))
                    return
                if edge2[0] < edge1[0] and edge1[0] < edge2[1] and edge2[1] < edge1[1] :
                    if k == 0 or int(self[k][3][HEAD]) == 0:   # if h is root, it cannot be lifted; instead lift edge1
                        self[j][3][HEAD] = self[h][3][HEAD]
#                        print("{} {} lifting word {} to depend from {}".format(edge1,edge2,j,self[j][3][HEAD]))
                    else: # principle: lift the first, i.e. i
                        self[i][3][HEAD] = self[k][3][HEAD]
#                        print("{} {} lifting word {} to depend from {}".format(edge1,edge2,i,self[i][3][HEAD]))
                    return
                            
    def projectivise(self, opts):
        print("------")
        while not self.test_projective():
            print("---projectivize")
            if opts.verbose:
                print("nonprojective ==> projective")
            self._projectivise(opts)
            
                    
