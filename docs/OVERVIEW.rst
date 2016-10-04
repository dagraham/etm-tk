Overview
========

In contrast to most calendar/todo applications, creating items (events,
tasks, and so forth) in etm does not require filling out fields in a
form. Instead, items are created as free-form text entries using a
simple, intuitive format and stored in plain text files.

Dates in the examples below are entered using *fuzzy parsing* - e.g.,
``+7`` for seven days from today, ``fri`` for the first Friday on or
after today, ``+1/1`` for the first day of next month, ``sun - 6d`` for
Monday of the current week. See `Dates <#dates>`__ for details.

Sample entries
--------------

-  A sales meeting (an event) [s]tarting seven days from today at 9:00am
   with an [e]xtent of one hour and a default [a]lert 5 minutes before
   the start:

   ::

       * sales meeting @s +7 9a @e 1h @a 5

-  The sales meeting with another [a]lert 2 days before the meeting to
   (e)mail a reminder to a list of recipients:

   ::

       * sales meeting @s +7 9a @e 1h @a 5
         @a 2d: e; who@when.com, what@where.org

-  Prepare a report (a task) for the sales meeting [b]eginning 3 days
   early:

   ::

       - prepare report @s +7 @b 3

-  A period [e]xtending 35 minutes (an action) spent working on the
   report yesterday:

   ::

       ~ report preparation @s -1 @e 35

-  Get a haircut (a task) on the 24th of the current month and then
   [r]epeatedly at (d)aily [i]ntervals of (14) days and, [o]n
   completion, (r)estart from the completion date:

   ::

       - get haircut @s 24 @r d &i 14 @o r

-  Payday (an occasion) on the last week day of each month. The
   ``&s -1`` part of the entry extracts the last date which is both a
   weekday and falls within the last three days of the month):

   ::

       ^ payday @s 1/1 @r m &w MO, TU, WE, TH, FR
         &m -1, -2, -3 &s -1

-  Take a prescribed medication daily (a reminder) [s]tarting today and
   [r]epeating (d)aily at [h]ours 10am, 2pm, 6pm and 10pm [u]ntil (12am
   on) the fourth day from today. Trigger the default [a]lert zero
   minutes before each reminder:

   ::

       * take Rx @s +0 @r d &h 10, 14, 18, 22 &u +4 @a 0

-  Move the water sprinkler (a reminder) every thirty mi[n]utes on
   Sunday afternoons using the default alert zero minutes before each
   reminder:

   ::

       * Move sprinkler @s 1 @r n &i 30 &w SU &h 14, 15, 16, 17 @a 0

   To limit the sprinkler movement reminders to the [M]onths of April
   through September each year append ``&M 4, 5, 6, 7, 8, 9`` to the @r
   entry.

-  Grandparent's day (an occasion) each year on the first Sunday in
   September after Labor day:

   ::

       ^ Grandparent's Day @s 2012-09-01
         @r y &M 9 &w SU &m 7, 8, 9, 10, 11, 12, 13 

-  Presidential election day (an occasion) every four years on the first
   Tuesday after a Monday in November:

   ::

       ^ Presidential Election Day @s 2012-11-06
         @r y &i 4 &M 11 &w TU &m 2, 3, 4, 5, 6, 7, 8 

-  Join the etm discussion group (a task) [s]tarting 14 days from today.
   Because of the @g (goto) link, pressing *G* when this item is
   selected in the gui would open the link using the system default
   application which, in this case, would be your default browser:

   ::

       - join the etm discussion group @s +14
         @g groups.google.com/group/eventandtaskmanager/topics

Starting etm
------------

To start the etm GUI open a terminal window and enter ``etm`` at the
prompt:

::

    $ etm

If you have not done a system installation of etm you will need first to
cd to the directory where you unpacked etm.

Note: if you change the window size and/or position of the etm window on
your display and quit etm from the etm file menu, then the closing size
and position will be restored when you restart etm.

You can add a command to use the CLI instead of the GUI. For example, to
get the complete command line usage information printed to the terminal
window just add a question mark:

::

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
        c ARGS  display a custom view using the remaining arguments as the
                specification. (Enclose ARGS in single quotes to prevent shell
                expansion.)
        d ARG   display the day view using ARG, if given, as a filter.
        k ARG   display the keywords view using ARG, if given, as a filter.
        m INT   display a custom view using the remaining argument, which 
                must be a positive integer, to display a custom view using the 
                corresponding entry from the file given by report_specifications 
                in etmtk.cfg.
                Use ? m to display the numbered list of entries from this file.
        n ARG   display the notes view using ARG, if given, as a filter.
        N ARGS  Create a new item using the remaining arguments as the item
                specification. (Enclose ARGS in single quotes to prevent shell
                expansion.)
        p ARG   display the path view using ARG, if given, as a filter.
        t ARG   display the tags view using ARG, if given, as a filter.
        v       display information about etm and the operating system.
        ? ARG   display (this) command line help information if ARGS = '' or,
                if ARGS = X where X is one of the above commands, then display
                details about command X. 'X ?' is equivalent to '? X'.

