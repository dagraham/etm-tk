# New: An alternative GUI for etm based on Tk

A new version of etm based on Tk instead of Qt is in the early stages of development. Screenshots and files can be found at [etmtk][].


This version has not been released. I'm providing this information here in the hopes that members of this group will give me some feedback. Are there aspects of the new interface that you prefer? Do you have suggestions for improvements? As always, your feedback is greatly appreciated.

[etmtk]: http://people.duke.edu/~dgraham/etmtk

## Unchanged

- Data files and their format are unchanged.

- The name of the configuration file has changed from etm.cfg to etmtk.cfg but is otherwise unchanged - you can just copy etm.cfg to etmtk.cfg to use your current settings.

- The configuration files completions.cfg and reports.cfg are unchanged.

- actions, timers and reports are unchanged.

- Both python 2.7x and >= 3.3 are supported.

## Changed

### Setup

- The only requirement for the GUI is tkinter and Tcl/Tk which are often already available and, if not, easily installed. *Sip, Qt and PyQt are not used.*

- Completely self contained packages made using cx_freeze are available on the web site for both Darwin (OSX) and Linux (Ubuntu). A package for Windows may be available soon.

- File sizes are smaller:

    - source tarball: Tk 260k vs. Qt 20.5mb

    - Darwin: Tk 8.5mb freeze tarball vs. Qt 23mb app dmg

    - Linux: Tk 3.7mb freeze tarball vs. Qt NA

### CLI

Usage:

    etm_qt [logging level] [path] [?] [acmsv]

With no arguments, etm will set logging level 3 (warn), use settings from
the configuration file ~/.etm/etmtk.cfg, and open the GUI.

If the first argument is an integer not less than 1 (debug) and not greater
than 5 (critical), then set that logging level and remove the argument.

If the first (remaining) argument is the path to a directory that contains
a file named etmtk.cfg, then use that configuration file and remove the
argument.

If the first (remaining) argument is one of the commands listed below, then
execute the remaining arguments without opening the GUI.

    a ARG   display the agenda view using ARG, if given, as a filter.
    k ARG   display the keywords view using ARG, if given, as a filter.
    n ARGS  Create a new item using the remaining arguments as the item
            specification. (Enclose ARGS in quotes to avoid shell
            expansion.)
    m INT   display a report using the remaining argument, which must be a
            positive integer, to display a report using the corresponding
            entry from the file given by report_specifications in etmtk.cfg.
            Use ? m to display the numbered list of entries from this file.
    p ARG   display the path view using ARG, if given, as a filter.
    r ARGS  display a report using the remaining arguments as the report
            specification. (Enclose ARGS in quotes to avoid shell
            expansion.)
    s ARG   display the schedule view using ARG, if given, as a filter.
    t ARG   display the tags view using ARG, if given, as a filter.
    v       display information about etm and the operating system.
    ? ARG   display (this) command line help information if ARGS = '' or,
            if ARGS = X where X is one of the above commands, then display
            details about command X. 'X ?' is equivalent to '? X'.

### GUI

- The main window is simpler. The tool bar and icons have been replaced by a menubar where all the operational commands are listed in English. (Support for other languages can be added.) See "Commands and Shortcuts" below for a listing.

- The display area of the main window is split into two panes. The top pane shows the selected view as a tree and, if an item is selected, the bottom pane shows the details of the selected item. Items can be selected and branches can be opened and closed using either the mouse or cursor keys.

- Items are displayed in the top pane using their type characters instead of icons.

- Double clicking on an item or pressing return or Ctrl-E with an item selected opens it for editing. Other actions are available for the selected item - see "Item" under "Commands and Shortcuts" for a list.

- When editing a repeating item in etmqt an option is presented to select  "this instance", "this and subsequent instances" and so forth. In etmtk the option to change "only the datetime of this instance" is split out and offered as a new "Reschedule" command where it can be also applied to non-repeating and undated items.

### Views

**Agenda view** is new and the default view. It represents a sort of executive summary - what you need to know *now* beginning with your schedule for the next few days and followed by items in these groups:

- **In basket**: In basket items and items with missing types or other errors.

- **Now**: All *scheduled* (dated) tasks whose due dates have passed including delegated tasks and waiting tasks (tasks with unfinished prerequisites) grouped by available, delegated and waiting and, within each group, by the due date.

- **Next**: All *unscheduled* (undated) tasks grouped by context (home, office, phone, computer, errands and so forth) and sorted by priority and extent. These tasks correspond to GTD's *next actions*. These are tasks which don't really have a deadline and can be completed whenever a convenient  opportunity arises.  Check this view, for example, before you leave to run errands for opportunities to clear other errands.

- **Someday**: Someday (maybe) items. Review these periodically.

There are no longer separate views for Now and Next and the Monthly view from etm-qt has been removed.

**Notes view** is also new and shows notes grouped and sorted by keyword.

**Week view** is similar to the week view from etm-qt with the following differences.

- Mouse over displays the item information at the bottom of the screen rather than in a tooltip.

- Items can be selected using either the mouse, as in etm-qt, or using the up and down cursor keys. In contrast to the mouse, cursor keys can be used to select an item that is underneath another scheduled item.

- Double clicking or control clicking an item or pressing Return with an item selected opens a context menu of available actions.

### Comands and Shortcuts

    Menubar
        File
            New
                Item                                    Ctrl-I
                Begin/Pause Action Timer                Ctrl-,
                Finish Action Timer                     Ctrl-.
            Open
                Data file ...                         Shift-Ctrl-D
                etmtk.cfg                             Shift-Ctrl-E
                completions.cfg                       Shift-Ctrl-C
                reports.cfg                           Shift-Ctrl-R
                scratchpad                            Shift-Ctrl-S
            ----
            Quit                                        Ctrl-Q
        View
            Agenda                                      Ctrl-A
            Schedule                                    Ctrl-S
            Tags                                        Ctrl-T
            Keywords                                    Ctrl-K
            Notes                                       Ctrl-N
            Paths                                       Ctrl-P
            Week
                Display weekly calendar                 Ctrl-W
                Display current week                     Space
                Jump to week                               j
                Previous week                            Left
                Next week                                Right
                Previous item                             Up
                Next item                                Down
                Show list of busy times                    b
            ----
            Home                                         Space
            Jump to date                                Ctrl-J
            Apply filter                                Ctrl-F
            Set outline depth                           Ctrl-O
            Choose active calendars
        Item
            Copy                                        Ctrl-C
            Delete                                    Ctrl-BackSpace
            Edit                                        Ctrl-E
            Finish                                    Ctrl-slash
            Reschedule                                  Ctrl-D
            Open link                                   Ctrl-G
            Export item as ical                         Ctrl-X
        Tools
            Display yearly calendar                     Ctrl-Y
            Open date calculator                        Ctrl-L
            Make report                                 Ctrl-R
            Show history of changes                     Ctrl-H
            Export active calendars to iCal           Shift-Ctrl-X
        Help
            Search
            Help                                          F1
            About                                         F2
            Check for update                              F3
