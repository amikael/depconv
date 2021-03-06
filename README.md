# depconv version 0.1 (5 Sep 2017) 

A tool for converting between various encoding formats for dependency graphs.  
Copyright (c) 2017 - Anssi Yli-Jyrä      

The GNU License.

Disclaimers:
------------
- This is currently released just for documentation purposes; may contain bugs.
- May need more documentation; please contact the developer.
- in any serius application, this script must be run in the inverse mode to verify that the encoding is lossless and bugless

Citing:
-------

1) to cite the weak bracketing part: 

   Anssi Yli-Jyrä (2017): 
   Bounded-Depth High-Coverage Search Space for Noncrossing Parses. FSMNLP 2017. Umeå.

2) to cite the strong bracketing part:

   Anssi Yli-Jyrä and Carlos Gómez-Rodríguez (2017): 
   Generic axiomatization of families of noncrossing graphs in dependency parsing. 
   ACL 2017. Vancouver. 
   The algorithm in this paper is not exactly the same, but the encoding comes from this.

3) the tool as a whole has not be properly published yet, but you can cite parts of it
  
File formats:
-------------
1) U-CONNL
2) one sentence per line (simplified)

Encodings:
----------

Main formats:

1) U-CONNL (default) (secondary links not supported)

2) The strong dependency bracketing due to Yli-Jyrä and Gómez-Rodríguez (2017): Generic axiomatization of families of noncrossing graphs in dependency parsing. ACL 2017. Vancouver. (Embargo until 5 September 2017 when the weak dependency bracketing is published.)

3) The weak bracketing due to Yli-Jyrä (2017): Bounded-Depth High-Coverage Search Space for Noncrossing Parses. FSMNLP 2017. Umeå.
   The weak bracketing format can be used for lossy encoding of nonprojective dependency trees.
   For example   [!1 {} > [!2 {} ]!1 {} ]!2 becomes now   [! {} > [! {} ]! {} ]!
   
Additional, tentative formats:

4) K. Oflazer 2003

5) dependency length encoding (currently called after Edward Gibson although an earlier publication is probable)

6) classic (used since the early days of projective dependency grammar)
 
7) ...

The algorithms for other formats are included for review purposes and the tool itself
needs a separate publication.  

Parts:
------
- depconv.py - the main of the converter script
- LIBopts.py - user interface (commandline options etc.)
- LIBconll1.py - basic U-CONLL handling
- LIBconll2.py - conversion functions etc.
- LIBstat.py   - the methods for computing various statistics from the data
                 (this part of the tool is controlled by commenting the useless parts out)
                 
extras:
- ud_per_language.tgz - directories of symbolic links to UD-files used for computing language specific statistics in YJ 2017 
- enum.depconv.foma - a version of Anssi Yli-Jyrä and Carlos Gómez-Rodríguez (2017) with some
  playing with transduction between formats.  This file is not part of depconv but is released for documentation purposes.
  Cleaning of the script is in the to-do list.

Known bugs/caveats & Requests for help in coding:
------------------------------------------------
- currently supports only the U-CONNL primary structure with further restrictions like nonprojective trees
- the naming of the formats is unsatisfatory
- does not treat secondary links 
- lacks support (a completely new data structure class) for noncrosssing nontrees
- lossless encoding for crossing trees and graphs
- needs support for various projectivisation methods
- projectivization is heuristic while optimizing methods exist 

Acknowledgements:
-----------------
- Carlos Gómez-Rodríguez for brainstorming some requirements
- Marco Kuhlmann for a caveat notice   