For example, you can print your agenda to the terminal window by adding
the letter "a":

::

    $ etm a
    Today
      > set up luncheon meeting with Joe Smith           4d
    Tomorrow
      * test command line event                      3pm ~ 4pm
      * Aerobics                                     5pm ~ 6pm
      - follow up with Mary Jones
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

::

    $ etm a hair
    Now
      Available
        - Hair cut                                      -1d

or ``etm d mar .*2014`` to show your items for March, 2014.

You can add a question mark to a command to get details about the
commmand, e.g.:

::

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
        -d depth (CLI type a only)
        -e end date
        -f file regex
        -k keyword regex
        -l location regex
        -o omit (type c only)
        -s summary regex
        -S search regex
        -t tags regex
        -u user regex
        -w column 1 width
        -W column 2 width

    Example:

        etm c 'c ddd, MMM dd yyyy -b 1 -e +1/1'

Note: The CLI offers the same views and reporting, with the exception of
week and month view, as the GUI. It is also possible to create new items
in the CLI with the ``n`` command. Other modifications such as copying,
deleting, finishing and so forth, can only be done in the GUI or,
perhaps, in your favorite text editor. An advantage to using the GUI is
that it provides auto-completion and validation.

Tip: If you have a terminal open, you can create a new item or put
something to finish later in your inbox quickly and easily with the "N"
command. For example,

::

        etm N '123 456-7890'

would create an entry in your inbox with this phone number. (With no
type character an "$" would be supplied automatically to make the item
an inbox entry and no further validation would be done.)

Views
-----

All views display only items consistent with the current choices of
active calendars. Click the settings icon on the left side of the top
menu bar to choose active calendars.

Week and month views have three panes. The top one displays a graphic
illustration of scheduled times for the relevant period, the middle one
displays an tree view of items grouped by date and the bottom one
displays detail information. Custom view also has three panes but the
top one is an entry area for providing the specification for the custom
view. All other views have two panes - a tree view in the top pane and
details in the bottom pane.

If a (case-insensitive) filter is entered then the display in the tree
view will be limited to items that match somewhere in either the branch
or the leaf. Relevant branches will automatically be expanded to show
matches.

In week and month views, *Home* selects the current date. In all views
other than week and month, *Home* selects the first item in the tree
pane.

In all views, pressing *Return* with an item selected will open a
context menu with options to copy, delete, edit and so forth.

In all views, clicking in the details panel with an item selected will
open the item for editing if it is not repeating and otherwise prompt
for the instance(s) to be changed.

In all views, pressing *O* will open a dialog to choose the outline
depth. Pressing *L* will toggle the display of a column displaying item
*labels* where, for example, an item with @a, @d and @u fields would
have the label "adu". Pressing *S* will show a text verion of the
current display suitable for copy and paste. The text version will
respect the current outline depth in the view.

In custom view it is possible to export the current view in either text
or CSV (comma separated values) format to a file of your choosing.

Note. In custom view you need to move the focus from the view
specification entry field in order for the shortcuts *O*, *L* and *S* to
work.

In all views:

-  if an item is selected:

   -  pressing *Shift-H* will show a history of changes for the file
      containing the selected item, first prompting for the number of
      changes.

   -  pressing *Shift-X* will export the selected item in iCal format.

-  if an item is not selected:

   -  pressing *Shift-H* will show a history of changes for all files,
      first prompting for the number of changes.

   -  pressing *Shift-X* will export all items in active calendars in
      iCal format.

Agenda View
~~~~~~~~~~~

What you need to know now beginning with your schedule for the next few
days and followed by items in these groups:

-  **In basket**: In basket items and items with missing types or other
   errors.

-  **Now**: All *scheduled* (dated) tasks whose due dates have passed
   including delegated tasks and waiting tasks (tasks with unfinished
   prerequisites) grouped by available, delegated and waiting and,
   within each group, by the due date.

