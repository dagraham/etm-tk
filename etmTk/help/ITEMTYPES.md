% Item types

There are several types of items in etm. Each item begins with a type character such as an asterisk (event) and continues on one or more lines either until the end of the file is reached or another line is found that begins with a type character. The type character for each item is followed by the item summary and then, perhaps, by one or more `@key value` pairs - see [&#64;-Keys](#keys) for details. The order in which such pairs are entered does not matter.

## ~ Action

A record of the expenditure of time (`@e`) and/or money (`@x`). Actions are not reminders, they are instead records of how time and/or money was actually spent. Action lines begin with a tilde, `~`.

        ~ picked up lumber and paint @s mon 3p @e 1h15m @x 127.32

Entries such as `@s mon 3p`, `@e 1h15m` and `@x 127.32` are discussed below under *Item details*. Action entries form the basis for time and expense billing using action reports - see [Reports](#reports) for details.

Tip: You can use either path or keyword or a combination of the two to organize your actions.

## * Event

Something that will happen on particular day(s) and time(s).  Event lines begin with an asterick, `*`.

        * dinner with Karen and Al @s sat 7p @e 3h

Events have a starting datetime, `@s` and an extent, `@e`. The ending datetime is given implicitly as the sum of the starting datetime and the extent. Events that span more than one day are possible, e.g.,

        * Sales conference @s 9a wed @e 2d8h

begins at 9am on Wednesday and ends at 5pm on Friday.

An event without an `@e` entry or with `@e 0` is regarded as a *reminder* and, since there is no extent, will not be displayed in *busy times*.

## ^ Occasion

Holidays, anniversaries, birthdays and such. Similar to an event with a date but no starting time and no extent. Occasions begin with a caret sign, `^`.

        ^ The !1776! Independence Day @s 2010-07-04 @r y &M 7 &m 4

On July 4, 2013, this would appear as `The 237th Independence Day`. Here !1776!` is an example of an *anniversary substitution* - see [Dates](#dates) for details.

## ! Note

A record of some useful information. Note lines begin with an exclamation point, `!`.

    ! xyz software @k software:passwords @d user: dnlg, pw: abc123def

Tip: Since both the GUI and CLI note views group and sort by keyword, it is a good idea to use keywords to organize your notes.

## - Task

Something that needs to be done. It may or may not have a due date. Task lines begin with a minus sign, `-`.

    - pay bills @s Oct 25

A task with an `@s` entry becomes due on that date and past due when that date has passed. If the task also has an `@b` begin-by entry, then advance warnings of the task will begin appearing the specified number of days before the task is due.  An `@e` entry in a task is interpreted as an estimate of the time required to finish the task.

## % Delegated task

A task that is assigned to someone else, usually the person designated in an `@u` entry. Delegated tasks begin with a percent sign, `%`.

        % make reservations for trip @u joe @s fri

## + Task group

A collection of related tasks, some of which may be prerequisite for others. Task groups begin with a plus sign, `+`.

        + dog house
          @j pickup lumber and paint      &q 1
          @j cut pieces                   &q 2
          @j assemble                     &q 3
          @j paint                        &q 4

Note that a task group is a single item and is treated as such. E.g., if any job is selected for editing then the entire group is displayed.

Individual jobs are given by the `@j` entries. The *queue* entries, `&q`, set the order --- tasks with smaller &q values are prerequisites for subsequent tasks with larger &q values. In the example above, neither "pickup lumber" nor "pickup paint" have any prerequisites. "Pickup lumber", however, is a prerequisite for "cut pieces" which, in turn, is a prerequisite for "assemble". Both "assemble" and "pickup paint" are prerequisites for "paint".


## $ In basket

A quick, don't worry about the details item to be edited later when you have the time. In basket entries begin with a dollar sign, `$`.

        $ joe 919 123-4567

If you create an item using *etm* and forget to provide a type character, an `$` will automatically be inserted.


## ? Someday maybe

Something are you don't want to forget about altogether but don't want to appear on your next or scheduled lists. Someday maybe items begin with a question mark, `?`.

        ? lose weight and exercise more

## # Hidden

Hidden items begin with a hash mark, `#`. Such items are ignored by etm save for appearing in the folder view.  Stick a hash mark in front of any item that you don't want to delete but don't want to see in your other views.

## = Defaults

Default entries begin with an equal sign, `=`. These entries consist of `@key value` pairs which then become the defaults for subsequent entries in the same file until another `=` entry is reached.

Suppose, for example, that a particular file contains items relating to "project_a" for "client_1". Then entering

    = @k client_1:project_a

on the first line of the file and

    =

on the twentieth line of the file would set the default keyword for entries between the first and twentieth line in the file.

