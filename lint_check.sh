#!/bin/sh
ls etmTk/*.py
if [ "$1" = "" ]; then
    echo no pattern
    pat="*.py"
else
    echo pattern $1
    pat="$1*.py"
fi
echo matching $pat
echo
#echo pep8 etm
#pep8 etm
#echo
#echo pyflakes etm
#pyflakes etm
#echo
for file in etmTk/$pat; do
    echo pep8 $file
    pep8 $file
    echo
    echo pyflakes $file
    pyflakes $file
    echo
done