-  **Next**: All *unscheduled* (undated) tasks grouped by context (home,
   office, phone, computer, errands and so forth) and sorted by priority
   and extent. These tasks correspond to GTD's *next actions*. These are
   tasks which don't really have a deadline and can be completed
   whenever a convenient opportunity arises. Check this view, for
   example, before you leave to run errands for opportunities to clear
   other errands.

-  **Someday**: Someday (maybe) items for periodic review.

Note: Finished tasks, actions and notes are not displayed in this view.

Week and Month Views
~~~~~~~~~~~~~~~~~~~~

These views only differ in whether the graphic in the top pane describes
a week or a month. All dated items appear in the middle, tree pane in
these view, grouped by date and sorted by starting time and item type.
Displayed items include:

-  All non-repeating, dated items.

-  All repetitions of repeating items with a finite number of
   repetitions. This includes 'list-only' repeating items and items with
   ``&u`` (until) or ``&t`` (total number of repetitions) entries.

-  For repeating items with an infinite number of repetitions, those
   repetitions that occur within the first ``weeks_after`` weeks after
   the current week are displayed along with the first repetition after
   this interval. This assures that at least one repetition will be
   displayed for infrequently repeating items such as voting for
   president.

The graphic display in the top pane has a square cell for each
week/month date. Within this cell, scheduled, *busy* times are indicated
by segments of a square busy border that surrounds the date. This border
can be regarded as a 24-hour clock face that proceeds clockwise from
12am at the lower, left-hand corner with 6 hour segments for each side:
12am - 6am moving upward on the left side, 6am - 12pm moving rightward
along the top, 12pm - 6pm moving downward along the right side and,
finally, 6pm - 12pm moving leftward along the bottom. When nothing is
scheduled for a date, the border is blank. When only one event is
scheduled for a date, say from 9am until 3pm, then the border would be
colored from the middle of the top side (9am) around the top, right-hand
corner and downward to the middle of the right side (3pm). When other
periods are scheduled, corresponding portions of the border would be
colored. If two or more scheduled periods overlap, then a small, red box
appears in the lower, left-hand corner of the border to warn of the
conflict.

When the top pane has the focus, the left/right cursor keys move to the
previous/subsequent week or month and the up/down cursor keys move to
the previous/subsequent date. Either *Home* or *Space* moves the display
to the current date. Pressing *J* will first prompt for a fuzzy-parsed
date and then "jump" to the specified date. Whenever a date is selected
in the top pane, the date tree in the middle pane is scrolled, if
necessary, to display the selected date first. Whenever a date is
selected in either week or month view, the same date is automatically
becomes the selection in the other view as well.

Note: If a date is selected for which no items are scheduled, then the
last date with scheduled items on or before the selected date will
become the selected date in the middle, tree pane.

Tip: Want to see your next appointment with Dr. Jones? Switch to day
view and enter "jones" in the filter.

Tip. You can display a list of busy times or, after providing the needed
period in minutes, a list of free times that would accommodate the
requirement within the selected week/month. Both options are in the
*View* menu.

Week View
~~~~~~~~~

Events and occasions displayed graphically by week with one column for
each day. Left and right cursor keys change, respectively, to the
previous and next week. Up and down cursor keys select, respectively,
the previous and next items within the given week. Items can also be
selected by moving the mouse over the item. The details for the selected
item are displayed at the bottom of the screen. Pressing return with an
item selected or double-clicking an item opens a context menu.
Control-clicking an unscheduled time opens a dialog to create an event
for that date and time.

Month View
~~~~~~~~~~

Events and occasions displayed graphically by month. Left and right
cursor keys change, respectively, to the previous and next month. Up and
down cursor keys select, respectively, the previous and next days within
the given month. Days can also be selected by moving the mouse over the
item. A list of occasions and events for the selected day is displayed
at the bottom of the screen. Double clicking a date or pressing *Return*
with a date selected opens a dialog to create an item for that date.

The current date and days with occasions are highlighted.

Tip. You can display a list of busy times or, after providing the needed
period in minutes, a list of free times that would accommodate the
requirement within the selected month. Both options are in the *View*
menu.

Tag View
~~~~~~~~

All items with tag entries grouped by tag and sorted by type and
*relevant datetime*. Note that items with multiple tags will be listed
under each tag.

Tip: Use the filter to limit the display to items with a particular tag.

Keyword View
~~~~~~~~~~~~

All items grouped by keyword and sorted by type and *relevant datetime*.

Path View
~~~~~~~~~

All items grouped by file path and sorted by type and *relevant
datetime*. Use this view to review the status of your projects.

The *relevant datetime* is the past due date for any past due task, the
starting datetime for any non-repeating item and the datetime of the
next instance for any repeating item.

