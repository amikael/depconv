#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

from LIBopts   import *
from LIBconll2 import *
from LIBstat   import *
import sys;

def main(argv):
    stat = Stat()
    opts = Opts(argv)
    s    = 0
    while opts.maxn < 0 or s < opts.maxn:

        # initialize
        sentence = CoNLL()

        # read
        try:
            sentence.read_conll(opts)
        except EOFError:
            if opts.verbose:
                print("(end of file)", file=sys.stderr)
            break
        except BrokenPipeError:
            sys.stdout.close()
            if opts.verbose:
                print("(input pipe broken; last sentence has been chopped)", file=sys.stderr)
            sys.stderr.close()
            exit(1)

        if opts.echo:
            try:
                sentence.print_conll(opts)
            except BrokenPipeError:
                sys.stdout.close()
                if opts.verbose:
                    print("(output pipe broken)", file=sys.stderr)
                sys.stderr.close()
                exit(1)

        if opts.verbose:
            print('converting  {} ===>  {}'.format(opts.fr,opts.to))

        # convert
        sentence.convert_from(opts)
        if opts.proj != "":
            if opts.verbose:
                print("projectivizing if necessary")
            sentence.projectivise(opts)

        sentence.convert_to(opts)

        if opts.echo:
            try:
                sentence.print_conll(opts)
            except BrokenPipeError:
                sys.stdout.close()
                if opts.verbose:
                    print("(output pipe broken)", file=sys.stderr)
                sys.stderr.close()
                exit(1)

        try:
            if opts.stat == True:
                if opts.to == "ylijyra":
                    stat.add(sentence.code_depth(0),len(sentence)-1)
                elif opts.to == "ylijyra2":
                    stat.add(sentence.code_depth(1),len(sentence)-1)
                else:
                    stat.add(0,len(self)-1)
            elif opts.string == True:
                if opts.to == "ylijyra":
                    if sentence.code_depth(0) >= 0:
                        print("sent",sentence.code_depth(0),len(sentence)-1,sentence.yj_code(0))
                elif opts.to == "ylijyra2":
                    if sentence.code_depth(1) >= 0:
                        print("sent",sentence.code_depth(1),len(sentence)-1,sentence.yj_code(1))
                else:
                    print("string format of this encoding has not been implemented yet")
            else:
                sentence.print_conll(opts)
                
        except BrokenPipeError:
            if opts.verbose:
                sys.stdout.close()
            print("(output pipe broken)", file=sys.stderr)
            sys.stderr.close()
            exit(1)

        s = s + 1

    if opts.stat == True:
        stat.flush()
    sys.stdout.close()
    sys.stderr.close()
    
main(sys.argv[1:])

