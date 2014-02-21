In contrast to most calendar/todo applications, creating items (events, tasks, and so forth) in etm does not require filling out fields in a form. Instead, items are created as free-form text entries using a simple, intuitive format and stored in plain text files.

There are several types of items in etm - see Help/Types for details. Each item begins with a type character such as an asterisk (event) and continues on one or more lines either until the end of the file is reached or another line is found that begins with a type character. The type character for each item is followed by the item summary and then, perhaps, by one or more `@key value` pairs - see Help/@ keys for details. The order in which such pairs are entered does not matter.

Dates can be entered in etm using *fuzzy parsing* - e.g., `+7` for seven days from today, `fri` for next Friday, `+1/1` for the first day of next month. See Help/Dates for details.

# Sample entries

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

        ^ payday @s 1/1 @r m &w (MO, TU, WE, TH, FR)
          &m (-1, -2, -3) &s -1

* Take a prescribed medication daily (a reminder) [s]tarting today and [r]epeating (d)aily at [h]ours 10am, 2pm, 6pm and 10pm [u]ntil (12am on) the fourth day from today. Trigger the default [a]lert zero minutes before each event:

        * take Rx @s +0 @r d &h 10, 14, 18, 22 &u +4 @a 0

* Presidential election day (an occasion) every four years on the first Tuesday after a Monday in November:

        ^ Presidential Election Day @s 2012-11-06
          @r y &i 4 &M 11 &m (2,3,4,5,6,7,8) &w TU

* Join the etm discussion group (a task) [s]tarting on the first day of the next month. Because of the @g (goto) link, pressing Ctrl-G when this item is selected in the gui would open the link using the system default application which, in this case, would be your default browser:

        - join the etm discussion group @s +1/1
          @g groups.google.com/group/eventandtaskmanager/topics

# Organization

*etm* offers two heirarchical ways of organizing your data: by folder (file path) and by keyword. There are no hard and fast rules about how to use these heirarchies but the goal is a system that makes complementary uses of folder and keyword and fits your needs. As with any filing system, planning and consistency are paramount.

For example, one pattern of use for a business would be to use folders for people and keywords for client-project-category.

Similarly, a family could use folders to separate personal and shared items for family members, for example:

    root etm data directory
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

    calendars
    - [dag, true, dag]
    - [erp, false, erp]
    - [shared, true, shared]

and

    calendars
    - [erp, true, erp]
    - [dag, false, dag]
    - [shared, true, shared]

then, by default, both dag and erp would see the entries from their personal files as well as the shared entries and each could optionally view the entries from the other's personal files as well.  See the *Preferences* tab for details on the `calendars` entry.