Note: Items that you have "commented out" by beginning the item with a
``#`` will only be visible in this view.

Note View
~~~~~~~~~

All notes grouped and sorted by keyword and summary.

Custom
~~~~~~

Design your own view. See `Custom view <#custom-view>`__ for details.

Creating New Items
------------------

Items of any type can be created by pressing *N* in the GUI and then
providing the details for the item in the resulting dialog.

An event can also be created by double-clicking in a date cell in either
Week or Month View - the corresponding date will be entered as the
starting date when the dialog opens.

When editing an item, clicking on *Finish* or pressing *Shift-Return*
will validate your entry. If there are errors, they will be displayed
and you can return to the editor to correct them. If there are no
errors, this will be indicated in a dialog, e.g.,

::

    Task scheduled for Tue Jun 03

    Save changes and exit?

Tip. When creating or editing a repeating item, pressing *Finish* will
also display a list of instances that will be generated.

Click on *Ok* or press *Return* or *Shift-Return* to save the item and
close the editor. Click on *Cancel* or press *Escape* to return to the
editor.

If this is a new item and there are no errors, clicking on *Ok* or
pressing *Return* will open a dialog to select the file to store the
item with the current monthly file already selected. Pressing
*Shift-Return* will bypass the file selection dialog and save to the
current monthly file.

Editing Existing Items
----------------------

Double-clicking an item or pressing *Return* when an item is selected
will open a context menu of possible actions:

-  Copy
-  Delete
-  Edit
-  Edit file
-  Finish (unfinished tasks only)
-  Reschedule
-  Schedule new
-  Klone as timer
-  Open link (items with ``@g`` entries only)
-  Show user details (items with ``@u`` entries only)

When either *Copy* or *Edit* is chosen for a repeating item, you can
further choose:

1. this instance
2. this and all subsequent instances
3. all instances

When *Delete* is chosen for a repeating item, a further choice is
available:

4. all previous instances

Tip: Use *Reschedule* to enter a date for an undated item or to change
the scheduled date for the item or the selected instance of a repeating
item. All you have to do is enter the new (fuzzy parsed) datetime.

Timers
------

countdown timer
~~~~~~~~~~~~~~~

To start a countdown timer press *z*, change the default number of
minutes if necessary and press *Return*. The time that the timer will
expire will be displayed in the status bar with a ``-`` prefix.

If ``countdown_command`` is given in *etmtk.cfg*, then it will be
executed when the timer expires and the countdown message dialog will
appear with the last chosen number of minutes as the default. You can
either press *Return* to start another countdown or press *Escape* to
cancel. If activated, the time that the countdown timer will expire will
be displayed in the status bar.

snooze timer
~~~~~~~~~~~~

When the last alert of type ``m`` (message) is triggered for an item,
the alert dialog that is displayed offers the option of snoozing, i.e.,
repeating the alert after a number of minutes you choose. If activated,
the alert corresponding to snooze timer can be displayed along with any
other remaining alerts using *Tools/Show remaining alerts*.

If ``snooze_command`` is given in *etmtk.cfg*, then it will be executed
when the snooze timer expires and the alert message dialog will appear
with the last chosen number of minutes as the default. You can either
press *Return* to snooze again or press *Escape* to cancel.

action timer
~~~~~~~~~~~~

For people who bill their time or just like to keep track of how they
spend their time, etm allows you to create an action by pressing *T* to
start a timer. You will see an entry area with a list of any existing
timers below. As you enter characters in the entry area, the list below
will shrink to those whose beginnings match the characters you've
entered. You can either select a timer from the list to start that timer
or enter new name in the entry area to create and start a new timer. If
a timer is running, it will automatically be paused when you start a new
timer or switch to another timer.

Tip. Devoting time to two different clients this morning? Create two
timers, one for each client and just switch back and forth using *T*
when you switch from one client to the other. The timers are ordered in
the list so that the most recently paused will be at the top.

While a timer is selected, the name, elapsed time and status - running
or paused - is displayed in the status bar along with the number of
active timers in parentheses. Pressing *I* toggles the timer between
running and paused. You can configure etm's options to, for example,
play one sound at intervals when a timer is running and another sound
when the selected timer is paused and you can also specify the length of
the interval and the volume.

When one or more timers are active and none are running, idle time is
accumulated and displayed, by default, in the status bar. The idle time
display can be toggled on and off and accumulated idle time can be reset
to zero. It is also possible to transfer minutes from accumulated idle
time to the current action timer.

