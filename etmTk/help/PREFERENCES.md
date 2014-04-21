# Preferences

Configuration options are stored in a file named `etmtk.cfg` which, by default, belongs to the folder `.etm` in your home directory. When this file is edited in *etm* (Shift Ctrl-P), your changes become effective as soon as they are saved --- you do not need to restart *etm*. These options are listed below with illustrative entries and brief descriptions.

## Template expansions

The following template expansions can be used in `alert_displaycmd`, `alert_template`, `alert_voicecmd`, `email_template`, `sms_message` and `sms_subject` below.

### `!summary!`

the item's summary (this will be used as the subject of email and message alerts)

### `!start_date!`

the starting date of the event

### `!start_time!`

the starting time of the event

### `!time_span!`

the time span of the event (see below)

### `!alert_time!`

the time the alert is triggered

### `!time_left!`

the time remaining until the event starts

### `!when!`

the time remaining until the event starts as a sentence (see below)

### `!d!`

the item's `@d` (description)

### `!l!`

the item's `@l` (location)

The value of `!time_span!` depends on the starting and ending datetimes. Here are some examples:

- if the start and end *datetimes* are the same (zero extent): `10am Wed, Aug 4`

- else if the times are different but the *dates* are the same: `10am - 2pm Wed, Aug 4`

- else if the dates are different: `10am Wed, Aug 4 - 9am Thu, Aug 5`

- additionally, the year is appended if a date falls outside the current year:

        10am - 2pm Thu, Jan 3 2013
        10am Mon, Dec 31 - 2pm Thu, Jan 3 2013

Here are values of `!time_left!` and `!when!` for some illustrative periods:

- `2d3h15m`

        time_left : '2 days 3 hours 15 minutes'
        when      : '2 days 3 hours 15 minutes from now'

- `20m`

        time_left : '20 minutes'
        when      : '20 minutes from now'

- `0m`

        time_left : ''
        when      : 'now'

Note that 'now', 'from now', 'days', 'day', 'hours' and so forth are determined by the translation file in use.

## Options

### action_interval

    action_interval: 1

Every `action_interval` minutes, execute `action_timercmd` when the timer is running and `action_pausecmd` when the timer is paused. Choose zero to disable executing these commands.

### action_markups

    action_markups:
        default: 1.0
        mu1: 1.5
        mu2: 2.0

Possible markup rates to use for `@x` expenses in actions. An arbitrary number of rates can be entered using whatever labels you like. These labels can then be used in actions in the `@w` field so that, e.g.,

    ... @x 25.80 @w mu1 ...

in an action would give this expansion in an action template:

    !expense! = 25.80
    !charge! = 38.70

### action_minutes

    action_minutes: 6

Round action times up to the nearest `action_minutes` in action reports. Possible choices are 1, 6, 12, 15, 30 and 60. With 1, no rounding is done and times are reported as integer minutes. Otherwise, the prescribed rounding is done and times are reported as floating point hours.

### action_rates

    action_rates:
        default: 30.0
        br1: 45.0
        br2: 60.0

Possible billing rates to use for `@e` times in actions. An arbitrary number of rates can be entered using whatever labels you like. These labels can then be used in the `@v` field in actions so that, e.g., with `action_minutes: 6` then:

    ... @e 75m @v br1 ...

in an action would give these expansions in an action template:

    !hours! = 1.3
    !value! = 58.50

If the label `default` is used, the corresponding rate will be used when `@v` is not specified in an action.

Note that etm accumulates group totals from the `time` and `value` of individual actions. Thus

    ... @e 75m @v br1 ...
    ... @e 60m @v br2 ...

would aggregate to

    !hours!  = 2.3     (= 1.3 + 1)
    !value! = 118.50   (= 1.3 * 45.0 + 1 * 60.0)

### action_template

    action_template: '!hours!h) !label! (!count!)'

Used for action reports. With the above settings for `action_minutes` and `action_template`, a report might appear as follows:

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

Available template expansions for `action_template` include:

- `!label!`: the item or group label.

- `!count!`: the number of children represented in the reported item or group.

