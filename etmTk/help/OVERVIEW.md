# Overview

In contrast to most calendar/todo applications, creating items (events, tasks, and so forth) in etm does not require filling out fields in a form. Instead, items are created as free-form text entries using a simple, intuitive format and stored in plain text files.

Dates in the examples below are entered using *fuzzy parsing* - e.g., `+7` for seven days from today, `fri` for next Friday, `+1/1` for the first day of next month, `sun - 6d` for Monday of the current week. See [Dates](#dates) for details.

## Sample entries

* A sales meeting (an event) [s]tarting seven days from today at 9:00am with an [e]xtent of one hour and a default [a]lert 5 minutes before the start:

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

        ^ payday @s 1/1 @r m &w MO, TU, WE, TH, FR
          &m -1, -2, -3 &s -1

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

* Join the etm discussion group (a task) [s]tarting 14 days from today. Because of the @g (goto) link, pressing *G* when this item is selected in the gui would open the link using the system default application which, in this case, would be your default browser:

        - join the etm discussion group @s +14
          @g groups.google.com/group/eventandtaskmanager/topics

## Starting etm

To start the etm GUI open a terminal window and enter `etm` at the prompt:

    $ etm

If you have not done a system installation of etm you will need first to cd to the directory where you unpacked etm.

You can add a command to use the CLI instead of the GUI. For example, to get the complete command line usage information printed to the terminal window just add a question mark:

    $ etm ?
    Usage:

        etm [logging level] [path] [?] [acmsv]

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
        d ARG   display the day view using ARG, if given, as a filter.
        k ARG   display the keywords view using ARG, if given, as a filter.
        m INT   display a report using the remaining argument, which must be a
                positive integer, to display a report using the corresponding
                entry from the file given by report_specifications in etmtk.cfg.
                Use ? m to display the numbered list of entries from this file.
        n ARGS  Create a new item using the remaining arguments as the item
                specification. (Enclose ARGS in single quotes to prevent shell
                expansion.)
        N ARG   display the notes view using ARG, if given, as a filter.
        p ARG   display the path view using ARG, if given, as a filter.
        r ARGS  display a report using the remaining arguments as the report
                specification. (Enclose ARGS in single quotes to prevent shell
                expansion.)
        t ARG   display the tags view using ARG, if given, as a filter.
        v       display information about etm and the operating system.
        ? ARG   display (this) command line help information if ARGS = '' or,
                if ARGS = X where X is one of the above commands, then display
                details about command X. 'X ?' is equivalent to '? X'.

For example, you can print your agenda to the terminal window by adding the letter "a":

    $ etm a
    Sun Apr 06, 2014
      > set up luncheon meeting with Joe Smith           4d
    Mon Apr 07, 2014
      * test command line event                      3pm ~ 4pm
      * Aerobics                                     5pm ~ 6pm
      - follow up with Mary Jones
    Wed Apr 09, 2014
      * Aerobics                                     5pm ~ 6pm
    Thu Apr 10, 2014
      * Frank Burns conference call 1pm Pacif..     4pm ~ 5:30pm
      * Book club                                    7pm ~ 9pm
      - sales meeting
      - set up luncheon meeting with Joe Smith          15m
    Now
      Available
        - Hair cut                                      -1d
    Next
      errands
        - milk and eggs
      phone
        - reservation for Saturday dinner
    Someday
      ? lose weight and exercise more

You can filter the output by adding a (case-insensitive) argument:

    $ etm a smith
    Sun Apr 06, 2014
      > set up luncheon meeting with Joe Smith           4d
    Thu Apr 10, 2014
      - set up luncheon meeting with Joe Smith          15m

or `etm d mar .*2014` to show your items for March, 2014.

You can add a question mark to a command to get details about the commmand, e.g.:

    Usage:

        etm c <type> <groupby> [options]

    Generate a custom view where type is either 'a' (action) or 'c' (composite).
    Groupby can include *semicolon* separated date specifications and
    elements from:
        c context
        f file path
        k keyword
        t tag
        u user

    A *date specification* is either
        w:   week number
    or a combination of one or more of the following:
        yy:   2-digit year
        yyyy:   4-digit year
        MM:   month: 01 - 12
        MMM:   locale specific abbreviated month name: Jan - Dec
        MMMM:   locale specific month name: January - December
        dd:   month day: 01 - 31
        ddd:   locale specific abbreviated week day: Mon - Sun
        dddd:   locale specific week day: Monday - Sunday

    Options include:
        -b begin date
        -c context regex
        -d depth (CLI a reports only)
        -e end date
        -f file regex
        -k keyword regex
        -l location regex
        -o omit (r reports only)
        -s summary regex
        -S search regex
        -t tags regex
        -u user regex
        -w column 1 width
        -W column 2 width

    Example:

        etm c 'c ddd, MMM dd yyyy -b 1 -e +1/1'

Note: The CLI offers the same views and reporting, with the exception of week view, as the GUI. It is also possible to create new items in the CLI with the `n` command. Other modifications such as copying, deleting, finishing and so forth, can only be done in the GUI or, perhaps, in your favorite text editor. An advantage to using the GUI is that it provides validation.

Tip: If you have a terminal open, you can create a new item or put something to finish later in your inbox quickly and easily with the "i" command. For example,

        etm i '123 456-7890'

would create an entry in your inbox with this phone number. (With no type character an "$" would be supplied automatically to make the item an inbox entry and no further validation would be done.)

## Views

All views, including week view, display only items consistent with the current choices of active calendars.

If a (case-insensitive) filter is entered then the display in all views other than week view and custom view will be limited to items that match somewhere in either the branch or the leaf.  Relevant branches will automatically be expanded to show matches.

In day and week views, pressing the space bar will move the display to the current date. In all other views, pressing the space bar will move the display to the first item in the outline.

In day and week views, pressing *J* will first prompt for a fuzzy-parsed date and then "jump" to the specified date.

If you scroll or jump to a date in either day view or week view and then open the other view, the same day(s) will be displayed.

In all views, pressing *Return* with an item selected or double clicking an item or a busy period in week view will open a context menu with options to copy, delete, edit and so forth.

In all views, clicking in the details panel with an item selected will open the item for editing if it is not repeating and otherwise prompt for the instance(s) to be changed.

In all views other than week view, pressing *O* will open a dialog to choose the outline depth.

In all views other than week view, pressing *L* will toggle the display of a column displaying item *labels* where, for example, an item with @a, @d and @u fields would have the label "adu".

In all views other than week view, pressing *S* will show a text verion of the current display suitable for copy and paste. The text version will respect the current outline depth in the view.

In custom view it is possible to export the current report in either text or CSV (comma separated values) format to a file of your choosing.

Note. In custom view you need to remove the focus from the report specification entry field in order for the shortcuts *O*, *L* and *S* to work.

In all views other than custom view and week view:

- if an item is selected:

    - pressing *Shift-H* will show a history of changes for the file containing the selected item, first prompting for the number of changes.

    - pressing *Shift-X* will export the selected item in iCal format.

- if an item is not selected:

    - pressing *Shift-H* will show a history of changes for all files, first prompting for the number of changes.

    - pressing *Shift-X* will export all items in active calendars in iCal format.

### Agenda View

What you need to know now beginning with your schedule for the next few days and followed by items in these groups:

- **In basket**: In basket items and items with missing types or other errors.

- **Now**: All *scheduled* (dated) tasks whose due dates have passed including delegated tasks and waiting tasks (tasks with unfinished prerequisites) grouped by available, delegated and waiting and, within each group, by the due date.

- **Next**: All *unscheduled* (undated) tasks grouped by context (home, office, phone, computer, errands and so forth) and sorted by priority and extent. These tasks correspond to GTD's *next actions*. These are tasks which don't really have a deadline and can be completed whenever a convenient  opportunity arises.  Check this view, for example, before you leave to run errands for opportunities to clear other errands.

- **Someday**: Someday (maybe) items for periodic review.

Note: Finished tasks, actions and notes are not displayed in this view.

### Day View

All dated items appear in this view, grouped by date and sorted by starting time and item type. This includes:

- All non-repeating, dated items.

- All repetitions of repeating items with a finite number of repetitions. This includes 'list-only' repeating items and items with `&u` (until) or `&t` (total number of repetitions) entries.

- For repeating items with an infinite number of repetitions, those repetitions that occur within the first `weeks_after` weeks after the current week are displayed along with the first repetition after this interval. This assures that at least one repetition will be displayed for infrequently repeating items such as voting for president.

Tip: Want to see your next appointment with Dr. Jones? Switch to day view and enter "jones" in the filter.

### Tag View

All items with tag entries grouped by tag and sorted by type and *relevant datetime*. Note that items with multiple tags will be listed under each tag.

Tip: Use the filter to limit the display to items with a particular tag.

### Keyword View

All items grouped by keyword and sorted by type and *relevant datetime*.

### Note View

All notes grouped and sorted by keyword and summary.

### Path View

All items grouped by file path and sorted by type and *relevant datetime*. Use this view to review the status of your projects.

The *relevant datetime* is the past due date for any past due task, the starting datetime for any non-repeating item and the datetime of the next instance for any repeating item.

Note: Items that you have "commented out" by beginning the item with a `#` will only be visible in this view.

### Week View

Events and occasions displayed graphically by week. Left and right cursor keys change, respectively, to the previous and next week. Up and down cursor keys select, respectively, the previous and next items within the given week. Items can also be selected by moving the mouse over the item. The summary and time period for the selected item is displayed at the bottom of the screen. Pressing return with an item selected or double-clicking an item opens a context menu. Control-clicking an unscheduled time opens a dialog to create an event for that date and time.

Tip. Press *Ctrl-B* to display a list of busy times for the selected week or *Ctrl-F* and provide the needed period in minutes to display a list of free times that would accomodate the requirement.

### Custom View

Design your own view. See [Reports](#reports) for details.

## Creating New Items

Items of any type can be created by pressing *N* in the GUI and then providing the details for the item in the resulting dialog.

An event can also be created by double-clicking in a free period in the Week View - the date and time corresponding to the mouse position will be entered as the starting datetime when the dialog opens.

An action can also be created by pressing *T* to start a timer for the action. You will be prompted for a summary (title) and, optionally, an `@e` entry to specify a starting time for the timer. If an item is selected when you press *T* then you will have the additional option of creating the action as a copy of the selected item.

The timer starts automatically when you close the dialog. Once the timer is running, pressing *T* toggles the timer between running and paused. Pressing *Shift-T* when a timer is active (either running or paused) stops the timer and begins a dialog to provide the details of the action - the elapsed time will already be entered.

While a timer is active, the title, elapsed time and status - running or paused - is displayed in the status bar.

Tip: When creating or editing a repeating item, press *Validate* to check your entry and see a list of the instances that it will generate.

## Editing Existing Items

Double-clicking an item or pressing *Return* when an item is selected will open a context menu of possible actions:

- Copy
- Delete
- Edit
- Finish (unfinished tasks only)
- Reschedule
- Open link (items with `@g` entries only)
- Export as iCal

When either *Copy* or *Edit* is chosen for a repeating item, you can further choose:

1. this instance
2. this and all subsequent instances
3. all instances

When *Delete* is chosen for a repeating item, a further choice is available:

4. all previous instances

Tip: Use *Reschedule* to enter a date for an undated item or to change the scheduled date for the item or the selected instance of a repeating item. All you have to do is enter the new (fuzzy parsed) datetime.

## Data Organization and Calendars

*etm* offers two hierarchical ways of organizing your data: by keyword and file path. There are no hard and fast rules about how to use these hierarchies but the goal is a system that makes complementary uses of folder and keyword and fits your needs. As with any filing system, planning and consistency are paramount.

For example, one pattern of use for a business would be to use folders for people and keywords for client-project-category.

Similarly, a family could use folders to separate personal and shared items for family members, for example:

    root etm data directory
        personal
            dag
            erp
        shared
            holidays
            birthdays
            events

Here

    ~dag/.etm/etm.cfg
    ~erp/.etm/etm.cfg

would both contain `datadir` entries specifying the common root data directory. Additionally, if these configuration files contained, respectively, the entries

    ~dag/.etm/etm.cfg
        calendars
        - [dag, true, personal/dag]
        - [erp, false, personal/erp]
        - [shared, true, shared]

and

    ~erp/.etm/etm.cfg
        calendars
        - [erp, true, personal/erp]
        - [dag, false, personal/dag]
        - [shared, true, shared]

then, by default, both dag and erp would see the entries from their personal files as well as the shared entries and each could optionally view the entries from the other's personal files as well.  See the [Preferences](#preferences) for details on the `calendars` entry.

Note for Windows users. The path separator needs to be "escaped" in the calendar paths, e.g., you should enter

     - [dag, true, personal\\dag]

instead of

     - [dag, true, personal\dag]
