.. _preferences-label:

Preferences
===========

Configuration options are stored in a file named ``etmtk.cfg`` which, by
default, belongs to the folder ``.etm`` in your home directory. When
this file is edited in *etm* (Shift Ctrl-P), your changes become
effective as soon as they are saved --- you do not need to restart
*etm*. These options are listed below with illustrative entries and
brief descriptions.

Template expansions
-------------------

The following template expansions can be used in ``alert_displaycmd``,
``alert_template``, ``alert_voicecmd``, ``email_template``,
``sms_message`` and ``sms_subject`` below.

-  ``!summary!``

the item's summary (this will be used as the subject of email and
message alerts)

-  ``!start_date!``

the starting date of the event

-  ``!start_time!``

the starting time of the event

-  ``!time_span!``

the time span of the event (see below)

-  ``!alert_time!``

the time the alert is triggered

-  ``!time_left!``

the time remaining until the event starts

-  ``!when!``

the time remaining until the event starts as a sentence (see below)

-  ``!next!``

how long before the starting time the next alert will be triggered

-  ``!next_alert!``

how long before the starting time the next alert will be triggered as a
sentence (see below)

-  ``!d!``

the item's ``@d`` (description)

-  ``!l!``

the item's ``@l`` (location)

The value of ``!next!`` for some illustrative cases:

-  The current alert is the last

   !next!: None

   !next\_alert!: 'This is the last alert.'

-  The next alert is at the start time

   !next!: 'at the start time'

   !next\_alert!: 'The next alert is at the start time.'

-  The next alert is 5 minutes before the start time:

   !next!: '5 minutes before the start time'

   !next\_alert!: 'The next alert is 5 minutes before the start time.'

The value of ``!time_span!`` depends on the starting and ending
datetimes. Here are some examples:

-  if the start and end *datetimes* are the same (zero extent):
   ``10am Wed, Aug 4``

-  else if the times are different but the *dates* are the same:
   ``10am - 2pm Wed, Aug 4``

-  else if the dates are different: ``10am Wed, Aug 4 - 9am Thu, Aug 5``

-  additionally, the year is appended if a date falls outside the
   current year:

   ::

       10am - 2pm Thu, Jan 3 2013
       10am Mon, Dec 31 - 2pm Thu, Jan 3 2013

Here are values of ``!time_left!`` and ``!when!`` for some illustrative
periods:

-  ``2d3h15m``

   ::

       time_left : '2 days 3 hours 15 minutes'
       when      : '2 days 3 hours 15 minutes from now'

-  ``20m``

   ::

       time_left : '20 minutes'
       when      : '20 minutes from now'

-  ``0m``

   ::

       time_left : ''
       when      : 'now'

Note that 'now', 'from now', 'days', 'day', 'hours' and so forth are
determined by the translation file in use.

Options
-------

action\_interval
~~~~~~~~~~~~~~~~

::

    action_interval: 1

Every ``action_interval`` minutes, execute ``action_timercmd`` when the
timer is running and ``action_pausecmd`` when the timer is paused.
Choose zero to disable executing these commands.

action\_keys
~~~~~~~~~~~~

::

    action_keys: "k"

When klone is used to create an action timer, copy the values of the
@-keys in this string from the item to the timer. With the default, "k",
klone will copy the item's @k entry, if there is one, in addition to the
summary when creating the action. Replacing "k", with "c" would cause
klone to copy the item's @c entry in addition to the summary. With "ck",
both the @c and @k entries would be copied. Any key that is valid for an
action can be used.

E.g., when

::

    - my task @c my context @k my keyword @t my tag

is selected, then the default would create a timer with the name
``my task @k my keyword``.

action\_markups
~~~~~~~~~~~~~~~

::

    action_markups:
        default: 1.0
        mu1: 1.5
        mu2: 2.0

Possible markup rates to use for ``@x`` expenses in actions. An
arbitrary number of rates can be entered using whatever labels you like.
These labels can then be used in actions in the ``@w`` field so that,
e.g.,

::

    ... @x 25.80 @w mu1 ...

in an action would give this expansion in an action template:

::

    !expense! = 25.80
    !charge! = 38.70

action\_minutes
~~~~~~~~~~~~~~~

::

    action_minutes: 6

