#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
# import sys
import re
import uuid
from copy import deepcopy
import subprocess
from dateutil.tz import tzlocal
import codecs

import logging
import logging.config

logger = logging.getLogger()

import platform

if platform.python_version() >= '3':
    import tkinter
    from tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, PanedWindow, OptionMenu, StringVar, IntVar, Menu, X, Canvas, CURRENT, Scrollbar
    from tkinter import ttk
    from tkinter import font as tkFont
    utf8 = lambda x: x

else:
    import Tkinter as tkinter
    from Tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, PanedWindow, OptionMenu, StringVar, IntVar, Menu, X, Canvas, CURRENT, Scrollbar
    import ttk
    import tkFont

    def utf8(s):
        return s

tkversion = tkinter.Tcl().eval('info patchlevel')

import etmTk.data as data

from dateutil.parser import parse

from calendar import Calendar

from decimal import Decimal


def getDayColor(num_minutes):
    red = 10 / 355.0
    hue = red
    saturation = 1
    min_b = .3
    max_b = 1  # must be <= 1
    max_minutes = 480
    lightness = min(
        max_b, min_b + (max_b - min_b) * num_minutes / float(max_minutes))
    r, g, b = hsv_to_rgb(
        hue, saturation, lightness)
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    return "#%02x%02x%02x" % (r, g, b)


def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)  # XXX assume int() truncates!
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q

from etmTk.data import (
    init_localization, fmt_weekday, fmt_dt, str2hsh, tstr2SCI, leadingzero, relpath, s2or3, send_mail, send_text, get_changes, checkForNewerVersion, datetime2minutes, calyear, expand_template, id2Type, get_current_time, windoz, mac, setup_logging, gettz, commandShortcut, rrulefmt, tree2Text, date_calculator, AFTER, export_ical_item, export_ical_active, fmt_time, TimeIt, getReportData, getFileTuples, getAllFiles, updateCurrentFiles, FINISH, availableDates, syncTxt, update_subscription)

from etmTk.dialog import MenuTree, Timer, ReadOnlyText, MessageWindow, TextDialog, OptionsDialog, GetInteger, GetDateTime, GetString, FileChoice, STOPPED, PAUSED, RUNNING, BGCOLOR, ONEDAY, ONEMINUTE

from etmTk.edit import SimpleEditor

import gettext

_ = gettext.gettext


from datetime import datetime, time

ETM = "etm"

# STOPPED = _('stopped')
# PAUSED = _('paused')
# RUNNING = _('running')

FILTER = _("filter")
FILTERCOLOR = "gray"

# Views #
AGENDA = _('Agenda')

DAY = _('Day')
WEEK = _("Week")
MONTH = _("Month")

PATH = _('Path')
KEYWORD = _('Keyword')
TAG = _('Tag')

NOTE = _('Note')
CUSTOM = _("Custom")

CALENDARS = _("Calendars")

COPY = _("Copy")
EDIT = _("Edit")
DELETE = _("Delete")

FILE = _("File")
NEW = _("New")
OPEN = _("Open")
VIEW = _("View")
ITEM = _("Item")
TOOLS = _("Tools")
HELP = _("Help")

MAKE = _("Make report")
PRINT = _("Print")
EXPORTTEXT = _("Export report in text format ...")
EXPORTCSV = _("Export report in CSV format ...")
SAVESPECS = _("Save changes to report specifications")

CLOSE = _("Close")

SEP = "----"

ACTIVEFILL = "#FAFCAC"
ACTIVEOUTLINE = "gray40"

DEFAULTFILL = "#D4DCFC"  # blue
OTHERFILL = "#C7EDC8"  # green

BUSYOUTLINE = ""

CONFLICTFILL = "#C1C4C9"
CURRENTFILL = "#FCF2F0"
CURRENTLINE = "#E0535C"
LASTLTR = re.compile(r'([a-z])$')
LINECOLOR = "gray80"

OCCASIONFILL = "gray96"

this_dir, this_filename = os.path.split(__file__)
USERMANUAL = os.path.normpath(os.path.join(this_dir, "help", "UserManual.html"))