When you have one or more active timers, you can press *Shift-T* to
select one to finish. The selected timer will be paused if it is running
and you will be presented with an entry area to create a new action with
the following details already filled in:
``~ timer name @s starting datetime @e elapsed time``. You can edit this
entry in any way you like and then save it. When you do so, this timer
will be removed from your list of active timers. You can also press
*Shift-I* to select a timer to delete. Any accumulated time for the
selected timer will be added to the accumulated idle time and the timer
will be removed from the list of active timers.

It is also possible to start a timer by selecting an event, note, task
or whatever, from one of *etm*'s Views and then choosing *Item/Klone as
timer* from the menu or pressing *K*. A start timer dialog will be
opened with the summary of the item you selected as the name together
with any @-keys from the selected item that are listed in
``action_keys`` in your ``etmtk.cfg``. You can edit this entry if you
like or just press *Return* to accept it and start the timer. If you
already have an active timer with this name, it will be restarted.
Otherwise a new timer will be created and started.

Tip. Suppose you have a client, John Smith, and will be doing some work
for him this morning relating to the project "Motion". If you don't
already have a task relating to this begin by creating one for today,
June 16, 2015, by pressing *N* and entering

::

    - work @k SmithJohn:Motion @s +0

The first activity related to this task involves a phone call to Sally.
Select the task you just created and then press *K* to start a timer.
Change ``work`` to ``call Sally`` and press *Return* to start the timer.
When you've finished the call, press *I* to pause the timer. Based on
this phone conversation, you decide the next activity should be to
review Local Rule 4567, so once again select the task, press *K* and
then change ``work`` to ``review Local Rule 4567`` and press *Return* to
start this timer. When you're done, once again press *I* to pause this
timer. You can repeat this process as often as you like. If you need to
spend more time on 4567, press *T* and select it from the list of
timers. When you're done, you can press *Shift-T* to select a timer from
the list and finish it. Selecting the "call Sally" timer would produce
an entry for the new action something like the following

::

    ~ call Sally @k SmithJohn:Motion @s 2015-06-16 9:27am @e 12m

You can edit this action if you like, but it is already set up to bill
12 minutes to the "Motion" project for client "John Smith" for an
activity labeled "call Sally" and will appear as such in reports you
generate for this period, so you can just save it as it is. Do the same
with your other timers and you will have a complete record of time spent
by client, project and activity for the day.

The state of your active timers is saved whenever you quit etm using by
choosing *Quit* from the file menu or using the shortcut so that
whenever you restart etm on the same day, the active timers will be
restored.

If etm is running when a new day begins (midnight local time) or if you
stop etm and start it again on a later date, in-basket entries for each
of your active timers will be created in the relevant monthly file.
These entries will be exactly the same as if you had finished each of
the timers save for the use of ``$`` (in basket) rather than ``~``
(action) as the type character. You can edit or delete these as you
wish. If a timer is selected (displayed in the status bar), then a new
timer with the same name will be created for the new date but with zero
elapsed time. If the timer was running at midnight, then the new timer
will also be running. Idle time will automatically be reset to zero.

Sharing with other calendar applications
----------------------------------------

Both export and import are supported for files in iCalendar format in
ways that depend upon settings in ``etmtk.cfg``.

If an absolute path is entered for ``current_icsfolder``, for example,
then ``.ics`` files corresponding to the entries in ``calendars`` will
be created in this folder and updated as necessary. If there are no
entries in calendars, then a single file, ``all.ics``, will be created
in this folder and updated as necessary.

If an item is selected, then pressing Shift-X in the gui will export the
selected item in iCalendar format to ``icsitem_file``. If an item is not
selected, pressing Shift-X will export the active calendars in iCalendar
format to ``icscal_file``.

If ``icssync_folder`` is given, then files in this folder with the
extension ``.txt`` and ``.ics`` will automatically kept concurrent using
export to iCalendar and import from iCalendar. I.e., if the ``.txt``
file is more recent than than the ``.ics`` then the ``.txt`` file will
be exported to the ``.ics`` file. On the other hand, if the ``.ics``
file is more recent then it will be imported to the ``.txt`` file. In
either case, the contents of the file to be updated will be overwritten
with the new content and the last acess/modified times for both will be
set to the current time.

If ``ics_subscriptions`` is given, it should be a list of [URL, FILE]
tuples. The URL is a calendar subscription, e.g., for a Google Calendar
subscription the URL, FILE tuple would be something like:

::

      ['https://www.google.com/calendar/ical/.../basic.ics', 'personal/google.txt']
        