Round action times up to the nearest ``action_minutes`` in action custom
view. Possible choices are 1, 6, 12, 15, 30 and 60. With 1, no rounding
is done and times are reported as integer minutes. Otherwise, the
prescribed rounding is done and times are reported as floating point
hours.

action\_rates
~~~~~~~~~~~~~

::

    action_rates:
        default: 30.0
        br1: 45.0
        br2: 60.0

Possible billing rates to use for ``@e`` times in actions. An arbitrary
number of rates can be entered using whatever labels you like. These
labels can then be used in the ``@v`` field in actions so that, e.g.,
with ``action_minutes: 6`` then:

::

    ... @e 75m @v br1 ...

in an action would give these expansions in an action template:

::

    !hours! = 1.3
    !value! = 58.50

If the label ``default`` is used, the corresponding rate will be used
when ``@v`` is not specified in an action.

Note that etm accumulates group totals from the ``time`` and ``value``
of individual actions. Thus

::

    ... @e 75m @v br1 ...
    ... @e 60m @v br2 ...

would aggregate to

::

    !hours!  = 2.3     (= 1.3 + 1)
    !value! = 118.50   (= 1.3 * 45.0 + 1 * 60.0)

action\_template
~~~~~~~~~~~~~~~~

::

    action_template: '!hours!h) !label! (!count!)'

Used for action type custom view. With the above settings for
``action_minutes`` and ``action_template``, a custom view might appear
as follows:

::

    27.5h) Client 1 (3)
        4.9h) Project A (1)
        15h) Project B (1)
        7.6h) Project C (1)
    24.2h) Client 2 (3)
        3.1h) Project D (1)
        21.1h) Project E (2)
            5.1h) Category a (1)
            16h) Category b (1)
    4.2h) Client 3 (1)
    8.7h) Client 4 (2)
        2.1h) Project F (1)
        6.6h) Project G (1)

Available template expansions for ``action_template`` include:

-  ``!label!``: the item or group label.

-  ``!count!``: the number of children represented in the reported item
   or group.

-  ``!minutes!:`` the total time from ``@e`` entries in minutes rounded
   up using the setting for ``action_minutes``.

-  ``!hours!``: if action\_minutes = 1, the time in hours and minutes.
   Otherwise, the time in floating point hours.

-  ``!value!``: the billing value of the rounded total time. Requires an
   action entry such as ``@v br1`` and a setting for ``action_rates``.

-  ``!expense!``: the total expense from ``@x`` entries.

-  ``!charge!``: the billing value of the total expense. Requires an
   action entry such as ``@w mu1`` and a setting for ``action_markups``.

-  ``!total!``: the sum of ``!value!`` and ``!charge!``.

Note: when aggregating amounts in action type custom view, billing and
markup rates are applied first to times and expenses for individual
actions and the resulting amounts are then aggregated. Similarly, when
times are rounded up, the rounding is done for individual actions and
the results are then aggregated.

action\_timer
~~~~~~~~~~~~~

::

    action_timer:
        paused: 'play ~/.etm/sounds/timer_paused.wav'
        running: 'play ~/.etm/sounds/timer_running.wav'

The command ``running`` is executed every ``action_interval`` minutes
whenever the action timer is running and ``paused`` every minute when
the action timer is paused.

agenda
~~~~~~

::

    agenda_days: 2
    agenda_colors: 2
    agenda_indent: 2
    agenda_omit: [ac, fn, ns]
    agenda_width1: 43
    agenda_width2: 17

Sets the number of days to display in agenda view and other parameters
affecting the display in the CLI. The colors setting only affects output
to current\_html. Items in agenda\_omit will not be displayed in the
agenda day list. Possible choices include:

-  ac: actions

-  by: begin by warnings

-  fn: finished tasks

-  ns: notes (dated)

-  oc: occasions

alert\_default
~~~~~~~~~~~~~~

::

    alert_default: [m]

The alert or list of alerts to be used when an alert is specified for an
item but the type is not given. Possible values for the list include:

-  d: display (requires ``alert_displaycmd``)

-  m: message (using ``alert_template``)

-  s: sound (requires ``alert_soundcmd``)

-  v: voice (requires ``alert_voicecmd``)

alert\_displaycmd
~~~~~~~~~~~~~~~~~

::

    alert_displaycmd: growlnotify -t !summary! -m '!time_span!'

The command to be executed when ``d`` is included in an alert. Possible
template expansions are discussed at the beginning of this tab.

