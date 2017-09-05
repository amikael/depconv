
# This file was used to compute the statistics for individual language buckets in the dataset on
# 10 August 2017 when the FSMNLP 2017 paper was finalised.

cd  ../ud2/ud-treebanks-v2.0/
for D in [a-z][a-z]_*
do
    echo $D | perl -ne 'chop; s/^.._//; print $_'
    cat $D/*.conllu | depconv-v0.1.py --stat -t ylijyra2 
done
