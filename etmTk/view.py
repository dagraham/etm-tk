#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
import re
import uuid
from copy import deepcopy, t
import subprocess
from dateutil.tz import tzlocal
import codecs

import logging
import logging.config

logger = logging.getLogger()

import platform

if platform.python_version() >= '3':
    import tkinter
    from tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, Text, PanedWindow, OptionMenu, StringVar, IntVar, Menu, BooleanVar, ACTIVE, Radiobutton, W, X, LabelFrame, Canvas, CURRENT
    #, PhotoImage
    from tkinter import ttk
    from tkinter import font as tkFont
    from tkinter.messagebox import askokcancel
    from tkinter.filedialog import askopenfilename
    utf8 = lambda x: x
    # from tkinter import simpledialog as tkSimpleDialog
else:
    import Tkinter as tkinter
    from Tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, Text, PanedWindow, OptionMenu, StringVar, IntVar, Menu, BooleanVar, ACTIVE, Radiobutton, W, X, LabelFrame, Canvas, CURRENT
    # PhotoImage
    # import tkMessageBox
    import ttk
    import tkFont
    from tkMessageBox import askokcancel
    from tkFileDialog import askopenfilename
    # import tkSimpleDialog
    def utf8(s):
        return s

tkversion = tkinter.Tcl().eval('info patchlevel')

# TODO: provide method to save changes to report specs


import etmTk.data as data
# from data import init_localization

from dateutil.parser import parse

from decimal import Decimal

from etmTk.data import (
    init_localization, fmt_weekday, fmt_dt, zfmt, rfmt, efmt, hsh2str, str2hsh, tstr2SCI, leadingzero, relpath, parse_datetime, s2or3, send_mail, send_text, fmt_period, get_changes, fmt_datetime, checkForNewerVersion, datetime2minutes, calyear, expand_template, sys_platform, id2Type, get_current_time, windoz, mac, setup_logging, uniqueId, gettz, commandShortcut, optionShortcut, rrulefmt, makeTree, tree2Text, checkForNewerVersion, date_calculator, AFTER, export_ical_item, export_ical, fmt_time)

from etmTk.help import (ATKEYS, DATES, ITEMTYPES,  OVERVIEW, PREFERENCES, REPORTS)

from etmTk.dialog import Node, MenuTree, Timer, ReadOnlyText, MessageWindow, HelpWindow, TextVariableWindow, TextDialog, OptionsDialog, GetInteger, GetDateTime, GetString, STOPPED, PAUSED, RUNNING,  BGCOLOR, ONEDAY, ONEMINUTE

from etmTk.edit import SimpleEditor, ReportWindow

import gettext

_ = gettext.gettext


from datetime import datetime, timedelta

ETM = "etm"

STOPPED = _('stopped')
PAUSED = _('paused')
RUNNING = _('running')

FILTER = _("filter")
FILTERCOLOR = "gray"

AGENDA = _('Agenda')
DAY = _('Day')
PATHS = _('Path')
KEYWORDS = _('Keyword')
TAGS = _('Tag')
NOTES = _('Note')
WEEK = _("Week")

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

CLOSE = _("Close")

SEP = "----"

# ACTIVEOUTLINE = "#7E96F7"
# ACTIVEOUTLINE = CONFLICTFILL
# BUSYOUTLINE = BUSYFILL
ACTIVEFILL = "#FAFCAC"
ACTIVEOUTLINE = "gray40"

DEFAULTFILL = "#D4DCFC" # blue
OTHERFILL = "#C7EDC8" # green
# BUSYFILL = "#D4DCFC" # blue
# BUSYFILL = "#CAECED" # cyan
# BUSYFILL = "#F8D7FA" # magenta
# BUSYFILL = "#C7EDC8" # green

BUSYOUTLINE = ""

CONFLICTFILL = "#C1C4C9"
CURRENTFILL = "#FCF2F0"
CURRENTLINE = "#E0535C"
LASTLTR = re.compile(r'([a-z])$')
LINECOLOR = "gray80"
# CONFLICTFILL = "#716DF7"
# CONFLICTFILL = "#9BAEFA"
# CONFLICTFILL = "#FAC2B6"

OCCASIONFILL = "gray96"
# OCCASIONFILL = "gray98"