alert\_soundcmd
~~~~~~~~~~~~~~~

::

    alert_soundcmd: 'play ~/.etm/sounds/etm_alert.wav'

The command to execute when ``s`` is included in an alert. Possible
template expansions are discussed at the beginning of this tab.

alert\_template
~~~~~~~~~~~~~~~

::

    alert_template: '!time_span!\n!l!\n\n!d!'

The template to use for the body of ``m`` (message) alerts. See the
discussion of template expansions at the beginning of this tab for other
possible expansion items.

alert\_voicecmd
~~~~~~~~~~~~~~~

::

    alert_voicecmd: say -v 'Alex' '!summary! begins !when!.'

The command to be executed when ``v`` is included in an alert. Possible
expansions are are discussed at the beginning of this tab.

alert\_wakecmd
~~~~~~~~~~~~~~

::

    alert_wakecmd: ~/bin/SleepDisplay -w

If given, this command will be issued to "wake up the display" before
executing ``alert_displaycmd``.

ampm
~~~~

::

    ampm: true

Use ampm times if true and twenty-four hour times if false. E.g., 2:30pm
(true) or 14:30 (false).

completions\_width
~~~~~~~~~~~~~~~~~~

::

    completions_width: 36

The width in characters of the auto completions popup window.

calendars
~~~~~~~~~

::

    calendars:
    - [dag, true, personal/dag]
    - [erp, false, personal/erp]
    - [shared, true, shared]

These are (label, default, path relative to ``datadir``) tuples to be
interpreted as separate calendars. Those for which default is ``true``
will be displayed as default calendars. E.g., with the ``datadir``
below, ``dag`` would be a default calendar and would correspond to the
absolute path ``/Users/dag/.etm/data/personal/dag``. With this setting,
the calendar selection dialog would appear as follows:

When non-default calendars are selected, busy times in the "week view"
will appear in one color for events from default calendars and in
another color for events from non-default calendars.

**Only data files that belong to one of the calendar directories or
their subdirectories will be accessible within etm.**

cfg\_files
~~~~~~~~~~

::

    cfg_files:
        - completions: []
        - reports:     []
        - users:       []

Each of the three list brackets can contain one or more comma separated
*absolute* file paths. Additionally, paths corresponding to active
calendars in the ``datadir`` directory are searched for files named
``completions.cfg``, ``reports.cfg`` and ``users.cfg`` and these are
processed in addition to the ones from ``cfg_files``.

Note. Windows users should place each absolute path in quotes and escape
backslashes, i.e., use ``\\`` anywhere ``\`` appears in a path.

-  Completions

   Each line in a completions file provides a possible completion when
   using the editor. E.g. with these completions

   ::

       @c computer
       @c home
       @c errands
       @c office
       @c phone
       @z US/Eastern
       @z US/Central
       @z US/Mountain
       @z US/Pacific
       dnlgrhm@gmail.com

   entering, for example, "@c" in the editor and pressing Ctrl-Space,
   would popup a list of possible completions. Choosing the one you want
   and pressing *Return* would insert it and close the popup.

   Up and down arrow keys change the selection and either *Tab* or
   *Return* inserts the selection.

-  Reports

   Each line in a reports file provides a possible reports
   specification. These are available when using the CLI ``m`` command
   and in the GUI custom view. See :ref:`Custom view <custom-label>` for
   details.

-  Users

   User files contain user (contact) information in a free form, text
   database. Each entry begins with a unique key for the person and is
   followed by detail lines each of which begins with a minus sign and
   contains some detail about the person that you want to record. Any
   detail line containing a colon should be quoted, e.g.,

   ::

       jbrown:
       - Brown, Joe
       - jbr@whatever.com
       - 'home: 123 456-7890'
       - 'birthday: 1978-12-14'
       dcharles:
       - Charles, Debbie
       - dch@sometime.com
       - 'cell: 456 789-0123'
       - 'spouse: Rebecca'

   Keys from this file are added to auto-completions so that if you
   type, say, ``@u jb`` and press *Ctrl-Space*, then ``@u jbrown`` would
   be offered for completion.

   If an item with the entry ``@u jbrown`` is selected in the GUI, you
   can press "u" to see a popup with the details:

   ::

       Brown, Joe
       jbr@whatever.com
       home: 123 456-7890
       birthday: 1978-12-14

countdown timer
~~~~~~~~~~~~~~~

