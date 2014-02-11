# etmtk Notes

123456789|123456789|123456789|123456789|123456789|123456789|123456789|123456789|

# TODO: don't trigger alerts for finished tasks

# TODO: history -> open file dialog, changes for all if none selected.

# TODO: main help: menu and toolbar optiions, main key bindings

# TODO: edit help:


## Menus

- Menu
    - File
        - Open
            - Configuration file
            - Auto completions
            - Report specification
            - Data files ...
        - Calendars ...
        - Export
    - View
        - Go to date
        - Outline depth
        - Busy times
        - Yearly calendar
        - Report
        - Date calculator
        - Check for updates
        - Change log
        - Error log
    - Help
        - About
        - Help

- Tool bar
    - Show
        - Agenda
        - Schedule
        - Paths
        - Keywords
        - Tags
    - Add
        - Item
        - Timer
    - Edit
        - Clone
        - Delete
        - Edit
        - Finish

## Commands

- Tool bar
    - Quit
    - Save
    - Search
    - Help

- Act menu
    - Create item
        - item selected
            prompt [copy selected item, NEW ITEM]
        - no selection
    - Start/Toggle timer
        - start
            - item selected
                - get summary [1. timer for selected item, 2. NEW TIMER summary]
                    - if empty
                        - if item is action with today's date: restart timer
                        - else: clone
                    - else
                        - start timer with summary
            - no selection
                get summary for NEW TIMER
        - finish
            - entry in hsh
                clone existing item as action
            - entry not in hsh

- Edit menu
    - Clone
        - open editor with copy as new item
    - Delete
        - repeating
            - open dialog for which
                - this instance: add @-
                - all subsequent: add @u
                - all: delete item
        - not repeating: delete item
    - Edit
        - repeating
            - open dialog for which
                - this instance:
                    - add @- to original
                    - open editor with instance copy as new item
                - this and all subsequent
                    - add @u to original
                    - open editor with @s instance as new item
                - all
                    - open editor with item as existing item
        - not repeating: open editor with item as existing item
    - Finish
        - get finish date and time
            - add done;due, to @f
            - not repeating: add @f with done;due

    - Reschedule (both repeating and non repeating)
        - get new date and time
            - repeating: add @- with original dt and @+ with new dt
            - not repeating: replace @s with new dt



## Editor

- Toolbar
    - Ok (check, if necessary, and save, prompting for file if necessary)
    - Check (str2hsh and back)
        - display messages if necessary
        - if repeating, show list of repetitions
    - Cancel (prompt if modified)


### Logic


We are calling an instance of editor with this init:

    - __init__(self, parent=None, newhsh=None, rephsh=None)

- if editing a configuration or data file, specify a filename for file

- if creating a new item or cloning or editing an existing item, specify a hash for item

    - if item is repeating

        - get which

            - 1. T

        item['fileinfo'] = (filename, beginning line number, ending line number)

    - mode = edit: fileinfo will have both beginning and ending line numbers

    - mode = clone: fileinfo will have only beginning line number

    - mode = new: fileinfo will have only filename



- item editing
    - invoke with item hash, possibly empty
        - if empty: entry = ""
        - else: entry = hsh2str (with no fileinfo in hsh, this will be anew item)

