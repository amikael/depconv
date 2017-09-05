def help():
    print("""\nDependency conversions from/to CoNLL (c) 2015-2017 Anssi Yli-Jyrä
Usage:  depconv -h -l -m 10 -n -d             -t <format> < inputfile > outputfile
        depconv -h -l -m 10 -n -d -f <format>             < inputfile > outputfile
        depconv -h -l -m 10 -n -d -f <format> -t <format> < inputfile > outputfile
Arguments:
        -d           --drop                drops secundary fields
        -h           --help                prints this message
        -l           --labeled             echo labels
        -m <N>       --maxn <N>            max sentences
        -n           --nocomments          drop comments
        -t <format>  --to=<format>         output format
        -f <format>  --from=<format>       input  format
        -p <method>  --proj=<method>       projectivization
        -v           --verbose             verbose
        -s           --string              string format instead of column format
        -e           --echo                echoes the input sentence
        -x           --stat                print statistics only

<format>:                                                   MISC FIELD
        gaifman   bracketing of projections                 ((*)   *)
        gibson    directed dependency lengts                +1     +0
        oflazer   bracketing of left/right links            *d     H*
        ylijyra   bracketing of leftward/rightward edges    <      \\
        ylijyra2  weak edge bracketing                      /! <   >!
        latex     
<method>:
        lift      projectivize by lifting
unimplemented:
        unit tests        have been run only for a small number of sentences
        gaifman           does not support error recover yet
        -l with gibson    not specified/implemented yet
        sec.dependencies  are not manipulated at all
        latex             is not yet implemented
bug-like features:
        without -p        gaifman/oflazer/ylijyra fail to encode nonprojective sentences
        oflazer/ylijyra   errors are fixed heuristically and the fixing makes thus some errors
        lift              from crossing pairs of arcs, the leftmost arc is usually lifted
examples/unit tests:
        depconv.py -p lift <data.conllu >data.conllu.proj
        depconv.py -t ylijyra -l -p lift <data.conllu | depconv.py -f ylijyra -l |diff - data.conllu.proj
        depconv.py -t gibson     -p lift <data.conllu | depconv.py -f gibson     |diff - data.conllu.proj
        depconv.py -t oflazer -l -p lift <data.conllu | depconv.py -f oflazer -l |diff - data.conllu.proj
        depconv.py -t gaifman -l -p lift <data.conllu | depconv.py -f gaifman -l |diff - data.conllu.proj

        You should always run these unit tests before scientific claims.
""")

import getopt, sys

class Opts:
    def __init__(self, av):
        self.labeled  = 0
        self.drop     = 0
        self.fr       = ""
        self.to       = ""
        self.comments = 1
        self.maxn     = -1
        self.proj     = ""
        self.verbose  = 0
        self.stat     = False
        self.echo     = False
        self.string   = False
        try:
            opts, args = getopt.getopt(av,"xhnldevsm:t:f:p:",
                                       ["stat","help","labeled","nocomments","verbose","echo","drop","string","maxn=","to=","from=","proj="])
        except getopt.GetoptError as err:
            print(str(err))
            help()
            print(sys.exit(__doc__))

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                help()
                sys.exit()
            elif opt in ("-m", "--maxn"):
                self.maxn = int(float(arg))
            elif opt in ("-l", "--labeled"):
                self.labeled = 1
            elif opt in ("-d", "--drop"):
                self.drop = 1
            elif opt in ("-e", "--echo"):
                self.echo = True
            elif opt in ("-x", "--stat"):
                self.stat = True
            elif opt in ("-t", "--to"):
                self.to = arg
            elif opt in ("-f", "--from"):
                self.fr = arg
            elif opt in ("-n", "--nocomments"):
                self.comments = 0
            elif opt in ("-p", "--proj"):
                self.proj = arg
            elif opt in ("-s", "--string"):
                self.string = True
            elif opt in ("-v", "--verbose"):
                self.verbose = 1

        if self.fr == "" and self.to == "" and self.proj == "":
            help()
            sys.exit()

        if self.fr == "":
            self.fr = "conll"
        if self.to == "":
            self.to = "conll"

        if self.fr not in ["gaifman","oflazer","gibson","ylijyra","ylijyra2","conll"]:
            print("unknown input format:  ", self.fr, file=sys.stderr)
            sys.exit()

        if self.to not in ["gaifman","oflazer","gibson","ylijyra","ylijyra2","conll","latex"]:
            print("unknown output format:  ", self.to, file=sys.stderr)
            sys.exit()