With this entry, pressing Shift-M in the gui would import the calendar
from the URL, convert it from ics to etm format and then write the
result to ``personal/google.txt`` in the etm data directory. Note that
this data file should be regarded as read-only since any changes made to
it will be lost with the next subscription update.

Finally, when creating a new item in the etm editor, you can paste an
iCalendar entry such as the following VEVENT:

::

    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//ForeTees//NONSGML v1.0//EN
    CALSCALE:GREGORIAN
    METHOD:PUBLISH
    BEGIN:VEVENT
    UID:1403607754438-11547@127.0.0.1-33
    DTSTAMP:20140624T070234
    DTSTART:20140630T080000
    SUMMARY:8:00 AM Tennis Reservation
    LOCATION:Governors Club
    DESCRIPTION: Player 1: ...
     
    URL:http://www1.foretees.com/governorsclub
    END:VEVENT
    END:VCALENDAR

When you press *Finish*, the entry will be converted to etm format

::

    ^ 8:00 AM Tennis Reservation @s 2014-06-30 8am 
    @d Player 1: ... 
    @z US/Eastern

and you can choose the file to hold it.

The following etm and iCalendar item types are supported:

-  export from etm:

   -  occasion to VEVENT without end time
   -  event (with or without extent) to VEVENT
   -  action to VJOURNAL
   -  note to VJOURNAL
   -  task to VTODO
   -  delegated task to VTODO
   -  task group to VTODO (one for each job)

-  import from iCalendar

   -  VEVENT without end time to occasion
   -  VEVENT with end time to event
   -  VJOURNAL to note
   -  VTODO to task

Tools
-----

Date and time calculator
~~~~~~~~~~~~~~~~~~~~~~~~

Enter an expression of the form ``x [+-] y`` where ``x`` is a date and
``y`` is either a date or a time period if ``-`` is used and a time
period if ``+`` is used. Both ``x`` and ``y`` can be followed by
timezones, e.g.,

::

     4/20 6:15p US/Central - 4/20 4:50p Asia/Shanghai:

     14h25m

or

::

     4/20 4:50p Asia/Shanghai + 14h25m US/Central:

     2014-04-20 18:15-0500

Fuzzy dates (other than relative date expressions using ``+`` or ``-``)
can be used to specify date entries. The local timezone is assumed when
none is given.

Available dates calculator
~~~~~~~~~~~~~~~~~~~~~~~~~~

Need to see a list of possible dates for a meeting? Get a list of busy
dates from each of the members of the group and then use an expression
of the form

::

    start; end; busy

where start and end are dates and busy is a comma separated list of the
busy dates or intervals for the members. E.g., if your group needs to
meet between 6/1 and 6/30 and the members indicate that they cannot meet
on 6/2, 6/14-6/22, 6/5-6/9, 6/11-6/15 or 6/17-6/29, then entering

::

    6/1; 6/30; 6/2, 6/14-6/22, 6/5-6/9, 6/11-6/15, 6/17-6/29

would give:

::

    Sun Jun 01
    Tue Jun 03
    Wed Jun 04
    Tue Jun 10
    Mon Jun 30

as the possible dates for the meeting.

Yearly calendar
~~~~~~~~~~~~~~~

Gives a display such as

::

          January 2014           February 2014             March 2014
      Mo Tu We Th Fr Sa Su    Mo Tu We Th Fr Sa Su    Mo Tu We Th Fr Sa Su
             1  2  3  4  5                    1  2                    1  2
       6  7  8  9 10 11 12     3  4  5  6  7  8  9     3  4  5  6  7  8  9
      13 14 15 16 17 18 19    10 11 12 13 14 15 16    10 11 12 13 14 15 16
      20 21 22 23 24 25 26    17 18 19 20 21 22 23    17 18 19 20 21 22 23
      27 28 29 30 31          24 25 26 27 28          24 25 26 27 28 29 30
                                                      31

           April 2014               May 2014               June 2014
      Mo Tu We Th Fr Sa Su    Mo Tu We Th Fr Sa Su    Mo Tu We Th Fr Sa Su
          1  2  3  4  5  6              1  2  3  4                       1
       7  8  9 10 11 12 13     5  6  7  8  9 10 11     2  3  4  5  6  7  8
      14 15 16 17 18 19 20    12 13 14 15 16 17 18     9 10 11 12 13 14 15
      21 22 23 24 25 26 27    19 20 21 22 23 24 25    16 17 18 19 20 21 22
      28 29 30                26 27 28 29 30 31       23 24 25 26 27 28 29
                                                      30

           July 2014              August 2014            September 2014
      Mo Tu We Th Fr Sa Su    Mo Tu We Th Fr Sa Su    Mo Tu We Th Fr Sa Su
          1  2  3  4  5  6                 1  2  3     1  2  3  4  5  6  7
       7  8  9 10 11 12 13     4  5  6  7  8  9 10     8  9 10 11 12 13 14
      14 15 16 17 18 19 20    11 12 13 14 15 16 17    15 16 17 18 19 20 21
      21 22 23 24 25 26 27    18 19 20 21 22 23 24    22 23 24 25 26 27 28
      28 29 30 31             25 26 27 28 29 30 31    29 30

          October 2014           November 2014           December 2014
      Mo Tu We Th Fr Sa Su    Mo Tu We Th Fr Sa Su    Mo Tu We Th Fr Sa Su
             1  2  3  4  5                    1  2     1  2  3  4  5  6  7
       6  7  8  9 10 11 12     3  4  5  6  7  8  9     8  9 10 11 12 13 14
      13 14 15 16 17 18 19    10 11 12 13 14 15 16    15 16 17 18 19 20 21
      20 21 22 23 24 25 26    17 18 19 20 21 22 23    22 23 24 25 26 27 28
      27 28 29 30 31          24 25 26 27 28 29 30    29 30 31

