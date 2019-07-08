#!/bin/bash

mkdir titles
mkdir releases
mkdir postscript
mkdir pdfs

for x in $(ls)
do
	if [ -f $x ]
	then
		python3 /mnt/c/Users/axfel/Dropbox/Documents/SFU/archives/mediareleases-old.py $x
	fi
done

for x in $(ls releases); do title=$(cat titles/$x); enscript --header="$title" --word-wrap releases/"$x" -p $(echo postscript/$(echo $x | sed 's/\.txt/.ps/g')); done

for x in $(ls postscript); do ps2pdf postscript/"$x" $(echo pdfs/$(echo $x | sed 's/\.ps/\.pdf/g')); done