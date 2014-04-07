# New: A GUI based on Tk

A new version of etm based on Tk instead of Qt is in the early stages of development. The homepage is [etmtk][]: people.duke.edu/~dgraham/etmtk.

The goals and initial results for this version:

- easier installation

    - The only requirement for the nrew GUI is tkinter and Tcl/Tk which are often already available and, if not, easily installed. *Sip, Qt and PyQt are not used.*

    - Completely self contained packages made using cx_freeze are available for both Darwin (OSX Mavericks) and Linux (Ubuntu 12.04 - 32bit). A package for Windows may be available soon.


- leaner and meaner

    - snappier performance

    - smaller files

        - source tarball: 254k for Tk vs. 20.5mb for Qt

        - Darwin: 8.2mb freeze tarball for Tk vs. 23mb app dmg for Qt

        - Linux: 3.6mb freeze tarball for Tk (nothing comparable was available for Qt)


- more informative display

    - The display area of the main window is split into two panes. The top pane shows the selected view either as a tree or, for week view, as a graph and, if an item is selected, the bottom pane shows the details of the selected item.

    - **Agenda view** is new and the default view. It represents a sort of executive summary - everything you need to know *now* in one view beginning with your schedule for the next few days and followed by items in these groups:

        - *In basket*: In basket items and items with missing types or other errors.

        - *Now*: All *scheduled* (dated) tasks whose due dates have passed including delegated tasks and waiting tasks (tasks with unfinished prerequisites) grouped by available, delegated and waiting and, within each group, by the due date.

        - *Next*: All *unscheduled* (undated) tasks grouped by context (home, office, phone, computer, errands and so forth) and sorted by priority and extent. These tasks correspond to GTD's *next actions*. These are tasks which don't really have a deadline and can be completed whenever a convenient  opportunity arises.  Check this, for example, before you leave to run errands for opportunities to clear other errands.

        - *Someday*: Someday (maybe) items. Review these periodically.

        Finished tasks, actions and notes are not displayed in this view.

    - **Notes view** is also new and shows notes grouped and sorted by keyword.

    - **Week view** is similar to the week view from etm-qt with the following differences.

        - Mouse over displays the details of the item at the bottom of the screen rather than a summary of the item in a tooltip.

        - Items can be selected using either the mouse, as in etm-qt, or using the up and down cursor keys. In contrast to the mouse, cursor keys can be used to select an item that is underneath another scheduled item.

        - Double clicking or control clicking an item or pressing Return with an item selected opens a context menu of available actions.

        - Double clicking or control clicking a free area in the week view begins a dialog to create a new event for that date and time.

    See Views under Main below for a complete list of the available views.


- more intuitive interface

    - The tool bar and icons have been replaced by a menubar where all the operational commands are easy to find and understand. See "Commands and Shortcuts" below for a complete listing.

    - Items can be selected using either the mouse or cursor keys.

    - Double clicking on an item or pressing return with an item selected opens a context menu with options to copy, delete, edit and so forth - see "Item" under "Commands and Shortcuts" for the complete list.

    - When editing a repeating item in etmqt an option is presented to select "this instance", "this and subsequent instances" and so forth.

    - In etmtk the option to change "only the datetime of this instance" is split out and offered as a new "Reschedule" command where it can be also applied to non-repeating and undated items.

    - The editor now has a validate button that will check the item being edited and report any problems and also, for repeating items, show a list of the repetitions that will be generated.

    - Completion in the editor is now triggered by pressing Control-Space instead of being automatic after a third matching character is entered.


[etmtk]: http://people.duke.edu/~dgraham/etmtk

## Unchanged

- Data files and their format are unchanged (and never will be).

- The name of the configuration file has changed from etm.cfg to etmtk.cfg but is otherwise unchanged - you can just copy etm.cfg to etmtk.cfg to use your current settings.

- The configuration files completions.cfg and reports.cfg are unchanged.

- actions, timers and reports are unchanged.

- Both python 2.7x and >= 3.3 are supported.

## Comands and Shortcuts

Note: Most dialogs can be closed by pressing Escape.

    Menubar
        File
            New
                Item                                    Ctrl-I
                Begin/Pause Action Timer                Ctrl-,
                Finish Action Timer                     Ctrl-.
            Open
                Data file ...                         Shift-Ctrl-F
                etmtk.cfg                             Shift-Ctrl-E
                completions.cfg                       Shift-Ctrl-C
                reports.cfg                           Shift-Ctrl-R
                scratchpad                            Shift-Ctrl-S
            ----
            Quit                                        Ctrl-Q
        View
            Home                                         Space
            Jump to date                                Ctrl-J
            ----
            Next sibling                              Control-Down
            Previous sibling                          Control-Up
            Set outline filter                          Ctrl-F
            Clear outline filter                        Escape
            Set outline depth                           Ctrl-O
            ----
            Previous week                                Left
            Next week                                    Right
            Previous item in week                         Up
            Next item in week                            Down
            Clear selection                             Escape
            List busy times in week                     Ctrl-B
        Item
            Copy                                        Ctrl-C
            Delete                                    Ctrl-BackSpace
            Edit                                        Ctrl-E
            Finish                                      Ctrl-X
            Reschedule                                  Ctrl-S
            Open link                                   Ctrl-G
            Export item as ical                           F6
        Tools
            Display yearly calendar                       F4
            Open date calculator                          F5
            Create report                               Ctrl-R
            Show history of changes                     Ctrl-H
            Export active calendars as iCal            Shift-F6
        Help
            Search
            Help                                          F1
            About                                         F2
            Check for update                              F3
    Main
        Views
            Agenda                                      Ctrl-A
            Day                                         Ctrl-D
            Tag                                         Ctrl-T
            Keyword                                     Ctrl-K
            Note                                        Ctrl-N
            Path                                        Ctrl-P
            Week                                        Ctrl-W
    Edit
        Show possible completions                     Ctrl-Space
        Validate entry                                  Ctrl-?
        Close editor                                    Ctrl-Q
        Save changes and close editor                   Ctrl-W
    Report
        Create and display selected report              Return
        Export report in text format ...                Ctrl-T
        Export report in csv format ...                 Ctrl-X
        Save changes to report specifications           Ctrl-W
        Expand report list                               Down
        Quit                                            Ctrl-Q