class App(Tk):
    def __init__(self, path=None):
        Tk.__init__(self)

        self.minsize(460, 460)
        self.uuidSelected = None
        self.timerItem = None
        self.loop = loop
        self.actionTimer = Timer(self, options=loop.options)
        self.monthly_calendar = Calendar()
        self.activeAlerts = []
        self.configure(background=BGCOLOR)
        self.option_add('*tearOff', False)
        self.menu_lst = []
        self.menutree = MenuTree()
        self.chosen_day = None
        self.active_date = None
        self.busy_info = None
        self.weekly = False
        self.monthly = False
        self.today_col = None
        self.specsModified = False
        self.active_tree = {}
        root = "_"

        ef = "%a %b %d"
        if 'ampm' in loop.options and loop.options['ampm']:
            self.efmt = "%I:%M%p {0}".format(ef)
        else:
            self.efmt = "%H:%M {0}".format(ef)

        self.default_calendars = deepcopy(loop.options['calendars'])

        # create the root node for the menu tree
        self.menutree.create_node(root, root)

        # leaf: (parent, (option, [accelerator])

        self.outline_depths = {}
        for view in DAY, TAG, KEYWORD, NOTE, PATH:
            # set all to the default
            logger.debug('Setting depth for {0} to {1}'.format(view, loop.options['outline_depth']))
            self.outline_depths[view] = loop.options['outline_depth']
        # set CUSTOM to 0
        self.outline_depths[AGENDA] = 0
        self.outline_depths[CUSTOM] = 0

        self.panedwindow = panedwindow = PanedWindow(self, orient="vertical", sashwidth=8, sashrelief='flat')
        self.toppane = toppane = Frame(panedwindow, bd=0, highlightthickness=0, background=BGCOLOR)
        self.tree = ttk.Treeview(toppane, show='tree', columns=["#1", "#2"], selectmode='browse')
        self.canvas = Canvas(self.toppane, background="white", bd=2, relief="sunken")

        self.canvas.bind("<Control-Button-1>", self.on_select_item)
        self.canvas.bind("<Double-1>", self.on_select_item)
        self.canvas.bind("<Configure>", self.configureCanvas)

        self.canvas.bind("<Return>", lambda e: self.on_activate_item(event=e))
        self.canvas.bind('<Left>', (lambda e: self.priorWeekMonth(event=e)))
        self.canvas.bind('<Right>', (lambda e: self.nextWeekMonth(event=e)))
        self.canvas.bind('<Up>', (lambda e: self.selectId(event=e, d=-1)))
        self.canvas.bind('<Down>', (lambda e: self.selectId(event=e, d=1)))

        self.canvas.bind("b", lambda event: self.after(AFTER, self.showBusyPeriods))
        self.canvas.bind("f", lambda event: self.after(AFTER, self.showFreePeriods))

        # main menu
        self.menubar = menubar = Menu(self)
        menu = _("Menubar")
        self.add2menu(root, (menu,))

        # File menu
        filemenu = Menu(menubar, tearoff=0)
        path = FILE
        self.add2menu(menu, (path, ))

        self.newmenu = newmenu = Menu(filemenu, tearoff=0)
        self.add2menu(path, (NEW, ))
        path = NEW

        label = _("Item")
        l = "N"
        c = "n"
        newmenu.add_command(label=label, command=self.newItem)
        # self.bindTop("n", self.newItem)
        self.bindTop(c, lambda e: self.after(AFTER, self.newItem(e)))
        self.canvas.bind(c, lambda e: self.after(AFTER, self.newItem(e)))

        newmenu.entryconfig(0, accelerator=l)
        self.add2menu(path, (label, l))

        l = "Shift-N"
        c = "N"
        label = _("File")
        newmenu.add_command(label=label, command=self.newFile)
        self.bindTop(c, self.newFile)
        newmenu.entryconfig(1, accelerator=l)
        self.add2menu(path, (label, l))

        label = _("Begin/Pause Action Timer")
        l = "T"
        c = 't'
        newmenu.add_command(label=label, command=self.startActionTimer)
        self.bindTop(c, self.startActionTimer)
        newmenu.entryconfig(2, accelerator=l)
        self.add2menu(path, (label, l))

        label = _("Finish Action Timer")
        l = "Shift-T"
        c = "T"
        newmenu.add_command(label=label, command=self.finishActionTimer)
        self.bind(c, self.finishActionTimer)
        filemenu.add_cascade(label=NEW, menu=newmenu)
        newmenu.entryconfig(3, state="disabled")
        self.add2menu(path, (label, l))

        label = _("Start/Resolve Idle Timer")
        l = "I"
        c = 'i'
        newmenu.add_command(label=label, command=self.startIdleTimer)
        self.bindTop(c, self.startIdleTimer)
        newmenu.entryconfig(4, accelerator=l)
        self.add2menu(path, (label, l))

        label = _("Stop Idle Timer")
        l = "Shift-I"
        c = "I"
        newmenu.add_command(label=label, command=self.stopIdleTimer)
        self.bind(c, self.stopIdleTimer)
        newmenu.entryconfig(5, accelerator=l)
        self.add2menu(path, (label, l))
        newmenu.entryconfig(5, state="disabled")

        path = FILE

        # Open
        openmenu = Menu(filemenu, tearoff=0)
        self.add2menu(path, (OPEN, ))
        path = OPEN

        l = "Shift-F"
        c = "F"
        label = _("Data file ...")
        openmenu.add_command(label=label, command=self.editData)
        self.bindTop(c, self.editData)
        openmenu.entryconfig(0, accelerator=l)
        self.add2menu(path, (label, l))

        l = "Shift-C"
        c = "C"
        label = _("Configuration file ...")
        openmenu.add_command(label=label, command=self.editCfgFiles)
        self.bindTop(c, self.editCfgFiles)
        openmenu.entryconfig(1, accelerator=l)
        self.add2menu(path, (label, l))

        l = "Shift-P"
        c = "P"
        label = "preferences"
        openmenu.add_command(label=label, command=self.editConfig)
        self.bindTop(c, self.editConfig)

        openmenu.entryconfig(2, accelerator=l)
        self.add2menu(path, (label, l))

        l = "Shift-S"
        c = "S"
        file = loop.options['scratchpad']
        label = relpath(file, loop.options['etmdir'])
        openmenu.add_command(label=label, command=self.editScratch)
        self.bindTop(c, self.editScratch)
        openmenu.entryconfig(3, accelerator=l)
        self.add2menu(path, (label, l))

        filemenu.add_cascade(label=OPEN, menu=openmenu)

        path = FILE

        filemenu.add_separator()
        self.add2menu(path, (SEP, ))

        # quit
        l, c = commandShortcut('q')
        label = _("Quit")
        filemenu.add_command(label=label, underline=0,
                             command=self.quit)
        self.bind(c, self.quit)  # w
        self.add2menu(path, (label, l))

        menubar.add_cascade(label=path, underline=0, menu=filemenu)

        # View menu
        self.viewmenu = viewmenu = Menu(menubar, tearoff=0)
        path = VIEW
        self.add2menu(menu, (path, ))

        # go home
        l = "Space"
        label = _("Home")
        viewmenu.add_command(label=label, command=self.goHome)

        viewmenu.entryconfig(0, accelerator=l)
        self.add2menu(path, (label, l))
        self.bindTop('<space>', self.goHome)

        # show alerts
        l = "A"
        c = "a"
        label = _("Show remaining alerts for today")
        viewmenu.add_command(label=label, underline=1, command=self.showAlerts)
        self.bindTop(c, self.showAlerts)

        viewmenu.entryconfig(1, accelerator=l)
        self.add2menu(path, (label, l))

        # go to date
        l = "J"
        c = "j"
        label = _("Jump to date")
        viewmenu.add_command(label=label, command=self.goToDate)
        self.bindTop(c, self.goToDate)

        viewmenu.entryconfig(2, accelerator=l)
        self.add2menu(path, (label, l))

        viewmenu.add_separator()  # 3
        self.add2menu(path, (SEP, ))

        l = "Control-Down"
        label = _("Next sibling")
        viewmenu.add_command(label=label, underline=1, command=self.nextItem)

        viewmenu.entryconfig(4, accelerator=l)
        self.add2menu(path, (label, l))

        l = "Control-Up"
        label = _("Previous sibling")
        viewmenu.add_command(label=label, underline=1, command=self.prevItem)

        viewmenu.entryconfig(5, accelerator=l)
        self.add2menu(path, (label, l))

        # apply filter
        l, c = commandShortcut('f')
        label = _("Set outline filter")
        viewmenu.add_command(label=label, underline=1, command=self.setFilter)
        self.bind(c, self.setFilter)

        viewmenu.entryconfig(6, accelerator=l)
        self.add2menu(path, (label, l))

        # clear filter
        l = "Shift-Ctrl-F"
        label = _("Clear outline filter")
        viewmenu.add_command(label=label, underline=1, command=self.clearFilter)

        viewmenu.entryconfig(7, accelerator=l)
        self.add2menu(path, (label, l))

        # toggle showing labels
        l = "L"
        c = "l"
        label = _("Toggle displaying labels column")
        viewmenu.add_command(label=label, underline=1, command=self.toggleLabels)
        self.bindTop(c, self.toggleLabels)

        viewmenu.entryconfig(8, accelerator=l)
        self.add2menu(path, (label, l))

        # expand to depth
        l = "O"
        c = "o"
        label = _("Set outline depth")
        viewmenu.add_command(label=label, underline=1, command=self.expand2Depth)
        self.bindTop(c, self.expand2Depth)

        viewmenu.entryconfig(9, accelerator=l)
        self.add2menu(path, (label, l))

        # popup active tree
        l = "S"
        c = "s"
        label = _("Show outline as text")
        viewmenu.add_command(label=label, underline=1, command=self.popupTree)
        self.bindTop(c, self.popupTree)

        viewmenu.entryconfig(10, accelerator=l)
        self.add2menu(path, (label, l))

        # print active tree
        l = "P"
        c = "p"
        label = _("Print outline")
        viewmenu.add_command(label=label, underline=1, command=self.printTree)
        self.bindTop("p", self.printTree)
        viewmenu.entryconfig(11, accelerator=l)
        self.add2menu(path, (label, l))

        # toggle showing finished
        l = "X"
        c = "x"
        label = _("Toggle displaying finished")
        viewmenu.add_command(label=label, underline=1, command=self.toggleFinished)
        self.bindTop(c, self.toggleFinished)
        viewmenu.entryconfig(12, accelerator=l)
        self.add2menu(path, (label, l))

        viewmenu.add_separator()  # 13
        self.add2menu(path, (SEP, ))

        l = "Left"
        label = _("Previous week/month")
        viewmenu.add_command(label=label, underline=1, command=lambda e=None: self.priorWeekMonth(event=e))

        viewmenu.entryconfig(14, accelerator=l)
        self.add2menu(path, (label, l))

        l = "Right"
        label = _("Next week/month")
        viewmenu.add_command(label=label, underline=1, command=lambda e=None: self.nextWeekMonth(event=e))

        viewmenu.entryconfig(15, accelerator=l)
        self.add2menu(path, (label, l))

        l = "Up"
        label = _("Previous item/day in week/month")
        viewmenu.add_command(label=label, underline=1, command=lambda e=None: self.selectId(event=e, d=-1))

        viewmenu.entryconfig(16, accelerator=l)
        self.add2menu(path, (label, l))

        l = "Down"
        label = _("Next item/day in week/month")
        viewmenu.add_command(label=label, underline=1, command=lambda e=None: self.selectId(event=e, d=1))

        viewmenu.entryconfig(17, accelerator=l)
        self.add2menu(path, (label, l))

        l = "B"
        c = 'b'
        label = _("List busy times in week/month")
        viewmenu.add_command(label=label, underline=5, command=self.showBusyPeriods)

        viewmenu.entryconfig(18, accelerator=l)
        self.add2menu(path, (label, l))

        l = "F"
        c = 'f'
        label = _("List free times in week/month")
        viewmenu.add_command(label=label, underline=5, command=self.showFreePeriods)

        viewmenu.entryconfig(19, accelerator=l)
        # set binding in showWeekly
        self.add2menu(path, (label, l))

        for i in range(14, 20):
            self.viewmenu.entryconfig(i, state="disabled")
        menubar.add_cascade(label=path, underline=0, menu=viewmenu)

        # Item menu
        self.itemmenu = itemmenu = Menu(menubar, tearoff=0)
        self.itemmenu.bind("<Escape>", self.closeItemMenu)
        self.itemmenu.bind("<FocusOut>", self.closeItemMenu)
        path = ITEM
        self.add2menu(menu, (path, ))
        self.em_options = [
            [_('Copy'), 'c'],
            [_('Delete'), 'd'],
            [_('Edit'), 'e'],
            [_('Edit file'), 'E'],
            [_('Finish'), 'f'],
            [_('Move'), 'm'],
            [_('Reschedule'), 'r'],
            [_('Schedule new'), 'R'],
            [_('Open link'), 'g'],
            [_('Show user details'), 'u']]
        self.edit2cmd = {
            'c': self.copyItem,
            'd': self.deleteItem,
            'e': self.editItem,
            'E': self.editItemFile,
            'f': self.finishItem,
            'm': self.moveItem,
            'r': self.rescheduleItem,
            'R': self.scheduleNewItem,
            'g': self.openWithDefault,
            'u': self.showUserDetails}
        self.em_opts = [x[0] for x in self.em_options]
        for i in range(len(self.em_options)):
            label = self.em_options[i][0]
            k = self.em_options[i][1]
            if k == 'd':
                l = "BackSpace"
                c = "<BackSpace>"
            elif k == 'E':
                l = "Shift-E"
                c = "E"
            elif k == 'R':
                l = "Shift-R"
                c = "R"
            else:
                l = k.upper()
                c = k
            itemmenu.add_command(label=label, underline=0, command=self.edit2cmd[k])
            if k == 'f':
                self.tree.bind(c, self.edit2cmd[k])
            else:
                self.bindTop(c, self.edit2cmd[k])

            itemmenu.entryconfig(i, accelerator=l)
            self.add2menu(path, (label, l))
        menubar.add_cascade(label=path, underline=0, menu=itemmenu)

        # tools menu
        path = TOOLS
        self.add2menu(menu, (path, ))
        toolsmenu = Menu(menubar, tearoff=0)

        # date calculator
        l = "Shift-D"
        c = "D"
        label = _("Date and time calculator")
        toolsmenu.add_command(label=label, underline=12, command=self.dateCalculator)
        self.bindTop(c, self.dateCalculator)

        toolsmenu.entryconfig(1, accelerator=l)
        self.add2menu(path, (label, l))

        # available date calculator
        l = "Shift-A"
        c = "A"
        label = _("Available dates calculator")
        toolsmenu.add_command(label=label, underline=12, command=self.availableDateCalculator)
        self.bindTop(c, self.availableDateCalculator)

        toolsmenu.entryconfig(2, accelerator=l)
        self.add2menu(path, (label, l))

        l = "Shift-Y"
        c = "Y"

        label = _("Yearly calendar")
        toolsmenu.add_command(label=label, underline=8, command=self.showCalendar)
        self.bindTop(c, self.showCalendar)

        toolsmenu.entryconfig(3, accelerator=l)
        self.add2menu(path, (label, l))

        # changes
        if loop.options['vcs_system']:

            l = 'Shift-H'
            c = 'H'
            label = _("History of changes")
            toolsmenu.add_command(label=label, underline=1, command=self.showChanges)
            self.bind(c, lambda event: self.after(AFTER, self.showChanges))

            toolsmenu.entryconfig(4, accelerator=l)
            self.add2menu(path, (label, l))

        # export
        l = "Shift-X"
        c = "X"
        label = _("Export to iCal")
        toolsmenu.add_command(label=label, underline=1, command=self.exportToIcal)
        self.bind(c, self.exportToIcal)

        toolsmenu.entryconfig(5, accelerator=l)
        self.add2menu(path, (label, l))

        # update subscriptions
        l = "Shift-M"
        c = "M"
        label = _("Update calendar subscriptions")
        toolsmenu.add_command(label=label, underline=1, command=self.updateSubscriptions)
        self.bind(c, self.updateSubscriptions)

        toolsmenu.entryconfig(5, accelerator=l)
        self.add2menu(path, (label, l))

        # load data
        l = "Shift-L"
        c = "L"
        label = _("Reload data from files")
        toolsmenu.add_command(label=label, underline=1, command=loop.loadData)
        self.bind(c, loop.loadData)

        toolsmenu.entryconfig(6, accelerator=l)
        self.add2menu(path, (label, l))

        menubar.add_cascade(label=path, menu=toolsmenu, underline=0)

        # report
        path = CUSTOM
        self.add2menu(menu, (path, ))
        self.custommenu = reportmenu = Menu(menubar, tearoff=0)

        self.rm_options = [[MAKE, 'm'],
                           [EXPORTTEXT, 't'],
                           [EXPORTCSV, 'x'],
                           [SAVESPECS, 'w']]

        self.rm2cmd = {'m': self.makeReport,
                       't': self.exportText,
                       'x': self.exportCSV,
                       'w': self.saveSpecs}

        self.rm_opts = [x[0] for x in self.rm_options]

        for i in range(len(self.rm_options)):
            label = self.rm_options[i][0]
            k = self.rm_options[i][1]
            l = k.upper()
            c = k

            reportmenu.add_command(label=label, underline=0, command=self.rm2cmd[k])
            reportmenu.entryconfig(i, state="disabled")

        self.add2menu(CUSTOM, (_("Create and display selected report"), "Return"))
        self.add2menu(CUSTOM, (_("Export report in text format ..."), "Ctrl-T"))
        self.add2menu(CUSTOM, (_("Export report in csv format ..."), "Ctrl-X"))
        self.add2menu(CUSTOM, (_("Save changes to report specifications"), "Ctrl-W"))
        self.add2menu(CUSTOM, (_("Expand report list"), "Down"))

        menubar.add_cascade(label=path, menu=reportmenu, underline=0)

        # help
        helpmenu = Menu(menubar, tearoff=0)
        path = HELP
        self.add2menu(menu, (path, ))

        # search is built in
        self.add2menu(path, (_("Search"), ))

        label = _("Shortcuts")
        helpmenu.add_command(label=label, underline=1, accelerator="?", command=self.showShortcuts)
        self.add2menu(path, (label, "?"))
        self.bindTop("?", self.showShortcuts)

        label = _("User manual")
        helpmenu.add_command(label=label, underline=1, accelerator="F1", command=self.help)
        self.add2menu(path, (label, "F1"))
        self.bind("<F1>", lambda e: self.after(AFTER, self.help))

        label = _("About")
        helpmenu.add_command(label="About", accelerator="F2", command=self .about)
        self.bind("<F2>", self.about)
        self.add2menu(path, (label, "F2"))

        # check for updates

        label = _("Check for update")
        helpmenu.add_command(label=label, underline=1, accelerator="F3", command=self.checkForUpdate)
        self.add2menu(path, (label, "F3"))
        self.bind("<F3>", lambda e: self.after(AFTER, self.checkForUpdate))

        menubar.add_cascade(label="Help", menu=helpmenu)

        self.config(menu=menubar)

        self.history = []
        self.index = 0
        self.count = 0
        self.count2id = {}
        self.now = get_current_time()
        self.today = self.now.date()
        self.options = loop.options

        tkfixedfont = tkFont.nametofont("TkFixedFont")
        if 'fontsize_fixed' in self.options and self.options['fontsize_fixed']:
            tkfixedfont.configure(size=self.options['fontsize_fixed'])
        logger.info("using fixedfont size: {0}".format(tkfixedfont.actual()['size']))
        self.tkfixedfont = tkfixedfont

        tktreefont = tkFont.nametofont("TkDefaultFont")
        if 'fontsize_tree' in self.options and self.options['fontsize_tree']:
            tktreefont.configure(size=self.options['fontsize_tree'])
        logger.info("using treefont size: {0}".format(tktreefont.actual()['size']))
        self.tktreefont = tktreefont

        self.popup = ''
        self.value = ''
        self.firsttime = True
        self.mode = 'command'   # or edit or delete
        self.item_hsh = {}
        self.depth2id = {}
        self.prev_week = None
        self.next_week = None
        self.curr_week = None
        self.week_beg = None
        self.itemSelected = None
        self.uuidSelected = None
        self.dtSelected = None
        self.rowSelected = None

        self.title(ETM)

        # self.wm_iconbitmap(bitmap='etmlogo.gif')
        # self.wm_iconbitmap('etmlogo-4.xbm')
        # self.call('wm', 'iconbitmap', self._w, '/Users/dag/etm-tk/etmTk/etmlogo.gif')

        # root = Tk()
        # img = PhotoImage(file='/Users/dag/etm-tk/etmTk/etmlogo.icns')
        # self.tk.call('wm', 'iconphoto', self._w, img)
        # if not mac:
        #     img = PhotoImage(file='etmlogo.gif')
        #     self.call('wm', 'iconphoto', self._w, img)

        # if sys_platform == 'Linux':
        #     logger.debug('using linux icon')
        #     self.wm_iconbitmap('@' + 'etmlogo.gif')
        #     # self.wm_iconbitmap('etmlogo-4.xbm')
        #     # self.call('wm', 'iconbitmap', self._w, '/Users/dag/etm-tk/etmlogo_128x128x32.ico')
        #     # self.iconbitmap(ICON_PATH)
        # elif sys_platform == 'Darwin':
        #     logger.debug('using darwin icon')
        # self.iconbitmap('/Users/dag/etm-tk/etmTk/etmlogo.ico')
        # self.wm_iconbitmap('etmlogo.icns')
        # else:
        #     logger.debug('using windows icon')
        #     self.wm_iconbitmap('etmlogo.ico')

        self.columnconfigure(0, minsize=300, weight=1)
        self.rowconfigure(1, weight=2)

        topbar = Frame(self, bd=0, relief="flat", highlightbackground=BGCOLOR, background=BGCOLOR)
        topbar.pack(side="top", fill="x", expand=0, padx=0, pady=0)

        # report
        # self.reportbar = reportbar = Frame(self, padx=4, bd=2, relief="sunken", highlightbackground=BGCOLOR, background=BGCOLOR)
        self.box_value = StringVar()
        self.custom_box = ttk.Combobox(self, textvariable=self.box_value, font=self.tkfixedfont)
        self.custom_box.bind("<<ComboboxSelected>>", self.newselection)
        self.bind("<Return>", self.makeReport)
        self.bind("<Control-q>", self.quit)
        self.saved_specs = ['']
        self.getSpecs()
        if self.specs:
            self.value_of_combo = self.specs[0]
            self.custom_box['values'] = self.specs
            self.custom_box.current(0)
            self.saved_specs = deepcopy(self.specs)
        self.custom_box.configure(width=30, background=BGCOLOR, takefocus=False)
        # self.report_box.pack(side="left", padx=3, bd=2, relief="sunken", fill=X, expand=1)

        self.vm_options = [[AGENDA, 'a'],
                           ['-', ''],
                           [DAY, 'd'],
                           [WEEK, 'w'],
                           [MONTH, 'm'],
                           ['-', ''],
                           [TAG, 't'],
                           [KEYWORD, 'k'],
                           [PATH, 'p'],
                           ['-', ''],
                           [NOTE, 'n'],
                           [CUSTOM, 'c']]

        self.view2cmd = {'a': self.agendaView,
                         'd': self.dayView,
                         'm': self.showMonthly,
                         'p': self.pathView,
                         'k': self.keywordView,
                         'n': self.noteView,
                         't': self.tagView,
                         'c': self.customView,
                         'w': self.showWeekly}

        self.view = self.vm_options[0][0]
        self.currentView = StringVar(self)
        self.currentView.set(self.view)

        MAIN = _("Main")
        self.add2menu(root, (MAIN, ))
        VIEWS = _("Views")
        self.add2menu(MAIN, (VIEWS, ))

        self.vm_opts = [x[0] for x in self.vm_options]
        # self.vm = OptionMenu(topbar, self.currentView, *self.vm_opts)
        self.vm = OptionMenu(topbar, self.currentView, [])
        self.vm["menu"].delete(0, END)
        self.vm.configure(pady=2)
        for i in range(len(self.vm_options)):
            label = self.vm_options[i][0]
            k = self.vm_options[i][1]
            if label == "-":
                self.vm["menu"].add_separator()
                self.add2menu(VIEWS, (SEP, ))
            else:
                l, c = commandShortcut(k)
                self.vm["menu"].add_command(label=label, command=self.view2cmd[k], accelerator=l)
                self.bind(c, lambda e, x=k: self.after(AFTER, self.view2cmd[x]))
                self.add2menu(VIEWS, (self.vm_opts[i], l))
        self.vm.pack(side="left", padx=2)
        self.vm.configure(background=BGCOLOR, takefocus=False)

        # calendars
        self.calbutton = Button(topbar, text=CALENDARS, command=self.selectCalendars, highlightbackground=BGCOLOR, bg=BGCOLOR, width=8, pady=2)
        self.calbutton.pack(side="right", padx=6)
        if not self.default_calendars:
            self.calbutton.configure(state="disabled")

        # filter
        self.filterValue = StringVar(self)
        self.filterValue.set('')
        self.filterValue.trace_variable("w", self.filterView)

        self.fltr = Entry(topbar, textvariable=self.filterValue, width=14, highlightbackground=BGCOLOR, bg=BGCOLOR)
        self.fltr.pack(side="left", padx=0, expand=1, fill=X)
        self.fltr.bind("<FocusIn>", self.setFilter)
        self.fltr.bind("<Escape>", self.clearFilter)
        self.bind("<Shift-Control-F>", self.clearFilter)
        self.filter_active = False
        self.viewmenu.entryconfig(6, state="normal")
        self.viewmenu.entryconfig(7, state="disabled")

        self.weekly = False

        self.col2_width = tktreefont.measure('abcdgklmprtuX')
        self.col3_width = tktreefont.measure('10:30pm ~ 11:30pmX')
        self.text_width = 260
        logger.info('column widths: {0}, {1}, {2}'.format(self.text_width, self.col2_width, self.col3_width))
        self.tree.column('#0', minwidth=140, width=self.text_width, stretch=1)
        self.labels = False
        # don't show the labels column to start with by setting width=0
        self.tree.column('#1', minwidth=0, width=0, stretch=0, anchor='center')
        self.tree.column('#2', width=self.col3_width, stretch=0, anchor='center')
        self.tree.bind('<<TreeviewSelect>>', self.OnSelect)
        self.tree.bind('<Double-1>', self.OnActivate)
        self.tree.bind('<Return>', self.OnActivate)
        self.tree.bind('<Control-Down>', self.nextItem)
        self.tree.bind('<Control-Up>', self.prevItem)
        # self.tree.bind('<space>', self.goHome)

        for t in tstr2SCI:
            self.tree.tag_configure(t, foreground=tstr2SCI[t][1])

        self.date2id = {}
        self.root = ('', '_')

        self.tree.pack(fill="both", expand=1, padx=4, pady=0)
        panedwindow.add(self.toppane, padx=0, pady=0, stretch="first")

        self.content = ReadOnlyText(panedwindow, wrap="word", padx=3, bd=2, relief="sunken", font=tkfixedfont, height=loop.options['details_rows'], width=46, takefocus=False)
        self.content.bind('<Escape>', self.cleartext)
        self.content.bind('<Tab>', self.focus_next_window)
        self.content.bind("<FocusIn>", self.editItem)

        panedwindow.add(self.content, padx=3, pady=0, stretch="never")

        self.statusbar = Frame(self)

        self.timerStatus = StringVar(self)
        self.timerStatus.set("")
        timer_status = Label(self.statusbar, textvariable=self.timerStatus, bd=0, relief="flat", anchor="w", padx=0, pady=0)
        timer_status.pack(side="left", expand=0, padx=2)
        timer_status.configure(background=BGCOLOR, highlightthickness=0)

        self.pendingAlerts = IntVar(self)
        self.pendingAlerts.set(0)
        self.pending = Button(self.statusbar, padx=8, pady=2,

                              takefocus=False, textvariable=self.pendingAlerts, command=self.showAlerts, anchor="center")
        self.pending.pack(side="right", padx=0, pady=0)
        self.pending.configure(highlightbackground=BGCOLOR,
                               background=BGCOLOR,
                               highlightthickness=0,
                               state="disabled")
        self.showPending = True

        self.currentTime = StringVar(self)
        currenttime = Label(self.statusbar, textvariable=self.currentTime, bd=1, relief="flat", anchor="e", padx=4, pady=0)
        currenttime.pack(side="right")
        currenttime.configure(background=BGCOLOR)

        self.statusbar.pack(side="bottom", fill="x", expand=0, padx=6, pady=0)
        self.statusbar.configure(background=BGCOLOR)

        panedwindow.pack(side="top", fill="both", expand=1, padx=2, pady=0)
        panedwindow.configure(background=BGCOLOR)
        self.panedwindow = panedwindow

        # set cal_regex here and update it in updateCalendars
        self.cal_regex = None
        if loop.calendars:
            cal_pattern = r'^%s' % '|'.join(
                [x[2] for x in loop.calendars if x[1]])
            self.cal_regex = re.compile(cal_pattern)
            logger.debug("cal_pattern: {0}".format(cal_pattern))

        self.default_regex = None
        if 'calendars' in loop.options and loop.options['calendars']:
            calendars = loop.options['calendars']
            default_pattern = r'^%s' % '|'.join(
                [x[2] for x in calendars if x[1]])
            self.default_regex = re.compile(default_pattern)

        self.add2menu(root, (EDIT, ))
        self.add2menu(EDIT, (_("Show completions"), "Ctrl-Space"))
        self.add2menu(EDIT, (_("Cancel"), "Escape"))
        self.add2menu(EDIT, (FINISH, "Ctrl-W"))

        # start clock
        self.updateClock()
        self.year_month = [self.today.year, self.today.month]
        # showView will be called from updateClock
        self.updateAlerts()
        self.etmgeo = os.path.normpath(os.path.join(loop.options['etmdir'], ".etmgeo"))
        self.restoreGeometry()
        self.tree.focus_set()

    def bindTop(self, c, cmd, e=None):
        if e and e.char != c:
            # ignore Control-c
            return
        self.tree.bind(c, lambda e: self.after(AFTER, cmd(e)))
        self.canvas.bind(c, lambda e: self.after(AFTER, cmd(e)))

    def toggleLabels(self, e=None):
        if e and e.char != "l":
            return
        if self.weekly or self.monthly:
            return
        if self.labels:
            width0 = self.tree.column('#0')['width']
            self.tree.column('#0', width=width0 + self.col2_width)
            self.tree.column('#1', width=0)
            self.labels = False
        else:
            width0 = self.tree.column('#0')['width']
            self.tree.column('#0', width=width0 - self.col2_width)
            self.tree.column('#1', width=self.col2_width)
            self.labels = True

    def toggleFinished(self, e=None):
        if e and e.char != "x":
            return
        if loop.options['hide_finished']:
            loop.options['hide_finished'] = False
        else:
            loop.options['hide_finished'] = True
        logger.debug('reloading data')
        # self.updateAlerts()
        if self.weekly:
            self.showWeek()
        elif self.monthly:
            self.showMonth()
        else:
            self.showView()

    def saveGeometry(self):
        str = self.geometry()
        fo = open(self.etmgeo, 'w')
        fo.write(str)
        fo.close()

    def restoreGeometry(self):
        if os.path.isfile(self.etmgeo):
            fo = open(self.etmgeo, "r")
            str = fo.read()
            fo.close()
            tup = [x.strip() for x in str.split(',')]
            if tup:
                self.geometry(tup[0])

    def closeItemMenu(self, event=None):
        if self.weekly or self.monthly:
            self.canvas.focus_set()
        else:
            self.tree.focus_set()
        self.itemmenu.unpost()

    def add2menu(self, parent, child):
        if child == (SEP, ):
            id = uuid.uuid1()
        elif len(child) > 1 and child[1]:
            id = uuid.uuid1()
            m = LASTLTR.search(child[1])
            if m:

                child = tuple(child)
        else:
            id = child[0]
        if len(child) >= 2:
            leaf = "{0}::{1}".format(child[0], child[1])
        else:
            leaf = "{0}::".format(child[0])
        self.menutree.create_node(leaf, id, parent=parent)

    def confirm(self, parent=None, title="", prompt="", instance="xyz"):
        ok, value = OptionsDialog(parent=parent, title=_("confirm").format(instance), prompt=prompt).getValue()
        return ok

    def selectCalendars(self):
        if self.default_calendars:
            prompt = _("Only items from selected calendars will be displayed.")
            title = CALENDARS
            if self.weekly or self.monthly:
                master = self.canvas
            else:
                master = self.tree

            values = OptionsDialog(parent=self, master=master, title=title, prompt=prompt, opts=loop.calendars, radio=False, yesno=False).getValue()

            if values != loop.calendars:
                loop.calendars = values
                loop.options['calendars'] = values
                data.setConfig(loop.options)
                self.updateCalendars()
        else:
            prompt = _("No calendars have been specified in etmtk.cfg.")
            self.textWindow(self, CALENDARS, prompt, opts=self.options)

    def updateCalendars(self, *args):
        cal_pattern = r'^%s' % '|'.join(
            [x[2] for x in loop.calendars if x[1]])
        self.cal_regex = re.compile(cal_pattern)
        if loop.calendars != self.default_calendars:
            self.calbutton.configure(text="{0}*".format(CALENDARS))
        else:
            self.calbutton.configure(text=CALENDARS)
        self.update()
        self.updateAlerts()
        if self.weekly:
            self.showWeek()
        elif self.monthly:
            self.showMonth()
        else:
            self.showView()

    def quit(self, e=None):
        ans = self.confirm(
            title=_('Quit'),
            prompt=_("Do you really want to quit?"),
            parent=self)
        if ans:
            self.saveGeometry()
            self.destroy()

    def donothing(self, e=None):
        """For testing"""
        logger.debug('donothing')
        return "break"

    def openWithDefault(self, e=None):
        if not self.itemSelected or 'g' not in self.itemSelected:
            return(False)
        path = self.itemSelected['g']

        if windoz:
            os.startfile(path)
            return()
        if mac:
            cmd = 'open' + " {0}".format(path)
        else:
            cmd = 'xdg-open' + " {0}".format(path)
        subprocess.call(cmd, shell=True)
        return

    def printWithDefault(self, s, e=None):
        fo = codecs.open(loop.tmpfile, 'w', loop.options['encoding']['file'])
        # add a trailing formfeed
        # fo.write("{0}".format(s))
        fo.write(s)
        fo.close()
        if windoz:
            os.startfile(loop.tmpfile, "print")
            return
        else:
            cmd = "lp -s -o media='letter' -o cpi=12 -o lpi=8 -o page-left=48 -o page-right=48 -o page-top=48 -o page-bottom=48 {0}\n".format(loop.tmpfile)
            # cmd = "lpr -l {0}".format(loop.tmpfile)
            subprocess.call(cmd, shell=True)
            return

    def showUserDetails(self, e=None):
        if not self.itemSelected or 'u' not in self.itemSelected:
            return
        if not loop.options['user_data']:
            return
        user = self.itemSelected['u']
        if user in loop.options['user_data']:
            detail = "\n".join(loop.options['user_data'][user])
        else:
            detail = _("No record was found for {0}".format(user))
        self.textWindow(self, user, detail, opts=loop.options)
        return

    def dateCalculator(self, event=None):
        prompt = """\
Enter an expression of the form "x [+-] y" where x is a date and y is
either a date or a time period if "-" is used and a time period if "+"
is used. Both x and y can be followed by timezones, e.g.,
     4/20 6:15p US/Central - 4/20 4:50p Asia/Shanghai
                       = 14h25m
     4/20 4:50p Asia/Shanghai + 14h25m US/Central
              = 2014-04-20 18:15-0500
The local timezone is used when none is given."""
        GetString(parent=self, title=_('date and time calculator'), prompt=prompt, opts=loop.options, process=date_calculator)
        return

    def availableDateCalculator(self, event=None):
        prompt = """\
Enter an expression of the form
    start; end; busy
where start and end are dates and busy is comma separated list of
busy dates or busy intervals, .e.g,
    6/1; 6/30; 6/2, 6/14-6/22, 6/5-6/9, 6/11-6/15, 6/17-6/29
returns:
    Sun Jun 01
    Tue Jun 03
    Wed Jun 04
    Tue Jun 10
    Mon Jun 30\
"""
        GetString(parent=self, title=_('available dates calculator'), prompt=prompt, opts={}, process=availableDates, font=self.tkfixedfont)
        return

    def exportToIcal(self, e=None):
        if self.itemSelected:
            self._exportItemToIcal()
        else:
            self._exportActiveToIcal()

    def _exportItemToIcal(self):
        if 'icsitem_file' in loop.options:
            res = export_ical_item(self.itemSelected, loop.options['icsitem_file'])
            if res:
                prompt = _("Selected item successfully exported to {0}".format(loop.options['icsitem_file']))
            else:
                prompt = _("Could not export selected item.")
        else:
            prompt = "icsitem_file is not set in etmtk.cfg"
        MessageWindow(self, 'Selected Item Export', prompt)

    def _exportActiveToIcal(self, event=None):
        if 'icscal_file' in loop.options:
            res = export_ical_active(loop.file2uuids, loop.uuid2hash, loop.options['icscal_file'], loop.calendars)
            if res:
                prompt = _("Active calendars successfully exported to {0}".format(loop.options['icscal_file']))
            else:
                prompt = _("Could not export active calendars.")
        else:
            prompt = "icscal_file is not set in etmtk.cfg"
        MessageWindow(self, 'Active Calendar Export', prompt)

    def newItem(self, e=None):
        # hack to avoid Ctrl-n activation
        if e and e.char != "n":
            return
        if self.weekly or self.monthly:
            master = self.canvas
        else:
            master = self.tree
        if self.view in [AGENDA] and self.active_date:
            if self.itemSelected:
                if 's' in self.itemSelected:
                    text = " @s {0}".format(self.active_date)
                elif 'c' in self.itemSelected:
                    text = " @c {0}".format(self.itemSelected['c'])
            else:
                text = " @s {0}".format(self.active_date)
            changed = SimpleEditor(parent=self, master=master, start=text, options=loop.options).changed
        elif self.view in [DAY, WEEK, MONTH] and self.active_date:
            text = " @s {0}".format(self.active_date)
            changed = SimpleEditor(parent=self, master=master, start=text, options=loop.options).changed
        elif self.view in [KEYWORD, NOTE] and self.itemSelected:
            if self.itemSelected and 'k' in self.itemSelected:
                text = " @k {0}".format(self.itemSelected['k'])
            else:
                text = ""
            changed = SimpleEditor(parent=self, master=master, start=text, options=loop.options).changed
        elif self.view in [TAG]:
            if self.itemSelected and 't' in self.itemSelected:
                text = " @t {0}".format(", ".join(self.itemSelected['t']))
            else:
                text = ""
            changed = SimpleEditor(parent=self, master=master, start=text, options=loop.options).changed
        else:
            changed = SimpleEditor(parent=self, master=master, options=loop.options).changed
        if changed:
            logger.debug('changed, reloading data')
            loop.do_update = True
            self.updateAlerts()
            if self.weekly:
                self.showWeek()
            elif self.monthly:
                self.showMonth()
            else:
                self.showView()

    def which(self, act, instance="xyz"):
        prompt = "\n".join([
            _("You have selected an instance of a repeating"),
            _("item. What do you want to {0}?").format(act)])
        if act == DELETE:
            opt_lst = [
                _("this instance"),
                _("this and all subsequent instances"),
                _("all instances"),
                _("all previous instances")]
        else:
            opt_lst = [
                _("this instance"),
                _("this and all subsequent instances"),
                _("all instances")]

        if self.weekly or self.monthly:
            master = self.canvas
        else:
            master = self.tree
        index, value = OptionsDialog(parent=self, master=master, title=_("instance: {0}").format(instance), prompt=prompt, opts=opt_lst, yesno=False).getValue()
        return index, value

    def copyItem(self, e=None):
        """
        newhsh = selected, rephsh = None
        """
        if not self.itemSelected:
            return
        if e and e.char != 'c':
            return
        if 'r' in self.itemSelected:
            choice, value = self.which(COPY, self.dtSelected)
            logger.debug("{0}: {1}".format(choice, value))
            if not choice:
                self.tree.focus_set()
                return
            self.itemSelected['_dt'] = self.dtSelected
        else:
            ans = self.confirm(
                parent=self.tree,
                title=_('Confirm'),
                prompt=_("Open a copy of this item?"))
            if not ans:
                self.tree.focus_set()
                return
            choice = 3
        hsh_cpy = deepcopy(self.itemSelected)
        hsh_cpy['fileinfo'] = None

        title = _("new item")
        self.mode = 'new'
        if choice in [1, 2]:
            # we need to modify the copy according to the choice
            dt = hsh_cpy['_dt'].replace(
                tzinfo=tzlocal()).astimezone(gettz(hsh_cpy['z']))
            dtn = dt.replace(tzinfo=None)

            if choice == 1:
                # this instance
                for k in ['_r', 'o', '+', '-']:
                    if k in hsh_cpy:
                        del hsh_cpy[k]
                hsh_cpy['s'] = dtn

            elif choice == 2:
                # this and all subsequent instances
                if u'+' in hsh_cpy:
                    tmp_cpy = []
                    for d in hsh_cpy['+']:
                        if d >= dtn:
                            tmp_cpy.append(d)
                    hsh_cpy['+'] = tmp_cpy
                if u'-' in hsh_cpy:
                    tmp_cpy = []
                    for d in hsh_cpy['-']:
                        if d >= dtn:
                            tmp_cpy.append(d)
                    hsh_cpy['-'] = tmp_cpy
                hsh_cpy['s'] = dtn

        changed = SimpleEditor(parent=self, newhsh=hsh_cpy, rephsh=None, options=loop.options, title=title, modified=True).changed
        if changed:
            self.updateAlerts()
            if self.weekly:
                self.showWeek()
            elif self.weekly:
                self.showMonth()
            else:
                self.showView(row=self.topSelected)
        else:
            if self.weekly or self.monthly:
                self.canvas.focus_set()
            else:
                self.tree.focus_set()

    def deleteItem(self, e=None):
        if not self.itemSelected:
            return
        logger.debug('{0}: {1}'.format(self.itemSelected['_summary'], self.dtSelected))
        indx = 3
        if 'r' in self.itemSelected:
            indx, value = self.which(DELETE, self.dtSelected)
            logger.debug("{0}: {1}/{2}".format(self.dtSelected, indx, value))
            if not indx:
                if self.weekly or self.monthly:
                    self.canvas.focus_set()
                else:
                    self.tree.focus_set()
                return
            self.itemSelected['_dt'] = self.dtSelected
        else:
            ans = self.confirm(
                title=_('Confirm'),
                prompt=_("Delete this item?"),
                parent=self.tree)
            if not ans:
                self.tree.focus_set()
                return
        loop.item_hsh = self.itemSelected
        loop.cmd_do_delete(indx)

        self.updateAlerts()
        if self.weekly:
            self.canvas.focus_set()
            self.showWeek()
        elif self.monthly:
            self.canvas.focus_set()
            self.showMonth()
        else:
            self.tree.focus_set()
            self.showView(row=self.topSelected)

    def moveItem(self, e=None):
        if not self.itemSelected:
            return
        if e and e.char != 'm':
            return
        logger.debug('{0}: {1}'.format(self.itemSelected['_summary'], self.dtSelected))
        oldrp, begline, endline = self.itemSelected['fileinfo']
        oldfile = os.path.join(loop.options['datadir'], oldrp)
        newfile = self.getDataFile(title="moving from {0}:".format(oldrp), start=oldfile)
        if not (newfile and os.path.isfile(newfile)):
            return
        if newfile == oldfile:
            return
        ret = loop.append_item(self.itemSelected, newfile)
        if ret != "break":
            # post message and quit
            prompt = _("""\
Adding item to {1} failed - aborted removing item from {2}""".format(
                newfile, oldfile))
            MessageWindow(self, 'Error', prompt)
            return
        loop.item_hsh = self.itemSelected
        ret = loop.delete_item()

        self.updateAlerts()
        if self.weekly:
            self.canvas.focus_set()
            self.showWeek()
        elif self.monthly:
            self.canvas.focus_set()
            self.showWeek()
        else:
            self.tree.focus_set()
            self.showView(row=self.topSelected)

    def editItem(self, e=None):
        if not self.itemSelected:
            return
        logger.debug('starting editItem: {0}; {1}, {2}'.format(self.itemSelected['_summary'], self.dtSelected, type(self.dtSelected)))
        choice = 3
        title = ETM
        start_text = None
        filename = None
        if self.itemSelected['itemtype'] == '$':
            start_text = self.itemSelected['entry']
            hsh_rev = deepcopy(self.itemSelected)
        elif 'r' in self.itemSelected:
            # repeating
            choice, value = self.which(EDIT, self.dtSelected)
            logger.debug("{0}: {1}".format(choice, value))
            if self.weekly or self.monthly:
                self.canvas.focus_set()
            else:
                self.tree.focus_set()
            logger.debug(('dtSelected: {0}, {1}'.format(type(self.dtSelected), self.dtSelected)))
            self.itemSelected['_dt'] = self.dtSelected
            if not choice:
                self.tree.focus_set()
                return
        hsh_rev = hsh_cpy = None
        self.mode = 2  # replace
        if choice in [1, 2]:
            self.mode = 3  # new and replace - both newhsh and rephsh
            title = _("new item")
            hsh_cpy = deepcopy(self.itemSelected)
            hsh_rev = deepcopy(self.itemSelected)
            # we will be editing and adding hsh_cpy and replacing hsh_rev

            dt = hsh_cpy['_dt'].replace(
                tzinfo=tzlocal()).astimezone(gettz(hsh_cpy['z']))
            dtn = dt.replace(tzinfo=None)

            if choice == 1:
                # this instance
                if '+' in hsh_rev and dtn in hsh_rev['+']:
                    hsh_rev['+'].remove(dtn)
                    if not hsh_rev['+'] and hsh_rev['r'] == 'l':
                        del hsh_rev['r']
                        del hsh_rev['_r']
                else:
                    hsh_rev.setdefault('-', []).append(dt)
                for k in ['_r', 'o', '+', '-']:
                    if k in hsh_cpy:
                        del hsh_cpy[k]
                hsh_cpy['s'] = dtn

            elif choice == 2:
                # this and all subsequent instances
                tmp = []
                for h in hsh_rev['_r']:
                    if 'f' in h and h['f'] != u'l':
                        h['u'] = dt - ONEMINUTE
                    tmp.append(h)
                hsh_rev['_r'] = tmp
                if u'+' in hsh_rev:
                    tmp_rev = []
                    tmp_cpy = []
                    for d in hsh_rev['+']:
                        if d < dtn:
                            tmp_rev.append(d)
                        else:
                            tmp_cpy.append(d)
                    hsh_rev['+'] = tmp_rev
                    hsh_cpy['+'] = tmp_cpy
                if u'-' in hsh_rev:
                    tmp_rev = []
                    tmp_cpy = []
                    for d in hsh_rev['-']:
                        if d < dtn:
                            tmp_rev.append(d)
                        else:
                            tmp_cpy.append(d)
                    hsh_rev['-'] = tmp_rev
                    hsh_cpy['-'] = tmp_cpy
                hsh_cpy['s'] = dtn
        else:  # replace
            self.mode = 2
            hsh_rev = deepcopy(self.itemSelected)

        logger.debug("mode: {0}; newhsh: {1}; rephsh: {2}".format(self.mode, hsh_cpy is not None, hsh_rev is not None))
        changed = SimpleEditor(parent=self, file=filename, newhsh=hsh_cpy, rephsh=hsh_rev, options=loop.options, title=title, start=start_text).changed

        if changed:
            logger.debug("starting if changed")
            loop.do_update = True
            self.updateAlerts()
            if self.weekly:
                self.canvas.focus_set()
                self.showWeek()
            elif self.monthly:
                self.canvas.focus_set()
                self.showMonth()
            else:
                self.tree.focus_set()
                self.showView(row=self.topSelected)
                self.update_idletasks()
            logger.debug("leaving if changed")

        else:
            if self.weekly or self.monthly:
                self.canvas.focus_set()
            else:
                self.tree.focus_set()
        logger.debug('ending editItem')
        return

    def editItemFile(self, e=None):
        if not self.itemSelected:
            return
        logger.debug('starting editItemFile: {0}; {1}, {2}, {3}'.format(self.itemSelected['_summary'], self.dtSelected, type(self.dtSelected), self.itemSelected['fileinfo']))
        self.editFile(e, file=os.path.join(loop.options['datadir'], self.itemSelected['fileinfo'][0]), line=self.itemSelected['fileinfo'][1])

    def editFile(self, e=None, file=None, line=None, config=False):
        if e and e.char and e.char not in ["F", "E", "C", "S", "P"]:
            logger.debug('e.char: "{0}"'.format(e.char))
            return
        titlefile = os.path.normpath(relpath(file, loop.options['datadir']))
        logger.debug('file: {0}; config: {1}'.format(file, config))
        if self.weekly or self.monthly:
            master = self.canvas
        else:
            master = self.tree
        changed = SimpleEditor(parent=self, master=master, file=file, line=line, options=loop.options, title=titlefile).changed
        logger.debug('changed: {0}'.format(changed))
        if changed:
            logger.debug("config: {0}".format(config))
            if config:
                current_options = deepcopy(loop.options)
                (user_options, options, use_locale) = data.get_options(
                    d=loop.options['etmdir'])
                loop.options = options
                if options['calendars'] != current_options['calendars']:
                    self.updateCalendars()
            loop.do_update = True

            logger.debug("changed - calling updateAlerts")
            self.updateAlerts()
            if self.weekly:
                self.canvas.focus_set()
                self.showWeek()
            elif self.monthly:
                self.canvas.focus_set()
                self.showMonth()
            else:
                self.tree.focus_set()
                self.showView()
        return changed

    def editConfig(self, e=None):
        file = loop.options['config']
        self.editFile(e, file=file, config=True)

    def editCfgFiles(self, e=None):
        other = []
        if 'cfg_files' in loop.options:
            for key in ['completions', 'reports', 'users']:
                other.extend(loop.options['cfg_files'][key])
        prefix, tuples = getFileTuples(loop.options['datadir'], include=r'*.cfg', other=other)
        ret = FileChoice(self, "open configuration file", prefix=prefix, list=tuples).returnValue()
        if not (ret and os.path.isfile(ret)):
            return False
        self.editFile(e, file=ret, config=True)

    def getReportsFile(self, e=None):
        ret = FileChoice(self, "append to reports file", prefix=self.loop.options['etmdir'], list=self.loop.options['report_files']).returnValue()
        if not (ret and os.path.isfile(ret)):
            return False
        return ret

    def getDataFile(self, e=None, title="data file", start=''):
        prefix, tuples = getFileTuples(loop.options['datadir'], include=r'*.txt')
        ret = FileChoice(self, title, prefix=prefix, list=tuples, start=start).returnValue()
        if not (ret and os.path.isfile(ret)):
            return False
        return ret

    def editScratch(self, e=None):
        file = loop.options['scratchpad']
        self.editFile(e, file=file)

    def editData(self, e=None):
        if e and e.char != "F":
            return
        prefix, tuples = getFileTuples(loop.options['datadir'], include=r'*.txt', all=False)
        ret = FileChoice(self, "open data file", prefix=prefix, list=tuples).returnValue()
        if not (ret and os.path.isfile(ret)):
            return False
        self.editFile(e, file=ret)

    def newFile(self, e=None):
        if e and e.char != "N":
            return
        other = [os.path.join(loop.options['etmdir'], 'etmtk.cfg')]
        if 'cfg_files' in loop.options:
            for key in ['completions', 'reports', 'users']:
                other.extend(loop.options['cfg_files'][key])
        prefix, tuples = getFileTuples(loop.options['datadir'], include=r'*', other=other, all=True)
        filename = FileChoice(self, "create new file", prefix=prefix, list=tuples, new=True).returnValue()
        if not filename:
            return
        if os.path.isfile(filename):
            prompt = _("Aborting. File {0} already exists.").format(filename)
            MessageWindow(self, title=_("new file"), prompt=prompt)
        else:
            pth = os.path.split(filename)[0]
            if not os.path.isdir(pth):
                os.makedirs(pth)
            fo = codecs.open(filename, 'w', loop.options['encoding']['file'])
            fo.write("")
            fo.close()
            prompt = _('created: {0}').format(filename)
            if self.weekly or self.monthly:
                p = self.canvas
            else:
                p = self.tree
            ans = self.confirm(
                parent=p,
                title=_('etm'),
                prompt=_("file: {0}\nhas been created.\nOpen it for editing?").format(filename))
            if ans:
                self.editFile(None, filename)

    def finishItem(self, e=None):
        if e and e.char != "f":
            return
        if not (self.itemSelected and self.itemSelected['itemtype'] in ['-', '+', '%']):
            return
        prompt = _("""\
Enter the completion date for the item or return an empty string to
use the current date. Relative dates and fuzzy parsing are supported.""")
        d = GetDateTime(parent=self, title=_('date'), prompt=prompt)
        chosen_day = d.value
        if chosen_day is None:
            return ()
        logger.debug('completion date: {0}'.format(chosen_day))
        loop.item_hsh = self.itemSelected
        loop.cmd_do_finish(chosen_day, options=loop.options)

        self.updateAlerts()
        if self.weekly:
            self.canvas.focus_set()
            self.showWeek()
        elif self.monthly:
            self.canvas.focus_set()
            self.showMonth()
        else:
            self.tree.focus_set()
            self.showView(row=self.topSelected)

    def rescheduleItem(self, e=None):
        if e and e.char != 'r':
            return
        if not self.itemSelected:
            return
        loop.item_hsh = self.itemSelected
        if self.dtSelected:
            loop.old_dt = old_dt = self.dtSelected
            title = _('rescheduling {0}').format(old_dt.strftime(
                rrulefmt))
        else:
            loop.old_dt = None
            title = _('scheduling an undated item')
        logger.debug('dtSelected: {0}'.format(self.dtSelected))
        prompt = _("""\
Enter the new date and time for the item or return an empty string to
use the current time. Relative dates and fuzzy parsing are supported.""")
        dt = GetDateTime(parent=self, title=title, prompt=prompt)
        new_dt = dt.value
        if new_dt is None:
            return
        new_dtn = new_dt.astimezone(gettz(self.itemSelected['z'])).replace(tzinfo=None)
        logger.debug('rescheduled from {0} to {1}'.format(self.dtSelected, new_dtn))
        loop.cmd_do_reschedule(new_dtn)

        self.updateAlerts()
        if self.weekly:
            self.canvas.focus_set()
            self.showWeek()
        elif self.monthly:
            self.canvas.focus_set()
            self.showMonthly()
        else:
            self.tree.focus_set()
            self.showView(row=self.topSelected)

    def scheduleNewItem(self, e=None):
        if e and e.char != 'i':
            return
        if not self.itemSelected:
            return
        loop.item_hsh = self.itemSelected
        if self.dtSelected:
            loop.old_dt = self.dtSelected
            title = _('adding new instance')
        else:
            loop.old_dt = None
            title = _('scheduling an undated item')
        logger.debug('dtSelected: {0}'.format(self.dtSelected))
        prompt = _("""\
Enter the new date and time for the item or return an empty string to
use the current time. Relative dates and fuzzy parsing are supported.""")
        dt = GetDateTime(parent=self, title=title, prompt=prompt)
        new_dt = dt.value
        if new_dt is None:
            return
        new_dtn = new_dt.astimezone(gettz(self.itemSelected['z'])).replace(tzinfo=None)
        logger.debug('scheduled new instance: {0}'.format(new_dtn))
        loop.cmd_do_schedulenew(new_dtn)

        self.updateAlerts()
        if self.weekly:
            self.canvas.focus_set()
            self.showWeek()
        elif self.weekly:
            self.canvas.focus_set()
            self.showMonth()
        else:
            self.tree.focus_set()
            self.showView(row=self.topSelected)

    def showAlerts(self, e=None):
        # hack to avoid activating with Ctrl-a
        if e and e.char != "a":
            return
        t = _('remaining alerts for today')
        header = "{0:^7}\t{1:^7}\t{2:<8}{3:<26}".format(
            _('alert'),
            _('event'),
            _('type'),
            _('summary'))
        divider = '-' * 52
        if self.activeAlerts:

            s = '%s\n%s\n%s' % (
                header, divider, "\n".join(
                    ["{0:^7}\t{1:^7}\t{2:<8}{3:<26}".format(
                        x[2]['alert_time'], x[2]['_event_time'],
                        ", ".join(x[2]['_alert_action']),
                        utf8(x[2]['summary'][:26])) for x in self.activeAlerts]))
        else:
            s = _("none")
        self.textWindow(self, t, s, opts=self.options)

    def agendaView(self, e=None):
        self.setView(AGENDA)

    def dayView(self, e=None):
        self.setView(DAY)

    def pathView(self, e=None):
        self.setView(PATH)

    def keywordView(self, e=None):
        self.setView(KEYWORD)

    def tagView(self, e=None):
        self.setView(TAG)

    def customView(self, e=None):
        # TODO: finish this
        self.content.delete("1.0", END)
        self.fltr.forget()
        self.clearTree()
        self.setView(CUSTOM)
        pass

    def noteView(self, e=None):
        self.setView(NOTE)

    def setView(self, view, row=None):
        self.rowSelected = None
        if view != WEEK and self.weekly:
            self.closeWeekly()
        if view != MONTH and self.monthly:
            self.closeMonthly()
        if view == CUSTOM:
            # self.reportbar.pack(side="top")
            logger.debug('showing custom_box')
            self.custom_box.pack(side="top", fill="x", padx=3)
            self.custom_box.focus_set()
            for i in range(len(self.rm_options)):
                self.custommenu.entryconfig(i, state="normal")
        else:
            if self.view == CUSTOM:
                # we're leaving custom view
                logger.debug('removing custom_box')
                self.custom_box.forget()
                for i in range(len(self.rm_options)):
                    self.custommenu.entryconfig(i, state="disabled")
                self.saveSpecs()
                self.fltr.pack(side="left", padx=0, expand=1, fill=X)
        self.view = view
        logger.debug("setView view: {0}. Calling showView.".format(view))
        self.showView(row=row)

    def filterView(self, e, *args):
        if self.weekly or self.monthly:
            return
        self.depth2id = {}
        fltr = self.filterValue.get()
        cmd = "{0} {1}".format(
            self.vm_options[self.vm_opts.index(self.view)][1], fltr)
        self.mode = 'command'
        self.process_input(event=e, cmd=cmd)

    def showView(self, e=None, row=None):
        tt = TimeIt(loglevel=2, label="{0} view".format(self.view))
        if self.weekly or self.monthly:
            return
        self.depth2id = {}
        self.currentView.set(self.view)
        fltr = self.filterValue.get()
        if self.view != CUSTOM:
            cmd = "{0} {1}".format(
                self.vm_options[self.vm_opts.index(self.view)][1], fltr)
            self.mode = 'command'
            self.process_input(event=e, cmd=cmd)
            if row:
                row = max(0, row - 1)
                self.tree.yview(row)
        tt.stop()

    def showBusyPeriods(self, e=None):
        if e and e.char != "b":
            return
        if self.busy_info is None:
            return()
        theweek, weekdays, busy_lst, occasion_lst = self.busy_info
        theweek = _("Busy periods in {0}").format(theweek)

        lines = [theweek, '-' * len(theweek)]
        ampm = loop.options['ampm']
        s1 = s2 = ''
        for i in range(len(busy_lst)):
            times = []
            for tup in busy_lst[i]:
                t1 = max(7 * 60, tup[0])
                t2 = min(23 * 60, max(420, tup[1]))
                if t1 != t2:
                    t1h, t1m = (t1 // 60, t1 % 60)
                    t2h, t2m = (t2 // 60, t2 % 60)
                    if ampm:
                        if t1h == 12:
                            s1 = 'pm'
                        elif t1h > 12:
                            t1h -= 12
                            s1 = 'pm'
                        else:
                            s1 = 'am'
                        if t2h == 12:
                            s2 = 'pm'
                        elif t2h > 12:
                            t2h -= 12
                            s2 = 'pm'
                        else:
                            s2 = 'am'

                    T1 = "%d:%02d%s" % (t1h, t1m, s1)
                    T2 = "%d:%02d%s" % (t2h, t2m, s2)

                    times.append("%s-%s" % (T1, T2))
            if times:
                lines.append("%s: %s" % (weekdays[i], "; ".join(times)))
        s = "\n".join(lines)
        self.textWindow(parent=self, title=_('busy times'), prompt=s, opts=self.options)

    def showFreePeriods(self, e=None):
        if e and e.char != 'f':
            return
        if self.busy_info is None or 'freetimes' not in loop.options:
            return()
        ampm = loop.options['ampm']
        om = loop.options['freetimes']['opening']
        cm = loop.options['freetimes']['closing']
        mm = loop.options['freetimes']['minimum']
        bm = loop.options['freetimes']['buffer']
        prompt = _("""\
Enter the shortest time period you want displayed in minutes.""")
        mm = GetInteger(parent=self, title=_("depth"), prompt=prompt, opts=[0], default=mm).value
        if mm is None:
            self.canvas.focus_set()
            return
        theweek, weekdays, busy_lst, occasion_lst = self.busy_info
        theweek = _("Free periods in {0}").format(theweek)
        lines = [theweek, '-' * len(theweek)]
        s1 = s2 = ''
        for i in range(len(busy_lst)):
            times = []
            busy = []
            for tup in busy_lst[i]:
                t1 = max(om, tup[0] - bm)
                t2 = min(cm, max(om, tup[1]) + bm)
                if t2 > t1:
                    busy.append((t1, t2))
            lastend = om
            free = []
            for tup in busy:
                if tup[0] - lastend >= mm:
                    free.append((lastend, tup[0]))
                lastend = tup[1]
            if cm - lastend >= mm:
                free.append((lastend, cm))
            for tup in free:
                t1, t2 = tup
                if t1 != t2:
                    t1h, t1m = (t1 // 60, t1 % 60)
                    t2h, t2m = (t2 // 60, t2 % 60)
                    if ampm:
                        if t1h == 12:
                            s1 = 'pm'
                        elif t1h > 12:
                            t1h -= 12
                            s1 = 'pm'
                        else:
                            s1 = 'am'
                        if t2h == 12:
                            s2 = 'pm'
                        elif t2h > 12:
                            t2h -= 12
                            s2 = 'pm'
                        else:
                            s2 = 'am'
                    T1 = "%d:%02d%s" % (t1h, t1m, s1)
                    T2 = "%d:%02d%s" % (t2h, t2m, s2)
                    times.append("%s-%s" % (T1, T2))
            if times:
                lines.append("%s: %s" % (weekdays[i], "; ".join(times)))
        lines.append('-' * len(theweek))
        lines.append("Only periods of at least {0} minutes are displayed.".format(mm))
        s = "\n".join(lines)
        self.textWindow(parent=self, title=_('free times'), prompt=s, opts=self.options)

    def setWeek(self, chosen_day=None):
        if chosen_day is None:
            chosen_day = get_current_time()
        yn, wn, dn = chosen_day.isocalendar()
        self.prev_week = chosen_day - 7 * ONEDAY
        self.next_week = chosen_day + 7 * ONEDAY
        self.curr_week = chosen_day
        if dn > 1:
            days = dn - 1
        else:
            days = 0
        self.week_beg = weekbeg = chosen_day - days * ONEDAY
        logger.debug('week_beg: {0}'.format(self.week_beg))
        weekend = chosen_day + (6 - days) * ONEDAY
        weekdays = []

        day = weekbeg
        self.active_date = weekbeg.date()
        busy_lst = []
        occasion_lst = []
        matching = self.cal_regex is not None and self.default_regex is not None
        while day <= weekend:
            weekdays.append(fmt_weekday(day))
            isokey = day.isocalendar()

            if isokey in loop.occasions:
                bt = []
                for item in loop.occasions[isokey]:
                    it = list(item)
                    if matching:
                        if not self.cal_regex.match(it[-1]):
                            continue
                        mtch = (self.default_regex.match(it[-1]) is not None)
                    else:
                        mtch = True
                    it.append(mtch)
                    item = tuple(it)
                    bt.append(item)
                occasion_lst.append(bt)
            else:
                occasion_lst.append([])

            if isokey in loop.busytimes:
                bt = []
                for item in loop.busytimes[isokey]:
                    it = list(item)
                    if it[0] == it[1]:
                        # skip reminders
                        continue
                    if matching:
                        if not self.cal_regex.match(it[-1]):
                            continue
                        mtch = (self.default_regex.match(it[-1]) is not None)
                    else:
                        mtch = True
                    it.append(mtch)
                    item = tuple(it)
                    bt.append(item)
                busy_lst.append(bt)
            else:
                busy_lst.append([])
            day = day + ONEDAY

        ybeg = weekbeg.year
        yend = weekend.year
        mbeg = weekbeg.month
        mend = weekend.month
        # busy_lst: list of days 0 (monday) - 6 (sunday) where each day is a list of (start minute, end minute, id, summary-time str and file info) tuples

        if mbeg == mend:
            header = "{0} - {1}".format(
                fmt_dt(weekbeg, '%b %d'), fmt_dt(weekend, '%d, %Y'))
        elif ybeg == yend:
            header = "{0} - {1}".format(
                fmt_dt(weekbeg, '%b %d'), fmt_dt(weekend, '%b %d, %Y'))
        else:
            header = "{0} - {1}".format(
                fmt_dt(weekbeg, '%b %d, %Y'), fmt_dt(weekend, '%b %d, %Y'))
        header = leadingzero.sub('', header)
        theweek = _("Week {0}: {1}").format(wn, header)
        self.busy_info = (theweek, weekdays, busy_lst, occasion_lst)
        return self.busy_info

    def configureCanvas(self, e=None):
        if self.weekly:
            self.showWeek()
        elif self.monthly:
            self.showMonth()
        else:
            return

    def closeWeekly(self, event=None):
        self.today_col = None
        for i in range(14, 20):
            self.viewmenu.entryconfig(i, state="disabled")
        self.canvas.pack_forget()
        self.weekly = False
        self.fltr.pack(side=LEFT, padx=8, pady=0, fill="x", expand=1)
        self.tree.pack(fill="both", expand=1, padx=4, pady=0)
        self.update_idletasks()
        if self.filter_active:
            self.viewmenu.entryconfig(6, state="disabled")
            self.viewmenu.entryconfig(7, state="normal")
        else:
            self.viewmenu.entryconfig(6, state="normal")
            self.viewmenu.entryconfig(7, state="disabled")

        for i in [4, 5, 8, 9, 10, 11, 12]:
            self.viewmenu.entryconfig(i, state="normal")
        self.bind("<Control-f>", self.setFilter)

    def showWeekly(self, event=None, chosen_day=None):
        """
        Open the canvas at the current week
        """
        self.custom_box.forget()
        tt = TimeIt(loglevel=2, label="week view")
        logger.debug("chosen_day: {0}; active_date: {1}".format(chosen_day, self.active_date))
        if self.weekly:
            # we're in weekview already
            return
        if self.monthly:
            self.closeMonthly()
        self.content.delete("1.0", END)
        self.weekly = True
        self.tree.pack_forget()
        self.fltr.pack_forget()
        for i in range(4, 13):
            self.viewmenu.entryconfig(i, state="disabled")

        self.view = WEEK
        self.currentView.set(WEEK)

        if chosen_day is not None:
            self.chosen_day = chosen_day
        elif self.active_date:
            self.chosen_day = datetime.combine(self.active_date, time())
        else:
            self.chosen_day = get_current_time()

        self.canvas.configure(highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand=1, padx=4, pady=0)

        if self.options['ampm']:
            self.hours = ["{0}am".format(i) for i in range(7, 12)] + ['12pm'] + ["{0}pm".format(i) for i in range(1, 12)]
        else:
            self.hours = ["{0}:00".format(i) for i in range(7, 24)]
        for i in range(14, 20):
            self.viewmenu.entryconfig(i, state="normal")
        self.canvas.focus_set()
        self.showWeek()
        tt.stop()

    def priorWeekMonth(self, event=None):
        if self.weekly:
            self.showWeek(event, week=-1)
        elif self.monthly:
            self.showMonth(event, month=-1)

    def nextWeekMonth(self, event=None):
        if self.weekly:
            self.showWeek(event, week=1)
        elif self.monthly:
            self.showMonth(event, month=1)

    def showWeek(self, event=None, week=None):
        self.canvas.focus_set()
        self.selectedId = None
        self.current_day = get_current_time().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        logger.debug('self.current_day: {0}, minutes: {1}'.format(self.current_day, self.current_minutes))
        self.x_win = self.canvas.winfo_width()
        self.y_win = self.canvas.winfo_height()
        logger.debug("win: {0}, {1}".format(self.x_win, self.y_win))
        logger.debug("event: {0}, week: {1}, chosen_day: {2}".format(event, week, self.chosen_day))
        if week in [-1, 0, 1]:
            if week == 0:
                day = get_current_time()
            elif week == 1:
                day = self.next_week
            elif week == -1:
                day = self.prev_week
            self.chosen_day = day
        elif self.chosen_day:
            day = self.chosen_day
        else:
            return
        logger.debug('week active_date: {0}'.format(self.active_date))
        theweek, weekdays, busy_lst, occasion_lst = self.setWeek(day)
        self.OnSelect()
        self.canvas.delete("all")
        l = 50
        r = 8
        t = 56
        b = 8
        if event:
            logger.debug('event: {0}'.format(event))
            w, h = event.width, event.height
            if type(w) is int and type(h) is int:
                self.canvas_width = w
                self.canvas_height = h
            else:
                w = self.canvas.winfo_width()
                h = self.canvas.winfo_height()
        else:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
        logger.debug("w: {0}, h: {1}, l: {2}, t: {3}".format(w, h, l, t))
        self.margins = (w, h, l, r, t, b)
        self.week_x = x = Decimal(w - 1 - l - r) / Decimal(7)
        self.week_y = y = Decimal(h - 1 - t - b) / Decimal(16)
        logger.debug("x: {0}, y: {1}".format(x, y))

        # week
        p = l + (w - 1 - l - r) / 2, 20
        self.canvas.create_text(p, text=theweek)
        self.busyHsh = {}

        # occasions
        occasion_ids = []
        for i in range(7):
            day = (self.week_beg + i * ONEDAY).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
            if not occasion_lst[i]:
                continue
            occasions = occasion_lst[i]
            start_x = l + i * x
            end_x = start_x + x
            for tup in occasions:
                xy = int(start_x), int(t), int(end_x), int(t + y * 16)
                id = self.canvas.create_rectangle(xy, fill=OCCASIONFILL, outline="", width=0, tag='occasion')
                tmp = list(tup)
                tmp.append(day)
                self.busyHsh[id] = tmp
                occasion_ids.append(id)
        self.y_per_minute = y_per_minute = y / Decimal(60)
        busy_ids = []
        conf_ids = []
        self.today_id = None
        self.today_col = None
        self.timeline = None
        self.last_minutes = None
        for i in range(7):
            day = (self.week_beg + i * ONEDAY).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
            busy_times = busy_lst[i]
            start_x = l + i * x
            end_x = start_x + x
            if day == self.current_day:
                self.today_col = i
                xy = int(start_x), int(t), int(end_x), int(t + y * 16)
                self.canvas.create_rectangle(xy, fill=CURRENTFILL, outline="", width=0, tag='current_day')
            if not busy_times and self.today_col is None:
                continue
            for tup in busy_times:
                conf = None
                mtch = tup[5]
                if mtch:
                    busyColor = DEFAULTFILL
                    ttag = 'default'
                else:
                    busyColor = OTHERFILL
                    ttag = 'other'
                daytime = day + tup[0] * ONEMINUTE
                t1 = t + (max(7 * 60, tup[0]) - 7 * 60) * y_per_minute

                t2 = t + min(23 * 60, max(7 * 60, tup[1]) - 7 * 60) * y_per_minute

                xy = int(start_x), int(max(t, t1)), int(end_x), int(min(t2, t + y * 16))
                conf = self.canvas.find_overlapping(*xy)
                id = self.canvas.create_rectangle(xy, fill=busyColor, width=0, tag=ttag)
                conf = [z for z in conf if z in busy_ids]
                busy_ids.append(id)
                conf_ids.extend(conf)
                if conf:
                    bb1 = self.canvas.bbox(id)
                    bb2 = self.canvas.bbox(*conf)

                    # we want the max of bb1[1], bb2[1]
                    # and the min of bb1[4], bb2[4]
                    ol = bb1[0], max(bb1[1], bb2[1]), bb1[2], min(bb1[3], bb2[3])
                    self.canvas.create_rectangle(ol, fill=CONFLICTFILL, outline="", width=0, tag="conflict")

                tmp = list(tup[2:])  # id, time str, summary and file info
                tmp.append(daytime)
                self.busyHsh[id] = tmp
            if self.today_col is not None:
                xy = self.get_timeline()
                if xy:
                    self.canvas.delete('current_time')
                    self.canvas.create_line(xy, width=2, fill=CURRENTLINE, tag='current_time')

        self.busy_ids = busy_ids
        self.conf_ids = conf_ids
        for id in occasion_ids + busy_ids + conf_ids:  # + conf_ids:
            self.canvas.tag_bind(id, '<Any-Enter>', self.on_enter_item)

        self.canvas.bind('<Escape>', self.on_clear_item)

        self.canvas_ids = [z for z in self.busyHsh.keys()]
        self.canvas_ids.sort()
        self.canvas_idpos = None
        # border
        xy = int(l), int(t), int(l + x * 7), int(t + y * 16)
        self.canvas.create_rectangle(xy, tag="grid")

        # verticals
        for i in range(1, 7):

            xy = int(l + x * i), int(t), int(l + x * i), int(t + y * 16)
            self.canvas.create_line(xy, fill=LINECOLOR, tag="grid")
        # horizontals
        for j in range(1, 16):
            xy = int(l), int(t + y * j), int(l + x * 7), int(t + y * j)
            self.canvas.create_line(xy, fill=LINECOLOR, tag="grid")
        # hours
        for j in range(17):
            if j % 2:
                p = int(l - 5), int(t + y * j)
                self.canvas.create_text(p, text=self.hours[j], anchor="e")
        # days
        for i in range(7):

            p = int(l + x / 2 + x * i), int(t - 13)

            if self.today_col is not None and i == self.today_col:
                self.canvas.create_text(p, text="{0}".format(weekdays[i]), fill=CURRENTLINE)
            else:
                self.canvas.create_text(p, text="{0}".format(weekdays[i]))

    def closeMonthly(self, event=None):
        self.today_col = None
        for i in range(14, 20):
            self.viewmenu.entryconfig(i, state="disabled")
        self.canvas.pack_forget()
        self.monthly = False
        self.fltr.pack(side=LEFT, padx=8, pady=0, fill="x", expand=1)
        self.tree.pack(fill="both", expand=1, padx=4, pady=0)
        self.update_idletasks()
        if self.filter_active:
            self.viewmenu.entryconfig(6, state="disabled")
            self.viewmenu.entryconfig(7, state="normal")
        else:
            self.viewmenu.entryconfig(6, state="normal")
            self.viewmenu.entryconfig(7, state="disabled")

        for i in [4, 5, 8, 9, 10, 11, 12]:
            self.viewmenu.entryconfig(i, state="normal")
        self.bind("<Control-f>", self.setFilter)

    def showMonthly(self, event=None, chosen_day=None):
        """
        Open the canvas at the current week
        """
        self.custom_box.forget()
        tt = TimeIt(loglevel=2, label="month view")
        logger.debug("chosen_day: {0}; active_date: {1}".format(chosen_day, self.active_date))
        if self.monthly:
            # we're in weekview already
            return
        if self.weekly:
            self.closeWeekly()
        self.content.delete("1.0", END)
        self.monthly = True
        self.tree.pack_forget()
        self.fltr.pack_forget()
        for i in range(4, 13):
            self.viewmenu.entryconfig(i, state="disabled")

        self.view = MONTH
        self.currentView.set(MONTH)

        if chosen_day is not None:
            self.chosen_day = chosen_day
        elif self.active_date:
            self.chosen_day = datetime.combine(self.active_date, time())
        else:
            self.chosen_day = get_current_time()

        self.canvas.configure(highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand=1, padx=4, pady=0)

        for i in range(14, 20):
            self.viewmenu.entryconfig(i, state="normal")
        self.canvas.focus_set()
        self.showMonth()
        tt.stop()

    def showMonth(self, event=None, month=None):
        self.canvas.focus_set()
        self.selectedId = None
        matching = self.cal_regex is not None and self.default_regex is not None
        busy_lst = []
        busy_dates = []
        occasion_lst = []

        self.current_day = get_current_time().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

        logger.debug('self.current_day: {0}, minutes: {1}'.format(self.current_day, self.current_minutes))
        self.x_win = self.canvas.winfo_width()
        self.y_win = self.canvas.winfo_height()
        if month in [-1, 0, 1]:
            if month == 0:
                self.year_month = [self.current_day.year, self.current_day.month]
            elif month == 1:
                self.year_month[1] += 1
                if self.year_month[1] > 12:
                    self.year_month[1] -= 12
                    self.year_month[0] += 1
            elif month == -1:
                self.year_month[1] -= 1
                if self.year_month[1] < 1:
                    self.year_month[1] += 12
                    self.year_month[0] -= 1
        elif self.chosen_day:
            self.year_month = [self.chosen_day.year, self.chosen_day.month]
        else:
            return
        logger.debug('month active_date: {0}'.format(self.active_date))
        weeks = self.monthly_calendar.monthdatescalendar(*self.year_month)
        num_weeks = len(weeks)
        weekdays = [x.strftime("%a") for x in weeks[0]]
        # weeknumbers = [x[0].strftime("%W") for x in weeks]
        weeknumbers = [x[0].isocalendar()[1] for x in weeks]
        themonth = weeks[1][0].strftime("%B %Y")
        self.canvas.delete("all")
        l = 36
        r = 8
        t = 56
        b = 8
        if event:
            logger.debug('event: {0}'.format(event))
            w, h = event.width, event.height
            if type(w) is int and type(h) is int:
                self.canvas_width = w
                self.canvas_height = h
            else:
                w = self.canvas.winfo_width()
                h = self.canvas.winfo_height()
        else:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
        logger.debug("w: {0}, h: {1}, l: {2}, t: {3}".format(w, h, l, t))

        self.margins = (w, h, l, r, t, b)

        self.month_x = x_ = Decimal(w - 1 - l - r) / Decimal(7)
        self.month_y = y_ = Decimal(h - 1 - t - b) / Decimal(num_weeks)

        logger.debug("x: {0}, y: {1}".format(x_, y_))

        # month
        p = l + (w - 1 - l - r) / 2, 20
        self.canvas.create_text(p, text="{0}".format(themonth))
        self.busyHsh = {}

        # occasions
        busy_ids = set([])
        monthid2date = {}

        self.canvas.bind('<Escape>', self.on_clear_item)

        # monthdays
        for j in range(num_weeks):
            for i in range(7):
                busytimes = 0
                start_x = l + i * x_
                end_x = start_x + x_
                start_y = int(t + y_ * j)
                end_y = start_y + y_
                xy = start_x, start_y, end_x, end_y
                p = int(l + x_ / 2 + x_ * i), int(t + y_ * j + y_ / 2)
                thisdate = weeks[j][i]
                isokey = thisdate.isocalendar()
                month = thisdate.month
                fill = None
                tags = []
                if (month != self.year_month[1]):
                    fill = "gray75"
                else:
                    id = self.canvas.create_rectangle(xy, outline="", width=0)
                    busy_ids.add(id)
                    monthid2date[id] = thisdate
                    today = (thisdate == self.current_day.date())
                    bt = []
                    if today:
                        tags.append('current_day')
                    if isokey in loop.occasions:
                        bt = []
                        for item in loop.occasions[isokey]:
                            it = list(item)
                            if matching:
                                if not self.cal_regex.match(it[-1]):
                                    continue
                                mtch = (self.default_regex.match(it[-1]) is not None)
                            else:
                                mtch = True
                            it.append(mtch)
                            item = tuple(it)
                            bt.append(item)
                        occasion_lst.append(bt)
                        if bt:
                            if not today:
                                tags.append('occasion')
                            self.busyHsh.setdefault(id, []).extend(["^ {0}".format(x[0]) for x in bt])
                    else:
                        occasion_lst.append([])

                    if isokey in loop.busytimes:
                        bt = []
                        for item in loop.busytimes[isokey]:
                            it = list(item)
                            if it[0] == it[1]:
                                # skip reminders
                                continue
                            if matching:
                                if not self.cal_regex.match(it[-1]):
                                    continue
                                mtch = (self.default_regex.match(it[-1]) is not None)
                            else:
                                mtch = True
                            it.append(mtch)
                            item = tuple(it)
                            bt.append(item)
                        busy_lst.append(bt)
                        busy_dates.append(thisdate.strftime("%a %d"))
                        if bt:
                            for pts in bt:
                                busytimes += pts[1] - pts[0]
                                self.busyHsh.setdefault(id, []).append("* {0}".format(pts[2]))
                            tags.append('busy')
                    else:
                        busy_lst.append([])
                        busy_dates.append(thisdate.strftime("%a %d"))
                    fill = getDayColor(busytimes)
                if 'current_day' in tags:
                    self.canvas.itemconfig(id, tag='current_day', fill=CURRENTFILL)
                elif 'occasion' in tags:
                    self.canvas.itemconfig(id, tag='occasion', fill=OCCASIONFILL)
                elif 'busy' in tags:
                    self.canvas.itemconfig(id, tag='busy', fill="white")
                if fill:
                    self.canvas.create_text(p, text="{0}".format(weeks[j][i].day), fill=fill)
                else:
                    self.canvas.create_text(p, text="{0}".format(weeks[j][i].day))
        busy_ids = list(busy_ids)
        for id in busy_ids:
            self.canvas.tag_bind(id, '<Any-Enter>', self.on_enter_item)
            self.canvas.tag_bind(id, '<Any-Leave>', self.on_leave_item)

        # border
        xy = int(l), int(t), int(l + x_ * 7), int(t + y_ * num_weeks + 1)
        self.canvas.create_rectangle(xy, tag="grid")

        # verticals
        for i in range(1, 7):
            xy = int(l + x_ * i), int(t), int(l + x_ * i), int(t + y_ * num_weeks)
            self.canvas.create_line(xy, fill=LINECOLOR, tag="grid")
        # horizontals
        for j in range(1, num_weeks):
            xy = int(l), int(t + y_ * j), int(l + x_ * 7), int(t + y_ * j)
            self.canvas.create_line(xy, fill=LINECOLOR, tag="grid")

        # week numbers
        for j in range(num_weeks):
            p = int(l - 5), int(t + y_ * j + y_ / 2)
            self.canvas.create_text(p, text=weeknumbers[j], anchor="e")
        # days
        for i in range(7):

            p = int(l + x_ / 2 + x_ * i), int(t - 13)

            if self.today_col is not None and i == self.today_col:
                self.canvas.create_text(p, text="{0}".format(weekdays[i]), fill=CURRENTLINE)
            else:
                self.canvas.create_text(p, text="{0}".format(weekdays[i]))

        self.busy_info = (themonth, busy_dates, busy_lst, occasion_lst)
        self.busy_ids = busy_ids
        self.busy_ids.sort()
        self.canvas_ids = self.busy_ids
        self.monthid2date = monthid2date
        self.canvas_idpos = None

    def get_timeline(self):
        if not (self.weekly and self.today_col is not None):
            return
        x = self.week_x
        if self.current_minutes < 7 * 60:
            return None
        elif self.current_minutes > 23 * 60:
            return None
        else:
            current_minutes = self.current_minutes
        (w, h, l, r, t, b) = self.margins
        start_x = l + self.today_col * x
        end_x = start_x + x

        t1 = t + (current_minutes - 7 * 60) * self.y_per_minute
        xy = int(start_x), int(t1), int(end_x), int(t1)
        return xy

    def selectId(self, event, d=1):
        ids = self.busy_ids
        if self.canvas_idpos is None:
            self.canvas_idpos = 0
            old_id = None
        else:
            old_id = self.canvas_ids[self.canvas_idpos]
            if old_id in ids:
                tags = self.canvas.gettags(old_id)
                if 'current_day' in tags:
                    self.canvas.itemconfig(old_id, fill=CURRENTFILL)
                elif 'occasion' in tags:
                    self.canvas.itemconfig(old_id, fill=OCCASIONFILL)
                elif 'other' in tags:
                    self.canvas.itemconfig(old_id, fill=OTHERFILL)
                elif self.weekly:
                    self.canvas.itemconfig(old_id, fill=DEFAULTFILL)
            else:
                self.canvas.itemconfig(old_id, fill=OCCASIONFILL)
                self.canvas.tag_lower(old_id)
            if d == -1:
                self.canvas_idpos -= 1
                if self.canvas_idpos < 0:
                    self.canvas_idpos = len(self.canvas_ids) - 1
            elif d == 1:
                self.canvas_idpos += 1
                if self.canvas_idpos > len(self.canvas_ids) - 1:
                    self.canvas_idpos = 0
        if self.weekly:
            self.selectedId = id = self.canvas_ids[self.canvas_idpos]
            self.canvas.itemconfig(id, fill=ACTIVEFILL)
            self.canvas.tag_raise('conflict')
            self.canvas.tag_raise(id)
            self.canvas.tag_lower('occasion')
            self.canvas.tag_lower('current_day')
            self.canvas.tag_raise('current_time')
            if id in self.busyHsh:
                self.OnSelect(uuid=self.busyHsh[id][-4], dt=self.busyHsh[id][-1])
                self.active_date = self.busyHsh[id][-1].date()

        elif self.monthly:
            if old_id is not None and old_id in self.busy_ids:
                tags = self.canvas.gettags(old_id)
                if 'current_day' in tags:
                    self.canvas.itemconfig(old_id, fill=CURRENTFILL)
                elif 'occasion' in tags:
                    self.canvas.itemconfig(old_id, fill=OCCASIONFILL)
                elif 'busy' in tags:
                    self.canvas.itemconfig(old_id, fill="white")
                else:
                    self.canvas.itemconfig(old_id, fill="white")
            self.selectedId = id = self.canvas_ids[self.canvas_idpos]
            self.active_date = self.monthid2date[id]
            self.canvas_idpos = self.canvas_ids.index(id)
            if id in self.busy_ids:
                self.canvas.itemconfig(id, fill=ACTIVEFILL)
            if id in self.busyHsh:
                txt = "\n".join(self.busyHsh[id])
                self.content.delete("1.0", END)
                self.content.insert("1.0", txt)
            else:
                self.content.delete("1.0", END)

    def setFocus(self, e):
        self.canvas.focus()
        self.canvas.focus_set()

    def on_enter_item(self, e):
        if self.weekly:
            old_id = None
            if self.canvas_idpos is not None:
                old_id = self.canvas_ids[self.canvas_idpos]
                if old_id in self.busy_ids:
                    tags = self.canvas.gettags(old_id)
                    if 'other' in tags:
                        self.canvas.itemconfig(old_id, fill=OTHERFILL)
                    else:
                        self.canvas.itemconfig(old_id, fill=DEFAULTFILL)
                else:
                    self.canvas.itemconfig(old_id, fill=OCCASIONFILL)
                    self.canvas.tag_lower(old_id)

            self.selectedId = id = self.canvas.find_withtag(CURRENT)[0]
            if id in self.busyHsh:
                self.active_date = self.busyHsh[id][-1].date()

            self.canvas.itemconfig(id, fill=ACTIVEFILL)
            self.canvas.tag_raise('conflict')
            self.canvas.tag_raise('grid')
            self.canvas.tag_raise(id)
            self.canvas.tag_lower('occasion')
            self.canvas.tag_lower('current_day')
            self.canvas.tag_raise('current_time')

            if id in self.busyHsh:
                self.canvas_idpos = self.canvas_ids.index(id)

                self.OnSelect(uuid=self.busyHsh[id][-4], dt=self.busyHsh[id][-1])
        elif self.monthly:
            if self.canvas_idpos is not None:
                old_id = self.canvas_ids[self.canvas_idpos]
                if old_id in self.busy_ids:
                    tags = self.canvas.gettags(old_id)
                    if 'current_day' in tags:
                        self.canvas.itemconfig(old_id, fill=CURRENTFILL)
                    elif 'occasion' in tags:
                        self.canvas.itemconfig(old_id, fill=OCCASIONFILL)
                    else:
                        self.canvas.itemconfig(old_id, fill="white")
            self.selectedId = id = self.canvas.find_withtag(CURRENT)[0]
            self.active_date = self.monthid2date[id]
            self.canvas_idpos = self.canvas_ids.index(id)
            if id in self.busy_ids:
                self.canvas.itemconfig(id, fill=ACTIVEFILL)
            if id in self.busyHsh:
                txt = "\n".join(self.busyHsh[id])
                self.content.delete("1.0", END)
                self.content.insert("1.0", txt)
            else:
                self.content.delete("1.0", END)

    def on_leave_item(self, e):
        if self.weekly or self.monthly:
            return
        self.content.delete("1.0", END)
        id = self.canvas.find_withtag(CURRENT)[0]
        if id in self.busy_ids:
            tags = self.canvas.gettags(id)
            if 'current_date' in tags:
                self.canvas.itemconfig(id, fill=CURRENTFILL)
            elif 'occasion' in tags:
                self.canvas.itemconfig(id, fill=OCCASIONFILL)
            else:
                self.canvas.itemconfig(id, fill="white")
        else:
            self.canvas.itemconfig(id, fill="white")

    def on_clear_item(self, e=None):
        if not self.weekly:
            return
        if self.selectedId:
            id = self.selectedId
            if id in self.busy_ids:
                tags = self.canvas.gettags(id)
                if 'other' in tags:
                    self.canvas.itemconfig(id, fill=OTHERFILL)
                else:
                    self.canvas.itemconfig(id, fill=DEFAULTFILL)
            else:
                self.canvas.itemconfig(id, fill=OCCASIONFILL)
        self.canvas.tag_raise('conflict')
        self.canvas.tag_raise('grid')
        self.canvas.tag_lower('occasion')
        self.selectedId = None
        self.OnSelect()
        self.canvas.focus("")

    def on_select_item(self, event):
        if self.monthly:
            self.newItem()
        else:
            current = self.canvas.find_withtag(CURRENT)
            logger.debug('current: {0}'.format(current))
            if current and current[0] in self.busy_ids:
                self.selectedId = current[0]
                self.on_activate_item(event)
            else:
                self.newEvent(event)
            return "break"

    def on_activate_item(self, event):
        if self.monthly:
            self.newItem()
        else:
            x = self.winfo_rootx() + 350
            y = self.winfo_rooty() + 50
            id = self.selectedId
            if not id:
                return

            logger.debug("id: {0}, coords: {1}, {2}\n    {3}".format(id, x, y, self.busyHsh[id]))
            self.uuidSelected = uuid = self.busyHsh[id][1]
            self.itemSelected = loop.uuid2hash[uuid]
            self.dtSelected = self.busyHsh[id][-1]
            self.itemmenu.post(x, y)
            self.itemmenu.focus_set()

    def newEvent(self, event):
        logger.debug("event: {0}".format(event))
        self.canvas.focus_set()
        min_round = 15
        px = event.x
        py = event.y
        (w, h, l, r, t, b) = self.margins
        x = Decimal(w - 1 - l - r) / Decimal(7)  # x per day intervals
        y = Decimal(h - 1 - t - b) / Decimal(16 * 60)  # y per minute intervals
        if px < l:
            px = l
        elif px > l + 7 * x:
            py = l + 7 * x
        if py < t:
            py = t
        elif py > t + 16 * 60 * y:
            py = t + 16 * 60 * y

        rx = int(round(Decimal(px - l) / x - Decimal(0.5)))  # number of days
        ry = int(7 * 60 + round(Decimal(py - t) / y))  # number of minutes
        ryr = round(Decimal(ry) / min_round) * min_round

        hours = int(ryr // 60)
        minutes = int(ryr % 60)
        dt = (self.week_beg + rx * ONEDAY).replace(hour=hours, minute=minutes, second=0, microsecond=0, tzinfo=None)

        tfmt = fmt_time(dt, options=loop.options)
        dfmt = dt.strftime("%a %b %d")
        dtfmt = "{0} {1}".format(tfmt, dfmt)
        s = "*  @s {0}".format(dtfmt)
        changed = SimpleEditor(parent=self, master=self.canvas, start=s, options=loop.options).changed

        if changed:
            logger.debug('changed, updating alerts, ...')

            self.updateAlerts()
            if self.weekly:
                self.showWeek()
            elif self.monthly:
                self.showMonth()
            else:
                self.showView()

    def showCalendar(self, e=None):
        cal_year = 0
        opts = loop.options
        cal_pastcolor = '#FFCCCC'
        cal_currentcolor = '#FFFFCC'
        cal_futurecolor = '#99CCFF'

        def showYear(x=0):
            global cal_year
            if x:
                cal_year += x
            else:
                cal_year = 0
            cal = "\n".join(calyear(cal_year, options=opts))
            if cal_year > 0:
                col = cal_futurecolor
            elif cal_year < 0:
                col = cal_pastcolor
            else:
                col = cal_currentcolor
            t.configure(bg=col)
            t.delete("0.0", END)
            t.insert("0.0", cal)

        win = Toplevel()
        win.title(_("Calendar"))
        f = Frame(win)
        # pack the button first so that it doesn't disappear with resizing
        b = Button(win, text=_('OK'), width=10, command=win.destroy, default='active', pady=2)
        b.pack(side='bottom', fill=tkinter.NONE, expand=0, pady=0)
        win.bind('<Return>', (lambda e, b=b: b.invoke()))
        win.bind('<Escape>', (lambda e, b=b: b.invoke()))

        t = ReadOnlyText(f, wrap="word", padx=2, pady=2, bd=2, relief="sunken",

                         font=self.tkfixedfont,

                         takefocus=False)
        win.bind('<Left>', (lambda e: showYear(-1)))
        win.bind('<Right>', (lambda e: showYear(1)))
        win.bind('<space>', (lambda e: showYear()))
        showYear()
        t.pack(side='left', fill=tkinter.BOTH, expand=1, padx=0, pady=0)
        ysb = Scrollbar(f, orient='vertical', command=t.yview, width=8)
        ysb.pack(side='right', fill=tkinter.Y, expand=0, padx=0, pady=0)

        t.configure(yscroll=ysb.set)
        f.pack(padx=2, pady=2, fill=tkinter.BOTH, expand=1)
        win.focus_set()
        win.grab_set()
        win.transient(self)
        win.wait_window(win)

    def newCommand(self, e=None):
        self.newValue.set(self.newLabel)

    def showShortcuts(self, e=None):
        if e and e.char != "?":
            return
        res = self.menutree.showMenu("_")
        self.textWindow(parent=self, title='etm', opts=self.options, prompt=res, modal=False)

    def help(self, event=None):
        path = USERMANUAL
        if windoz:
            os.startfile(USERMANUAL)
            return()
        if mac:
            cmd = 'open' + " {0}".format(path)
        else:
            cmd = 'xdg-open' + " {0}".format(path)
        subprocess.call(cmd, shell=True)
        return True

    def about(self, event=None):
        res = loop.do_v("")
        self.textWindow(parent=self, title='etm', opts=self.options, prompt=res, modal=False)

    def checkForUpdate(self, event=None):
        res = checkForNewerVersion()[1]
        self.textWindow(parent=self, title='etm', prompt=res, opts=self.options)

    def showChanges(self, event=None):
        if not loop.options['vcs_system']:
            prompt = """An entry for 'vcs_system' in etmtk.cfg is required but missing."""
            self.textWindow(parent=self, title="etm", prompt=prompt, opts=loop.options)
            return

        if self.itemSelected:
            f = self.itemSelected['fileinfo'][0]
            fn = ' {0}"{1}"'.format(self.options['vcs']['file'], os.path.normpath(os.path.join(self.options['datadir'], f)))
            title = _("Showing changes for {0}.").format(f)

        else:
            fn = ""
            title = _("Showing changes for all files.")
        logger.debug('fn: {0}'.format(fn))
        prompt = _("""\
{0}

If an item is selected, changes will be shown for the file containing
the item. Otherwise, changes will be shown for all files.

Enter an integer number of changes to display
or 0 to display all changes.""").format(title)
        depth = GetInteger(
            parent=self,
            title=_("Changes"),
            prompt=prompt, opts=[0], default=10).value
        if depth is None:
            return ()
        if depth == 0:
            # all changes
            numstr = ""
        else:
            numstr = "{0} {1}".format(loop.options['vcs']['limit'], depth)
        command = loop.options['vcs']['history'].format(
            repo=loop.options['vcs']['repo'],
            work=loop.options['vcs']['work'],
            numchanges=numstr, rev="{rev}", desc="{desc}", file=fn)
        logger.debug('vcs history command: {0}'.format(command))
        tt = TimeIt(loglevel=2, label="showChanges")
        s = subprocess.check_output(command, shell=True, universal_newlines=True)
        tt.stop()
        p = s2or3(s)
        if not p:
            p = 'no output from command:\n    {0}'.format(command)

        p = "\n".join([x for x in p.split('\n') if not (x.startswith('index') or x.startswith('diff') or x.startswith('\ No newline'))])

        self.textWindow(parent=self, title=title, prompt=s2or3(p), opts=self.options)

    def focus_next_window(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def goHome(self, event=None):
        if self.weekly:
            self.showWeek(week=0)
        elif self.monthly:
            self.showMonth(month=0)
        elif self.view == DAY:
            today = get_current_time().date()
            self.scrollToDate(today)
        else:
            self.tree.focus_set()
            self.tree.focus(1)
            self.tree.selection_set(1)
            self.tree.yview(0)

    def nextItem(self, e=None):
        item = self.tree.selection()[0]
        if item:
            next = self.tree.next(item)
            if next:

                next = int(next)
                next -= 1
                self.tree.focus(next)
                self.tree.selection_set(next)

    def prevItem(self, e=None):
        item = self.tree.selection()[0]
        if item:
            prev = self.tree.prev(item)
            if prev:

                prev = int(prev)
                prev += 1
                self.tree.focus(prev)
                self.tree.selection_set(prev)

    def OnSelect(self, event=None, uuid=None, dt=None):
        """
        Tree row has gained selection.
        """
        logger.debug("starting OnSelect with uuid: {0}".format(uuid))
        self.content.delete("1.0", END)
        if self.weekly:  # week view
            if uuid:
                # an item is selected, enable clear selection
                hsh = loop.uuid2hash[uuid]
                type_chr = hsh['itemtype']
        elif uuid is None:  # tree view
            item = self.tree.selection()[0]
            self.rowSelected = int(item)
            logger.debug('rowSelected: {0}'.format(self.rowSelected))
            # type_chr is the actual type, e.g., "-"
            # show_chr is what's displayed in the tree, e.g., "X"
            type_chr = show_chr = self.tree.item(item)['text'][0]
            uuid, dt, hsh = self.getInstance(item)
            logger.debug('tree rowSelected: {0}; {1}; {2}'.format(self.rowSelected, self.tree.item(item)['text'], dt))
            if self.view in [AGENDA, DAY]:
                if self.rowSelected in self.id2date:
                    if dt is None:
                        # we have the date selected
                        self.active_date = self.id2date[self.rowSelected]
                        logger.debug("active_date from id2date: {0}; {1}".format(self.active_date, self.tree.item(item)['text']))
                    else:
                        # we have an item
                        self.active_date = dt.date()
                        logger.debug('active date from dt: {0}; {1}'.format(self.active_date, self.tree.item(item)))
                else:
                    if dt:
                        self.active_date = dt.date()
                        logger.debug('active date from dt: {0}; {1}'.format(self.active_date, self.tree.item(item)))
                    else:
                        self.active_date = None
                logger.debug('active_date: {0}'.format(self.active_date))
            if hsh:
                type_chr = hsh['itemtype']
        self.update_idletasks()

        if uuid is not None:
            isRepeating = ('r' in hsh and dt)
            if isRepeating:
                logger.debug('selected: {0}, {1}'.format(dt, type(dt)))
                item = "{0} {1}".format(_('selected'), dt)
                self.itemmenu.entryconfig(1, label="{0} ...".format(self.em_opts[1]))
                self.itemmenu.entryconfig(2, label="{0} ...".format(self.em_opts[2]))
            else:
                self.itemmenu.entryconfig(1, label=self.em_opts[1])
                self.itemmenu.entryconfig(2, label=self.em_opts[2])
                item = _('selected')
            isUnfinished = (type_chr in ['-', '+', '%'] and show_chr != 'X')
            hasLink = ('g' in hsh and hsh['g'])
            # hasUser = ('u' in hsh and hsh['u'] and hsh['u'] in loop.options['user_data'])
            hasUser = ('u' in hsh and hsh['u'])
            l1 = hsh['fileinfo'][1]
            l2 = hsh['fileinfo'][2]
            if l1 == l2:
                lines = "{0} {1}".format(_('line'), l1)
            else:
                lines = "{0} {1}-{2}".format(_('lines'), l1, l2)
            self.filetext = filetext = "{0}, {1}".format(hsh['fileinfo'][0], lines)
            if 'errors' in hsh and hsh['errors']:
                text = "{1}\n\n{2}: {3}\n\n{4}: {5}".format(item, hsh['entry'].lstrip(), _("Errors"), hsh['errors'], _("file"), filetext)
            else:
                text = "{1}\n\n{2}: {3}".format(item, hsh['entry'].lstrip(), _("file"), filetext)
            for i in [0, 1, 2, 3, 5, 6, 7]:  # everything except finish (4), open link (8) and show user (9)
                self.itemmenu.entryconfig(i, state='normal')
            if isUnfinished:
                self.itemmenu.entryconfig(4, state='normal')
            else:
                self.itemmenu.entryconfig(4, state='disabled')
            if hasLink:
                self.itemmenu.entryconfig(8, state='normal')
            else:
                self.itemmenu.entryconfig(8, state='disabled')
            if hasUser:
                self.itemmenu.entryconfig(9, state='normal')
            else:
                self.itemmenu.entryconfig(9, state='disabled')
            self.uuidSelected = uuid
            self.itemSelected = hsh
            logger.debug('dt selected: {0}, {1}'.format(dt, type(dt)))
            self.dtSelected = dt
        else:
            text = ""
            for i in range(10):
                self.itemmenu.entryconfig(i, state='disabled')
            self.itemSelected = None
            self.uuidSelected = None
            self.dtSelected = None
        r = self.tree.identify_row(1)
        if r:
            self.topSelected = int(r)
        else:
            self.topSelected = 1
        logger.debug("row: {0}; uuid: {1}; instance: {2}, {3}; top: {4}".format(self.rowSelected, self.uuidSelected, self.dtSelected, type(self.dtSelected), self.topSelected))
        self.content.insert(INSERT, text)
        self.update_idletasks()
        logger.debug('ending OnSelect')
        return

    def OnActivate(self, event):
        """
        Return pressed with tree row selected
        """
        if not self.itemSelected:
            return "break"
        item = self.tree.selection()[0]
        uuid, dt, hsh = self.getInstance(item)
        x = self.winfo_rootx() + 350
        y = self.winfo_rooty() + 50
        logger.debug("id: {0}, coords: {1}, {2}".format(id, x, y))
        self.itemmenu.post(x, y)
        self.itemmenu.focus_set()
        return "break"

    def getInstance(self, item):
        instance = self.count2id[item]
        logger.debug('starting getInstance: {0}; {1}'.format(item, instance))
        if instance is not None:
            uuid, dt = self.count2id[item].split("::")
            hsh = loop.uuid2hash[uuid]
            dt = parse(dt)
            logger.debug('returning uuid: {0}, dt: {1}'.format(uuid, dt))
            return uuid, dt, hsh
        else:
            logger.debug('returning None')
            return None, None, None

    def updateClock(self):
        tt = TimeIt(loglevel=2, label="updateClock")
        self.now = get_current_time()
        self.current_minutes = self.now.hour * 60 + self.now.minute
        nxt = (60 - self.now.second) * 1000 - self.now.microsecond // 1000
        logger.debug('next update in {0} milliseconds.'.format(nxt))
        self.after(nxt, self.updateClock)
        nowfmt = "{0} {1}".format(
            s2or3(self.now.strftime(loop.options['reprtimefmt']).lower()),
            s2or3(self.now.strftime("%a %b %d")))

        nowfmt = leadingzero.sub("", nowfmt)
        self.currentTime.set("{0}".format(nowfmt))
        today = self.now.date()
        newday = (today != self.today)
        self.today = today

        new, modified, deleted = get_changes(
            self.options, loop.file2lastmodified)

        if newday or new or modified or deleted:
            if newday:
                logger.info('newday')
            logger.info("new: {0}; modified: {1}; deleted: {2}".format(len(new), len(modified), len(deleted)))
            logger.debug('calling loadData')
            loop.loadData()
            # we now have file2uuids ...

            if self.weekly:
                logger.debug('calling showWeek')
                self.showWeek()
            elif self.monthly:
                logger.debug('calling showMonth')
                self.showMonth()
            else:
                logger.debug('calling showView')
                self.showView()
        elif self.today_col is not None:
            xy = self.get_timeline()
            if xy:
                self.canvas.delete('current_time')
                self.canvas.create_line(xy, width=2, fill=CURRENTLINE, tag='current_time')
                self.update_idletasks()

        if self.current_minutes % loop.options['update_minutes'] == 0:
            if loop.do_update:
                updateCurrentFiles(loop.rows, loop.file2uuids, loop.uuid2hash, loop.options)
                loop.do_update = False

            if loop.options['icssync_folder']:
                fullpath = os.path.join(loop.options['datadir'], loop.options['icssync_folder'])
                prefix, files = getAllFiles(fullpath, include="*")
                base_files = set([])
                # file_lst = []
                for tup in files:
                    base, ext = os.path.splitext(tup[0])
                    if ext in [".txt", ".ics"]:
                        base_files.add(base)
                file_lst = list(base_files)
                datadir = loop.options['datadir']
                for file in file_lst:
                    relfile = relpath(file, datadir)
                    logger.debug('calling syncTxt: {0}; {1}'.format(datadir, relfile))
                    syncTxt(self.loop.file2uuids, self.loop.uuid2hash, datadir, relfile)
                # any updated txt files will be reloaded in the next update

        self.updateAlerts()

        if self.actionTimer.idle_active or self.actionTimer.timer_status != STOPPED:
            self.timerStatus.set(self.actionTimer.get_time())
            if self.actionTimer.timer_minutes >= 1:
                if (self.options['action_interval'] and self.actionTimer.timer_minutes % loop.options['action_interval'] == 0):
                    logger.debug('action_minutes trigger: {0} {1}'.format(self.actionTimer.timer_minutes, self.actionTimer.timer_status))
                    if self.actionTimer.timer_status == 'running':
                        if ('running' in loop.options['action_timer'] and
                                loop.options['action_timer']['running']):
                            tcmd = loop.options['action_timer']['running']
                            logger.debug('running: {0}'.format(tcmd))

                            subprocess.call(tcmd, shell=True)

                    elif self.actionTimer.timer_status == 'paused':
                        if ('paused' in loop.options['action_timer'] and
                                loop.options['action_timer']['paused']):
                            tcmd = loop.options['action_timer']['paused']

                            logger.debug('paused: {0}'.format(tcmd))
                            subprocess.call(tcmd, shell=True)

        tt.stop()

    def updateAlerts(self):
        self.update_idletasks()
        if loop.alerts:
            logger.debug('updateAlerts: {0}'.format(len(loop.alerts)))
        alerts = deepcopy(loop.alerts)
        if alerts and loop.options['calendars']:
            alerts = [x for x in alerts if self.cal_regex.match(x[-1])]
        if alerts:
            curr_minutes = datetime2minutes(self.now)
            td = -1
            # pop old alerts
            while td < 0 and alerts:
                td = alerts[0][0] - curr_minutes
                if td < 0:
                    a = alerts.pop(0)
            # alerts for this minute will have td's < 1.0
            if td < 1.0:
                if ('alert_wakecmd' in loop.options and
                        loop.options['alert_wakecmd']):
                    cmd = s2or3(loop.options['alert_wakecmd'])
                    subprocess.call(cmd, shell=True)
                while td < 1.0 and alerts:
                    hsh = alerts[0][2]
                    alerts.pop(0)
                    actions = hsh['_alert_action']
                    if 's' in actions:
                        if ('alert_soundcmd' in self.options and
                                self.options['alert_soundcmd']):
                            scmd = s2or3(expand_template(
                                self.options['alert_soundcmd'], hsh))
                            subprocess.call(scmd, shell=True)
                        else:
                            self.textWindow(parent=self, title="etm", prompt=_("""\
A sound alert failed. The setting for 'alert_soundcmd' is missing from  your etmtk.cfg."""), opts=self.options)
                    if 'd' in actions:
                        if ('alert_displaycmd' in self.options and
                                self.options['alert_displaycmd']):
                            dcmd = s2or3(expand_template(
                                self.options['alert_displaycmd'], hsh))
                            subprocess.call(dcmd, shell=True)
                        else:
                            self.textWindow(parent=self, title="etm", prompt=_("""\
A display alert failed. The setting for 'alert_displaycmd' is missing \
from your etmtk.cfg."""), opts=self.options)
                    if 'v' in actions:
                        if ('alert_voicecmd' in self.options and
                                self.options['alert_voicecmd']):
                            vcmd = s2or3(expand_template(
                                self.options['alert_voicecmd'], hsh))
                            subprocess.call(vcmd, shell=True)
                        else:
                            self.textWindow(parent=self, title="etm", prompt=_("""\
An email alert failed. The setting for 'alert_voicecmd' is missing from \
your etmtk.cfg."""), opts=self.options)
                    if 'e' in actions:
                        missing = []
                        for field in ['smtp_from', 'smtp_id', 'smtp_pw', 'smtp_server', 'smtp_to']:
                            if not self.options[field]:
                                    missing.append(field)
                        if missing:
                            self.textWindow(parent=self, title="etm", prompt=_("""\
An email alert failed. Settings for the following variables are missing \
from your etmtk.cfg: %s.""" % ", ".join(["'%s'" % x for x in missing])), opts=self.options)
                        else:
                            subject = hsh['summary']
                            message = expand_template(
                                self.options['email_template'], hsh)
                            arguments = hsh['_alert_argument']
                            recipients = [str(x).strip() for x in arguments[0]]
                            if len(arguments) > 1:
                                attachments = [str(x).strip()
                                               for x in arguments[1]]
                            else:
                                attachments = []
                            if subject and message and recipients:
                                send_mail(
                                    smtp_to=recipients,
                                    subject=subject,
                                    message=message,
                                    files=attachments,
                                    smtp_from=self.options['smtp_from'],
                                    smtp_server=self.options['smtp_server'],
                                    smtp_id=self.options['smtp_id'],
                                    smtp_pw=self.options['smtp_pw'])
                    if 'm' in actions:
                        MessageWindow(
                            self,
                            title=expand_template('!summary!', hsh),
                            prompt=expand_template(
                                self.options['alert_template'], hsh))

                    if 't' in actions:
                        missing = []
                        for field in ['sms_from', 'sms_message', 'sms_phone', 'sms_pw', 'sms_server', 'sms_subject']:
                            if not self.options[field]:
                                missing.append(field)
                        if missing:
                            self.textWindow(parent=self, title="etm", prompt=_("""\
A text alert failed. Settings for the following variables are missing \
from your 'emt.cfg': %s.""" % ", ".join(["'%s'" % x for x in missing])), opts=self.options)
                        else:
                            message = expand_template(
                                self.options['sms_message'], hsh)
                            subject = expand_template(
                                self.options['sms_subject'], hsh)
                            arguments = hsh['_alert_argument']
                            if arguments:
                                sms_phone = ",".join([str(x).strip() for x in
                                                      arguments[0]])
                            else:
                                sms_phone = self.options['sms_phone']
                            if message:
                                send_text(
                                    sms_phone=sms_phone,
                                    subject=subject,
                                    message=message,
                                    sms_from=self.options['sms_from'],
                                    sms_server=self.options['sms_server'],
                                    sms_pw=self.options['sms_pw'])
                    if 'p' in actions:
                        arguments = hsh['_alert_argument']
                        proc = str(arguments[0][0]).strip()
                        cmd = s2or3(expand_template(proc, hsh))
                        subprocess.call(cmd, shell=True)

                    if not alerts:
                        break
                    td = alerts[0][0] - curr_minutes
        if alerts and len(alerts) > 0:
            self.pendingAlerts.set(len(alerts))
            self.pending.configure(state="normal")
            self.activeAlerts = alerts
        else:
            self.pendingAlerts.set(0)
            self.activeAlerts = []
            self.pending.configure(state="disabled")

    def textWindow(self, parent, title=None, prompt=None, opts=None, modal=True):
        TextDialog(parent, title=title, prompt=prompt, opts=opts, modal=modal)

    def goToDate(self, e=None):
        """
        :param e:
        :return:
        """
        if e and e.char != "j":
            return
        prompt = _("""\
Return an empty string for the current date or a date to be parsed.
Relative dates and fuzzy parsing are supported.""")
        if self.view not in [DAY, WEEK]:
            self.view = DAY
            self.showView()
        d = GetDateTime(parent=self, title=_('date'), prompt=prompt)
        day = d.value

        logger.debug('day: {0}'.format(day))
        if day is not None:
            self.chosen_day = day

            if self.weekly:
                self.showWeek(event=e, week=None)
            elif self.monthly:
                self.showMonth(event=e, month=None)
            else:
                self.scrollToDate(day.date())
        return

    def setFilter(self, *args):
        if self.view in [WEEK, MONTH, CUSTOM]:
            return
        self.filter_active = True
        self.viewmenu.entryconfig(6, state="disabled")
        self.viewmenu.entryconfig(7, state="normal")
        self.fltr.configure(bg="white", state="normal")
        self.fltr.focus_set()

    def clearFilter(self, e=None):
        if self.view in [WEEK, MONTH, CUSTOM]:
            return
        self.filter_active = False
        self.viewmenu.entryconfig(6, state="normal")
        self.viewmenu.entryconfig(7, state="disabled")
        self.filterValue.set('')
        self.fltr.configure(bg=BGCOLOR)
        self.tree.focus_set()
        if self.rowSelected:
            self.tree.focus(self.rowSelected)
            self.tree.selection_set(self.rowSelected)
            self.tree.see(self.rowSelected)

    def startIdleTimer(self, e=None):
        if self.actionTimer.timer_status != STOPPED:
            prompt = "The active action timer must be stopped before starting the idle timer."
            MessageWindow(self, title="error", prompt=prompt)
            return
        if self.actionTimer.idle_active:
            self.actionTimer.idle_resolve()
        else:
            self.actionTimer.idle_start()
        self.newmenu.entryconfig(4, state="disabled")
        self.newmenu.entryconfig(5, state="normal")

    def stopIdleTimer(self, e=None):
        if not self.actionTimer.idle_active:
            return
        if self.actionTimer.timer_status != STOPPED:
            prompt = "The active action timer must be stopped before stopping the idle timer."
            MessageWindow(self, title="error", prompt=prompt)
            return
        self.actionTimer.idle_stop()
        self.timerStatus.set("")
        self.newmenu.entryconfig(4, state="normal")
        self.newmenu.entryconfig(5, state="disabled")

    def startActionTimer(self, e=None):
        """
        Prompt for a summary and start action timer.
        if uuid:
            if ~
                restart timer?
            else:
                enter summary or empty
        """
        # hack to avoid activating with Ctrl-t
        if e and e.char != "t":
            return
        if self.actionTimer.idle_active and self.actionTimer.timer_status in [STOPPED, PAUSED] and self.actionTimer.idle_delta > int(loop.options['idle_minutes']) * ONEMINUTE:
            self.actionTimer.idle_resolve()
        if self.actionTimer.timer_status == STOPPED:
            if self.uuidSelected:
                nullok = True
                sel_hsh = loop.uuid2hash[self.uuidSelected]
                prompt = _("""\
    Enter a summary for the new action timer or return an empty string
    to create a timer based on the selected item.""")
            else:
                nullok = False

                prompt = _("""\
    Enter a summary for the new action timer.""")
            value = GetString(parent=self, title=_('action timer'), prompt=prompt, opts={'nullok': nullok}, font=self.tkfixedfont).value

            self.tree.focus_set()
            logger.debug('value: {0}'.format(value))
            if value is None:
                return

            if value:
                self.timerItem = None
                hsh, msg = str2hsh(value, options=loop.options)
            elif nullok:
                self.timerItem = self.uuidSelected
                # Based on item, 'entry' will be in hsh
                hsh = sel_hsh
                ('hsh', hsh)
                for k in ['_r', 'o', '+', '-']:
                    if k in hsh:
                        del hsh[k]
                hsh['e'] = 0 * ONEMINUTE
            else:
                # shouldn't happen
                return "break"
            logger.debug('item: {0}'.format(hsh))

            self.actionTimer.timer_start(hsh)
            if ('running' in loop.options['action_timer'] and
                    loop.options['action_timer']['running']):
                tcmd = loop.options['action_timer']['running']
                logger.debug('command: {0}'.format(tcmd))
                subprocess.call(tcmd, shell=True)
        elif self.actionTimer.timer_status in [PAUSED, RUNNING]:
            self.actionTimer.timer_toggle()
            if (self.actionTimer.timer_status == RUNNING and 'running' in loop.options['action_timer'] and loop.options['action_timer']['running']):
                tcmd = loop.options['action_timer']['running']
                logger.debug('command: {0}'.format(tcmd))
                subprocess.call(tcmd, shell=True)
            elif (self.actionTimer.timer_status == PAUSED and 'paused' in loop.options['action_timer'] and loop.options['action_timer']['paused']):
                tcmd = loop.options['action_timer']['paused']
                logger.debug('command: {0}'.format(tcmd))
                subprocess.call(tcmd, shell=True)
        self.timerStatus.set(self.actionTimer.get_time())
        self.newmenu.entryconfig(3, state="normal")
        return

    def finishActionTimer(self, e=None):
        if e and e.char != "T":
            return
        if self.actionTimer.timer_status not in [RUNNING, PAUSED]:
            logger.info('stopping already stopped timer')
            return "break"
        self.actionTimer.timer_stop()
        self.timerStatus.set(self.actionTimer.get_time())
        hsh = self.actionTimer.timer_hsh
        changed = SimpleEditor(parent=self, newhsh=hsh, rephsh=None, options=loop.options, title=_("new action"), modified=True).changed
        if changed:
            # clear status and reload
            self.actionTimer.timer_clear()
            # self.timerStatus.set("")
            self.newmenu.entryconfig(3, state="disabled")

            self.updateAlerts()
            if self.weekly:
                self.showWeek()
            elif self.monthly:
                self.showMonth()
            else:
                self.showView(row=self.topSelected)
        else:
            # edit canceled
            ans = self.confirm(
                title=_('timer'),
                prompt=_('Retain the timer for "{0}"').format(self.actionTimer.timer_hsh['_summary']),
                parent=self)
            if ans:
                # restore timer with the old status
                self.actionTimer.timer_start(hsh=hsh, toggle=False)
            else:
                if self.actionTimer.idle_active:
                    # add the time back into idle
                    self.actionTimer.idle_delta += self.actionTimer.timer_delta
                self.actionTimer.timer_clear()
                # self.timerStatus.set("")
                self.newmenu.entryconfig(3, state="disabled")
        self.timerStatus.set(self.actionTimer.get_time())
        self.tree.focus_set()

    def gettext(self, event=None):
        s = self.e.get()
        if s is not None:
            return s
        else:
            return ''

    def cleartext(self, event=None):
        self.showView()
        return 'break'

    def process_input(self, event=None, cmd=None):
        """
        """

        if not cmd:
            return True
        if self.mode == 'command':
            cmd = cmd.strip()
            # if cmd[0] in ['a', 'c']:
            if cmd[0] in ['a']:
                # simple command history for report commands
                if cmd in self.history:
                    self.history.remove(cmd)
                self.history.append(cmd)
                self.index = len(self.history) - 1
            else:
                parts = cmd.split(' ')
                if len(parts) == 2:
                    try:
                        i = int(parts[0])
                    except:
                        i = None
                    if i:
                        parts.pop(0)
                        parts.append(str(i))
                        cmd = " ".join(parts)
            try:
                res = loop.do_command(cmd)
            except:
                return _('could not process command "{0}"').format(cmd)

        elif self.mode == 'delete':
            loop.cmd_do_delete(cmd)
            res = ''

        elif self.mode == 'finish':
            loop.cmd_do_finish(cmd)
            res = ''

        elif self.mode == 'new_date':
            res = loop.new_date(cmd)

        if not res:
            res = _('command "{0}" returned no output').format(cmd)

            logger.debug('no output')

            self.clearTree()
            return ()

        if type(res) == dict:
            self.showTree(res, event=event)
        else:
            # not a hash => not a tree
            self.textWindow(self, title='etm', prompt=res, opts=self.options)
            return 0

    def expand2Depth(self, e=None):
        if e and e.char != "o":
            return
        prompt = _("""\
Enter an integer depth to expand branches
or 0 to expand all branches completely.""")
        depth = GetInteger(
            parent=self,
            title=_("depth"), prompt=prompt, opts=[0], default=0).value
        if depth is None:
            return ()
        maxdepth = max([k for k in self.depth2id])
        logger.debug('expand2Depth {0}: {1}/{2}'.format(self.view, depth, maxdepth))
        if self.view in [AGENDA, DAY, KEYWORD, NOTE, TAG, PATH, CUSTOM]:
            self.outline_depths[self.view] = depth
            logger.debug('outline_depths: {0}'.format(self.outline_depths))
        if depth == 0:
            # expand all
            for k in self.depth2id:
                for item in self.depth2id[k]:
                    self.tree.item(item, open=True)
        else:
            depth -= 1
            depth = max(depth, 0)
            logger.debug('using depth: {0}; {1}'.format(depth, maxdepth))
            for i in range(depth):
                if i in self.depth2id:
                    for item in self.depth2id[i]:
                        try:
                            self.tree.item(item, open=True)
                        except:
                            logger.exception('open: {0}, {1}'.format(i, item))
            for i in range(depth, maxdepth + 1):
                if i in self.depth2id:
                    for item in self.depth2id[i]:
                        try:
                            self.tree.item(item, open=False)
                        except:
                            logger.exception('open: {0}, {1}'.format(i, item))

    def scrollToDate(self, date):
        # only makes sense for schedule
        logger.debug("DAY: {0}; date: {1}".format(self.view == DAY, date))
        if self.view != DAY or date not in loop.prevnext:
            return
        active_date = loop.prevnext[date][1]
        if active_date not in self.date2id:
            return
        uid = self.date2id[active_date]
        self.active_date = active_date
        self.scrollToId(uid)

    def scrollToId(self, uid):
        self.update_idletasks()
        self.tree.focus_set()
        self.tree.focus(uid)
        self.tree.selection_set(uid)
        self.tree.yview(int(uid) - 1)

    def showTree(self, tree, event=None):
        self.date2id = {}
        self.id2date = {}
        self.clearTree()
        self.count = 0
        self.count2id = {}
        self.active_tree = tree
        self.depth2id = {}
        self.add2Tree(u'', tree[self.root], tree)
        loop.count2id = self.count2id
        self.tree.tag_configure('treefont', font=self.tktreefont)

        self.content.delete("0.0", END)

        if event is None:

            if self.view == DAY and self.active_date:
                self.scrollToDate(self.active_date)
            else:
                if self.view in [AGENDA, DAY, TAG, KEYWORD, NOTE, PATH]:
                    depth = self.outline_depths[self.view]
                    if depth == 0:
                        # expand all
                        for k in self.depth2id:
                            for item in self.depth2id[k]:
                                self.tree.item(item, open=True)
                    else:
                        maxdepth = max([k for k in self.depth2id])
                        depth -= 1
                        depth = max(depth, 0)
                        for i in range(depth):
                            for item in self.depth2id[i]:
                                self.tree.item(item, open=True)
                        for i in range(depth, maxdepth + 1):
                            for item in self.depth2id[i]:
                                self.tree.item(item, open=False)
                self.goHome()

    def popupTree(self, e=None):
        if self.weekly or self.monthly:
            return
        if not self.active_tree:
            return
        depth = self.outline_depths[self.view]
        if loop.options:
            if 'report_indent' in loop.options:
                indent = loop.options['report_indent']
            if 'report_width1' in loop.options:
                width1 = loop.options['report_width1']
            if 'report_width2' in loop.options:
                width2 = loop.options['report_width2']
        else:
            indent = 4
            width1 = 43
            width2 = 20
        res = tree2Text(self.active_tree, indent=indent, width1=width1, width2=width2, depth=depth)
        if not res[0][0]:
            res[0].pop(0)
        prompt = "\n".join(res[0])
        self.textWindow(parent=self, title='etm', opts=self.options, prompt=prompt, modal=False)

    def printTree(self, e=None):
        if e and e.char != "p":
            return
        if self.weekly or self.monthly:
            return
        if not self.active_tree:
            return
        ans = self.confirm(parent=self.tree, prompt=_("""Print current outline?"""))
        if not ans:
            return False
        depth = self.outline_depths[self.view]

        if loop.options:
            if 'report_indent' in loop.options:
                indent = loop.options['report_indent']
            if 'report_width1' in loop.options:
                width1 = loop.options['report_width1']
            if 'report_width2' in loop.options:
                width2 = loop.options['report_width2']
        else:
            indent = 4
            width1 = 43
            width2 = 20
        res = tree2Text(self.active_tree, indent=indent, width1=width1, width2=width2, depth=depth)
        if not res[0][0]:
            res[0].pop(0)
        res[0].append('')
        s = "{0}".format("\n".join(res[0]))
        self.printWithDefault(s)

    def clearTree(self):
        """
        Remove all items from the tree
        """
        self.active_tree = {}
        for child in self.tree.get_children():
            self.tree.delete(child)

    def add2Tree(self, parent, elements, tree, depth=0):
        max_depth = 100
        for text in elements:
            self.count += 1
            # text is a key in the element (tree) hash
            # these keys are (parent, item) tuples
            if text in tree:
                # this is a branch
                item = " {0}".format(text[1])  # this is the label of the parent
                children = tree[text]  # these are the children tuples of item
                oid = self.tree.insert(parent, 'end', iid=self.count, text=item,
                                       open=(depth <= max_depth))
                self.depth2id.setdefault(depth, set([])).add(oid)
                # recurse to get children
                self.count2id[oid] = None
                self.add2Tree(oid, children, tree, depth=depth + 1)
            else:
                # this is a leaf
                if len(text[1]) == 4:
                    uuid, item_type, col1, col3 = text[1]
                    dt = ''
                else:  # len 5 day view with datetime appended
                    uuid, item_type, col1, col3, dt = text[1]

                if item_type:
                    # This hack avoids encoding issues under python 2
                    col1 = "{0} {1}".format(id2Type[item_type], col1)

                if type(col3) == int:
                    col3 = '%s' % col3
                else:
                    col3 = s2or3(col3)

                # Drop the instance information from the id
                id = uuid.split(':')[0]
                if id in loop.uuid2labels:
                    col2 = loop.uuid2labels[id]
                else:
                    col2 = "***"
                    if item_type not in ["=", "ib"]:
                        logger.warn('Missing key {0} for {1} {2}'.format(id, col1, col3))
                oid = self.tree.insert(parent, 'end', iid=self.count, text=col1, open=(depth <= max_depth), values=[col2, col3], tags=(item_type, 'treefont'))
                self.count2id[oid] = "{0}::{1}".format(uuid, dt)
                if dt:
                    if item_type == 'by':
                        # we want today, not the starting date for this
                        d = get_current_time().date()
                    else:
                        if type(dt) is datetime:
                            d = dt.date()
                        else:
                            d = parse(dt).date()
                    if d and d not in self.date2id:
                        # logger.debug('date2id[{0}] = {1}'.format(d, parent))
                        self.date2id[d] = int(parent)
                    if int(parent) not in self.id2date:
                        # logger.debug('id2date[{0}] = {1}'.format(int(parent), d))
                        self.id2date[int(parent)] = d

    def makeReport(self, event=None):
        if self.view != CUSTOM:
            return
        self.outline_depths[CUSTOM] = 0
        self.value_of_combo = self.custom_box.get()
        if not self.value_of_combo.strip():
            return
        try:
            res = getReportData(
                self.value_of_combo,
                self.loop.file2uuids,
                self.loop.uuid2hash,
                self.loop.options,
                cli=False)
            if not res:
                res = _("Report contains no output.")
            if self.value_of_combo not in self.specs:
                self.specs.append(self.value_of_combo)
                self.specs.sort()
                self.specs = [x for x in self.specs if x]
                self.custom_box["values"] = self.specs
                self.specsModified = True
            logger.debug("spec: {0}".format(self.value_of_combo))
        except:
            logger.exception("could not process: {0}".format(self.value_of_combo))
            res = _("'{0}' could not be processed".format(self.value_of_combo))
        if type(res) == dict:
            self.showTree(res, event=event)
        else:
            # not a hash => not a tree
            self.textWindow(self, title='etm', prompt=res, opts=self.options)
            self.custom_box.focus_set()
            return 0

    def getSpecs(self, e=None):
        self.specs = []
        if 'reports' in loop.options:
            self.specs = loop.options['reports']

    def saveSpecs(self, e=None):
        # called when changing from custom view or
        # when calling save changes to specs
        if self.view != CUSTOM:
            return
        if not self.specsModified:
            return
        # remove duplicates
        self.specs = list(set(self.specs))
        self.specs.sort()
        added = [x for x in self.specs if x not in self.saved_specs]
        if not added:
            self.specsModified = False
            return
        ans = self.confirm(parent=self, prompt=_("""Save the additions to your report specifications? {0} """.format("\n    ".join(added))))
        if ans:
            file = self.getReportsFile()
            if not (file and os.path.isfile(file)):
                return
            with codecs.open(file, 'r', loop.options['encoding']['file']) as fo:
                lines = fo.readlines()
            lines.extend(added)
            lines.sort()
            content = "\n".join([x.strip() for x in lines if x.strip()])
            with codecs.open(file, 'w', loop.options['encoding']['file']) as fo:
                    fo.write(content)
            logger.debug("saved: {0}".format(file))
            self.getSpecs()
            self.custom_box['values'] = self.specs
            self.value_of_combo = self.specs[0]
            self.specsModified = False

    def exportText(self):
        if self.view != CUSTOM:
            return
        logger.debug("spec: {0}".format(self.value_of_combo))
        tree = getReportData(
            self.value_of_combo,
            self.loop.file2uuids,
            self.loop.uuid2hash,
            self.loop.options,
            export=False)
        text = "\n".join([x for x in tree2Text(tree)[0]])
        prefix, tuples = getFileTuples(loop.options['etmdir'], include=r'*.text', all=True)
        filename = FileChoice(self, "cvs file", prefix=prefix, list=tuples, ext="text", new=False).returnValue()
        if not filename:
            return False
        fo = codecs.open(filename, 'w', self.options['encoding']['file'])
        fo.write(text)
        fo.close()
        MessageWindow(self, "etm", "Exported text to {0}".format(filename))

    def exportCSV(self):
        if self.view != CUSTOM:
            return
        logger.debug("spec: {0}".format(self.value_of_combo))
        data = getReportData(
            self.value_of_combo,
            self.loop.file2uuids,
            self.loop.uuid2hash,
            self.loop.options,
            export=True)
        prefix, tuples = getFileTuples(loop.options['etmdir'], include=r'*.csv', all=True)
        filename = FileChoice(self, "cvs file", prefix=prefix, list=tuples, ext="csv", new=False).returnValue()
        if not filename:
            return
        import csv as CSV
        c = CSV.writer(open(filename, "w"), delimiter=",")
        for line in data:
            c.writerow(line)
        MessageWindow(self, "etm", "Exported CSV to {0}".format(filename))

    def updateSubscriptions(self, e=None):
        if not self.loop.options['ics_subscriptions']:
            MessageWindow(self, 'etm', "A configuration setting for 'ics_subscriptions' is required but missing.")
            return
        good = []
        bad = []
        msg = []
        for url, rp in self.loop.options['ics_subscriptions']:
            fp = os.path.join(self.loop.options['datadir'], rp)
            logger.debug('updating: {0}, {1}'.format(rp, fp))
            res = update_subscription(url, fp)
            if res:
                good.append(rp)
            else:
                bad.append(rp)

        if good:
            msg.append(_("Succesfully updated:\n  {0}").format("\n  ".join(good)))
        if bad:
            msg.append(_("Not updated:\n  {0}").format("\n  ".join(bad)))
        MessageWindow(self, "etm", "\n".join(msg))

    def newselection(self, event=None):
        self.value_of_combo = self.custom_box.get()

loop = None

log_levels = {
    '1': logging.DEBUG,
    '2': logging.INFO,
    '3': logging.WARN,
    '4': logging.ERROR,
    '5': logging.CRITICAL
}


def main(dir=None):  # debug, info, warn, error, critical
    global loop
    etmdir = ''
    logger.debug('in view.main with dir: {0}'.format(dir))
    # For testing override etmdir:
    if dir is not None:
        etmdir = dir
        logger.debug('using etmdir: {0}'.format(etmdir))
    init_localization()
    (user_options, options, use_locale) = data.get_options(etmdir)
    loop = data.ETMCmd(options=options)
    loop.tkversion = tkversion

    app = App()
    app.mainloop()


if __name__ == "__main__":
    setup_logging('3')
    main()
