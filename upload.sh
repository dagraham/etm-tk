#!/usr/bin/env bash

# etm tk
# This version of etm will be kept in '~/dgraham/public_html/etmtk'


if [ -z "$1" ]; then
    echo "usage: upload.sh [-b|D|L|W|d|e|i|l|p|s]"
    echo "    where b: base files; D: Darwin freeze file; L: Linux freeze file;"
    echo "          d: documentation; e: examples; i: images; l: language files; "
    echo "          m: movies; p: PyPI; s: sound files "
else
    copy=0
    # version=`cat v.txt`
#    version=`cat etmTk/v.py | head -1 | sed 's/\"//g' | sed 's/^.*= *//g'`
    version=`cat etmTk/v.py | head -1 | sed 's/\"//g' | sed 's/^.*= *//g' | sed 's/-.*$//g'`

    echo $version
    if [ -d ~/.TEMP ]
    then
        rm -Rf ~/.TEMP
    fi
    mkdir ~/.TEMP
    mkdir ~/.TEMP/images
    mkdir ~/.TEMP/help

    while getopts "DLWbdeilps" Option
    do
      case $Option in
        D)
        echo "### copying etmtk-$version-freeze-Darwin.tar.gz ###"
        cp -p dist-Darwin/etmtk-$version-freeze-Darwin.tar.gz ~/.TEMP/
        copy=1
        ;;
        L)
        echo "### copying etmtk-$version-freeze-Linux.tar.gz ###"
        cp -p dist-Linux/etmtk-$version-freeze-Linux.tar.gz ~/.TEMP/
        copy=1
        ;;
        W)
        echo "### copying etmtk-$version-freeze-Windows.tar.gz ###"
        cp -p dist-Windows/etmtk-$version-freeze-Windows.tar.gz ~/.TEMP/
        copy=1
        ;;
        b)
        echo "### copying version $version base files ###"
        cp -p version.txt ~/.TEMP/version.txt
        cp -p CHANGES dist/etmtk-$version.tar.gz dist/etm_tk-$version.zip  ~/.TEMP/
        copy=1
        ;;
        d)
        echo "### copying html and pdf documentation files ###"
        for file in INDEX OVERVIEW ITEMTYPES ATKEYS DATES PREFERENCES REPORTS SHORTCUTS; do
            cp -p etm-tk.wiki/help/$file.html ~/.TEMP/help
         done
        cp -p etm-tk.wiki/help/UserManual.pdf ~/.TEMP
        cp -p etm-tk.wiki/help/UserManual.html ~/.TEMP

        # careful that the following doesn't overwrite modified files
        cp -p HEADER.html README.html ~/.TEMP
        cp -p cheatsheet.pdf ~/.TEMP
        copy=1
        ;;
#        e)
#        echo "### copying examples ###"
#        cp -p etm-sample/data/shared/sample_datafile.txt ~/.TEMP/sample
#        cp -p etm-sample/reports.cfg ~/.TEMP/sample
#        cp -p etm-sample/locale.cfg ~/.TEMP/sample
#        cp -p COMPLETIONS ~/.TEMP/sample/
#        cp -p TIMEZONES ~/.TEMP/sample/
#        copy=1
#        ;;
        i)
        echo "### copying images ###"
        cp -p images/*.gif ~/.TEMP/images
        copy=1
        ;;
#        l)
#        echo "### copying language files ###"
#        cp -p etmTk/etm_*.ts ~/.TEMP/language/
#        copy=1
#        ;;
#        m)
#        echo "### copying movies ###"
#        cp -p movies/*.mov ~/.TEMP/
#        # cp -p ~/Movies/Horizon-Feynman.mov ~/.TEMP/
#        copy=1
#        ;;
#        # not yet ready
        p)
        # echo "etm version $version"
        echo "### uploading version $version to pypi ###"
        # python setup.py register sdist upload
        echo "### using python3 and -0 switch"
        # python3 -O setup.py register sdist upload
        python3 -O setup.py register sdist upload
        /usr/bin/afplay -v 2 ~/.etm/sounds/etm_ding.m4a
        ;;
#        s)
#        echo "### copying sound files ###"
#        cp -p etmTk/sounds/*.m4a ~/.TEMP/sounds/
#        cp -p etmTk/sounds/*.wav ~/.TEMP/sounds/
#        copy=1
#        ;;
      esac
    done
    if [ "$copy" = "1" ]
    then
        echo "about to copy the following"
        ls -R ~/.TEMP
        rsync -ptrhv --progress  ~/.TEMP/* \
        dgraham@login.oit.duke.edu://winhomes/dgraham/public_html/etmTk
        echo "### Remember to remove redundant files at www.duke.edu ###"
        /usr/bin/afplay -v 2 ~/.etm/sounds/etm_ding.m4a
    fi
fi
