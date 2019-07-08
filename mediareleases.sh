#!/bin/bash

while IFS= read -r line; do
	if [[ $(echo "$line" | sed -e "s/ .*//g") == *"html" ]]
	then 
		wkhtmltopdf https://www.sfu.ca/"$line" $(echo "$line" | sed -Ee "s/\/university-communications\/media-releases\///g" | sed -e "s/\//-/g" | sed -e "s/\.html//g").pdf
	else
		# fix letter scaling
		magick "$(echo "$line" | sed -e "s/ # .*//g")" -units pixelsperinch -density 72 -page letter "$(echo "$line" | sed -Ee "s/\.[A-Za-z]+ # .*/.pdf/g")"
		pdftk $(echo "$line" | sed -e "s/.* # //g" | sed -Ee "s/\/university-communications\/media-releases\///g" | sed -e "s/\//-/g" | sed -e "s/\.html//g").pdf "$(echo "$line" | sed -Ee "s/\.[A-Za-z]+ # .*/.pdf/g")" cat output new.pdf
		mv new.pdf $(echo "$line" | sed -e "s/.* # //g" | sed -Ee "s/\/university-communications\/media-releases\///g" | sed -e "s/\//-/g" | sed -e "s/\.html//g").pdf
	fi
done <releases.txt