class App(Tk):
    def __init__(self, path=None):
        Tk.__init__(self)
        # minsize: width, height
        self.minsize(460, 480)
        self.uuidSelected = None
        self.timerItem = None
        self.actionTimer = Timer(self)
        self.loop = loop
        self.activeAlerts = []
        self.configure(background=BGCOLOR)
        self.option_add('*tearOff', False)
        self.menu_lst = []
        self.menutree = MenuTree()
        self.chosen_day = None
        self.busy_info = None
        self.weekly = False # showWeekly
        self.today_col = None
        root = "_"

        ef = "%a %b %d"
        if 'ampm' in loop.options and loop.options['ampm']:
            reprtimefmt = "%I:%M%p"
            # self.rfmt = "{0} %I:%M%p".format(df)
            self.efmt = "%I:%M%p {0}".format(ef)
        else:
            reprtimefmt = "%H:%M"
            # self.rfmt = "{0} %H:%M%z".format(df)
            self.efmt = "%H:%M {0}".format(ef)

        # self.default_calendars = []
        self.default_calendars = deepcopy(loop.options['calendars'])

        # create the root node for the menu tree
        self.menutree.create_node(root, root)
        # branch: (parent, child)
        # leaf: (parent, (option, [accelerator])
        # menuwidth = 9

        # main menu
        menubar = Menu(self)
        logger.debug('AFTER: {0}'.format(AFTER))
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
        l, c = commandShortcut('i')
        logger.debug("{0}: {1}, {2}".format(label, l, c))
        newmenu.add_command(label=label, command=self.newItem)
        self.bind(c, lambda e: self.after(AFTER, self.newItem))
        if not mac:
            newmenu.entryconfig(0, accelerator=l)
        self.add2menu(path, (label, l))

        label = _("Begin/Pause Action Timer")
        l, c = commandShortcut(',')
        logger.debug("{0}: {1}, {2}".format(label, l, c))
        newmenu.add_command(label=label, command=self.startActionTimer)
        self.bind("<Control-comma>", lambda e: self.after(AFTER, self.startActionTimer))
        if not mac:
            newmenu.entryconfig(1, accelerator=l)
        self.add2menu(path, (label, l))

        label = _("Finish Action Timer")
        l, c = commandShortcut('.')
        logger.debug("{0}: {1}, {2}".format(label, l, c))
        newmenu.add_command(label=label, command=self.startActionTimer)
        self.bind("<Control-period>", lambda e: self.after(AFTER, self.finishActionTimer))
        if not mac:
            newmenu.entryconfig(2, accelerator=l)
        self.add2menu(path, (label, l))

        filemenu.add_cascade(label=NEW, menu=newmenu)
        newmenu.entryconfig(2, state="disabled")

        path = FILE
        # Open
        openmenu = Menu(filemenu, tearoff=0)
        self.add2menu(path, (OPEN, ))
        path = OPEN
        l, c = commandShortcut('F')
        label = _("Data file ...")
        openmenu.add_command(label=label, command=self.editData)
        self.bind(c, lambda e: openmenu.invoke(0))
        if not mac:
            openmenu.entryconfig(0, accelerator=l)
        self.add2menu(path, (label, l))

        l, c = commandShortcut('E')
        logger.debug("config: {0}, {1}".format(l, c))
        file = loop.options['config']
        label = relpath(file, loop.options['etmdir'])
        openmenu.add_command(label=label, command=lambda x=file: self.editFile(file=x, config=True))
        self.bind(c, lambda e: openmenu.invoke(1))
        if not mac:
            openmenu.entryconfig(1, accelerator=l)
        self.add2menu(path, (label, l))

        l, c = commandShortcut('C')
        file = loop.options['auto_completions']
        label = relpath(file, loop.options['etmdir'])
        openmenu.add_command(label=label, command=lambda x=file: self.editFile(file=x))
        self.bind(c, lambda e: openmenu.invoke(2))
        if not mac:
            openmenu.entryconfig(2, accelerator=l)
        self.add2menu(path, (label, l))

        l, c = commandShortcut('R')
        file = loop.options['report_specifications']
        label = relpath(file, loop.options['etmdir'])
        logger.debug("{0}: {1}, {2}".format(label, l, c))
        openmenu.add_command(label=label, command=lambda x=file: self.editFile(file=x))
        self.bind(c, lambda e: openmenu.invoke(3))
        if not mac:
            openmenu.entryconfig(3, accelerator=l)
        self.add2menu(path, (label, l))

        l, c = commandShortcut('S')
        file = loop.options['scratchpad']
        label = relpath(file, loop.options['etmdir'])
        # label = _("Scratchpad")
        openmenu.add_command(label=label, command=lambda x=file: self.editFile(file=x))
        self.bind(c, lambda e: openmenu.invoke(4))
        if not mac:
            openmenu.entryconfig(4, accelerator=l)
        self.add2menu(path, (label, l))

        filemenu.add_cascade(label=OPEN, menu=openmenu)

        path = FILE

        filemenu.add_separator()
        self.add2menu(path, (SEP, ))

        ## quit
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
        viewmenu.add_command(label=label, command=lambda: self.goHome())
        if not mac:
            viewmenu.entryconfig(0, accelerator=l)
        self.add2menu(path, (label, l))
        self.bind('<space>', self.goHome)


        # go to date
        l, c = commandShortcut('j')
        label=_("Jump to date")
        viewmenu.add_command(label=label, command=self.goToDate)
        self.bind(c, lambda event: self.after(AFTER, self.goToDate))
        if not mac:
            viewmenu.entryconfig(1, accelerator=l)
        self.add2menu(path, (label, l))

        viewmenu.add_separator()
        self.add2menu(path, (SEP, ))

        l = "Control-Down"
        label = _("Next sibling")
        viewmenu.add_command( label=label, underline=1,  command=self.nextItem)
        if not mac:
            viewmenu.entryconfig(3, accelerator=l)
        self.add2menu(path, (label, l))

        l = "Control-Up"
        label = _("Previous sibling")
        viewmenu.add_command( label=label, underline=1,  command=self.prevItem)
        if not mac:
            viewmenu.entryconfig(4, accelerator=l)
        self.add2menu(path, (label, l))

        # apply filter
        l, c = commandShortcut('f')
        label=_("Set outline filter")
        viewmenu.add_command( label=label, underline=1,  command=self.setFilter)
        self.bind(c, lambda event: self.after(AFTER, self.setFilter))
        if not mac:
            viewmenu.entryconfig(5, accelerator=l)
        self.add2menu(path, (label, l))

        # clear filter
        l = "Escape"
        label=_("Clear outline filter")
        viewmenu.add_command( label=label, underline=1, command=self.clearFilter)
        if not mac:
            viewmenu.entryconfig(6, accelerator=l)
        self.add2menu(path, (label, l))

        # expand to depth
        l, c = commandShortcut('o')
        label=_("Set outline depth")
        viewmenu.add_command( label=label, underline=1, command=self.expand2Depth)
        self.bind(c, lambda event: self.after(AFTER, self.expand2Depth))
        if not mac:
            viewmenu.entryconfig(7, accelerator=l)
        self.add2menu(path, (label, l))

        viewmenu.add_separator()
        self.add2menu(path, (SEP, ))

        l = "Left"
        label=_("Previous week")
        viewmenu.add_command(label=label, underline=1, command=lambda e=None: self.showWeek(event=e, week=-1))
        if not mac:
            viewmenu.entryconfig(9, accelerator=l)
        self.add2menu(path, (label, l))

        l = "Right"
        label=_("Next week")
        viewmenu.add_command(label=label, underline=1, command=lambda e=None: self.showWeek(event=e, week=+1))
        if not mac:
            viewmenu.entryconfig(10, accelerator=l)
        self.add2menu(path, (label, l))

        l = "Up"
        label=_("Previous item in week")
        viewmenu.add_command(label=label, underline=1, command=lambda e=None: self.selectId(event=e, d=-1))
        if not mac:
            viewmenu.entryconfig(11, accelerator=l)
        self.add2menu(path, (label, l))

        l = "Down"
        label=_("Next item in week")
        viewmenu.add_command(label=label, underline=1, command=lambda e=None: self.selectId(event=e, d=1))
        if not mac:
            viewmenu.entryconfig(12, accelerator=l)
        self.add2menu(path, (label, l))

        l = "Escape"
        label=_("Clear selection")
        viewmenu.add_command(label=label, underline=1, command=self.on_clear_item)
        if not mac:
            viewmenu.entryconfig(13, accelerator=l)
        self.add2menu(path, (label, l))

        l, c = commandShortcut("b")
        label=_("List busy times in week")
        viewmenu.add_command(label=label, underline=5, command=self.showBusyTimes)
        if not mac:
            viewmenu.entryconfig(14, accelerator=l)
        self.bind(c, lambda event: self.after(AFTER, self.showBusyTimes))
        self.add2menu(path, (label, l))

        # viewmenu.add_cascade(label=path, menu=viewmenu, underline=0)

        # self.viewmenu.entryconfig(0, state="normal")
        for i in range(9, 15):
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
            [_('Delete'), 'delete'],
            [_('Edit'), 'e'],
            [_('Finish'), 'x'],
            [_('Reschedule'), 's'],
            [_('Open link'), 'g'],
            [_('Export item as ical'), 'f6'],
            ]
        self.edit2cmd = {
            'c': self.copyItem,
            'delete': self.deleteItem,
            'e': self.editItem,
            'x': self.finishItem,
            's': self.rescheduleItem,
            'g': self.openWithDefault,
            'f6': self.exportItemToIcal,
            }
        self.em_opts = [x[0] for x in self.em_options]
        # em_cmds = [x[1] for x in self.em_options]

        for i in range(len(self.em_options)):
            label = self.em_options[i][0]
            k = self.em_options[i][1]
            if k == 'delete':
                l = "Ctrl-BackSpace"
                c = "<Control-BackSpace>"
            elif k == "f6":
                l = "F6"
                c = "<F6>"
            # elif k == "e":
            #     l, c  = commandShortcut(k)
            #     l = "{0}, Return".format(l)
            else:
                l, c = commandShortcut(k)
            logger.debug('binding {0} to {1}'.format(c, self.edit2cmd[k]))
            itemmenu.add_command(label=label, underline=0, command=self.edit2cmd[k])
            # if k != "delete":
            self.bind(c, lambda e, x=k: self.after(AFTER, self.edit2cmd[x]))
            if not mac:
                itemmenu.entryconfig(i, accelerator=l)
            self.add2menu(path, (label, l))

        menubar.add_cascade(label=path, underline=0, menu=itemmenu)

        # tools menu
        path = TOOLS
        self.add2menu(menu, (path, ))
        toolsmenu = Menu(menubar, tearoff=0)

        l = "F4"
        c = "<F4>"
        # l, c = commandShortcut('y')
        label=_("Display yearly calendar")
        toolsmenu.add_command(label=label, underline=8, command=self.showCalendar)
        self.bind(c, lambda event: self.after(AFTER, self.showCalendar))
        if not mac:
            toolsmenu.entryconfig(0, accelerator=l)
        self.add2menu(path, (label, l))

        # date calculator
        l = "F5"
        c = "<F5>"
        # l, c = commandShortcut('l')
        label=_("Open date calculator")
        toolsmenu.add_command(label=label, underline=12, command=self.dateCalculator)
        self.bind(c, lambda event: self.after(AFTER, self.dateCalculator))
        if not mac:
            toolsmenu.entryconfig(1, accelerator=l)
        self.add2menu(path, (label, l))

        # report
        l, c = commandShortcut('r')
        label=_("Create report")
        toolsmenu.add_command(label=label, underline=5, command=self.makeReport)
        self.bind(c, self.makeReport)
        if not mac:
            toolsmenu.entryconfig(2, accelerator=l)
        self.add2menu(path, (label, l))

        # changes
        l, c = commandShortcut('h')
        label = _("Show history of changes")
        toolsmenu.add_command(label=label, underline=1, command=self.showChanges)
        self.bind(c, lambda event: self.after(AFTER, self.showChanges))
        if not mac:
            toolsmenu.entryconfig(3, accelerator=l)
        self.add2menu(path, (label, l))


        ## export
        l = "Shift-F6"
        c = "<Shift-F6>"
        label = _("Export active calendars as iCal")
        toolsmenu.add_command(label=label, underline=1, command=self.exportActiveToIcal)
        self.bind(c, self.exportActiveToIcal)
        if not mac:
            toolsmenu.entryconfig(4, accelerator=l)
        self.add2menu(path, (label, l))

        menubar.add_cascade(label=path, menu=toolsmenu, underline=0)

        # help
        helpmenu = Menu(menubar, tearoff=0)
        path = HELP
        self.add2menu(menu, (path, ))

        # search is built in
        self.add2menu(path, (_("Search"), ))

        label = _("Help")
        helpmenu.add_command(label=label, underline=1, accelerator="F1", command=self.help)
        self.add2menu(path, (label, "F1"))
        self.bind("<F1>", lambda e: self.after(AFTER, self.help))


        label = _("About")
        helpmenu.add_command(label="About", accelerator="F2", command=self \
                             .about)
        self.bind("<F2>", self.about)
        self.add2menu(path, (label, "F2"))

        # check for updates
        # l, c = commandShortcut('u')
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
        tkfixedfont.configure(size=self.options['fontsize'])
        logger.debug("fixedfont: {0}".format(tkfixedfont.actual()))
        self.tkfixedfont = tkfixedfont

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

        self.vm_options = [[AGENDA, 'a'],
                           [DAY, 'd'],
                           [TAGS, 't'],
                           [KEYWORDS, 'k'],
                           [NOTES, 'n'],
                           [PATHS, 'p'],
                           [WEEK, 'w'],
                           ]

        self.view2cmd = {'a': self.agendaView,
                         'd': self.dayView,
                         'p': self.pathView,
                         'k': self.keywordView,
                         'n': self.noteView,
                         't': self.tagView,
                         'w': self.showWeekly}

        self.view = self.vm_options[0][0]
        self.currentView = StringVar(self)
        self.currentView.set(self.view)

        MAIN = _("Main")
        self.add2menu(root, (MAIN, ))
        VIEWS = _("Views")
        self.add2menu(MAIN, (VIEWS, ))

        self.vm_opts = [x[0] for x in self.vm_options]
        self.vm = OptionMenu(topbar, self.currentView, *self.vm_opts)
        self.vm.configure(pady=2)
        for i in range(len(self.vm_options)):
            label = self.vm_options[i][0]
            k = self.vm_options[i][1]
            l, c = commandShortcut(k)
            logger.debug("k: {0}; l: {1}; c: {2}".format(k, l, c))
            self.bind(c, lambda e, x=k: self.after(AFTER, self.view2cmd[x]))
            self.vm["menu"].entryconfig(i, command=lambda x=k: self.after(AFTER, self.view2cmd[x]))
            self.add2menu(VIEWS, (self.vm_opts[i], l))
        self.vm.pack(side="left", padx=2)
        self.vm.configure(background=BGCOLOR, takefocus=False)

        # calendars
        self.calbutton = Button(topbar, text=CALENDARS, command=self.selectCalendars, highlightbackground=BGCOLOR, bg=BGCOLOR, width=8, pady=2)
        # self.calbutton.pack(side="right", padx=0)
        self.calbutton.pack(side="right", padx=6)
        if not self.default_calendars:
            self.calbutton.configure(state="disabled")

        # filter
        self.fltrbox = fltrbox = Frame(topbar, bd=0, relief="flat", highlightbackground=BGCOLOR, background=BGCOLOR)
        self.filterValue = StringVar(self)
        self.filterValue.set('')
        self.filterValue.trace_variable("w", self.filterView)
        # self.dummyValue = StringVar(self)
        # self.dummyValue.set(FILTER)
        # self.dummyValue.trace_variable("w", self.setFilter)

        self.fltr = Entry(fltrbox, textvariable=self.filterValue, width=14, highlightbackground=BGCOLOR, bg=BGCOLOR)
        # self.fltr.configure(fg=FILTERCOLOR)
        self.fltr.pack(side="left", padx=0) #, expand=1, fill=X)
        self.bind("<Escape>", self.clearFilter)
        self.fltr.bind("<FocusIn>", self.setFilter)
        self.fltrbtn = Button(fltrbox, text='x', command=self.clearFilter, highlightbackground=BGCOLOR, pady=2)
        self.fltrbtn.configure(state="disabled")
        self.filter_active = False
        self.viewmenu.entryconfig(5, state="normal")
        self.viewmenu.entryconfig(6, state="disabled")
        self.fltrbtn.pack(side=LEFT, padx=0)
        self.fltrbox.pack(side=LEFT, padx=0, pady=0)

        # topbar.pack(side="top", fill="both", expand=0, padx=0, pady=0)

        self.panedwindow = panedwindow = PanedWindow(self, orient="vertical",
                                                     # showhandle=True,
                                                     sashwidth=6, sashrelief='flat',
                                                     )

        self.toppane = toppane = Frame(self.panedwindow, bd=0, highlightthickness=0, background=BGCOLOR)
        self.weekly = False
        self.tree = ttk.Treeview(toppane, show='tree', columns=["#1"], selectmode='browse')
        self.tree.column('#0', minwidth=200, width=260, stretch=1)
        self.tree.column('#1', minwidth=80, width=140, stretch=0, anchor='center')
        self.tree.bind('<<TreeviewSelect>>', self.OnSelect)
        self.tree.bind('<Double-1>', self.OnActivate)
        self.tree.bind('<Return>', self.OnActivate)
        self.tree.bind('<Control-Down>', self.nextItem)
        self.tree.bind('<Control-Up>', self.prevItem)
        # self.tree.bind('<Escape>', self.cleartext)
        # self.tree.bind('<j>', self.jumpToDate)
        self.tree.bind('<space>', self.goHome)

        for t in tstr2SCI:
            self.tree.tag_configure(t, foreground=tstr2SCI[t][1])

        self.date2id = {}
        # padx = 2

        self.root = ('', '_')

        self.tree.pack(fill="both", expand=1, padx=4, pady=0)
        panedwindow.add(self.toppane, padx=0, pady=0, stretch="first")

        self.content = ReadOnlyText(panedwindow, wrap="word", padx=3, bd=2, relief="sunken",
                                    # font=tkFont.Font(family="Lucida Sans Typewriter"), height=6,
                                    font=tkfixedfont, height=4,
                                    width=46, takefocus=False)
        self.content.bind('<Escape>', self.cleartext)
        # self.content.bind('<space>', self.goHome)
        self.content.bind('<Tab>', self.focus_next_window)

        panedwindow.add(self.content, padx=3, pady=0, stretch="never")

        self.statusbar = Frame(self)

        self.timerStatus = StringVar(self)
        self.timerStatus.set("")
        timer_status = Label(self.statusbar, textvariable=self.timerStatus, bd=0,  relief="flat",  anchor="w", padx=0, pady=0)
        timer_status.pack(side="left", expand=0, padx=2)
        timer_status.configure(background=BGCOLOR, highlightthickness=0)

        self.pendingAlerts = IntVar(self)
        self.pendingAlerts.set(0)
        self.pending = Button(self.statusbar, padx=8, pady=2,
                              # relief="flat",
                              takefocus=False, textvariable=self.pendingAlerts, command=self.showAlerts, anchor="center")
        self.pending.pack(side="right", padx=0, pady=0)
        self.pending.configure(highlightbackground=BGCOLOR,
                               background=BGCOLOR,
                               highlightthickness=0,
                               state="disabled"
        )
        self.showPending = True

        self.currentTime = StringVar(self)
        currenttime = Label(self.statusbar, textvariable=self.currentTime, bd=1, relief="flat",
                            anchor="e", padx=4, pady=0)
        currenttime.pack(side="right")
        currenttime.configure(background=BGCOLOR)

        self.statusbar.pack(side="bottom", fill="x", expand=0, padx=6, pady=0)
        self.statusbar.configure(background=BGCOLOR)

        panedwindow.pack(side="top", fill="both", expand=1, padx=2, pady=0)
        panedwindow.configure(background=BGCOLOR)

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
        self.add2menu(EDIT, (_("Show possible completions"), "Ctrl-Space"))
        self.add2menu(EDIT, (_("Validate entry"), "Ctrl-?"))
        self.add2menu(EDIT, (_("Cancel"), "Ctrl-Q"))
        self.add2menu(EDIT, (_("Save changes and close editor"), "Ctrl-W"))

        REPORT = _("Report")
        self.add2menu(root, (REPORT, ))
        self.add2menu(REPORT, (_("Create and display selected report"), "Return"))
        self.add2menu(REPORT, (_("Export report in text format ..."), "Ctrl-T"))
        self.add2menu(REPORT, (_("Export report in csv format ..."), "Ctrl-X"))
        self.add2menu(REPORT, (_("Save changes to report specifications"), "Ctrl-W"))
        self.add2menu(REPORT, (_("Expand report list"), "Down"))
        self.add2menu(REPORT, (_("Quit"), "Ctrl-Q"))



        # start clock
        self.updateClock()

        # show default view
        self.updateAlerts()
        self.showView()

    def closeItemMenu(self, event=None):
        if self.weekly:
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
                # child = list(child)
                child = tuple(child)
        else:
            id = child[0]
        if len(child) >= 2:
            leaf = "{0}::{1}".format(child[0], child[1])
        else:
            leaf = "{0}::".format(child[0])
        logger.debug('calling create_node. leaf: {0}, id: {1}, parent: {2}'.format(leaf, id,  parent))
        self.menutree.create_node(leaf, id, parent=parent)


    def confirm(self, parent=None, title="", prompt="", instance="xyz"):
        ok, value = OptionsDialog(parent=parent, title=_("confirm").format(instance), prompt=prompt).getValue()
        return ok

    def selectCalendars(self):
        if self.default_calendars:
            prompt = _("Only items from selected calendars will be displayed.")
            title = CALENDARS
            if self.weekly:
                master = self.canvas
            else:
                master = self.tree

            values = OptionsDialog(parent=self, master=master, title=title, prompt=prompt, opts=loop.calendars, radio=False, yesno=False).getValue()
            if values != loop.calendars:
                loop.calendars = values
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
        else:
            self.showView()

    def quit(self, e=None):
        ans = self.confirm(
            title=_('Quit'),
            prompt=_("Do you really want to quit?"),
            parent=self)
        if ans:
            self.destroy()

    def donothing(self, e=None):
        """For testing"""
        logger.debug('donothing')
        return "break"

    def makeReport(self, e=None):
        logger.debug('makeReport')
        ReportWindow(parent=self, options=self.options, title=_("report"))


    def openWithDefault(self):
        if 'g' not in self.itemSelected:
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
        return True


    def dateCalculator(self, event=None):
        prompt = """\
Enter an expression of the form "x [+-] y" where x is a date
and y is either a date or a time period if "-" is used and
a time period if "+" is used."""
        value = GetString(parent=self, title=_('date calculator'),  prompt=prompt, opts={}).value
        if not value:
            return
        res = date_calculator(value, self.options)
        prompt = "{0}:\n\n{1}".format(value, res)
        MessageWindow(self, title=_("result"), prompt=prompt)

    def exportItemToIcal(self):
        if not self.itemSelected:
            return
        if 'icsitem_file' in loop.options:
            res = export_ical_item(self.itemSelected, loop.options['icsitem_file'])
            if res:
                prompt = _("Selected item successfully exported to {0}".format(loop.options['icsitem_file']))
            else:
                prompt = _("Could not export selected item.")
        else:
            prompt = "icsitem_file is not set in etmtk.cfg"
        MessageWindow(self, 'Selected Item Export', prompt)

    def exportActiveToIcal(self, event=None):
        if 'icscal_file' in loop.options:
            res = export_ical(loop.uuid2hash, loop.options['icscal_file'], loop.calendars)
            if res:
                prompt = _("Active calendars successfully exported to {0}".format(loop.options['icscal_file']))
            else:
                prompt = _("Could not export active calendars.")
        else:
            prompt = "icscal_file is not set in etmtk.cfg"
        MessageWindow(self, 'Active Calendar Export', prompt)

    def newItem(self, e=None):
        logger.debug('newItem')
        changed = SimpleEditor(parent=self, options=loop.options).changed
        if changed:
            logger.debug('changed, reloading data')
            # FIXME: if updateDataFromFile doesn't work
            # loop.loadData()

            self.updateAlerts()
            if self.weekly:
                self.showWeek()
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

        if self.weekly:
            master = self.canvas
        else:
            master = self.tree
        index, value = OptionsDialog(parent=self, master=master, title=_("instance: {0}").format(instance), prompt=prompt, opts=opt_lst, yesno=False).getValue()
        return index, value

    def copyItem(self, e=None):
        """
        newhsh = selected, rephsh = None
        """
        if 'r' in self.itemSelected:
            choice, value = self.which(COPY, self.dtSelected)
            logger.debug("{0}: {1}".format(choice, value))
            if not choice:
                self.tree.focus_set()
                return
            self.itemSelected['_dt'] = parse(self.dtSelected)
        else:
            # ans = DialogWindow(self, title=_('confirm'),
            #                    prompt=_("Clone this item?"))
            # ans = askokcancel('confirm', "Clone this item?", parent=self.tree, icon="question")
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
        # hsh_cpy['i'] = uniqueId()
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
                # edit_str = hsh2str(hsh_cpy, loop.options)

            elif choice == 2:
                # this and all subsequent instances
                tmp = []
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
                # edit_str = hsh2str(hsh_cpy, loop.options)

        changed = SimpleEditor(parent=self, newhsh=hsh_cpy, rephsh=None,
                         options=loop.options, title=title, modified=True).changed
        if changed:
            # loop.loadData()
            self.updateAlerts()
            if self.weekly:
                self.showWeek()
            else:
                self.showView(row=self.topSelected)
        else:
            self.tree.focus_set()

    def deleteItem(self, e=None):
        logger.debug('{0}: {1}'.format(self.itemSelected['_summary'], self.dtSelected))
        indx = 3
        if 'r' in self.itemSelected:
            indx, value = self.which(DELETE, self.dtSelected)
            logger.debug("{0}: {1}/{2}".format(self.dtSelected, indx, value))
            if not indx:
                if self.weekly:
                    self.canvas.focus_set()
                else:
                    self.tree.focus_set()
                return
            self.itemSelected['_dt'] = parse(self.dtSelected)
        else:
            # ans = askokcancel('Verify deletion', "Delete this item?", parent=self.tree)
            ans = self.confirm(
                title=_('Confirm'),
                prompt=_("Delete this item?"),
                parent=self.tree)
            if not ans:
                self.tree.focus_set()
                return
        loop.item_hsh = self.itemSelected
        loop.cmd_do_delete(indx)
        # loop.loadData()
        self.updateAlerts()
        if self.weekly:
            self.canvas.focus_set()
            self.showWeek()
        else:
            self.tree.focus_set()
            self.showView(row=self.topSelected)


    def editItem(self, e=None):
        logger.debug('{0}: {1}'.format(self.itemSelected['_summary'], self.dtSelected))
        choice = 3
        title = ETM
        if 'r' in self.itemSelected:
            # repeating
            choice, value = self.which(EDIT, self.dtSelected)
            logger.debug("{0}: {1}".format(choice, value))
            if self.weekly:
                self.canvas.focus_set()
            else:
                self.tree.focus_set()
            logger.debug(('dtSelected: {0}, {1}'.format(type(self.dtSelected), self.dtSelected)))
            self.itemSelected['_dt'] = parse(self.dtSelected)
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
        else: # replace
            self.mode = 2
            hsh_rev = deepcopy(self.itemSelected)

        logger.debug("mode: {0}; newhsh: {1}; rephsh: {2}".format( self.mode, hsh_cpy is not None, hsh_rev is not None))
        changed = SimpleEditor(parent=self, newhsh=hsh_cpy, rephsh=hsh_rev,
                     options=loop.options, title=title).changed

        if changed:
            # loop.loadData()
            self.updateAlerts()
            if self.weekly:
                self.showWeek()
            else:
                self.showView(row=self.topSelected)
        else:
            if self.weekly:
                self.canvas.focus_set()
            else:
                self.tree.focus_set()

    def editFile(self, e=None, file=None, config=False):
        if e is not None:
            logger.debug('event: {0}'.format(e))
            e = None
        relfile = relpath(file, self.options['etmdir'])
        logger.debug('file: {0}; config: {1}'.format(file, config))
        changed = SimpleEditor(parent=self, file=file, options=loop.options, title=relfile).changed
        if changed:
            logger.debug("config: {0}".format(config))
            if config:
                current_options = deepcopy(loop.options)
                (user_options, options, use_locale) = data.get_options(
                    d=loop.options['etmdir'])
                loop.options = options
                if options['calendars'] != current_options['calendars']:
                    self.updateCalendars()
            logger.debug("changed - calling loadData and updateAlerts")
            # loop.loadData()
            self.updateAlerts()
            self.showView()

    def editData(self, e=None):
        initdir = self.options['datadir']
        fileops = {'defaultextension': '.txt',
                   'filetypes': [('text files', '.txt')],
                   'initialdir': initdir,
                   'initialfile': "",
                   'title': 'etmtk data files',
                   'parent': self}
        filename = askopenfilename(**fileops)
        if not (filename and os.path.isfile(filename)):
            return False
        self.editFile(e, file=filename)

    def finishItem(self, e=None):
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
        loop.cmd_do_finish(chosen_day)
        # loop.loadData()
        self.updateAlerts()
        if self.weekly:
            self.showWeek()
        else:
            self.showView(row=self.topSelected)

    def rescheduleItem(self, e=None):
        if not self.itemSelected:
            return
        loop.item_hsh = item_hsh = self.itemSelected
        if self.dtSelected:
            loop.old_dt = old_dt = parse(self.dtSelected)
            title = _('rescheduling {0}').format(old_dt.strftime(
                rrulefmt))
        else:
            loop.old_dt = None
            title = _('scheduling an undated item')
        logger.debug('dtSelected: {0}'.format(self.dtSelected))
        if self.weekly:
            master = self.canvas
        else:
            master = self.tree
        prompt = _("""\
Enter the new date and time for the item or return an empty string to
use the current time. Relative dates and fuzzy parsing are supported.""")
        dt = GetDateTime(parent=self,  title=title,
                         prompt=prompt)
        new_dt = dt.value
        if new_dt is None:
            return
        new_dtn = new_dt.astimezone(gettz(self.itemSelected['z'])).replace(tzinfo=None)
        logger.debug('rescheduled from {0} to {1}'.format(self.dtSelected, new_dtn))
        loop.cmd_do_reschedule(new_dtn)
        # loop.loadData()
        self.updateAlerts()
        if self.weekly:
            self.showWeek()
        else:
            self.showView(row=self.topSelected)


    def showAlerts(self, e=None):
        t = _('remaining alerts for today')
        header = "{0:^7}\t{1:^7}\t{2:<8}{3:<26}".format(
            _('alert'),
            _('event'),
            _('type'),
            _('summary'))
        divider = '-' * 52
        if self.activeAlerts:
            # for alert in loop.alerts:
            s = '%s\n%s\n%s' % (
                header, divider, "\n".join(
                    ["{0:^7}\t{1:^7}\t{2:<8}{3:<26}".format(
                        x[1]['alert_time'], x[1]['_event_time'],
                        ", ".join(x[1]['_alert_action']),
                        utf8(x[1]['summary'][:26])) for x in self.activeAlerts]))
        else:
            s = _("none")
        self.textWindow(self, t, s, opts=self.options)

    def agendaView(self, e=None):
        self.setView(AGENDA)

    def dayView(self, e=None):
        self.setView(DAY)

    def pathView(self, e=None):
        self.setView(PATHS)

    def keywordView(self, e=None):
        self.setView(KEYWORDS)

    def tagView(self, e=None):
        self.setView(TAGS)

    def noteView(self, e=None):
        self.setView(NOTES)

    def setView(self, view, row=None):
        self.rowSelected = None
        logger.debug("view: {0}".format(view))
        if view != WEEK and self.weekly:
            self.closeWeekly()
        self.view = view
        self.showView(row=row)

    def filterView(self, e, *args):
        if self.weekly:
            return
        self.depth2id = {}
        fltr = self.filterValue.get()
        cmd = "{0} {1}".format(
            self.vm_options[self.vm_opts.index(self.view)][1], fltr)
        self.mode = 'command'
        self.process_input(event=e, cmd=cmd)

    def showView(self, e=None, row=None):
        logger.debug("view: {0}".format(self.view))
        if self.weekly:
            return
        self.depth2id = {}
        self.currentView.set(self.view)
        fltr = self.filterValue.get()
        cmd = "{0} {1}".format(
            self.vm_options[self.vm_opts.index(self.view)][1], fltr)
        self.mode = 'command'
        self.process_input(event=e, cmd=cmd)
        if row:
            logger.debug("row: {0}".format(row))
            # self.tree.see(max(0, self.rowSelected))
            # self.tree.yview(max(0, row - 1))
            self.tree.yview(max(0, row - 1))

    def showBusyTimes(self, event=None):
        if self.busy_info is None:
            return()
        theweek, weekdays, busy_lst, occasion_lst = self.busy_info

        lines = [theweek, '-'*len(theweek)]
        ampm = loop.options['ampm']
        s1 = s2 = ''
        for i in range(7):
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
        self.textWindow(parent=self.canvas, title=_('busy times'), prompt=s, opts=self.options)

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
        weekend = chosen_day + (6 - days) * ONEDAY
        weekdays = []

        day = weekbeg
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
                for item in loop.busytimes[isokey][1]:
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

    def closeWeekly(self, event=None):
        self.today_col = None
        for i in range(9, 15):
            self.viewmenu.entryconfig(i, state="disabled")
        self.canvas.pack_forget()
        self.weekly = False
        self.fltrbox.pack(side=LEFT, padx=0, pady=0)
        self.tree.pack(fill="both", expand=1, padx=4, pady=0)
        self.update_idletasks()
        if self.filter_active:
            self.viewmenu.entryconfig(5, state="disabled")
            self.viewmenu.entryconfig(6, state="normal")
        else:
            self.viewmenu.entryconfig(5, state="normal")
            self.viewmenu.entryconfig(6, state="disabled")

        for i in [3, 4, 5, 7]:
            self.viewmenu.entryconfig(i, state="normal")

        # self.fltr.configure(state="normal")
        # self.fltrbtn.configure(state="normal")
        # if self.filter_active:
        #     self.fltr.configure(bg="white")


    def showWeekly(self, event=None, chosen_day=None):
        """
        Open the canvas at the current week
        """
        if self.weekly:
            # we're in weekview already
            return
        self.weekly = True
        self.tree.pack_forget()
        self.fltrbox.pack_forget()
        for i in range(3, 8):
            self.viewmenu.entryconfig(i, state="disabled")

        self.view = WEEK
        self.currentView.set(WEEK)

        # self.current_day = get_current_time().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        self.chosen_day = chosen_day
        if chosen_day is None:
            self.chosen_day = get_current_time()
        else:
            self.chosen_day = chosen_day
        # self.selectedId = None

        self.canvas = canvas = Canvas(self.toppane, background="white", bd=2, relief="sunken")
        canvas.configure(highlightthickness=0)
        canvas.pack(side="top", fill="both", expand=1, padx=4, pady=0)

        self.canvas.bind("<Control-Button-1>", self.on_select_item)
        self.canvas.bind("<Double-1>", self.on_select_item)
        self.canvas.bind("<Configure>", self.showWeek)

        # canvas.bind('b', lambda e=event: self.after(AFTER, self.showBusyTimes))
        # canvas.bind('j', lambda e=event: self.after(AFTER, self.gotoWeek(event=e)))
        # disable ^J calling gotoDate
        # canvas.bind('<Control-j>', self.gotoWeek)
        canvas.bind("<Return>", lambda e: self.on_activate_item(event=e))
        canvas.bind('<Left>', (lambda e: self.showWeek(event=e, week=-1)))
        canvas.bind('<Right>', (lambda e: self.showWeek(event=e, week=1)))
        # canvas.bind('<space>', (lambda e: self.showWeek(event=e, week=0)))
        canvas.bind('<Up>', (lambda e: self.selectId(event=e, d=-1)))
        canvas.bind('<Down>', (lambda e: self.selectId(event=e, d=1)))

        if self.options['ampm']:
            self.hours = ["{0}am".format(i) for i in range(7,12)] + ['12pm'] + ["{0}pm".format(i) for i in range(1,12)]
        else:
            self.hours = ["{0}:00".format(i) for i in range(7, 24)]
        for i in [9, 10, 11, 12, 13, 15]:
            self.viewmenu.entryconfig(i, state="normal")
        self.canvas.focus_set()
        self.showWeek()

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
            return "break"

        theweek, weekdays, busy_lst, occasion_lst = self.setWeek(day)
        self.OnSelect()
        # self.content.delete("0.0", END)
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

        self.week_x = x = Decimal(w-1-l-r)/Decimal(7)
        self.week_y = y = Decimal(h-1-t-b)/Decimal(16)

        logger.debug("x: {0}, y: {1}".format(x, y))

        # week
        p = l + (w-1-l-r)/2, 20
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
                xy = start_x, t, end_x, t+y*16
                id = self.canvas.create_rectangle(xy, fill=OCCASIONFILL, outline="", width=0, tag='occasion')
                tmp = list(tup)
                tmp.append(day)
                self.busyHsh[id] = tmp
                occasion_ids.append(id)

        self.y_per_minute = y_per_minute = y/Decimal(60)
        busy_ids = []
        conf_ids = []
        self.today_id = None
        self.today_col = None
        self.timeline = None
        self.last_minutes = None
        for i in range(7):
            # x = X
            day = (self.week_beg + i * ONEDAY).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
            busy_times = busy_lst[i]
            start_x = l + i * x
            end_x = start_x + x
            if day == self.current_day:
                self.today_col = i
                xy = start_x, t, end_x, t+y*16
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
                t1 = t + (max(7 * 60, tup[0]) - 7 * 60 ) * y_per_minute
                # t1 = t + tup[0] * y_per_minute
                t2 = t + min(23 * 60, max(7 * 60, tup[1]) - 7 * 60) * y_per_minute
                # t2 = t + tup[1] * y_per_minute
                xy = start_x, max(t, t1), end_x, min(t2, t+y*16)
                conf = self.canvas.find_overlapping(*xy)
                id = self.canvas.create_rectangle(xy, fill=busyColor, width=0, tag=ttag)
                conf = [z for z in conf if z in busy_ids]
                busy_ids.append(id)
                conf_ids.extend(conf)
                if conf:
                    bb1 = self.canvas.bbox(id)
                    bb2 = self.canvas.bbox(*conf)
                    # bb1[0] = bb2[0], bb1[2] = bb2[2] - same day
                    # we want the max of bb1[1], bb2[1]
                    # and the min of bb1[4], bb2[4]
                    ol = bb1[0], max(bb1[1], bb2[1]), bb1[2], min(bb1[3], bb2[3])
                    self.canvas.create_rectangle(ol, fill=CONFLICTFILL, outline="", width=0, tag="conflict")

                tmp = list(tup[2:]) #id, time str, summary and file info
                tmp.append(daytime)
                self.busyHsh[id] = tmp
            if self.today_col is not None:
                xy = self.get_timeline()
                if xy:
                    self.canvas.delete('current_time')
                    self.canvas.create_line(xy, width=1, fill=CURRENTLINE, tag='current_time')

        self.busy_ids = busy_ids
        self.conf_ids = conf_ids
        for id in occasion_ids + busy_ids + conf_ids: #  + conf_ids:
            self.canvas.tag_bind(id, '<Any-Enter>', self.on_enter_item)
            # self.canvas.tag_bind(id, '<Any-Leave>', self.on_leave_item)
        self.canvas.bind('<Escape>', self.on_clear_item)

        self.canvas_ids = [z for z in self.busyHsh.keys()]
        self.canvas_ids.sort()
        self.canvas_idpos = None
        # border
        xy = l, t, l+x*7, t+y*16
        self.canvas.create_rectangle(xy, tag="grid")

        # verticals
        for i in range(1,7):
            # x = X
            xy = l+x*i, t, l+x*i, t+y*16
            self.canvas.create_line(xy, fill=LINECOLOR, tag="grid")
        # horizontals
        for j in range(1,16):
            xy = l, t+y*j, l+x*7, t+y*j
            self.canvas.create_line(xy, fill=LINECOLOR, tag="grid")
        # hours
        for j in range(17):
            if j%2:
                p = l-5, t+y*j
                self.canvas.create_text(p, text=self.hours[j], anchor="e")
        # days
        for i in range(7):
            # x = X
            p = l + x/2 + x*i, t-13
            # logger.debug("x: {0}, i: {1}, p: {2}".format(x, i, p))
            if self.today_col and i == self.today_col:
                self.canvas.create_text(p, text="{0}".format(weekdays[i]), fill=CURRENTLINE)
            else:
                self.canvas.create_text(p, text="{0}".format(weekdays[i]))

    def get_timeline(self):
        if not (self.weekly and self.today_col):
            return
        x = self.week_x
        if self.current_minutes < 7 * 60:
            return None
        elif self.current_minutes > 23 * 60:
            return None
        else:
            current_minutes = self.current_minutes
        (w, h, l, r, t, b) = self.margins
        start_x = l
        end_x = l + x * 7
        # t1 = t + (max(7 * 60, current_minutes) - 7 * 60 ) * y_per_minute
        t1 = t + (current_minutes - 7 * 60 ) * self.y_per_minute
        xy = start_x, t1, end_x, t1
        return xy

    def selectId(self, event, d=1):
        if self.canvas_idpos is None:
            self.canvas_idpos = 0
        else:
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
            if d == -1:
                self.canvas_idpos -= 1
                if self.canvas_idpos < 0:
                    self.canvas_idpos = len(self.canvas_ids) - 1
            elif d == 1:
                self.canvas_idpos += 1
                if self.canvas_idpos > len(self.canvas_ids) - 1:
                    self.canvas_idpos = 0
        self.selectedId = id = self.canvas_ids[self.canvas_idpos]
        self.canvas.itemconfig(id, fill=ACTIVEFILL)
        self.canvas.tag_raise('conflict')
        self.canvas.tag_raise(id)
        self.canvas.tag_lower('occasion')
        self.canvas.tag_lower('current_day')
        self.canvas.tag_raise('current_time')
        if id in self.busyHsh:
            self.OnSelect(uuid=self.busyHsh[id][0], dt=self.busyHsh[id][-1])

    def setFocus(self, e):
        self.canvas.focus()
        self.canvas.focus_set()

    def on_enter_item(self, e):
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
        self.canvas.itemconfig(id, fill=ACTIVEFILL)
        self.canvas.tag_raise('conflict')
        self.canvas.tag_raise('grid')
        self.canvas.tag_raise(id)
        self.canvas.tag_lower('occasion')
        self.canvas.tag_lower('current_day')
        self.canvas.tag_raise('current_time')

        if id in self.busyHsh:
            self.canvas_idpos = self.canvas_ids.index(id)
            # self.content.delete("1.0", END)
            self.OnSelect(uuid=self.busyHsh[id][0], dt=self.busyHsh[id][-1])

    def on_leave_item(self, e):
        id = self.canvas.find_withtag(CURRENT)[0]
        self.content.delete("0.0", END)

        if id in self.busy_ids:
            tags = self.canvas.gettags(id)
            if 'other' in tags:
                self.canvas.itemconfig(id, fill=OTHERFILL)
            else:
                self.canvas.itemconfig(id, fill=DEFAULTFILL)
        else:
            self.canvas.itemconfig(id, fill=OCCASIONFILL)
        self.canvas.tag_raise('conflict')
        self.canvas.tag_lower('occasion')
        self.selectedId = None
        self.canvas.focus("")

    def on_clear_item(self, e=None):
        # id = self.canvas.find_withtag(CURRENT)[0]
        # self.content.delete("0.0", END)

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
        # self.update_idletasks()

    def on_select_item(self, event):
        current = self.canvas.find_withtag(CURRENT)
        logger.debug('current: {0}'.format(current))
        if current and current[0] in self.busy_ids:
            self.selectedId = id = current[0]
            self.on_activate_item(event)
        else:
            self.newEvent(event)
        return "break"

    def on_activate_item(self, event):
        x = self.winfo_rootx() + 350
        y = self.winfo_rooty() + 50
        id = self.selectedId
        if not id:
            return
        # x1, y1, x2, y2 = self.canvas.coords(id)
        logger.debug("id: {0}, coords: {1}, {2}".format(id, x, y))
        self.uuidSelected = uuid = self.busyHsh[id][0]
        self.itemSelected = hsh = loop.uuid2hash[uuid]
        self.dtSelected = dt = fmt_datetime(self.busyHsh[id][-1], options=loop.options)
        self.itemmenu.post(x, y)
        self.itemmenu.focus_set()


    def newEvent(self, event):
        logger.debug("event: {0}".format(event))
        self.canvas.focus_set()
        min_round = 15
        px = event.x
        py = event.y
        (w, h, l, r, t, b) = self.margins
        x = Decimal(w-1-l-r)/Decimal(7)        # x per day intervals
        y = Decimal(h-1-t-b)/Decimal(16 * 60)       # y per minute intervals
        if px < l:
            px = l
        elif px > l + 7 * x:
            py = l + 7 * x
        if py < t:
            py = t
        elif py > t + 16 * 60 * y:
            py = t + 16 * 60 * y

        rx = round(Decimal(px - l)/x - Decimal(0.5))  # number of days
        ry = 7 * 60 + round(Decimal(py - t)/y)  # number of minutes
        ryr = round(ry/Decimal(min_round)) * min_round

        hours = ryr//60
        minutes = ryr % 60
        time = "{0}:{1:02d}".format(hours, minutes)

        dt = (self.week_beg + rx * ONEDAY).replace(hour=hours, minute=minutes, second=0, microsecond=0, tzinfo=None)
        # dtfmt = dt.strftime(loop.options['efmt'])
        tfmt = fmt_time(dt, options=loop.options)
        dfmt = dt.strftime("%a %b %d")
        dtfmt = "{0} {1}".format(tfmt, dfmt)
        ans = self.confirm(
            title=_('New event'),
            prompt=_("Create a new event for {0}?").format(dtfmt),
            parent=self.canvas)
        if ans:

            s = "* ? @s {0} @e 1h".format(dtfmt)
            hsh, msg = str2hsh(s, options=loop.options)

            changed = SimpleEditor(parent=self, master=self.canvas, newhsh=hsh, options=loop.options).changed

            if changed:
                logger.debug('changed, updating alerts, ...')
                # loop.loadData()
                self.updateAlerts()
                self.showView()
                self.showWeek()

    # noinspection PyShadowingNames
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
        b = Button(win, text=_('OK'), width=10, command=win.destroy, default='active')
        b.pack(side='bottom', fill=tkinter.NONE, expand=0, pady=0)
        win.bind('<Return>', (lambda e, b=b: b.invoke()))
        win.bind('<Escape>', (lambda e, b=b: b.invoke()))

        t = ReadOnlyText(f, wrap="word", padx=2, pady=2, bd=2, relief="sunken",
                         # font=tkFont.Font(family="Lucida Sans Typewriter"),
                         font=self.tkfixedfont,
                         # height=14,
                         # width=52,
                         takefocus=False)
        win.bind('<Left>', (lambda e: showYear(-1)))
        win.bind('<Right>', (lambda e: showYear(1)))
        win.bind('<space>', (lambda e: showYear()))
        showYear()
        t.pack(side='left', fill=tkinter.BOTH, expand=1, padx=0, pady=0)
        ysb = ttk.Scrollbar(f, orient='vertical', command=t.yview)
        ysb.pack(side='right', fill=tkinter.Y, expand=0, padx=0, pady=0)
        # t.configure(state="disabled", yscroll=ysb.set)
        t.configure(yscroll=ysb.set)
        f.pack(padx=2, pady=2, fill=tkinter.BOTH, expand=1)
        win.focus_set()
        win.grab_set()
        win.transient(self)
        win.wait_window(win)

    def newCommand(self, e=None):
        newcommand = self.newValue.get()
        self.newValue.set(self.newLabel)

    def help(self, event=None):
        res = self.menutree.showMenu("_")
        opts = self.options
        opts['help_opts'] = [
            [_("Shortcuts"), res],
            [_("Overview"), OVERVIEW],
            [_("Types"), ITEMTYPES],
            [_("@Keys"),ATKEYS],
            [_("Dates"), DATES],
            [_("Preferences"), PREFERENCES],
            [_("Reports"), REPORTS],
        ]

        hw = HelpWindow(parent=self, opts=opts)

    def about(self, event=None):
        res = loop.do_v("")
        self.textWindow(parent=self, title='etm', opts=self.options, prompt=res, modal=False)

    def checkForUpdate(self, event=None):
        res = checkForNewerVersion()[1]
        self.textWindow(parent=self, title='etm', prompt=res, opts=self.options)

    def showChanges(self, event=None):
        if self.itemSelected:
            f = self.itemSelected['fileinfo'][0]
            fn = " -f {0}".format(os.path.join(self.options['datadir'], f))
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
            numstr = "-l {0}".format(depth)
        command = loop.options['hg_history'].format(
            repo=loop.options['datadir'],
            numchanges=numstr, rev="{rev}", desc="{desc}") + fn
        logger.debug('history command: {0}'.format(command))
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True,
                             universal_newlines=True).stdout.read()
        self.textWindow(parent=self, title=title, prompt=str(p), opts=self.options)

    def focus_next_window(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def goHome(self, event=None):
        if self.weekly:
            self.showWeek(week=0)
        elif self.view == DAY:
            today = get_current_time().date()
            self.scrollToDate(today)
        else:
            self.tree.focus_set()
            self.tree.focus(1)
            self.tree.selection_set(1)
            self.tree.yview(0)
        return 'break'

    def nextItem(self, e=None):
        item = self.tree.selection()[0]
        if item:
            next = self.tree.next(item)
            if next:
                # self.tree.see(next)
                next = int(next)
                next -= 1
                self.tree.focus(next)
                self.tree.selection_set(next)

    def prevItem(self, e=None):
        item = self.tree.selection()[0]
        if item:
            prev = self.tree.prev(item)
            if prev:
                # self.tree.see(prev)
                prev = int(prev)
                prev += 1
                self.tree.focus(prev)
                self.tree.selection_set(prev)

    def OnSelect(self, event=None, uuid=None, dt=None):
        """
        Tree row has gained selection.
        """
        self.content.delete("1.0", END)
        if self.weekly: # week view
            if uuid is None:
                # disable clear selection
                self.viewmenu.entryconfig(13, state="disabled")
            else:
                # an item is selected, enable clear selection
                hsh = loop.uuid2hash[uuid]
                type_chr = hsh['itemtype']
                self.viewmenu.entryconfig(13, state="normal")
        elif uuid is None: # tree view
            item = self.tree.selection()[0]
            self.rowSelected = int(item)
            # type_chr is the actual type, e.g., "-"
            # show_chr is what's displayed in the tree, e.g., "X"
            type_chr = show_chr = self.tree.item(item)['text'][0]
            uuid, dt, hsh = self.getInstance(item)
            if hsh:
                type_chr = hsh['itemtype']

        if uuid is not None:
            # self.itemmenu.configure(state="normal")
            isRepeating = ('r' in hsh and dt)
            if isRepeating:
                item = "{0} {1}".format(_('selected'), dt)
                self.itemmenu.entryconfig(1, label="{0} ...".format(self.em_opts[1]))
                self.itemmenu.entryconfig(2, label="{0} ...".format(self.em_opts[2]))
            else:
                self.itemmenu.entryconfig(1, label=self.em_opts[1])
                self.itemmenu.entryconfig(2, label=self.em_opts[2])
                item = _('selected')
            isUnfinished = (type_chr in ['-', '+', '%'] and show_chr != 'X')
            hasLink = ('g' in hsh and hsh['g'])
            l1 = hsh['fileinfo'][1]
            l2 = hsh['fileinfo'][2]
            if l1 == l2:
                lines = "{0} {1}".format(_('line'), l1)
            else:
                lines = "{0} {1}-{2}".format(_('lines'), l1, l2)
            self.filetext = filetext = "{0}, {1}".format(hsh['fileinfo'][0],
                                                      lines)
            if 'errors' in hsh and hsh['errors']:
                text = "{1}\n\n{2}: {3}\n\n{4}: {5}".format(item, hsh['entry'].lstrip(), _("Errors"), hsh['errors'],  _("file"), filetext)
            else:
                text = "{1}\n\n{2}: {3}".format(item, hsh['entry'].lstrip(), _("file"), filetext)
            for i in [0, 1, 2, 4, 6]: # everything except finish and open link
                self.itemmenu.entryconfig(i, state='normal')
            if isUnfinished:
                self.itemmenu.entryconfig(3, state='normal')
            else:
                self.itemmenu.entryconfig(3, state='disabled')
            if hasLink:
                self.itemmenu.entryconfig(5, state='normal')
            else:
                self.itemmenu.entryconfig(5, state='disabled')
            self.uuidSelected = uuid
            self.itemSelected = hsh
            # self.dtSelected = dt.strftime(rfmt)
            if type(dt) is not datetime:
                dt = parse(dt)
            self.dtSelected = fmt_datetime(dt, options=loop.options)
            # logger.debug(('selected: {0}'.format(hsh)))
        else:
            text = ""
            for i in range(7):
                self.itemmenu.entryconfig(i, state='disabled')
            self.itemSelected = None
            self.uuidSelected = None
            self.dtSelected = None
        r = self.tree.identify_row(1)
        if r:
            self.topSelected = int(r)
        else:
            self.topSelected = 1

        logger.debug("top: {3}; row: '{0}'; uuid: '{1}'; instance: '{2}'".format(self.rowSelected, self.uuidSelected, self.dtSelected,  self.topSelected));
        self.content.delete("1.0", END)
        self.insert = self.content.insert(INSERT, text)
        return "break"

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

    def OnDoubleClick(self, event):
        """
        Double click on tree row
        """
        self.update_idletasks()

        item = self.tree.identify('item', event.x, event.y)
        uuid, dt, hsh = self.getInstance(item)
        if uuid is not None:
            self.editItem()
        return "break"

    def getInstance(self, item):
        instance = self.count2id[item]
        if instance is None:
            return None, None, None
        uuid, dt = self.count2id[item].split("::")
        hsh = loop.uuid2hash[uuid]
        logger.debug('item: {0}; uuid: {1}, dt: {2}'.format(item, uuid, dt))
        return uuid, dt, hsh

    def updateClock(self):
        self.now = get_current_time()
        self.current_minutes = self.now.hour * 60 + self.now.minute
        nxt = (60 - self.now.second) * 1000 - self.now.microsecond // 1000
        self.after(nxt, self.updateClock)
        nowfmt = "{0} {1}".format(
            s2or3(self.now.strftime(loop.options['reprtimefmt']).lower()),
            s2or3(self.now.strftime("%a %b %d %Z")))
        nowfmt = leadingzero.sub("", nowfmt)
        self.currentTime.set("{0}".format(nowfmt))
        today = self.now.date()
        newday = (today != self.today)
        self.today = today

        new, modified, deleted = get_changes(
            self.options, loop.file2lastmodified)
        if newday or new or modified or deleted:
            logger.debug('updating: newday or new: {0}; modified: {1}; deleted: {2}'
                         .format(new, modified, deleted))
            loop.loadData()
            if self.weekly:
                self.showWeek()
            else:
                self.showView()
        elif self.today_col is not None:
            xy = self.get_timeline()
            if xy:
                self.canvas.delete('current_time')
                self.canvas.create_line(xy, width=1, fill=CURRENTLINE, tag='current_time')
                self.update_idletasks()

        self.updateAlerts()

        if self.actionTimer.timer_status != STOPPED:
            self.timerStatus.set(self.actionTimer.get_time())
            if self.actionTimer.timer_minutes >= 1:
                if (self.options['action_interval'] and self.actionTimer.timer_minutes % loop.options['action_interval'] == 0):
                    logger.debug('action_minutes trigger: {0} {1}'.format(self.actionTimer.timer_minutes, self.actionTimer.timer_status))
                    if self.actionTimer.timer_status == 'running':
                        if ('running' in loop.options['action_timer'] and
                                loop.options['action_timer']['running']):
                            tcmd = loop.options['action_timer']['running']
                            logger.debug('running: {0}'.format(tcmd))
                            # process.startDetached(tcmd)
                            subprocess.call(tcmd, shell=True)

                    elif self.actionTimer.timer_status == 'paused':
                        if ('paused' in loop.options['action_timer'] and
                                loop.options['action_timer']['paused']):
                            tcmd = loop.options['action_timer']['paused']
                            # process.startDetached(tcmd)
                            logger.debug('running: {0}'.format(tcmd))
                            subprocess.call(tcmd, shell=True)

        logger.debug("next update in {0} milliseconds".format(nxt))

    def updateAlerts(self):
        self.update_idletasks()
        if loop.alerts:
            logger.debug('updateAlerts 1: {0}'.format(len(loop.alerts)))
        alerts = deepcopy(loop.alerts)
        if loop.options['calendars']:
            # logger.debug("cal_regex: {0}".format(self.cal_regex))
            alerts = [x for x in alerts if self.cal_regex.match(x[-1])]
        if alerts:
            curr_minutes = datetime2minutes(self.now)
            td = -1
            while td < 0 and alerts:
                file = alerts[0][-1]
                logger.debug('file: {0}'.format(file))
                td = alerts[0][0] - curr_minutes
                logger.debug('curr_minutes: {0}; td: {1}'.format(
                    curr_minutes, td))
                if td < 0:
                    logger.debug('including: {0}'.format(alerts[0]))
                    alerts.pop(0)
            logger.debug('remaining: {0}'.format(alerts))
            if td == 0:
                if ('alert_wakecmd' in loop.options and
                        loop.options['alert_wakecmd']):
                    cmd = loop.options['alert_wakecmd']
                    subprocess.call(cmd, shell=True)
                while td == 0:
                    hsh = alerts[0][1]
                    alerts.pop(0)
                    actions = hsh['_alert_action']
                    if 's' in actions:
                        if ('alert_soundcmd' in self.options and
                                self.options['alert_soundcmd']):
                            scmd = expand_template(
                                self.options['alert_soundcmd'], hsh)
                            subprocess.call(scmd, shell=True)
                        else:
                            self.textWindow(parent=self,
                                title="etm", prompt=_("""\
A sound alert failed. The setting for 'alert_soundcmd' is missing from \
your etmtk.cfg."""), opts=self.options)
                    if 'd' in actions:
                        if ('alert_displaycmd' in self.options and
                                self.options['alert_displaycmd']):
                            dcmd = expand_template(
                                self.options['alert_displaycmd'], hsh)
                            subprocess.call(dcmd, shell=True)
                        else:
                            self.textWindow(parent=self,
                                title="etm", prompt=_("""\
A display alert failed. The setting for 'alert_displaycmd' is missing \
from your etmtk.cfg."""), opts=self.options)
                    if 'v' in actions:
                        if ('alert_voicecmd' in self.options and
                                self.options['alert_voicecmd']):
                            vcmd = expand_template(
                                self.options['alert_voicecmd'], hsh)
                            subprocess.call(vcmd, shell=True)
                        else:
                            self.textWindow(parent=self,
                                title="etm", prompt=_("""\
An email alert failed. The setting for 'alert_voicecmd' is missing from \
your etmtk.cfg."""), opts=self.options)
                    if 'e' in actions:
                        missing = []
                        for field in [
                            'smtp_from',
                            'smtp_id',
                            'smtp_pw',
                            'smtp_server',
                            'smtp_to']:
                            if not self.options[field]:
                                missing.append(field)
                        if missing:
                            self.textWindow(parent=self,
                                title="etm", prompt=_("""\
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
                        for field in [
                            'sms_from',
                            'sms_message',
                            'sms_phone',
                            'sms_pw',
                            'sms_server',
                            'sms_subject']:
                            if not self.options[field]:
                                missing.append(field)
                        if missing:
                            self.textWindow(parent=self,
                                title="etm", prompt=_("""\
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
                        cmd = expand_template(proc, hsh)
                        subprocess.call(cmd, shell=True)

                    if not alerts:
                        break
                    td = alerts[0][0] - curr_minutes
        if alerts:
            logger.debug('updateAlerts 2: {0}'.format(len(alerts)))
        if alerts and len(alerts) > 0:
            self.pendingAlerts.set(len(alerts))
            self.pending.configure(state="normal")
            self.activeAlerts = alerts
        else:
            self.pendingAlerts.set(0)
            self.activeAlerts = []
            self.pending.configure(state="disabled")

    def textWindow(self, parent, title=None, prompt=None, opts=None, modal=True):
        d = TextDialog(parent, title=title, prompt=prompt, opts=opts, modal=modal)


    def goToDate(self, e=None):
        """
        :param e:
        :return:
        """
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
            else:
                self.scrollToDate(day.date())
        return "break"

    def setFilter(self, *args):
        if self.weekly:
            return
        self.filter_active = True
        self.viewmenu.entryconfig(5, state="disabled")
        self.viewmenu.entryconfig(6, state="normal")
        self.fltr.configure(bg="white", state="normal")
        self.fltrbtn.configure(state="normal")
        self.fltr.focus_set()

    def clearFilter(self, e=None):
        self.filter_active = False
        self.viewmenu.entryconfig(5, state="normal")
        self.viewmenu.entryconfig(6, state="disabled")
        self.filterValue.set('')
        self.fltr.configure(bg=BGCOLOR)
        self.fltrbtn.configure(state="disabled")
        self.tree.focus_set()


    def startActionTimer(self, event=None):
        """
        Prompt for a summary and start action timer.
        if uuid:
            if ~
                restart timer?
            else:
                enter summary or empty
        """
        if self.actionTimer.timer_status == STOPPED:
            if self.uuidSelected:
                nullok = True
                sel_hsh = loop.uuid2hash[self.uuidSelected]
                prompt = _("""\
    Enter a summary for the new action timer or return an empty string
    to create a timer based on the selected item.""")
            else:
                nullok = False
                # options = {'nullok': False}
                prompt = _("""\
    Enter a summary for the new action timer.""")
            options = {'nullok': nullok}
            value = GetString(parent=self, title=_('action timer'),  prompt=prompt, opts=options).value
            # value = d.value
            self.tree.focus_set()
            logger.debug('value: {0}'.format(value))
            if value is None:
                return "break"
            if value:
                self.timerItem = None
                hsh = str2hsh(value, options=loop.options)[0]
                # hsh['_summary'] = tmp['_summary']}
                # if 'e' in tmp:
                #     hsh['e'] = tmp['e']
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
        self.newmenu.entryconfig(2, state="normal")
        return "break"

    def finishActionTimer(self, event=None):
        if self.actionTimer.timer_status not in [RUNNING, PAUSED]:
            logger.info('stopping already stopped timer')
            return "break"
        self.actionTimer.timer_stop()
        self.timerStatus.set(self.actionTimer.get_time())
        hsh = self.actionTimer.timer_hsh
        changed = SimpleEditor(parent=self, newhsh=hsh, rephsh=None,
                         options=loop.options, title=_("new action"), modified=True).changed

        if changed:
            # clear status and reload
            self.actionTimer.timer_clear()
            self.timerStatus.set("")
            self.newmenu.entryconfig(2, state="disabled")
            # loop.loadData()
            self.updateAlerts()
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
                self.timerStatus.set(self.actionTimer.get_time())
            else:
                self.actionTimer.timer_clear()
                self.timerStatus.set("")
                self.newmenu.entryconfig(2, state="disabled")
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
        logger.debug('process_input cmd: {0}'.format(cmd))
        if not cmd:
            return True
        if self.mode == 'command':
            cmd = cmd.strip()
            if cmd[0] in ['a', 'c']:
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

        elif self.mode == 'edit':
            res = loop.cmd_do_edit(cmd)

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
            # MessageWindow(self, 'info', res)
            self.clearTree()
            return ()

        if type(res) == dict:
            self.showTree(res, event=event)
        else:
            # not a hash => not a tree
            self.textWindow(self, title='etm', prompt=res, opts=self.options)
            return 0

    def expand2Depth(self, event=None):
        prompt = _("""\
Enter an integer depth to expand branches
or 0 to expand all branches completely.""")
        depth = GetInteger(
            parent=self,
            title=_("depth"), prompt=prompt, opts=[0], default=0).value
        if depth is None:
            return ()
        maxdepth = max([k for k in self.depth2id])
        logger.debug('expand2Depth: {0}/{1}'.format(depth, maxdepth))
        if depth == 0:
            # expand all
            for k in self.depth2id:
                for item in self.depth2id[k]:
                    self.tree.item(item, open=True)
        else:
            depth -= 1
            for i in range(depth):
                for item in self.depth2id[i]:
                    self.tree.item(item, open=True)
            for i in range(depth, maxdepth+1):
                for item in self.depth2id[i]:
                    self.tree.item(item, open=False)
                # return('break')

    def scrollToDate(self, date):
        # only makes sense for schedule
        logger.debug("DAY: {0}; date: {1}".format(self.view == DAY, date))
        if self.view != DAY or date not in loop.prevnext:
            return ()
        active_date = loop.prevnext[date][1]
        if active_date not in self.date2id:
            return ()
        uid = self.date2id[active_date]
        self.scrollToId(uid)

    def scrollToId(self, uid):
        self.update_idletasks()
        self.tree.focus_set()
        self.tree.focus(uid)
        self.tree.selection_set(uid)
        self.tree.yview(int(uid) - 1)

    def showTree(self, tree, event=None):
        self.date2id = {}
        self.clearTree()
        self.count = 0
        self.count2id = {}
        self.addToTree(u'', tree[self.root], tree)
        loop.count2id = self.count2id
        # self.l.configure(state="normal")
        self.content.delete("0.0", END)
        # self.l.configure(state="disabled")
        if event is None:
            # view selected from menu
            self.goHome()

    def clearTree(self):
        """
        Remove all items from the tree
        """
        for child in self.tree.get_children():
            self.tree.delete(child)

    def addToTree(self, parent, elements, tree, depth=0):
        max_depth = 100
        for text in elements:
            self.count += 1
            # text is a key in the element (tree) hash
            # these keys are (parent, item) tuples
            if text in tree:
                # this is a branch
                item = " " + text[1]  # this is the label of the parent
                children = tree[text]  # this are the children tuples of item
                oid = self.tree.insert(parent, 'end', iid=self.count, text=item,
                                       open=(depth <= max_depth))
                self.depth2id.setdefault(depth, set([])).add(oid)
                # recurse to get children
                self.count2id[oid] = None
                self.addToTree(oid, children, tree, depth=depth + 1)
            else:
                # this is a leaf
                if len(text[1]) == 4:
                    uuid, item_type, col1, col2 = text[1]
                    dt = ''
                else:  # len 5 day view with datetime appended
                    uuid, item_type, col1, col2, dt = text[1]

                # This hack avoids encoding issues under python 2
                col1 = "{0} ".format(id2Type[item_type]) + col1

                if type(col2) == int:
                    col2 = '%s' % col2
                else:
                    col2 = s2or3(col2)

                oid = self.tree.insert(parent, 'end', iid=self.count, text=col1, open=(depth <= max_depth), value=[col2], tags=(item_type))
                # oid = self.tree.insert(parent, 'end', text=col1, open=True, value=[col2])
                self.count2id[oid] = "{0}::{1}".format(uuid, dt)
                if dt:
                    try:
                        if item_type == 'by':
                            # we want today, not the starting date for this
                            d = get_current_time().date()
                        else:
                            d = parse(dt[:10]).date()
                        if d not in self.date2id:
                            self.date2id[d] = parent
                    except:
                        logger.warn('could not parse: {0}'.format(dt))

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

    # errors = os.path.join(options['etmdir'], '.stderr.log')
    # outstr=codecs.open(errors, "w", 'utf-8')
    # sys.stderr = outstr
    # sys.stdout = outstr

    app = App()
    app.mainloop()


if __name__ == "__main__":
    setup_logging('3')
    main()
