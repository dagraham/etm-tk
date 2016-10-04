Custom view
===========

You can create a custom display of your items using either the *custom
view* in the GUI or the "c" command in the CLI. In both cases, you enter
a specification that determines which items will be displayed and how
they will be grouped and sorted.

A view *specification* begins with a *type character*, either ``a`` or
``c``, followed by a *groupby setting* and then, perhaps, by one or more
view *options*.

View type
---------

-  **a**: action

   Actions only. Expenditures of time and money recorded in *actions*
   with output formatted using ``action_template`` computations and
   expansions. See `Preferences <#preferences>`__ for further details
   about the role of ``action_template`` in formatting actions output.
   Note that only *actions* are included in this view and, by default,
   all actions in your active calendars will be included.

-  **c**: composite

   Any item types, including actions, but without ``action_template``
   computations and expansions. Note that only unfinished tasks and
   unfinished instances of repeating tasks will be displayed. By
   default, all items from your active calendars will be included.

Groupby setting
---------------

A semicolon separated list that determines how items will be grouped and
sorted. Possible elements include elements from

-  c: context

-  f: file path

-  k: keyword

-  l: location

-  t: tag

-  u: user

and/or a *date specifications* where a *date specification* is either

-  w: week number

or a combination of one or more of the following:

-  yy: 2-digit year

-  yyyy: 4-digit year

-  MM: month: 01 - 12

-  MMM: locale specific abbreviated month name: Jan - Dec

-  MMMM: locale specific month name: January - December

-  dd: month day: 01 - 31

-  ddd: locale specific abbreviated week day: Mon - Sun

-  dddd: locale specific week day: Monday - Sunday

Note that the groupby specification affects which items will be
displayed. Items that are missing an element specified in ``groupby``
will be omitted from the output. E.g., undated tasks and notes will be
omitted when a date specification is included, items without keywords
will be omitted when ``k`` is included and so forth. The latter behavior
depends upon the value of the `-m MISSING <#m-missing>`__ option.

When a date specification is not included in the groupby setting,
undated notes and tasks will be potentially included, but only those
instances of dated items that correspond to the *relevant datetime* of
the item of the item will be included, where the *relevant datetime* is
the past due date for any past due tasks, the starting datetime for any
non-repeating item and the datetime of the next instance for any
repeating item.

Within groups, items are automatically sorted by date, type and time.

Groupby examples
----------------

For example, the specification ``c ddd, MMM dd yyyy`` would group by
year, month and day together to give output such as

::

    Fri, Apr 1 2011
        items for April 1
    Sat, Apr 2 2011
        items for April 2
    ...

On the other hand, the specification ``a w; u; k[0]; k[1:]`` would group
by week number, user and keywords to give output such as

::

    13.1) 2014 Week 14: Mar 31 - Apr 6
       6.3) agent 1
          1.3) client 1
             1.3) project 2
                1.3) Activity (12)
          5) client 2
             4.5) project 1
                4.5) Activity (21)
             0.5) project 2
                0.5) Activity (22)
       6.8) agent 2
          2.2) client 1
             2.2) project 2
                2.2) Activity (13)
          4.6) client 2
             3.9) project 1
                3.9) Activity (23)
             0.7) project 2
                0.7) Activity (23)

With the heirarchial elements, file path and keyword, it is possible to
use parts of the element as well as the whole. Consider, for example,
the file path ``A/B/C`` with the components ``[A, B, C]``. Then for this
file path:

::

    f[0] = A
    f[:2] = A/B
    f[2:] = C
    f = A/B/C

Suppose that keywords have the format ``client:project``. Then grouping
by year and month, then client and finally project to give output such
as

::

    specification: a MMM yyyy; u; k[0]; k[1] -b 1 -e +1/1

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

View Options
------------

View options are listed below. View type ``c`` supports all options
except ``-d``. Type ``a`` supports all options except ``-o``. These
options can be used to further limit which items are displayed.

-b BEGIN\_DATE
~~~~~~~~~~~~~~

Fuzzy parsed date. When a date specification is provided, limit the
display of dated items to those with datetimes falling *on or after*
this datetime. Relative day and month expressions can also be used so
that, for example, ``-b -14`` would begin 14 days before the current
date and ``-b -1/1`` would begin on the first day of the previous month.
It is also possible to add (or subtract) a time period from the fuzzy
date, e.g., ``-b mon + 7d`` would begin with the second Monday falling
on or after today. Default: None.

-c CONTEXT
~~~~~~~~~~

Regular expression. Limit the display to items with contexts matching
CONTEXT (ignoring case). Prepend an exclamation mark, i.e., use !CONTEXT
rather than CONTEXT, to limit the display to items which do NOT have
contexts matching CONTEXT.