- `!minutes!:` the total time from `@e` entries in minutes rounded up using the setting for `action_minutes`.

- `!hours!`: if action_minutes = 1, the time in hours and minutes. Otherwise, the time in floating point hours.

- `!value!`: the billing value of the rounded total time. Requires an action entry such as `@v br1` and a setting for `action_rates`.

- `!expense!`: the total expense from `@x` entries.

- `!charge!`: the billing value of the total expense. Requires an action entry such as `@w mu1` and a setting for `action_markups`.

- `!total!`: the sum of `!value!` and `!charge!`.

Note: when aggregating amounts in action reports, billing and markup rates are applied first to times and expenses for individual actions and the resulting amounts are then aggregated. Similarly, when times are rounded up, the rounding is done for individual actions and the results are then aggregated.

### action_timer

    action_timer:
        paused: 'play ~/.etm/sounds/timer_paused.wav'
        running: 'play ~/.etm/sounds/timer_running.wav'

The command `running` is executed every `action_interval` minutes whenever the action timer is running and `paused` every minute when the action timer is paused.


### agenda

    agenda_days: 4,
    agenda_colors: 2,
    agenda_indent: 2,
    agenda_width1: 43,
    agenda_width2: 17,

Sets the number of days with scheduled items to display in agenda view and other parameters affecting the display in the CLI.


### alert_default

    alert_default: [m]

The alert or list of alerts to be used when an alert is specified for an item but the type is not given. Possible values for the list include:
- d: display (requires `alert_displaycmd`)
- m: message (using `alert_template`)
- s: sound (requires `alert_soundcmd`)
- v: voice (requires `alert_voicecmd`)


### alert_displaycmd

    alert_displaycmd: growlnotify -t !summary! -m '!time_span!'

The command to be executed when `d` is included in an alert. Possible template expansions are discussed at the beginning of this tab.

### alert_soundcmd

    alert_soundcmd: 'play ~/.etm/sounds/etm_alert.wav'

The command to execute when `s` is included in an alert. Possible template expansions are discussed at the beginning of this tab.

### alert_template

    alert_template: '!time_span!\n!l!\n\n!d!'

The template to use for the body of `m` (message) alerts. See the discussion of template expansions at the beginning of this tab for other possible expansion items.

### alert_voicecmd

    alert_voicecmd: say -v 'Alex' '!summary! begins !when!.'

The command to be executed when `v` is included in an alert. Possible expansions are are discussed at the beginning of this tab.

### alert_wakecmd

    alert_wakecmd: ~/bin/SleepDisplay -w

If given, this command will be issued to "wake up the display" before executing `alert_displaycmd`.

### ampm

    ampm: true

Use ampm times if true and twenty-four hour times if false. E.g., 2:30pm (true) or 14:30 (false).

### auto_completions

        auto_completions: ~/.etm/completions.cfg

The absolute path to the file to be used for autocompletions. Each line in the file provides a possible completion. E.g.

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

If you enter, for example, "@c" in the editor and press Ctrl-Space, a list of possible completions will pop up. Choose the one you want and press *Return* to insert it and close the popup.

Up and down arrow keys change the selection and either *Tab* or *Return* inserts the selection.

To edit the auto_completions file, press *Shift-Control-C* in the main window or from the main menu under *File/Open*.

### shared_completions

        shared_completions: ''

The absolute path to an optional file to be used to augment autocompletions. Each line in the file provides a possible completion.


### calendars

    calendars:
    - [dag, true, personal/dag]
    - [erp, false, personal/erp]
    - [shared, true, shared]

These are (label, default, path relative to `datadir`) tuples to be interpreted as separate calendars. Those for which default is `true` will be displayed as default calendars. E.g., with the `datadir` below, `dag` would be a default calendar and would correspond to the absolute path `/Users/dag/.etm/data/personal/dag`. With this setting, the calendar selection dialog would appear as follows:

When non-default calendars are selected, busy times in the "week view" will appear in one color for events from default calendars and in another color for events from non-default calendars.

