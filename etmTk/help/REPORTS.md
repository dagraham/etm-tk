*etm* supports creating, printing and exporting reports. Either click on the report icon in the main window or press *Control-R* to open the report dialog.

A *report specification* is created by entering a report *type character* followed by a *groupby setting* and, perhaps, by one or more *report options*. Together, the type character, groupby setting and options determine which items will appear in the report and how they will be organized and displayed.

# Report types

There are two possible report type characters, *a* and *c*:

## **a**: action report.

A report of expenditures of time and money recorded in actions with output formatted using `action_template` computations and expansions. See Help/Preferences for further details about the role of `action_template` in formatting action report output. E.g., with this setting in `etmtk.cfg`:

    action_template: '!hours!h) !label! (!count!)'

a report might appear as follows:

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

## **c**: composite report.

Any item types but without `action_template` computations and expansions.

You can select a report specification from a list of saved specifications, modify an existing specification or create an entirely new specification. Clicking on the *create report* icon or pressing *Control-R* will create a report based on the current specification.

When you edit an existing specification, the background color of the entry field will change to yellow to indicate that this is a new, as yet unsaved specification. Pressing *Return* will add the new specification temporarily to the list without affecting the original specification.

If the current specification has been modified, then deleting it by clicking on the *delete* icon or pressing *Control-D* will replace the modified specification with the original. If the current specification has not been modified, then deleting it will temporarily remove it from the list.

When temporary changes have been made to the list, the *save* button will be enabled and you can either click on this button or press *Control-S* to save the changes. If you attempt to close the reports dialog while there are unsaved changes, you will be given the opportunity to save them.

# groupby

A semicolon separated list that determines how items will be grouped and sorted. Possible elements include *date specifications* and elements from

c
:   context
f
:   file path
k
:   keyword
t
:   tag
u
:   user

A *date specification* is a combination of one or more of the following:

yy
:   2-digit year
yyyy
:   4-digit year
M
:   month: 1 - 12
MM
:   month: 01 - 12
MMM
:   locale specific abbreviated month name: Jan - Dec
MMMM
:   locale specific month name: January - December
d
:   month day: 1 - 31
dd
:   month day: 01 - 31
ddd
:   locale specific abbreviated week day: Mon - Sun
dddd
:   locale specific week day: Monday - Sunday

For example, `c ddd, MMM d yyyy` would group by year, month and day together to give output such as

    Fri, Apr 1 2011
        items for April 1
    Sat, Apr 2 2011
        items for April 2
    ...

As another example, `c t -t tag 1, !tag 3` would group by tag showing items that have a tag matching `tag 1` but not one matching `tag 3`.

With the heirarchial elements, file path and keyword, it is possible to use parts of the element as well as the whole. Consider, for example, the file path `A/B/C` with the components `[A, B, C]`. Then for this file path:

    f[0] = A
    f[:2] = A/B
    f[2:] = C
    f = A/B/C

Suppose that keywords have the format `client:project`. Then grouping by year and month, then client and finally project to give output such as

    report: a MMM yyyy; u; k[0]; k[1] -b 1 -e +1/1

    13.1) Feb 2014
       6.3) agent 1
          1.3) client 1
             1.3) project 2
                1.3) Activity 12
          5) client 2
             4.5) project 1
                4.5) Activity 21
             0.5) project 2
                0.5) Activity 22
       6.8) agent 2
          2.2) client 1
             2.2) project 2
                2.2) Activity 13
          4.6) client 2
             3.9) project 1
                3.9) Activity 23
             0.7) project 2
                0.7) Activity 23

Items that are missing an element specified in `groupby` will be omitted from the output. E.g., undated tasks and notes will be omitted when a date specification is included, items without keywords will be omitted when `k` is included and so forth.

When a date specification is not included in `groupby`, undated notes and tasks will be potentially included, but only those instances of dated items that correspond to the *relevant datetime* of the item of the item will be included, where the *relevant datetime* is the past due date for any past due tasks, the starting datetime for any non-repeating item and the datetime of the next instance for any repeating item.

