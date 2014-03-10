#!/usr/bin/env bash
# FiXME: This needs work - not ready to run
# Update the man file
cd /Users/dag/etm-tk
echo Making the man file
vinfo=`cat etmTk/v.py | head -1 | sed 's/\"//g' | sed 's/^.*= *//g'`
txt2man -t etm -s 1 -r "version $vinfo" -v "Unix user's manual" etmtk_man.text | sed '1 s/\.\"/\.\\\"/' > etm.1
# tar -cvzf etm_qt.1.gz etm_qt.1
cp etm.1 etmTk/

echo Creating ps version of man file
groff -t -e -mandoc -Tps etm.1 > etm-man.ps

echo Creating pdf version of man file
ps2pdf etm-man.ps etm-man.pdf

pandoc -s --toc --toc-depth=2 -B ~/etm-tk/etmTk/style-before -f markdown -t html -o whatsnew.html whatsnew.md

#cd /Users/dag/etm-tk/etmTk/help
#echo Creating individual html files
#pwd
#for file in OVERVIEW ITEMTYPES ATKEYS DATES PREFERENCES REPORTS SHORTCUTS; do
#    pandoc -s --toc --toc-depth=2 -B ~/etm-tk/etmTk/style-before -f markdown -t html -o $file.html $file.md
#done

echo Creating help.py
quotes='"""'
echo "" > ../help.py
for file in OVERVIEW ITEMTYPES ATKEYS DATES PREFERENCES REPORTS SHORTCUTS; do
    pandoc  -s --toc --toc-depth=2 -o $file.text -t plain --no-wrap $file.md
    echo "$file = $quotes\\" >> ../help.py
    cat $file.text >> ../help.py
    echo '"""' >> ../help.py
    echo '' >> ../help.py
done

echo Creating help.md
echo "% ETM Users Manual" > help.md
for file in OVERVIEW ITEMTYPES ATKEYS DATES PREFERENCES REPORTS SHORTCUTS; do
    echo "" >> help.md
    sed '1 s/%/##/' <$file.md >> help.md
done
echo Creating help.html
pandoc -s --toc --toc-depth=2 -B ~/etm-tk/etmTk/style-before -f markdown -t html -o help.html  help.md

echo Creating help.tex
pandoc -s --toc --toc-depth=2 -f markdown -t latex -o help.tex help.md

echo Creating help.pdf
pdflatex help.tex

#echo Creating help.text
#pandoc -s --toc --toc-depth=2 -f markdown -t plain -o help.text  help.md

# pandoc -s --toc --toc-depth=3 -f markdown -t html -o help.html  help.md overview.md data.md views.md reports.md shortcuts.md preferences.md
# pdflatex help.tex

echo Creating HEADER and README
cd ~/etm-tk/etmTk
for file in HEADER README; do
    pandoc -s --toc -B ~/etm-tk/etmTk/style-before -f markdown -t html -o $file.html $file.md
done


## TODO: fix INSTALL
#cd /Users/dag/etm-tk/etmTk
#file=INSTALL
#pandoc -s --toc -B style-before -f markdown -t html -o $file.html $file.md
#
#rm -fR *.ps
#
## TODO: fix cheatsheet
#cd /Users/dag/etm-tk
#pdflatex cheatsheet.tex

echo Cleaning up
cd ~/etm-tk
rm -fR *.ps
rm -fR *.log *.aux *.fdb_latexmk *.fls
rm -fR *.synctex.gz *.out *.toc

cd ~/etm-tk