**Only data files that belong to one of the calendar directories or their subdirectories will be accessible within etm.**

### current files

    current_htmlfile:  ''
    current_textfile:  ''
    current_indent:    3
    current_opts:      ''
    current_width1:    40
    current_width2:    17

If absolute file paths are entered for `current_textfile` and/or `current_htmlfile`, then these files will be created and automatically updated by etm as as plain text or html files, respectively. If `current_opts` is given then the file will contain a report using these options; otherwise the file will contain an agenda. Indent and widths are taken from these setting with other settings, including color, from *report* or *agenda*, respectively.

Hint: fans of geektool can use the shell command `cat <current_textfile>` to have the current agenda displayed on their desktops.

### datadir

    datadir: ~/.etm/data

All etm data files are in this directory.

### dayfirst

    dayfirst: false

If dayfirst is False, the MM-DD-YYYY format will have precedence over DD-MM-YYYY in an ambiguous date. See also `yearfirst`.

### edit_cmd

    edit_cmd: ~/bin/vim !file! +!line!

This command is used in the command line version of etm to create and edit items. When the command is expanded, `!file!` will be replaced with the complete path of the file to be edited and `!line!` with the starting line number in the file. If the editor will open a new window, be sure to include the command to wait for the file to be closed before returning, e.g., with vim:

    edit_cmd: ~/bin/gvim -f !file! +!line!

or with sublime text:

    edit_cmd: ~/bin/subl -n -w !file!:!line!


### email_template

    email_template: 'Time: !time_span!
    Locaton: !l!


    !d!'

Note that two newlines are required to get one empty line when the template is expanded. This template might expand as follows:

        Time: 1pm - 2:30pm Wed, Aug 4
        Location: Conference Room

        <contents of @d>

See the discussion of template expansions at the beginning of this tab for other possible expansion items.

### etmdir

    etmdir: ~/.etm

Absolute path to the directory for etm.cfg and other etm configuration files.

### encoding

    encoding: {file: utf-8, gui: utf-8, term: utf-8}

The encodings to be used for file IO, the GUI and terminal IO.

### filechange_alert

    filechange_alert: 'play ~/.etm/sounds/etm_alert.wav'

The command to be executed when etm detects an external change in any of its data files. Leave this command empty to disable the notification.

### fontsize

    fontsize: 13

Use this font size in the gui treeviews.

### freetimes

    freetimes:
        opening:  480  # 8*60 minutes after midnight = 8am
        closing: 1020  # 17*60 minutes after midnight = 5pm
        minimum:   30  # 30 minutes
        buffer:    15  # 15 minutes

Only display free periods between *opening* and *closing* that last at least *minimum* minutes and preserve at least *buffer* minutes between events. Note that each of these settings must be an *interger* number of minutes.

E.g., with the above settings and these busy periods:

    Busy periods in Week 16: Apr 14 - 20, 2014
    ------------------------------------------
    Mon 14: 10:30am-11:00am; 12:00pm-1:00pm; 5:00pm-6:00pm
    Tue 15: 9:00am-10:00am
    Wed 16: 8:30am-9:30am; 2:00pm-3:00pm; 5:00pm-6:00pm
    Thu 17: 11:00am-12:00pm; 6:00pm-7:00pm; 7:00pm-9:00pm
    Fri 18: 3:00pm-4:00pm; 5:00pm-6:00pm
    Sat 19: 9:00am-10:30am; 7:30pm-10:00pm

This would be the corresponding list of free periods:

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

When displaying free times in week view you will be prompted for the shortest period to display using the setting for *minimum* as the default.

Tip: Need to tell someone when you're free in a given week? Jump to that week in week view, press *Ctrl-F*, set the minimum period and then copy and paste the resulting list into an email.

### Mercurial commands

If *Mercurial* is installed on your system, then the default versions of the `hg` commands given below should work without modification. If you want to use another version control system, then enter the commands for your version control system. `{repo}` will be replaced with the internally generated name of the repository in `hg_commit` and `hg_history`, `{file}` with the internally generated file name in `hg_history`, `{mesg}` with the internally generated commit message in `hg_commit` and `{0}` with the name of the repository in `hg_init`.

