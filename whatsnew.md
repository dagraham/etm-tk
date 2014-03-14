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

- The only requirement for the GUI is tkinter and Tcl/Tk which are often already available and, if not, easily installed. *Sip, Qt and PyQt need not be installed.*

- Completely self contained packages made using cx_freeze are available on the web site for both Darwin (OSX) and Linux (Ubuntu). A package for Windows may be available soon.

- File sizes are smaller:

    - source tarball: Tk 254k vs. Qt 20.5mb

    - Darwin: Tk 8.2md freeze tarball vs. Qt 23mb app dmg

    - Linux: Tk 3.7mb freeze tarball vs. Qt NA

### The main window of the GUI

- The main window is simpler. The tool bar and icons have been replaced by a menubar where all the operational commands are listed in the language of your choice along with keyboard shortcuts. (Currently the only choice is English but more can/will be added. :-) See "Commands and Shortcuts" below for a listing.

- The display area of the main window is split into two panes. The top pane shows the selected view as a tree and, if an item is selected, the bottom pane shows the details of the selected item.

- Items are displayed in the top, tree pane using their type characters instead of icons.

- Double clicking on an item or pressing return or Ctrl-E with an item selected opens it for editing. Other actions are available for the selected item - see "Item" under "Commands and Shortcuts" for a list.

- When editing a repeating item in etmqt an option is presented to select "only the datetime of this instance", "this instance" and so forth. In etmtk the first option is split out and offered as a new "Reschedule" command where it can be applied to non-repeating and even undated items.

### Views

**Agenda view** is new and the default view. It represents a sort of executive summary - what you need to know *now* beginning with your schedule for the next few days and followed by items in these groups:

- **In basket**: In basket items and items with missing types or other errors.

- **Now**: All *scheduled* (dated) tasks whose due dates have passed including delegated tasks and waiting tasks (tasks with unfinished prerequisites) grouped by available, delegated and waiting and, within each group, by the due date.

- **Next**: All *unscheduled* (undated) tasks grouped by context (home, office, phone, computer, errands and so forth) and sorted by priority and extent. These tasks correspond to GTD's *next actions*. These are tasks which don't really have a deadline and can be completed whenever a convenient  opportunity arises.  Check this view, for example, before you leave to run errands for opportunities to clear other errands.

- **Someday**: Someday (maybe) items. Review these periodically.

There are no longer separate views for Now and Next. The Monthly view from etm-qt has been removed and the Weekly view is being prepared.

**Notes view** is also new and shows notes grouped and sorted by keyword.

### Comands and Shortcuts

    Menubar
        File
            New
                Item                                    Ctrl-N
                Timer                                   Ctrl-I
            Open
                Data file ...                         Shift-Ctrl-D
                etmtk.cfg                             Shift-Ctrl-E
                completions.cfg                       Shift-Ctrl-C
                reports.cfg                           Shift-Ctrl-R
                scratchpad                            Shift-Ctrl-S
            ----
            Quit
        View
            Agenda                                      Ctrl-A
            Schedule                                    Ctrl-S
            Tags                                        Ctrl-T
            Keywords                                    Ctrl-K
            Paths                                       Ctrl-P
            ----
            Apply filter                                Ctrl-F
            Set outline depth                           Ctrl-O
            Choose active calendars
        Item
            Copy                                        Ctrl-C
            Delete                                      Ctrl-D
            Edit                                        Ctrl-E
            Finish                                      Ctrl-X
            Reschedule                                  Ctrl-R
            Open link                                   Ctrl-G
            Export item to iCal                         Ctrl-V
        Tools
            Jump to date                                Ctrl-J
            Show busy periods                           Ctrl-B
            Display yearly calendar                     Ctrl-Y
            Open date calculator                        Ctrl-L
            ----
            Make report                                 Ctrl-M
            Show changes                                Ctrl-H
            Export active calendars to iCal           Shift-Ctrl-V
        Help
            Search
            Help                                          F1
            About                                         F2
            Check for update                              F3