::

    countdown_command: ''
    countdown_minutes: 10

If ``countdown_command`` is given, it will be executed when the timer
expires; otherwise a beep will be sounded. The default number of minutes
for a countdown is given by ``countdown_minutes``. When a timer is
active, the time that the timer will expire is displayed in the status
bar using the format -H:M:S(am/pm). When a countdown and a snooze timer
are both active, the one that will expire first is displayed in the
status bar.

current files
~~~~~~~~~~~~~

::

    current_htmlfile:  ''
    current_textfile:  ''
    current_icsfolder:  ''
    current_indent:    3
    current_opts:      ''
    current_width1:    40
    current_width2:    17

If absolute file paths are entered for ``current_textfile`` and/or
``current_htmlfile``, then these files will be created and automatically
updated by etm as as plain text or html files, respectively. If
``current_opts`` is given then the file will contain a report using
these options; otherwise the file will contain an agenda. Indent and
widths are taken from these setting with other settings, including
color, from *report* or *agenda*, respectively.

If an absolute path is entered for ``current_icsfolder``, then ics files
corresponding to the entries in ``calendars`` will be created in this
folder and updated as necessary. If there are no entries in calendars,
then a single file, ``all.ics``, will be created in this folder and
updated as necessary.

Hint: fans of geektool can use the shell command
``cat <current_textfile>`` to have the current agenda displayed on their
desktops.

datadir
~~~~~~~

::

    datadir: ~/.etm/data

All etm data files are in this directory.

dayfirst
~~~~~~~~

::

    dayfirst: false

If dayfirst is False, the MM-DD-YYYY format will have precedence over
DD-MM-YYYY in an ambiguous date. See also ``yearfirst``.

details\_rows
~~~~~~~~~~~~~

::

    details_rows: 4

The number of rows to display in the bottom, details panel of the main
window.

display\_idletime
~~~~~~~~~~~~~~~~~

::

    display_idletime: True

Show idle time in the status bar by default if True. Display can be
toggled on and off in the File/Timer menu. Idle time is accumulated when
there are are one or more active timers and none are running.

early\_hour
~~~~~~~~~~~

::

    early_hour: 6

When scheduling an event or action with a starting time that begins
before this hour, append the query "Is \_\_ the starting time you
intended?" to the confirmation. Use 0 to disable this warning
altogether. The default, 6, will warn for starting times *before* 6am.

edit\_cmd
~~~~~~~~~

::

    edit_cmd: ~/bin/vim !file! +!line!

This command is used in the command line version of etm to create and
edit items. When the command is expanded, ``!file!`` will be replaced
with the complete path of the file to be edited and ``!line!`` with the
starting line number in the file. If the editor will open a new window,
be sure to include the command to wait for the file to be closed before
returning, e.g., with vim:

::

    edit_cmd: ~/bin/gvim -f !file! +!line!

or with sublime text:

::

    edit_cmd: ~/bin/subl -n -w !file!:!line!

email\_template
~~~~~~~~~~~~~~~

::

    email_template: 'Time: !time_span!
    Locaton: !l!


    !d!'

Note that two newlines are required to get one empty line when the
template is expanded. This template might expand as follows:

::

        Time: 1pm - 2:30pm Wed, Aug 4
        Location: Conference Room

        <contents of @d>

See the discussion of template expansions at the beginning of this tab
for other possible expansion items.

etmdir
~~~~~~

::

    etmdir: ~/.etm

Absolute path to the directory for etmtk.cfg and other etm configuration
files.

exportdir
~~~~~~~~~

::

    exportdir: ~/.etm

Absolute path to the directory for exported CSV files.

encoding
~~~~~~~~

::

    encoding: {file: utf-8, gui: utf-8, term: utf-8}

The encodings to be used for file IO, the GUI and terminal IO.

filechange\_alert
~~~~~~~~~~~~~~~~~

::

    filechange_alert: 'play ~/.etm/sounds/etm_alert.wav'

The command to be executed when etm detects an external change in any of
its data files. Leave this command empty to disable the notification.

fontsize\_fixed
~~~~~~~~~~~~~~~

::

    fontsize_fixed: 0

Use this font size in the details panel, editor and reports. Use 0 to
keep the system default.

fontsize\_tree
~~~~~~~~~~~~~~

::

    fontsize_tree: 0

Use this font size in the gui treeviews. Use 0 to keep the system
default.

