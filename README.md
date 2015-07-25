## Screen shots ##

### Idle timer in 3.1.43+

<table align="center" hspace="10" vspace="10" width="100%">
<tr>
    <td>
    <center><img src="images/timer_running.gif" /></a></center>
    </td>
    <td>
    <center><img src="images/timer_paused.gif"/></a></center>
    </td>
</tr>
</table>

### Custom colors in 3.1.35+

<table align="center" hspace="10" vspace="10" width="100%">
<tr>
    <td>
    <center><img src="images/dark_agenda.gif" /></a></center>
    </td>
    <td>
    <center><img src="images/dark_week.gif"/></a></center>
    </td>
</tr>
</table>

### Internationalization in 3.1.20+

<table align="center" hspace="10" vspace="10" width="100%">
<tr>
    <td>
    <center><img src="images/international.gif" /></a></center>
    </td>
</tr>
<tr>
    <td>
    <center><img src="images/poedit.gif"/></a></center>
    </td>
</tr>
</table>

### New in 3.1.x

<table align="center" hspace="10" vspace="10" width="100%">
<tr>
    <td>
    <center><img src="images/new_agenda.gif" /></a></center>
    </td>
    <td>
    <center><img src="images/new_week.gif"/></a></center>
    </td>
</tr>
<tr>
    <td>
    <center><img src="images/new_month.gif"/></a></center>
    </td>
    <td>
    <center><img src="images/new_custom.gif"/></a></center>
    </td>
</tr>
</table>

### Original

<table align="center" hspace="10" vspace="10" width="100%">
<tr>
    <td>
    <center><img src="images/agenda.gif" /></a></center>
    </td>
    <td>
    <center><img src="images/day.gif"/></a></center>
    </td>
</tr>
<tr>
    <td>
    <center><img src="images/week.gif"/></a></center>
    </td>
    <td>
    <center><img src="images/monthly.gif"/></a></center>
    </td>
</tr>
<tr>
    <td>
    <center><img src="images/finishitem.gif"/></a></center>
    </td>
    <td>
    <center><img src="images/completion.gif"/></a></center>
    </td>
</tr>
<tr>
    <td>
    <center><img src="images/openfile.gif"/></a></center>
    </td>
    <td>
    <center><img src="images/newfile.gif"/></a></center>
    </td>
</tr>
<tr>
    <td>
    <center><img src="images/date_calculator_entry.gif"/></a></center>
    </td>
    <td>
    <center><img src="images/date_calculator_result.gif"/></a></center>
    </td>
</tr>
<tr>
    <td>
    <center><img src="images/availabledates1.gif"/></a></center>
    </td>
    <td>
    <center><img src="images/availabledates2.gif"/></a></center>
    </td>
</tr>
<tr>
    <td>
    <center><img src="images/custom0.gif"/></a></center>
    </td>
    <td>
    <center><img src="images/custom3.gif"/></a></center
    </td>
</tr>
<tr>
    <td colspan=2>
    <center><img src="images/customCSV.gif"/></a></center>
    </td>
</tr>
</table>

<hr/>

## Sample entries ##

Items in *etm* begin with a type character such as an asterisk (event) and continue on one or more lines either until the end of the file is reached or another line is found that begins with a type character. The beginning type character for each item is followed by the item summary and then, perhaps, by one or more `@key value` pairs. The order in which such pairs are entered does not matter.

* A sales meeting (an event) [s]tarting seven days from today at 9:00am and [e]xtending for one hour with a default [a]lert 5 minutes before the start:

        * sales meeting @s +7 9a @e 1h @a 5

* The sales meeting with another [a]lert 2 days before the meeting to (e)mail a reminder to a list of recipients:

        * sales meeting @s +7 9a @e 1h @a 5
          @a 2d: e; who@when.com, what@where.org

* Prepare a report (a task) for the sales meeting [b]eginning 3 days early:

        - prepare report @s +7 @b 3

* A period [e]xtending 35 minutes (an action) spent working on the report yesterday:

        ~ report preparation @s -1 @e 35

* Get a haircut (a task) on the 24th of the current month and then [r]epeatedly at (d)aily [i]ntervals of (14) days and, [o]n completion,  (r)estart from the completion date:

        - get haircut @s 24 @r d &i 14 @o r

* Payday (an occasion) on the last week day of each month. The `&s -1` part of the entry extracts the last date which is both a weekday and falls within the last three days of the month):

        ^ payday @s 1/1 @r m &w MO, TU, WE, TH, FR &m -1, -2, -3 &s -1

* Take a prescribed medication daily (a reminder) [s]tarting today and [r]epeating (d)aily at [h]ours 10am, 2pm, 6pm and 10pm [u]ntil (12am on) the fourth day from today. Trigger the default [a]lert zero minutes before each reminder:

        * take Rx @s +0 @r d &h 10, 14, 18, 22 &u +4 @a 0

* Move the water sprinkler (a reminder) every thirty mi[n]utes on Sunday afternoons using the default alert zero minutes before each reminder:

        * Move sprinkler @s 1 @r w &w SU &h 14, 15, 16, 17 &n 0, 30 @a 0

    To limit the sprinkler movement reminders to the [M]onths of April through September each year change the @r entry to this:

        @r w &w SU &h 14, 15, 16, 17 &n 0, 30 &M 4, 5, 6, 7, 8, 9

     or this:

        @r n &i 30 &w SU &h 14, 15, 16, 17 &M 4, 5, 6, 7, 8, 9