#### hg_commit

The command to commit changes to the repository.

    hg_commit: hg commit -q -A -R {repo} -m '{mesg}'


#### hg_history

The command to show the history of changes for a particular data file.

    hg_history: 'hg log --style compact \
        --template `{rev}: {desc}\n` \
        -R {repo} -p {numchanges}'

#### hg_init

The command to initialize or create a repository.

    hg_init: hg init {0}

### iCalendar files

#### icscal_file

Pressing F8 in the gui main window will export the selected calendars in iCalendar format to this file.

    icscal_file: ~/.etm/etmcal.ics

#### icsitem_file

Pressing F8 in the gui detail view will export the selected item in iCalendar format to this file.

    icsitem_file: ~/.etm/etmitem.ics

### local_timezone

    local_timezone: US/Eastern

This timezone will be used as the default when a value for `@z` is not given in an item.

### monthly

    monthly: monthly

Relative path from `datadir`. With the settings above and for `datadir` the suggested location for saving new items in, say, October 2012, would be the file:

    ~/.etm/data/monthly/2012/10.txt

The directories `monthly` and `2012` and the file `10.txt` would, if necessary, be created. The user could either accept this default or choose a different file.

### outline_depth

    outline_depth: 2

The default outline depth to use when opening keyword, note or path view. Once a view is opened, use Ctrl-O to change the depth for that view.

### report

    report_begin:           '1'
    report_end:             '+1/1'
    report_colors:          2
    report_specifications:  ~/.etm/reports.cfg
    report_width:           54

Report begin and end are fuzzy parsed dates specifying the default period for reports that group by dates. Each line in the file specified by `report_specifications` provides a possible specification for a report. E.g.

    a MMM yyyy; k[0]; k[1:] -b -1/1 -e 1
    a k, MMM yyyy -b -1/1 -e 1
    c ddd MMM d yyyy
    c f

In the reports dialog these appear in the report specifications pop-up list. A specification from the list can be selected and, perhaps, modified or an entirely new specification can be entered. See the *Reports* tab for details. See also the *agenda* settings above.

### show_finished

    show_finished: 1

Show this many of the most recent completions of repeated tasks or, if 0, show all completions.

### smtp

    smtp_from: dnlgrhm@gmail.com
    smtp_id: dnlgrhm
    smtp_pw: **********
    smtp_server: smtp.gmail.com

Required settings for the smtp server to be used for email alerts.

### sms

    sms_message: '!summary!'
    sms_subject: '!time_span!'
    sms_from: dnlgrhm@gmail.com
    sms_pw:  **********
    sms_phone: 0123456789@vtext.com
    sms_server: smtp.gmail.com:587

Required settings for text messaging in alerts. Enter the 10-digit area code and number and mms extension for the mobile phone to receive the text message when no numbers are specified in the alert. The illustrated phone number is for Verizon. Here are the mms extensions for the major carriers:

    Alltel          @message.alltel.com
    AT&T            @txt.att.net
    Nextel          @messaging.nextel.com
    Sprint          @messaging.sprintpcs.com
    SunCom          @tms.suncom.com
    T-mobile        @tmomail.net
    VoiceStream     @voicestream.net
    Verizon         @vtext.com

### sundayfirst

    sundayfirst: false

The setting affects only the twelve month calendar display.

### weeks_after

    weeks_after: 52

In the schedule view, all non-repeating, dated items are shown. Additionally all repetitions of repeating items with a finite number of repetitions are shown. This includes 'list-only' repeating items and items with `&u` (until) or `&t` (total number of repetitions) entries. For repeating items with an infinite number of repetitions, those repetitions that occur within the first `weeks_after` weeks after the current week are displayed along with the first repetition after this interval. This assures that for infrequently repeating items such as voting for president, at least one repetition will be displayed.

### yearfirst

    yearfirst: true

If yearfirst is true, the YY-MM-DD format will have precedence over MM-DD-YY in an ambiguous date. See also `dayfirst`.