Within groups, items are automatically sorted by date, type and time.

# options

Report options are listed below. Report types `c` supports all options except `-d`. Report type `a` supports all options except `-o` and `-h`.

## -b  BEGIN_DATE

Fuzzy parsed date. Limit the display of dated items to those with datetimes falling *on or after* this datetime. Relative day and month expressions can also be used so that, for example, `-b -14` would begin 14 days before the current date and `-b -1/1` would begin on the first day of the previous month. It is also possible to add (or subtract) a time period from the fuzzy date, e.g., `-b mon + 7d` would begin with the second Monday falling on or after today. Default: None.

## -c CONTEXT

Regular expression. Limit the display to items with contexts matching CONTEXT (ignoring case). Prepend an exclamation mark, i.e., use !CONTEXT rather than CONTEXT, to limit the display to items which do NOT have contexts matching CONTEXT.

## -d DEPTH

The default, `-d 0`, includes all outline levels. Use `-d 1` to include only level 1, `-d 2` to include levels 1 and 2 and so forth.

For example, modifying the report above by adding `-d 3` would give the
following:

    report: a MMM yyyy; u; k[0]; k[1] -b 1 -e +1/1 -d 3

    13.1) Feb 2014
       6.3) agent 1
          1.3) client 1
          5) client 2
       6.8) agent 2
          2.2) client 1
          4.6) client 2

## -e END_DATE

Fuzzy parsed date. Limit the display of dated items to those with datetimes falling *before* this datetime. As with BEGIN_DATE relative month expressions can be used so that, for example, `-b -1/1  -e 1` would include all items from the previous month. As with `-b`, period strings can be appended, e.g., `-b mon -e mon + 7d` would include items from the week that begins with the first Monday falling on or after today. Default: None.

## -f FILE

Regular expression. Limit the display to items from files whose paths match FILE (ignoring case). Prepend an exclamation mark, i.e., use !FILE rather than FILE, to limit the display to items from files whose path does NOT match FILE.

## -h HUE

0, 1 or 2. `-h 2` uses all possible colors for leaf fonts, `-h 1` uses red for past due items and black for everything else and `-h 0` uses black for everything. The default is taken from the setting for `colors` in `emt.cfg`.

## -k KEYWORD

Regular expression. Limit the display to items with contexts matching KEYWORD (ignoring case). Prepend an exclamation mark, i.e., use !KEYWORD rather than KEYWORD, to limit the display to items which do NOT have keywords matching KEYWORD.

## -l LOCATION

Regular expression. Limit the display to items with location matching LOCATION (ignoring case). Prepend an exclamation mark, i.e., use !LOCATION rather than LOCATION, to limit the display to items which do NOT have a location that matches LOCATION.

## -o OMIT

String. Show/hide a)ctions, d)elegated tasks, e)vents, g)roup tasks, n)otes, o)ccasions and/or other t)asks. For example, `-o on` would show everything except occasions and notes and `-o !on` would show only occasions and notes.

## -s SUMMARY

Regular expression. Limit the display to items containing SUMMARY (ignoring case) in the item summary. Prepend an exclamation mark, i.e., use !SUMMARY rather than SUMMARY, to limit the display to items which do NOT contain SUMMARY in the summary.

## -t TAGS

Comma separated list of case insensitive regular expressions. E.g., use

    -t tag1, !tag2

to display items with one or more tags that match 'tag1' but none that match 'tag2'.

## -u USER

Regular expression. Limit the display to items with user matching USER (ignoring case). Prepend an exclamation mark, i.e., use !USER rather than USER, to limit the display to items which do NOT have a user that matches USER.

## -w WIDTH1

Integer. Limit the first column display width to this number of characters. Default: `report_width1` in etm.cfg.

## -W WIDTH2

Integer. Limit the second column display width to this number of characters. Default: `report_width2` in etm.cfg.