Left and right cursor keys move backward and forward a year at a time,
respectively, and pressing the Home key returns to the current year.

History of changes
~~~~~~~~~~~~~~~~~~

This requires that either *git* or *mercurial* is installed. If an item
is selected show a history of changes to the file that contains the
item. Otherwise show a history of changes for all etm data files. In
either case, choose an integer number of the most recent changes to show
or choose 0 to show all changes.

Calendars
---------

*etm* supports using the directory structure in your data directory to
create separate *calendars*. For example, my wife, *erp*, and I, *dag*,
separate personal and shared items with this structure:

::

    root etm data directory
        personal
            dag
            erp
        shared
            holidays
            birthdays
            events

Here, our etm configuration files are located in our home directories:

::

    ~dag/.etm/etmtk.cfg
    ~erp/.etm/etmtk.cfg

Both contain ``datadir`` entries specifying the common root data
directory mentioned above with these additional entries, respectively:

In ``~dag/.etm/etmtk.cfg``:

::

        calendars
        - [dag, true, personal/dag]
        - [erp, false, personal/erp]
        - [shared, true, shared]

In ``~erp/.etm/etmtk.cfg``:

::

        calendars
        - [erp, true, personal/erp]
        - [dag, false, personal/dag]
        - [shared, true, shared]

Thus, by default, both *dag* and *erp* see the entries from their
personal files as well as the shared entries and each can optionally
view the entries from the other's personal files as well. See the
`Preferences <#preferences>`__ for details on the ``calendars`` entry.

Note for Windows users. The path separator needs to be "escaped" in the
calendar paths, e.g., you should enter

::

     - [dag, true, personal\\dag]

instead of

::

     - [dag, true, personal\dag]

Data Organization
-----------------

*etm* offers many ways of organizing your data. Perhaps, the most
obvious is by *path*, i.e., the directory structure inside your data
directory. *Path View* presents your data using this organization and,
as noted above, calendars can be specified using this structure to allow
you to choose quickly the calendars whose items will appear in other etm
views as well.

The other hierarchical way of organizing your data uses the keywords you
specify in your items. *Keyword View* presents your data using this
organization. E.g.,

::

    - my task @k A:B:C
    - my other task

would appear in *Keyword View* as:

::

    A
        B
            C
                - my task
    ~ none ~
        - my other task

There are no hard and fast rules about how to use these hierarchies but
the goal is a system that makes complementary uses of path and keyword
and fits your needs. As with any filing system, planning and consistency
are paramount. For example, one pattern of use for a business might be
to use folders for departments and people and keywords for client and
project.

It is also possible to add one or more tags to items and use *Tag View*
to see the resulting organization. For example

::

    - item 1 @t red, white, blue
    - item 2 @t red @t white
    - item 3 @t white @t blue
    - item 4 @t red, blue
    - item 5 @t white

would appear in *Tag View* as

::

    blue
        - item 1
        - item 3
        - item 4
    red 
        - item 1
        - item 2
        - item 4
    white
        - item 1
        - item 2
        - item 3
        - item 5

A final important way of organizing your data is provided by *context*.
This is designed to support a GTD (Getting Things Done) common practice
where possible contexts includes things like phone, errands, email and
so forth. Undated tasks such as

::

    - pick up milk @c errands
    - call Saul @c phone
    - confirm schedule with Bob @c email

would appear *Agenda View* as

