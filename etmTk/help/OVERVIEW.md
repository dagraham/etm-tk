# Overview

In contrast to most calendar/todo applications, creating items (events, tasks, and so forth) in etm does not require filling out fields in a form. Instead, items are created as free-form text entries using a simple, intuitive format and stored in plain text files.

Dates in the examples below are entered using *fuzzy parsing* - e.g., `+7` for seven days from today, `fri` for next Friday, `+1/1` for the first day of next month. See Help/Dates for details.

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

* Payday (an occassion) on the last week day of each month. The `&s -1` part of the entry extracts the last date which is both a weekday and falls within the last three days of the month):

        ^ payday @s 1/1 @r m &w MO, TU, WE, TH, FR
          &m -1, -2, -3 &s -1

* Take a prescribed medication daily (a reminder) [s]tarting today and [r]epeating (d)aily at [h]ours 10am, 2pm, 6pm and 10pm [u]ntil (12am on) the fourth day from today. Trigger the default [a]lert zero minutes before each event:

        * take Rx @s +0 @r d &h 10, 14, 18, 22 &u +4 @a 0

* Presidential election day (an occasion) every four years on the first Tuesday after a Monday in November:

        ^ Presidential Election Day @s 2012-11-06
          @r y &i 4 &M 11 &m 2, 3, 4, 5, 6, 7, 8 &w TU

* Join the etm discussion group (a task) [s]tarting 14 days from today. Because of the @g (goto) link, pressing Ctrl-G when this item is selected in the gui would open the link using the system default application which, in this case, would be your default browser:

        - join the etm discussion group @s +14
          @g groups.google.com/group/eventandtaskmanager/topics

## Views

Note: if a (case-insensitive) filter is entered then the display in all views will be limited to items that match somewhere in either the branch or the leaf.

### Agenda

What you need to know now beginning with your schedule for the next few days and followed by items in these groups:

- **In basket**: In basket items and items with missing types or other errors.

- **Now**: All *scheduled* (dated) tasks whose due dates have passed including delegated tasks and waiting tasks (tasks with unfinished prerequisites) grouped by available, delegated and waiting and, within each group, by the due date.

- **Next**: All *unscheduled* (undated) tasks grouped by context (home, office, phone, computer, errands and so forth) and sorted by priority and extent. These tasks correspond to GTD's *next actions*. These are tasks which don't really have a deadline and can be completed whenever a convenient  opportunity arises.  Check this view, for example, before you leave to run errands for opportunities to clear other errands.

- **Someday**: Someday (maybe) items. Review these periodically.

Note: finished tasks, actions and notes are not displayed in this view.

### Day

All dated items appear in this view, grouped by date and sorted by starting time and item type. This includes:

- All non-repeating, dated items.

- All repetitions of repeating items with a finite number of repetitions. This includes 'list-only' repeating items and items with `&u` (until) or `&t` (total number of repetitions) entries.

- For repeating items with an infinite number of repetitions, those repetitions that occur within the first `weeks_after` weeks after the current week are displayed along with the first repetition after this interval. This assures that at least one repetition will be displayed for infrequently repeating items such as voting for president.

### Tag

All items with tag entries grouped by tag and sorted by type and *relevant datetime*. Note that items with multiple tags will be listed under each tag.

### Keyword

All items grouped by keyword and sorted by type and *relevant datetime*.

### Note

All notes grouped and sorted by keyword and summary.

### Path

All items grouped by file path and sorted by type and *relevant datetime*. Use this view to review the status of your projects.

The *relevant datetime* is the past due date for any past due task, the starting datetime for any non-repeating item and the datetime of the next instance for any repeating item.

### Week

Events and occasions displayed graphically by week. Left and right cursor keys change, respectively, to the previous and next week. Up and down cursor keys select, respectively, the previous and next items within the given week. Items can also be selected by moving the mouse over the item. The summary and time period for the selected item is displayed at the bottom of the screen. Pressing return with an item selected or control-clicking an item opens a context menu. Control-clicking an unscheduled time opens a dialog to create an event for that date and time.

Pressing "j" opens a dialog to jump to the week containing a fuzzy parsed date. Pressing "b" displays a list of busy times for the active week.

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

then, by default, both dag and erp would see the entries from their personal files as well as the shared entries and each could optionally view the entries from the other's personal files as well.  See the Help/Preferences for details on the `calendars` entry.

Note for Windows users. The path separator needs to be "escaped" in the calendar paths, e.g., you should enter

     - [dag, true, personal\\dag]

instead of

     - [dag, true, personal\dag]
