#!/bin/bash
echo ""
echo ""
echo "#################### Automatic tag verification et correction #####################"
echo ""


echo "The programme's output is shown in three columns:
• the first one is the original text line;
• the second one is the output code;
• the third one is either the indication of error, either the suggestion for a correction;
The possible output codes (corresponding to the situation after the possible correction):
0 : line without tags
1 : the tags are well-formed, and they respect the open/closed tag sequence;
2 : the tags are well-formed and there are as many open tags as closed ones, but the open/closed sequence is not respected;
3 : the tags are well-formed but the number of the open/closed tags is not the same; 
4 : there is at least one potentially incorrect tag which could not be corrected."

echo "##########################################################################################"
echo ""
for f in /Users/carolinecorbieres/Desktop/OCR-cat/eval_txt/doc/Cat_Paris_1969.txt
do
	python3 /Users/carolinecorbieres/Desktop/OCR-cat/eval_txt/scripts/score_corr.py $f

done
