.. _dates-label:

Dates
=====

Fuzzy dates
-----------

When either a *datetime* or an *time period* is to be entered, special
formats are used in *etm*. Examples include entering a starting datetime
for an item using ``@s`` and jumping to a date using Ctrl-J.

Suppose, for example, that it is currently 8:30am on Friday, February
15, 2013. Then, *fuzzy dates* would expand into the values illustrated
below.

    ========   ==============================
    enter      result
    ========   ==============================
    mon 2p     2:00pm Monday, February 19
    fri        12:00am Friday, February 15
    9a -1/1    9:00am Tuesday, January 1
    +2/15      12:00am Monday, April 15 2013
    8p +7      8:00pm Friday, February 22
    -14        8:30am Friday, February 1
    now        8:30am Friday, February 15
    ========   ==============================

Note that expressions using ``+`` or ``-`` give datetimes relative to
the current datetime.

12am is the default time when a time is not explicitly entered. E.g.,
``+2/15`` in the examples above gives 12:00am on April 15.

To avoid ambiguity, always append either 'a', 'p' or 'h' when entering
an hourly time, e.g., use ``1p`` or ``13h``.

Time periods
------------

Time periods are entered using the format ``WwDdHhMm`` where W, D, H and
M are integers and w, d, h and m refer to weeks, days, hours and minutes
respectively. For example:

    =======   =====================
    enter     result
    =======   =====================
    2h30m     2 hours, 30 minutes
    2w3d      2 weeks, 3 days
    45m       45 minutes
    =======   =====================

As an example, if it is currently 8:50am on Friday February 15, 2013,
then entering ``now + 2d4h30m`` into the date calculator would give
``2013-02-17 1:20pm``.

Tip. Need to schedule a reminder in 15 minutes? Use ``@s +15m``.

Time zones
----------

Dates and times are always stored in *etm* data files as times in the
time zone given by the entry for ``@z``. On the other hand, dates and
times are always displayed in *etm* using the local time zone of the
system.

For example, if it is currently 8:50am EST on Friday February 15, 2013,
and an item is saved on a system in the ``US/Eastern`` time zone
containing the entry::

    @s now @z Australia/Sydney

then the data file would contain::

    @s 2013-02-16 12:50am @z Australia/Sydney

but this item would be displayed as starting at ``8:50am 2013-02-15`` on
the system in the ``US/Eastern`` time zone.

Tip. Need to determine the flight time when the departing timezone is
different that the arriving timezone? The date calculator (shortcut
Shift-D) will accept timezone information so that, e.g., entering the
arrival time minus the departure time::

    4/20 6:15p US/Central - 4/20 4:50p Asia/Shanghai

into the calculator would give::

    14h25m

as the flight time.

Anniversary substitutions
-------------------------

An anniversary substitution is an expression of the form ``!YYYY!`` that
appears in an item summary. Consider, for example, the occasion::

    ^ !2010! anniversary @s 2011-02-20 @r y

This would appear on Feb 20 of 2011, 2012, 2013 and 2014, respectively,
as *1st anniversary*, *2nd anniversary*, *3rd anniversary* and *4th
anniversary*. The suffixes, *st*, *nd* and so forth, depend upon the
translation file for the locale.

Easter
------

An expression of the form ``easter(yyyy)`` can be used as a date
specification in ``@s`` entries and in the datetime calculator. E.g.

::

    @s easter(2014) 4p

would expand to ``2014-04-20 4pm``. Similarly, in the date calculator::

    easter(2014) - 48d

(Rose Monday) would return ``2014-03-03``. In repeating items
``easter(yyyy)`` is replaced by ``&E``, e.g.,

::

    ^ Easter Sunday @s 2010-01-01 @r y &E 0
    ^ Ash Wednesday @s 2010-01-01 @r y &E -46
    ^ Rose Monday @s 2010-01-01 @r y &E -48

