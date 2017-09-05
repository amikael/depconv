
# this script was used to compute the statistics of the union of all languages in the dataset
# on 10 August 2017 when the FSMNLP 2017 paper was finalized.

cd  ../ud2/ud-treebanks-v2.0/
cat [a-z][a-z]_*/*.conllu | depconv-v0.1.py --stat -t ylijyra2 