-d DEPTH
~~~~~~~~

CLI only. In the GUI use *View/Set outline depth*. The default,
``-d 0``, includes all outline levels. Use ``-d 1`` to include only
level 1, ``-d 2`` to include levels 1 and 2 and so forth. This setting
applies to the CLI only. In the GUI use the command *set outline depth*.

For example, modifying the specification above by adding ``-d 3`` would
give the following:

::

    specification: a MMM yyyy; u; k[0]; k[1] -b 1 -e +1/1 -d 3

    13.1) Feb 2014
       6.3) agent 1
          1.3) client 1
          5) client 2
       6.8) agent 2
          2.2) client 1
          4.6) client 2

-e END\_DATE
~~~~~~~~~~~~

Fuzzy parsed date. When a date specification is provided, limit the
display of dated items to those with datetimes falling *before* this
datetime. As with BEGIN\_DATE relative month expressions can be used so
that, for example, ``-b -1/1  -e 1`` would include all items from the
previous month. As with ``-b``, period strings can be appended, e.g.,
``-b mon -e mon + 7d`` would include items from the week that begins
with the first Monday falling on or after today. Default: None.

-f FILE
~~~~~~~

Regular expression. Limit the display to items from files whose paths
match FILE (ignoring case). Prepend an exclamation mark, i.e., use !FILE
rather than FILE, to limit the display to items from files whose path
does NOT match FILE.

-k KEYWORD
~~~~~~~~~~

Regular expression. Limit the display to items with contexts matching
KEYWORD (ignoring case). Prepend an exclamation mark, i.e., use !KEYWORD
rather than KEYWORD, to limit the display to items which do NOT have
keywords matching KEYWORD.

-l LOCATION
~~~~~~~~~~~

Regular expression. Limit the display to items with a location matching
LOCATION (ignoring case). Prepend an exclamation mark, i.e., use
!LOCATION rather than LOCATION, to limit the display to items which do
NOT have a location that matches LOCATION.

-m MISSING
~~~~~~~~~~

Either 0 (the default) or 1. When 1 include items that would otherwise
be excluded because of a *non-date*, groupby specification. E.g.,
``c k`` would omit items without a keyword entry, but ``c k -m 1`` would
include such items under a "None" heading. This option does not apply to
date specifications, i.e., if a date specification is part of the
groupby setting, then undated items will be excluded whatever the value
of ``-m``.

-o OMIT
~~~~~~~

String. Composite type only. Show/hide a)ctions, d)elegated tasks,
e)vents, g)roup tasks, n)otes, o)ccasions, s)omeday items and/or t)asks.
For example, ``-o on`` would show everything except occasions and notes
and ``-o !on`` would show only occasions and notes.

-s SUMMARY
~~~~~~~~~~

Regular expression. Limit the display to items containing SUMMARY
(ignoring case) in the item summary. Prepend an exclamation mark, i.e.,
use !SUMMARY rather than SUMMARY, to limit the display to items which do
NOT contain SUMMARY in the summary.

-S SEARCH
~~~~~~~~~

Regular expression. Composite type only. Limit the display to items
containing SEARCH (ignoring case) anywhere in the *item* or its file
path. Prepend an exclamation mark, i.e., use !SEARCH rather than SEARCH,
to limit the display to items which do NOT contain SEARCH in the item or
its file path.

-t TAGS
~~~~~~~

Comma separated list of case insensitive regular expressions. E.g., use

::

    -t tag1, !tag2

or

::

    -t tag1, -t !tag2

to display items with one or more tags that match 'tag1' but none that
match 'tag2'.

-u USER
~~~~~~~

Regular expression. Limit the display to items with user matching USER
(ignoring case). Prepend an exclamation mark, i.e., use !USER rather
than USER, to limit the display to items which do NOT have a user that
matches USER.

-w WIDTH
~~~~~~~~

Non-negative integer. Truncate the output for column 1 if it exceeds
this integer. Do not truncate if this integer is zero.

-W WIDTH
~~~~~~~~

Non-negative integer. Truncate the output for column 2 if it exceeds
this integer.

Saving view specifications
--------------------------

You can save view specifications in your specifications file,
``~./etm/reports.cfg`` by default, and then select them in the selection
box at the bottom of the custom view window in the GUI or from a list in
the CLI.

You can also add specifications to file in the GUI by selecting any item
from the list and then replacing the content with anything you like.
Press *Return* to *add* your specification temporarily to the list.
*Note that the original entry will not be affected.* When you leave the
custom view you will have an opportunity to save the additions you have
made. If you choose a file, your additions will be inserted into the
list and it will be opened for editing.