Tip: Leave the font sizes set to 0 and run etm with logging level 2 to
see the system default sizes.

freetimes
~~~~~~~~~

::

    freetimes:
        opening:  480  # 8*60 minutes after midnight = 8am
        closing: 1020  # 17*60 minutes after midnight = 5pm
        minimum:   30  # 30 minutes
        buffer:    15  # 15 minutes

Only display free periods between *opening* and *closing* that last at
least *minimum* minutes and preserve at least *buffer* minutes between
events. Note that each of these settings must be an *interger* number of
minutes.

E.g., with the above settings and these busy periods:

::

    Busy periods in Week 16: Apr 14 - 20, 2014
    ------------------------------------------
    Mon 14: 10:30am-11:00am; 12:00pm-1:00pm; 5:00pm-6:00pm
    Tue 15: 9:00am-10:00am
    Wed 16: 8:30am-9:30am; 2:00pm-3:00pm; 5:00pm-6:00pm
    Thu 17: 11:00am-12:00pm; 6:00pm-7:00pm; 7:00pm-9:00pm
    Fri 18: 3:00pm-4:00pm; 5:00pm-6:00pm
    Sat 19: 9:00am-10:30am; 7:30pm-10:00pm

This would be the corresponding list of free periods:

::

    Free periods in Week 16: Apr 14 - 20, 2014
    ------------------------------------------
    Mon 14: 8:00am-10:15am; 11:15am-11:45am; 1:15pm-4:45pm
    Tue 15: 8:00am-8:45am; 10:15am-5:00pm
    Wed 16: 9:45am-1:45pm; 3:15pm-4:45pm
    Thu 17: 8:00am-10:45am; 12:15pm-5:00pm
    Fri 18: 8:00am-2:45pm; 4:15pm-4:45pm
    Sat 19: 8:00am-8:45am; 10:45am-5:00pm
    Sun 20: 8:00am-5:00pm
    ----------------------------------------
    Only periods of at least 30 minutes are displayed.

When displaying free times in week view you will be prompted for the
shortest period to display using the setting for *minimum* as the
default.

Tip: Need to tell someone when you're free in a given week? Jump to that
week in week view, press *Ctrl-F*, set the minimum period and then copy
and paste the resulting list into an email.

iCalendar settings
~~~~~~~~~~~~~~~~~~

icscal\_file
^^^^^^^^^^^^

If an item is not selected, pressing Shift-X in the gui will export the
active calendars in iCalendar format to this file.

::

    icscal_file: ~/.etm/etmcal.ics

icsitem\_file
^^^^^^^^^^^^^

If an item is selected, pressing Shift-X in the gui will export the
selected item in iCalendar format to this file.

::

    icsitem_file: ~/.etm/etmitem.ics

icssync\_folder
^^^^^^^^^^^^^^^

::

    icssync_folder: ''

A relative path from ``etmdata`` to a folder. If given, files in this
folder with the extension ``.txt`` and ``.ics`` will automatically kept
concurrent using export to iCalendar and import from iCalendar. I.e., if
the ``.txt`` file is more recent than than the ``.ics`` then the
``.txt`` file will be exported to the ``.ics`` file. On the other hand,
if the ``.ics`` file is more recent then it will be imported to the
``.txt`` file. In either case, the contents of the file to be updated
will be overwritten with the new content and the last acess/modified
times for both will be set to the current time.

Note that the calendar application you use to modify the ``.ics`` file
will impose restrictions on the subsequent content of the ``.txt`` file.
E.g., if the ``.txt`` file has a note entry, then this note will be
exported by etm as a VJOURNAL entry to the ``.ics`` file. But VJOURNAL
entries are not be recognized by many (most) calendar apps. When
importing this file to such an application, the note will be omitted and
thus will be missing from the ``.ics`` file after the next export from
the application. The note will then be missing from the ``.txt`` file as
well after the next automatic update. Restricting the content to events
should be safe with with any calendar application.

Additionally, if an absolute path is entered for ``current_icsfolder``,
then ics files corresponding to the entries in ``calendars`` will be
created in this folder and updated as necessary. If there are no entries
in calendars, then a single file, ``all.ics``, will be created in this
folder and updated as necessary.

ics\_subscriptions
^^^^^^^^^^^^^^^^^^

::

    ics_subscriptions: []

