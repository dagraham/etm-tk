#!/usr/bin/env bash
# On linux systems, use wmctrl to set the properties of the etm GUI

usage='Usage:

    etmctrl.sh [-v] -(a|c|R|<argument>)

where

  -v    Be verbose. Useful for debugging.

  -a    Activate the etm window by switching to its desktop and raising it.
  -c    Close the etm window gracefully.
  -R    Move the etm window to the current desktop and activate it.

and the format for <argument> is:

   (remove|add|toggle),<PROP1>[,<PROP2>]

and PROP1, PROP2, ... come from:

   modal, sticky, maximized_vert, maximized_horz, shaded, skip_taskbar,
   skip_pager, hidden, fullscreen, above, below

E.g.,

    etmctrl.sh toggle,above

would toggle the "above" state of the etm window.'

if [ -z "$1" ] || [ "$1" = "?" ]; then
    echo "$usage"
    exit 1
fi

# get the id for the etmTk window - thanks Mel
id=`wmctrl -l -x | grep "^[^ ]*  *[^ ]*  *[^ ]*etmTk" | sed 's/ .*//g'`

if [ -z "$id" ]; then
    echo "etm does not appear to be running"
    exit 1
fi

verbose=""
if [ "$1" = "-v" ]; then
    verbose="-v"
    shift
fi


if [ -z "$1" ]; then
    echo "$usage"
    exit 1
fi

arg=$1
# arg should be -a, -c, -R or <argument>
if [ $arg = "-a" ] || [ $arg = "-c" ] || [ $arg = "-R" ]; then
    wmctrl $verbose -i $arg $id
else
    wmctrl $verbose -i -r $id -b $arg
fi
