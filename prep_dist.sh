#!/bin/bash
yes=$1
#tag=$1
home=`pwd`
plat=`uname`
#echo "home: $home; plat: $plat"
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
#vinfo=`cat etmTk/v.py | head -1 | sed 's/\"//g' | sed 's/^.*= *//g'`
vinfo=`cat etmTk/v.py | head -1 | sed 's/\"//g' | sed 's/^.*= *//g' | sed 's/-.*$//g'`
patch=${vinfo#*.*.}
major=${vinfo%%.*.*}
mm=${vinfo#*.}
minor=${mm%.*}
if [ "$patch" == "x" ]; then
    patch=-1
fi
vinfo=$major.$minor.$patch
now=`date`
#status=`hg status`
status=`git status -s`
#version=`hg tip --template '{rev}'`
#versioninfo=`hg tip --template '{rev}: {date|isodate}'`
versioninfo=`git log --pretty=format:"%ai" -n 1`
echo "Started: $now" >> $logfile
#echo "Current version: $vinfo ($versioninfo)" >> $logfile

#otag=`git describe --tags --long | sed 's/-[^-]*$//g'`
otag=`git describe  | sed 's/-[^-]*$//g'`


echo "The current version number is $vinfo ($otag $versioninfo)."
echo -n "Do you want to increment the patch number?"

if asksure; then
    newpatch=$(($patch +1))
    tag=$major.$minor.$newpatch
    change="incrementing the current version $vinfo.
Edit etmTk/v.py to change the major and minor numbers."
#    hg tag $tag -f
#    git tag -a $tag -m "$versioninfo" HEAD
    echo "Updated to $tag [$versioninfo]" >> $logfile
    echo "version = \"$tag\"" > /Users/dag/etm-tk/etmTk/v.py
    echo "version = \"$tag [$versioninfo]\"" > etmTk/version.py
    echo "$tag [$versioninfo]" > version.txt
    git add etmTk/v.py etmTk/version.py
    git commit -a -m "tagged version $tag"
    git tag -a -f $tag -m "$versioninfo" HEAD
else
    # drop the abbrev header and a trailing -0, if there is one
#    tag=`git describe --tags --long | sed 's/-[^\-]*$//g' | sed 's/-0$//g'`  # something like 0.0.65-2
    tag=$otag
    change="retaining version $vinfo."
    echo "Using $tag [$versioninfo]" >> $logfile
    echo "version = \"$tag\"" > /Users/dag/etm-tk/etmTk/v.py
    echo "version = \"$tag [$versioninfo]\"" > etmTk/version.py
    echo "$tag [$versioninfo]" > version.txt
#    git add etmTk/v.py etmTk/version.py
#    git commit -a -m "tagged version $tag"
    git tag -f $tag HEAD
fi

echo $tag > etmTk/v.txt

#./mk_docs.sh
weeks=2
echo "# Changes in the $weeks weeks preceding $now:" > CHANGES.txt
     #Changes in the 4 weeks :
#hg log --template '{rev} {date|shortdate} [{tags}]\n\t{desc|fill68|tabindent}\n' -r tip:-30 >> "$home/CHANGES"
#git log --pretty=format:"%ai: %an%n%w(70,4,8)%s" -n 30 >> "$home/CHANGES.txt"
git log --pretty=format:'- %ai%d: %an%n%w(70,3,3)%s' --since="$weeks weeks ago" >> "$home/CHANGES.txt"
# TODO: remove this eventually
echo "" >> $home/CHANGES.txt
#echo "### mercurial logs ###" >> $home/CHANGES.txt
#hg log --template '{rev} {date|shortdate} [{tags}]\n\t{desc|fill68|tabindent}\n' -r tip:-30 >> "$home/CHANGES.txt"
cp CHANGES.txt CHANGES

echo "Creating $tag from tip: $version - $change"
echo "Edit etmTk/v.py to change the major and minor numbers."
echo

# make sure the man file, docs and ui files are current
#"$home"/mk_docs.sh
# update the sample files
# cp /Users/dag/etm-qt/etm-sample/data/shared/sample_datafile.txt.orig /Users/dag/etm-qt/etm-sample/data/shared/sample_datafile.txt
#echo "Updating etm-sample"
#cp "/Users/dag/etm-sample/data/shared/sample_datafile.txt.orig" "$home/etm-sample/data/shared/sample_datafile.txt"

cd "$home/etmTk"
pwd
# TODO: fix gettext stuff
#xgettext --omit-header --language=Python --keyword=_ --output=po/etm.pot --from-code=UTF-8 `find . -name "*.py"`
#xgettext --language=Python --keyword=_ --output=po/etm.pot --from-code=UTF-8 --copyright-holder="Daniel A Graham" --copyright-year="2009-2014"  --package-name="etm" --package-version="$vinfo" `find . -name "*.py"`

cd "$home"
pwd

echo "### processing $tag ###"

echo "Cleaning up build/ and dist/"
sudo rm -fR build/*
sudo rm -fR dist/*

ls build
ls dist

echo "Creating python sdist for $tag"
if [ "$plat" = 'Darwin' ]; then
    python3 -O setup.py sdist --formats=gztar,zip
else
    python -O setup.py sdist --formats=gztar,zip
fi

echo "Finished making sdist for $tag"

cd "$home/dist"
echo
echo "unpacking etmtk-${tag}.tar.gz"
tar -xzf "etmtk-${tag}.tar.gz"
echo
#echo "copying etmtk-${tag} to ../etmtk-current"


# rm -fR /Users/dag/etm_qt-current/*
#sudo rm -fR /Users/dag/etmtk-current/*
#sudo cp -fR "etmtk-${tag}/" /Users/dag/etmtk-current
#echo "home: "$home""
cd "$home"

echo
echo -n "Do system installation?"
if asksure; then
    echo "Building for $plat"
    echo
    echo "changing to etmtk-${tag} and running setup.py"
    cd "$home/dist/etmtk-${tag}"
    pwd
    if [ "$plat" = 'Darwin' ]; then
        echo
        echo "Installing etmtk for python 2" && sudo python2 setup.py install
        echo
        echo "Installing etmtk for python 3.3" && sudo python3.3 setup.py install
        echo
        echo "Installing etmtk for python 3.4" && sudo python3.4 setup.py install
        echo "Doing system installation" >> $logfile
    else
        echo "installing etmtk for python 2" && sudo python setup.py install
    fi
    echo "Finished system install of etmtk-${tag}"
    cd "$home"
else
    echo "Skipping system wide installaton"
fi

pwd

#echo
#echo Removing etm-tk/dist/etmtk-$tag
## cd /Users/dag/etm-qt/dist && sudo rm -fdR etm_qt-${tag}
#cd "$home"/dist
#rm -fdR etmtk-${tag}

cd "$home"

# # for new pyinstaller???
# pyinstaller  --runtime-hook rthook_pyqt4.py --clean -w --noupx etm_qt

echo
echo -n "Create $plat package?"
if asksure; then
    echo "Building for $plat"
    echo
    sudo rm -fR dist-$plat/*
    if [ "$plat" = 'Darwin' ]; then
        cxfreeze3 -s -c -OO etm --icon=etmTk/etmlogo.icns --target-dir dist-$plat/etmtk-${tag}-freeze-$plat
    else
        cxfreeze -OO etm --target-dir dist-$plat/etmtk-${tag}-freeze-$plat
    fi
    cd dist-$plat
    tar czf etmtk-${tag}-freeze-$plat.tar.gz etmtk-${tag}-freeze-$plat
#    zip -r etmtk-${tag}-freeze-UBUNTU.zip etmtk-${tag}-freeze-UBUNTU
    cd "$home"
    echo "Creating package" >> $logfile
else
    echo "Skipping etm.app creation."
fi
now=`date`
echo "Finished: $now"
echo "Finished: $now" >> $logfile