::

    Next
        email
            - confirm schedule with Bob
        errands
            - pick up milk
        phone
            - call Saul
            

When you are next checking email, running errands, using the phone or
whatever, you can check *Agenda View* to see what else might be
accomplished at the same time. Note that, unlike tags, items can have at
most a single context.

Colors
------

Versions of etm after 3.1.39 support custom settings for both foreground
(font) and background colors in the GUI. If a file named ``colors.cfg``
is found in the etm directory on startup, then the color settings in
this file will override the default color settings. If this file is not
found, then it will be created and populated with the default color
settings. This file can be opened for editing in etm using
*File/Open/Configuration file* from the main menu.

Example files for both dark and light backgrounds are available for
download and customization. You can also download ``colors.py``, set
your preferred background color inside this script and then run it to
see how the different font colors would appear against your chosen
background. See also the setting for ``style`` under Preferences.

Internationalization
--------------------

Versions of etm after 3.1.20 provide support for languages beyond
English.

End User
~~~~~~~~

If you, for example, are French and would like to use a version of etm
in which menu items and standard phrases are French then you need to
download the file ``fr_FR.mo`` either from `GitHub
locale <https://github.com/dagraham/locale>`__ or from `etmtk
languages <http://people.duke.edu/~dgraham/etmtk/languages>`__ and copy
it to the following location in your ``etmdir``:

::

    <your etmdir>
        languages
            fr_FR
                LC_MESSAGES
                    fr_FR.mo
                    

creating the corresponding directory structure when necessary. Be sure
to get the file with the ``.mo`` extension, not the one with the ``.po``
extension. Next you need to create a file named ``locale.cfg`` in your
``etmdir`` with the line:

::

    [[fr_FR, UTF-8], QLocale.French, QLocale.France]

perhaps modifying ``UTF-8`` to reflect your actual file encoding.

That's it! When you next start etm, ``locale.cfg`` will be read,
``fr_FR`` will be set as the desired locale and, if it can be found in
the specified directory, the translations in ``fr_FR.mo`` will be
loaded. Now, e.g, instead of *Agenda* you will see *Ordre du jour*.

Translator
~~~~~~~~~~

If you would like to assist in providing etm for a particular language,
the process is pretty simple. You will need to download the program
`poedit <https://poedit.net/>`__. A free version is available for all
major platforms.

In the etm source code, whenever a word or phrase appears that will be
seen by the user, it is wrapped in a special format using ``_()`` so
that, e.g., ``Agenda`` appears in the source code as ``_("Agenda")``,
``Today`` as ``_("Today")`` and so forth.

When etm is being prepared for distribution a program called *gettext*
is used to extract the ``_()`` entries from wherever they appear in the
source and copy them to specially formatted file called ``etm.pot``.
This file can be then be used in the open-source program *poedit* to
create a special translation files for different languages. This is how
``fr_FR.po`` was created, for example. Translation files are available
from the above sources for French (``fr_FR.po``), German (``de_DE.po``),
Spanish (``es_ES.po``) and Polish (``pl_PL.mo``). Alternatively,
``etm.pot`` is also available and you can use it to create whatever
translation files you wish.

When a ``.po`` translation file is opened in *poedit*, two columns are
displayed, the first lists the ``_()`` entries from the source code and
the second lists the corresponding translation. E.g.,

::

        Agenda          Ordre du jour
        Today           Aujourd’hui

Initially, of course, the translation column is empty and it is the job
of the translator to provide the translations. The *pro* version of
*poedit* (~ $20) provides a third column with likely guesses about the
appropriate translation. Most of the choices in ``fr_FR.po``, in fact,
came from accepting these best guesses since my knowledge of French is
miniscule.

Whenever a ``.po`` file is saved in *poedit*, a compiled version with
the extension ``.mo`` is automatically created. This compiled version is
the one actually used by etm and the only file that an end user needs.

When an end user has followed the steps given above to enable support
for a particular language, the actual translations will, of course be
limited to those with "second column choices". Extending the example
above, suppose the translator has omitted some items

::

        Agenda          Ordre du jour
        Yesterday
        Today           Aujourd’hui
        Tomorrow

Then whenever ``_("Agenda")`` appears in the source, it will effectively
be replaced by ``"Ordre du jour"`` and whenever ``_("Yesterday")``
appears, it will be replaced by ``"Yesterday"``. I.e., when a
translation is available, it will be used; otherwise, the original text
will be used.

A translator can thus do as much or as little as he or she pleases and
then send me the resulting ``.po`` file. I'll replace the current
on-line version with this updated version so the next translator can
improve upon prior results.
