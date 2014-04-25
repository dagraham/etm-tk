#!/usr/bin/env bash
# FiXME: This needs work - not ready to run
# Update the man file
cd /Users/dag/etm-tk

echo "Processing what's new"
pandoc -s -B ~/etm-tk/style-before -f markdown -t html -o WhatsNew.html whatsnew.md

pandoc -s -f markdown -t plain -o WhatsNew.txt whatsnew.md

echo Making the man file
vinfo=`cat etmTk/v.py | head -1 | sed 's/\"//g' | sed 's/^.*= *//g'`
txt2man -t etm -s 1 -r "version $vinfo" -v "Unix user's manual" etmtk_man.text | sed '1 s/\.\"/\.\\\"/' > etm.1
# tar -cvzf etm_qt.1.gz etm_qt.1
cp etm.1 etmTk/

echo Creating ps version of man file
groff -t -e -mandoc -Tps etm.1 > etm-man.ps

echo Creating pdf version of man file
ps2pdf etm-man.ps etm-man.pdf

#cd /Users/dag/etm-tk/etmTk/help
#echo Creating individual html files
#pwd
#for file in OVERVIEW ITEMTYPES ATKEYS DATES PREFERENCES REPORTS SHORTCUTS; do
#    pandoc -s --toc --toc-depth=2 -B ~/etm-tk/etmTk/style-before -f markdown -t html -o $file.html $file.md
#done

cd etmTk/help
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

echo Creating UserManual.md
echo "% ETM Users Manual" > UserManual.md
for file in OVERVIEW ITEMTYPES ATKEYS DATES PREFERENCES REPORTS SHORTCUTS; do
    echo "" >> UserManual.md
    sed '1 s/%/##/' <$file.md >> UserManual.md
done
echo Creating UserManual.html
pandoc -s --toc --toc-depth=2 -B ~/etm-tk/etmTk/style-before -f markdown -t html -o UserManual.html  UserManual.md

echo Creating UserManual.tex
pandoc -s --toc --toc-depth=2 -f markdown -t latex -o UserManual.tex UserManual.md

echo Creating UserManual.pdf
pdflatex UserManual.tex

#echo Creating help.text
#pandoc -s --toc --toc-depth=2 -f markdown -t plain -o help.text  help.md

# pandoc -s --toc --toc-depth=3 -f markdown -t html -o help.html  help.md overview.md data.md views.md reports.md shortcuts.md preferences.md
# pdflatex help.tex

cd ~/etm-tk
echo Creating HEADER and README
for file in HEADER README; do
    pandoc -s --toc -B ~/etm-tk/style-before -f markdown -t html -o $file.html $file.md
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
