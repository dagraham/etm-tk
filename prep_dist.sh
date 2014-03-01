#!/bin/bash
yes=$1
#tag=$1
home=`pwd`
# etm's version numbering now uses the `major.minor.patch` format where each of the three components is an integer:

# - Major version numbers change whenever there is something significant, a large or potentially backward-incompatible change.

# - Minor version numbers change when a new, minor feature is introduced, when a set of smaller features is rolled out or, when the change is from zero to one, when the status of the version has changed from beta to stable.

# - Patch numbers change when a new build is released. This is normally for small bugfixes or the like.

# When the major version number is incremented, both the minor version number and patch number will be reset to zero. Similarly, when the minor version number is incremented, the patch number will be reset to zero. All increments are by one.

# The patch number is incremented by one whenever this script is run to completion. Changes in the major and minor numbers require editing etmQt/v.py.

#cxfreeze3 -OO etmTk/etmtk.py --target-dir ~/etm-tk/dist

asksure() {
echo -n " (Y/N)? "

while read -r -n 1 -s answer; do
  if [[ $answer = [YyNn] ]]; then
    [[ $answer = [Yy] ]] && retval=0
    [[ $answer = [Nn] ]] && retval=1
    break
  fi
done

echo # just a final linefeed, optics...

return $retval
}

#echo Tk/Tcl version information:
#otool -L $(arch -i386 python3 -c 'import _tkinter;\
#               print(_tkinter.__file__)')
#otool -L $(arch -x86_64 python3 -c 'import _tkinter;\
#               print(_tkinter.__file__)')

logfile="prep_dist.txt"
# get the current major.minor.patch tag
vinfo=`cat etmTk/v.py | head -1 | sed 's/\"//g' | sed 's/^.*= *//g'`
now=`date`
status=`hg status`
version=`hg tip --template '{rev}'`
versioninfo=`hg tip --template '{rev}: {date|isodate}'`
echo "Started: $now" > $logfile
#echo "Current version: $vinfo ($versioninfo)" >> $logfile

echo "The current version number is $vinfo ($versioninfo)."
echo -n "Do you want to increment the patch number?"

patch=${vinfo#*.*.}
major=${vinfo%%.*.*}
mm=${vinfo#*.}
minor=${mm%.*}

if asksure; then
    newpatch=$(($patch +1))
    tag=$major.$minor.$newpatch
    change="incrementing the current version $vinfo.
Edit etmQt/v.py to change the major and minor numbers."
    hg tag $tag -f
    echo "version = \"$tag\"" > /Users/dag/etm-tk/etmTk/v.py
    echo "Updated to $tag [$versioninfo]" >> $logfile
else
    tag=$major.$minor.$patch
    change="retaining version $vinfo."
    echo "Kept $tag [$versioninfo]" >> $logfile
    # hg tag $tag -f
fi
echo "version = \"$tag [$versioninfo]\"" > etmTk/version.py
echo "$tag [$versioninfo]" > version.txt

echo $tag > etmTk/v.txt

# echo "RECENT CHANGES" > /Users/dag/etm-qt/CHANGES
echo "RECENT CHANGES" > CHANGES
hg log --template '{rev} {date|shortdate} [{tags}]\n\t{desc|fill68|tabindent}\n' -r tip:-30 >> /Users/dag/etm-qt/CHANGES
cp CHANGES ./etmTk/CHANGES

echo "Creating $tag from tip: $version - $change"
echo "Edit etmTk/v.py to change the major and minor numbers."
echo

# make sure the man file, docs and ui files are current
#$home/mk_docs.sh
# update the sample files
# cp /Users/dag/etm-qt/etm-sample/data/shared/sample_datafile.txt.orig /Users/dag/etm-qt/etm-sample/data/shared/sample_datafile.txt
echo "Updating etm-sample"
cp $home/etm-sample/data/shared/sample_datafile.txt.orig $home/etm-sample/data/shared/sample_datafile.txt
# cd /Users/dag/etm-qt/etmQt/language

#cd $home/etmTk/language
# translations
#for file in etm_*_*.ts; do
#    # make etm_xx_XX.qm file from etm_xx_XX.ts
#    echo Processing $file
#    lrelease $file
#    # # move resulting qm file to language/ for inclusion in qrc file
#    # root=${file%%.*}
#    # echo Moving $root.qm to language
#    # mv $root.qm language/
#    # cp $root.ts language/
#done

cd $home

#echo -n  "Continue?"
#if asksure; then
#    echo "### processing $tag ###"
#else
#    echo "Cancelled"
#    exit
#fi

echo "### processing $tag ###"

# cd /Users/dag/etm-qt
#cp -f one2two.py one2two.py.txt

# build
# cd /Users/dag/etm-qt
sudo rm -fR /Users/dag/etm-tk/build/*
sudo rm -fR /Users/dag/etm-tk/dist/*
echo ""
echo "Creating python sdist for $tag"
python3 -O setup.py sdist --formats=gztar,zip
echo ""

cd $home/dist
echo
echo "unpacking etmtk-${tag}.tar.gz"
tar -xzf "etmtk-${tag}.tar.gz"
echo
echo "copying etmtk-${tag} to ../etmtk-current"


# rm -fR /Users/dag/etm_qt-current/*
sudo rm -fR /Users/dag/etmtk-current/*
sudo cp -fR "etmtk-${tag}/" /Users/dag/etmtk-current

cd $home

echo
echo -n "Do system installation?"
if asksure; then
    echo
    echo "changing to etmtk-${tag} and running setup.py"
    cd "$home/dist/etmtk-${tag}"
    pwd
    echo "installing etmtk for python 2" && sudo python2 setup.py install
    pwd
    echo "installing etmtk for python 3" && sudo python3 setup.py install
    echo "Finished system install of etmtk-${tag}"
    cd $home
    echo "Doing system installation" >> $logfile
else
    echo "Skipping system wide installaton"
fi

pwd

#echo
#echo Removing etm-tk/dist/etmtk-$tag
## cd /Users/dag/etm-qt/dist && sudo rm -fdR etm_qt-${tag}
#cd $home/dist
#rm -fdR etmtk-${tag}

cd $home

# # for new pyinstaller???
# pyinstaller  --runtime-hook rthook_pyqt4.py --clean -w --noupx etm_qt

echo
echo -n "Create OSX package?"
if asksure; then
    sudo rm -fR releases/*
#    cxfreeze3 -OO etm --icon=etmTk/etmlogo.icns --target-dir releases/etmtk-${tag}-freeze-OSX
    cxfreeze3 -s -c -OO etm --icon=etmTk/etmlogo.icns --target-dir dist/etmtk-${tag}-freeze-OSX
    cd dist
    tar czf etmtk-${tag}-freeze-OSX.tar.gz etmtk-${tag}-freeze-OSX
    zip -r etmtk-${tag}-freeze-OSX.zip etmtk-${tag}-freeze-OSX
    cd $home
#    sudo rm -fR releases/etmtk-${tag}
    echo "Creating OSX package" >> $logfile
else
    echo "Skipping etm.app creation."
fi
now=`date`
echo "Finished: $now"
echo "Finished: $now" >> $logfile