A list of (URL, path) tuples for automatic updates. The URL is a
calendar subscription, e.g., for a Google Calendar subscription the
entry might be something like:

::

    ics_subscriptions:
        - ['https://www.google.com/calendar/ical/.../basic.ics', 'personal/dag/google.txt']
        

With this entry, pressing Shift-M in the gui would import the calendar
from the URL, convert it from ics to etm format and then write the
result to ``personal/google.txt`` in the etm data directory. Note that
this data file should be regarded as read-only since any changes made to
it will be lost with the next subscription update.

local\_timezone
~~~~~~~~~~~~~~~

::

    local_timezone: US/Eastern

This timezone will be used as the default when a value for ``@z`` is not
given in an item.

message\_last
~~~~~~~~~~~~~

::

    message_last: 0

The number of seconds to display the message alert for an item before
closing it when it is the last. With 0, the message dialog will be kept
open indefinitely.

message\_next
~~~~~~~~~~~~~

::

    message_next: 0

The number of seconds to display the message alert for an item before
closing it when it is not the last alert. With 0, the message dialog
will be kept open indefinitely.

monthly
~~~~~~~

::

    monthly: monthly

Relative path from ``datadir``. With the settings above and for
``datadir`` the suggested location for saving new items in, say, October
2012, would be the file:

::

    ~/.etm/data/monthly/2012/10.txt

The directories ``monthly`` and ``2012`` and the file ``10.txt`` would,
if necessary, be created. The user could either accept this default or
choose a different file.

outline\_depth
~~~~~~~~~~~~~~

::

    outline_depth: 2

The default outline depth to use when opening keyword, note, path or tag
view. Once any view is opened, use Ctrl-O to change the depth for that
view.

prefix
~~~~~~

::

    prefix: "\n  "
    prefix_uses: "rj+-tldm"

Apply ``prefix`` (whitespace only) to the @keys in ``prefix_uses`` when
displaying and saving items. The default would cause the selected
elements to begin on a newline and indented by two spaces. E.g.,

::

    + summary @s 2014-05-09 12am @z US/Eastern
      @m memo
      @j job 1 &f 20140510T1411;20140509T0000 &q 1
      @j job 2 &f 20140510T1412;20140509T0000 &q 2
      @j job 3 &q 3
      @d description

report
~~~~~~

::

    report_begin:           '1'
    report_end:             '+1/1'
    report_colors:          2
    report_width1:          61
    report_width2:          19

Report begin and end are fuzzy parsed dates specifying the default
period for reports that group by dates. Each line in the file specified
by ``report_specifications`` provides a possible specification for a
report. E.g.

::

    a MMM yyyy; k[0]; k[1:] -b -1/1 -e 1
    a k, MMM yyyy -b -1/1 -e 1
    c ddd MMM d yyyy
    c f

In custom view these appear in the report specifications pop-up list. A
specification from the list can be selected and, perhaps, modified or an
entirely new specification can be entered. See :ref:`Custom
view <custom-label>` for details. See also the `agenda <#agenda>`__
settings above.

retain\_ids
~~~~~~~~~~~

::

    retain_ids: false

If true, the unique ids that etm associates with items will be written
to the data files and retained between sessions. If false, new ids will
be generated for each session.

Retaining ids enables etm to avoid duplicates when importing and
exporting iCalendar files.

show\_finished
~~~~~~~~~~~~~~

::

    show_finished: 1

Show this many of the most recent completions of repeated tasks or, if
0, show all completions.

smtp
~~~~

::

    smtp_from: dnlgrhm@gmail.com
    smtp_id: dnlgrhm
    smtp_pw: **********
    smtp_server: smtp.gmail.com

Required settings for the smtp server to be used for email alerts.

sms
~~~

::

    sms_message: '!summary!'
    sms_subject: '!time_span!'
    sms_from: dnlgrhm@gmail.com
    sms_pw:  **********
    sms_phone: 0123456789@vtext.com
    sms_server: smtp.gmail.com:587

Required settings for text messaging in alerts. Enter the 10-digit area
code and number and mms extension for the mobile phone to receive the
text message when no numbers are specified in the alert. The illustrated
phone number is for Verizon. Here are the mms extensions for the major
carriers:

::

    Alltel          @message.alltel.com
    AT&T            @txt.att.net
    Nextel          @messaging.nextel.com
    Sprint          @messaging.sprintpcs.com
    SunCom          @tms.suncom.com
    T-mobile        @tmomail.net
    VoiceStream     @voicestream.net
    Verizon         @vtext.com