* Presidential election day (an occasion) every four years on the first Tuesday after a Monday in November:

        ^ Presidential Election Day @s 2012-11-06
          @r y &i 4 &M 11 &m 2, 3, 4, 5, 6, 7, 8 &w TU

* Join the etm discussion group (a task) [s]tarting on the first day of the next month. Because of the @g (goto) link, pressing Ctrl-G when the details of this item are displayed in the gui would open the link using the system default application which, in this case, would be your default browser:

        - join the etm discussion group @s +1/1
          @g http://groups.google.com/group/eventandtaskmanager/topics

## Installation ##

### Source installation under OS X, Linux or Windows

Python 2.7.x or python >= 3.3.0 is required.

The following python packages are required for etm but are not included in the python standard library:

-   dateutil (1.5 is OK but >= 2.1 is strongly recommended)
-   PyYaml (>= 3.10)
-   icalendar (>=3.5 for python 2, >= 3.6 for python 3)

Tk and the python module tkinter are also required but are typically already installed on most modern operating systems. If needed, installation instructions are given at www.tkdocs.com/tutorial/install.html.

### Installing etm

Download 'etmtk-x.x.x.tar.gz' from this site, unpack the tarball, cd to the resulting directory and do the normal

    sudo python setup.py install

for a system installation. You can then run from any directory either

    $ etm ?

for information about command line usage or

    $ etm

to open the etm gui.

Alternatively, you can avoid doing a system installation and simply run either

    $ python etm ?

or

    $ python etm

or

    $ ./etm

from this directory.

### Installing Git or Mercurial

*Having one of these version control systems is optional but strongly recommended!*

With either progam installed, etm will automatically commit any change made to any data file. You can see the history of your changes either to a specific file or to any file from the GUI and, of course, you have the entire range of possibilities for showing changes, restoring previous versions and so forth from the command line.

#### Git

Download Git from

    http://git-scm.com/downloads

Install git and then in a terminal enter your personal information

    $ git config --global user.name "John Doe"
    $ git config --global user.email johndoe@example.com

the editor you would like to use

    $ git config --global core.editor vim

and the diff program

    $ git config --global merge.tool vimdiff

Usage information can be obtained in several ways from the terminal

    $ git help <verb>
    $ git <verb> --help
    $ man git-<verb>

Finally, *Pro Git* by Scott Chacon is available to read or download at:

    http://git-scm.com/book/en

If you have been using Mercurial and would like to give Git a try, you can import your etm Mercurial records into Git as follows:

    $ cd
    $ git clone git://repo.or.cz/fast-export.git
    $ git init new_temp_repo
    $ cd new_temp_repo
    $ ~/fast-export/hg-fast-export.sh -r /path/to/etm/datadir
    $ git checkout HEAD

If an "unnamed head" error is reported, try adding `--force` to the end of the fast-export line.

At this point, you should have a copy of your etm datadir in `new_temp_repo` along with a directory, `.git`, that you can copy to the root of your etm datadir where it will join its Mercurial counterpart, `.hg`. You can then delete `new_temp_repo`.

You can now open `etmtk.cfg` for editing and change the setting for `vcs_system` to

    vcs_system: git

#### Mercurial

Download Mercurial from

    http://mercurial.selenic.com/

install it and then create the file *~/.hgrc*, if it doesn't already exist, with at least the following two lines:

    [ui]
    username = Your Name <your email address>


### New etm users

By default, etm will use the directory

    ~/.etm

The first time you run etm it will create, if necessary, the following:

    ~/.etm/
    ~/.etm/etmtk.cfg
    ~/.etm/etmtk_log.txt
    ~/.etm/data/


If the data directory needs to be created, then the following structure will be added:

    ~/.etm/data/
        personal/
            monthly/
        sample/
            completions.cfg
            reports.cfg
            sample.txt
            users.cfg
        shared/
            holidays.txt


The files `sample.txt` and `holidays.txt` contain illustrative data entries and the `*.cfg` files contain illustrative configuration entries.

The following entry will also be inserted in `etmtk.cfg`:

        calendars:
        - - personal
          - true
          - personal
        - - sample
          - true
          - sample
        - - shared
          - true
          - shared

to illustrate the use of calendars.

### Previous etm users

The first time you run etm, it will copy your current configuration settings from `~/.etm/etm.cfg` to `~/.etm/etmtk.cfg`. You can make any changes you like to the latter file without affecting the former.

You can switch back and forth between etm_qt and etm. Any changes made to your data files by either one will be compatible with the other one.


## Feedback ##

Please share your ideas in the discussion group at [GoogleGroups][].

[GoogleGroups]: http://groups.google.com/group/eventandtaskmanager

## Version numbers ##

*etm*'s version numbering uses the `major.minor.patch` format where each of the three components is an integer:

- Major version numbers change whenever there is a large or potentially backward-incompatible change.

- Minor version numbers change when a new, minor feature or a set of smaller features is introduced or when a status change has occured.

- Patch numbers change for new builds involving small bugfixes or the like. Some new builds may not be released.

When the major version number is incremented, both the minor version number and patch number are reset to zero. Similarly, when the minor version number is incremented, the patch number is reset to zero. All increments are by one.

## License ##

Copyright (c) 2009-2015 [Daniel Graham]. All rights reserved.

[Daniel Graham]: mailto://daniel.graham@duke.edu

This program is free software; you can redistribute it and/or modify it under the terms of the [GNU General Public License] as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.

[GNU General Public License]: http://www.gnu.org/licenses/gpl.html