snooze
~~~~~~

::

    snooze_command: ''
    snooze_minutes: 10

If ``snooze_command`` is given, it will be executed when the timer
expires; otherwise a beep will be sounded. The default number of minutes
for a snooze is given by ``snooze_minutes``. When a snooze timer is
active, the time that the timer will expire is displayed in the status
bar in the format +H:M:S(am/pm). When a countdown and a snooze timer are
both active, the one that will expire first is displayed in the status
bar.

style
~~~~~

::

    style: default

The style to be used for Tk/Tcl widgets. Options for linux include clam,
alt, default and classic. Options for OSX add aqua. Note that aqua does
not support background colors for buttons and may not be suitable with
darker background colors.

sundayfirst
~~~~~~~~~~~

::

    sundayfirst: false

The setting affects only the twelve month calendar display.

update\_minutes
~~~~~~~~~~~~~~~

::

    update_minutes: 15

Update ``current_html``, ``current_text`` and the files in
``icssync_folder`` when the number of minutes past the hour modulo
``update_minutes`` is equal to zero. I.e. with the default, the update
would occur on the hour and at 15, 30 and 45 minutes past the hour.
Acceptable settings are integers between 1 and 59. Note that with a
setting greater than or equal to 30, the update will occur only twice
each hour.

vcs\_settings
~~~~~~~~~~~~~

::

    vcs_settings:
      command: ''
      commit: ''
      dir: ''
      file: ''
      history: ''
      init: ''
      limit: ''

These settings are ignored unless the setting for ``vcs_system`` below
is either ``git`` or ``mercurial``.

Default values will be provided for these settings based on the choice
of ``vcs_system`` below. Any of the settings that you define here will
overrule the defaults.

Here, for example, are the default values of these settings for git
under OS X:

::

    vcs_settings:
        command: '/usr/bin/git --git-dir {repo} --work-dir {work}'
        commit: '/usr/bin/git --git-dir {repo} --work-dir {work} add */\*.txt
            && /usr/bin/git --git-dir {repo} --work-dir {work} commit -a -m "{mesg}"'
        dir: '.git'
        file: ''
        history: '/usr/bin/git -git-dir {repo} --work-dir {work} log
            --pretty=format:"- %ar: %an%n%w(70,0,4)%s" -U1  {numchanges}
                {file}'
        init: '/usr/bin/git init {work}; /usr/bin/git -git-dir {repo}
            --work-dir {work} add */\*.txt; /usr/bin/git-git-dir {repo}
                --work-dir {work} commit -a -m "{mesg}"'
        limit: '-n'

In these settings, ``{mesg}`` will be replaced with an internally
generated commit message, ``{numchanges}`` with an expression that
depends upon ``limit`` that determines how many changes to show and,
when a file is selected, ``{file}`` with the corresponding path. If
``~/.etm/data`` is your etm datadir, the ``{repo}`` would be replaced
with ``~/.etm/data/.git`` and {work} with ``~/.etm/data``.

Leave these settings empty to use the defaults.

vcs\_system
~~~~~~~~~~~

::

    vcs_system: ''

This setting must be either ``''`` or ``git`` or ``mercurial``.

If you specify either git or mercurial here (and have it installed on
your system), then etm will automatically commit any changes you make to
any of your data files. The history of these changes is available in the
GUI with the show changes command (*Ctrl-H*) and you can, of course, use
any git or mercurial commands in your terminal to, for example, restore
a previous version of a file.

weeks\_after
~~~~~~~~~~~~

::

    weeks_after: 52

In the day view, all non-repeating, dated items are shown. Additionally
all repetitions of repeating items with a finite number of repetitions
are shown. This includes 'list-only' repeating items and items with
``&u`` (until) or ``&t`` (total number of repetitions) entries. For
repeating items with an infinite number of repetitions, those
repetitions that occur within the first ``weeks_after`` weeks after the
current week are displayed along with the first repetition after this
interval. This assures that for infrequently repeating items such as
voting for president, at least one repetition will be displayed.

yearfirst
~~~~~~~~~

::

    yearfirst: true

If yearfirst is true, the YY-MM-DD format will have precedence over
MM-DD-YY in an ambiguous date. See also ``dayfirst``.
