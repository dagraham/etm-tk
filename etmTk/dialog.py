#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import logging.config
import uuid
import os
import os.path

logger = logging.getLogger()
import codecs
import ruamel.yaml as yaml

import platform

if platform.python_version() >= '3':
    import tkinter
    from tkinter import (
        ACTIVE,
        BooleanVar,
        BOTH,
        BROWSE,
        Button,
        Checkbutton,
        END,
        Entry,
        FLAT,
        Frame,
        INSERT,
        IntVar,
        Label,
        LEFT,
        Listbox,
        Radiobutton,
        RAISED,
        RIGHT,
        Scrollbar,
        StringVar,
        TclError,
        Text,
        Toplevel,
        W,
        X,
    )
    from tkinter import ttk
    from tkinter import font as tkFont
    unicode = str
else:
    import Tkinter as tkinter
    from Tkinter import (
        ACTIVE,
        BooleanVar,
        BOTH,
        BROWSE,
        Button,
        Checkbutton,
        END,
        Entry,
        FLAT,
        Frame,
        INSERT,
        IntVar,
        Label,
        LEFT,
        Listbox,
        Radiobutton,
        RAISED,
        RIGHT,
        Scrollbar,
        StringVar,
        TclError,
        Text,
        Toplevel,
        W,
        X,
    )
    import ttk
    import tkFont

from datetime import datetime, timedelta

from etmTk.data import (
    BGCOLOR,
    FGCOLOR,
    commandShortcut,
    completion_regex,
    ensureMonthly,
    fmt_date,
    fmt_period,
    fmt_shortdatetime,
    fmt_time,
    get_current_time,
    get_reps,
    getFileTuples,
    hsh2str,
    import_ical,
    parse_str,
    parse_period,
    relpath,
    rrulefmt,
    s2or3,
    str2hsh,
    uniqueId,
)

SOMEREPS = _('selected repetitions')
ALLREPS = _('all repetitions')
MESSAGES = _('Error messages')
VALID = _("Valid entry")
FOUND = "found"  # for found text marking
FINISH = _("Save and Close")

# MAKE = _("Make")
PRINT = _("Print")
EXPORTTEXT = _("Export report in text format ...")
EXPORTCSV = _("Export report in CSV format ...")
SAVESPECS = _("Save changes to report specifications")
CLOSE = _("Close")

# VALID = _("Valid {0}").format(u"\u2714")
SAVEANDEXIT = _("Save changes and exit?")
UNCHANGEDEXIT = _("Item is unchanged. Exit?")
CREATENEW = _("creating a new item")
EDITEXISTING = _("editing an existing item")

type2Text = {
    '$': _("In Basket"),
    '=': _("Default"),
    '^': _("Occasion"),
    '*': _("Event"),
    '~': _("Action"),
    '!': _("Note"),  # undated only appear in folders
    '-': _("Task"),  # for next view
    '+': _("Task Group"),  # for next view
    '%': _("Delegated Task"),
    '?': _("Someday"),
    '#': _("Hidden")
}

def sanitize_id(id):
    if type(id) == str:
        return id.strip().replace(" ", "")
    else:
        return id

(_ADD, _DELETE, _INSERT) = range(3)
(_ROOT, _DEPTH, _WIDTH) = range(3)


ONEMINUTE = timedelta(minutes=1)
ONEHOUR = timedelta(hours=1)

ONEDAY = timedelta(days=1)
ONEWEEK = timedelta(weeks=1)

STOPPED = _('stopped')
PAUSED = _('paused')
RUNNING = _('running')

FOUND = "found"

class SimpleEditor(Toplevel):

    def __init__(self, parent=None, master=None, file=None, line=None, newhsh=None, rephsh=None, options=None, title=None, start=None, modified=False):
        """
        If file is given, open file for editing.
        Otherwise, we are creating a new item and/or replacing an item
        mode:
          1: new: edit newhsh, replace none
          2: replace: edit and replace rephsh
          3: new and replace: edit newhsh, replace rephsh

        :param parent:
        :param file: path to file to be edited
        """
        # self.frame = frame = Frame(parent)
        if master is None:
            master = parent
        self.master = master
        Toplevel.__init__(self, master)
        self.minsize(400, 300)
        self.geometry('500x200')
        self.transient(parent)
        self.parent = parent
        self.loop = parent.loop
        BGCOLOR = self.loop.options['background_color']
        self.BGCOLOR = BGCOLOR
        HLCOLOR = self.loop.options['highlight_color']
        self.HLCOLOR = HLCOLOR
        FGCOLOR = self.loop.options['foreground_color']
        self.FGCOLOR = FGCOLOR
        self.configure(background=BGCOLOR, highlightcolor=HLCOLOR)
        self.messages = self.loop.messages
        self.messages = []
        self.mode = None
        self.changed = False

        self.scrollbar = None
        self.listbox = None
        self.autocompletewindow = None
        self.line = None
        self.match = None

        self.file = file
        self.initfile = None
        self.fileinfo = None
        self.repinfo = None
        self.title = title
        self.edithsh = {}
        self.newhsh = newhsh
        self.rephsh = rephsh
        self.value = ''
        self.options = options
        self.tkfixedfont = tkFont.nametofont("TkFixedFont")
        self.tkfixedfont.configure(size=self.options['fontsize_fixed'])
        # self.text_value.trace_variable("w", self.setSaveStatus)


        frame = Frame(self, bd=0)
        frame.pack(side="bottom", fill=X, padx=4, pady=0)
        frame.configure(background=BGCOLOR, highlightcolor=HLCOLOR, highlightbackground=BGCOLOR)

        qb = ttk.Button(frame, text=_("Cancel"), style="bg.TButton",  command=self.quit)
        qb.pack(side=LEFT, padx=4)
        self.bind("<Escape>", self.quit)

        l, c = commandShortcut('q')
        self.bind(c, self.quit)
        self.bind("<Escape>", self.cancel)

        # finish will evaluate the item entry and, if repeating, show reps
        finish = ttk.Button(frame, text=FINISH, style="bg.TButton", command=self.onFinish)
        finish.pack(side=RIGHT, padx=4)
        self.bind("<Control-s>", self.onFinish)


        # find
        xb = ttk.Button(frame, text='\u2716', command=self.clearFind, style="bg.TButton", width=0)
        xb.pack(side=LEFT, padx=0)
        self.find_text = StringVar(frame)
        self.e = Entry(frame, textvariable=self.find_text, width=10, highlightcolor=HLCOLOR, background=BGCOLOR, highlightbackground=BGCOLOR, highlightthickness=2, bd=2, foreground=FGCOLOR)
        self.e.pack(side=LEFT, padx=2, expand=1, fill=X)
        self.e.bind("<Return>", self.onFind)
        nb = ttk.Button(frame, text='\u279c', command=self.onFind, style="bg.TButton", width=0)
        nb.pack(side=LEFT, padx=0)

        text = Text(self, wrap="word", bd=2, relief="sunken", padx=3, pady=2, font=self.tkfixedfont, undo=True, width=70)
        text.configure(highlightthickness=0,  background=BGCOLOR, foreground=FGCOLOR, insertbackground=FGCOLOR)
        text.tag_configure(FOUND, background=FGCOLOR, foreground=BGCOLOR)

        text.pack(side="bottom", padx=4, pady=3, expand=1, fill=BOTH)
        self.text = text

        self.completions = self.loop.options['completions']

        if start is not None:
            # we have the starting text but will need a new uid
            text = start
            if self.rephsh is None:
                self.edithsh = {}
                self.mode = 1
                self.title = CREATENEW
            else:
                self.edithsh = self.rephsh
                self.mode = 2
                self.title = EDITEXISTING

        elif file is not None:
            # we're editing a file - if it's a data file we will add uid's
            # as necessary when saving
            self.mode = 'file'
            if not os.path.isfile(file):
                logger.warn('could not open: {0}'.format(file))
                text = ""
            else:
                with codecs.open(file, 'r', self.options['encoding']['file']) as f:
                    text = f.read()
        else:
            # we are creating a new item and/or replacing an item
            # mode:
            #   1: new
            #   2: replace
            #   3: new and replace
            initfile = ensureMonthly(options=self.options, date=datetime.now())
            # set the mode
            if newhsh is None and rephsh is None:
                # we are creating a new item from scratch and will need
                # a new uid
                self.mode = 1
                self.title = CREATENEW
                self.edithsh = {}
                self.edithsh['I'] = uniqueId()
                text = ''
            elif rephsh is None:  # newhsh is not None
                # we are creating a new item as a copy and will need
                # a new uid
                self.mode = 1
                self.title = CREATENEW
                self.edithsh = self.newhsh
                self.edithsh['I'] = uniqueId()
                if ('fileinfo' in newhsh and newhsh['fileinfo']):
                    initfile = newhsh['fileinfo'][0]
                text, msg = hsh2str(self.edithsh, self.options)
            elif newhsh is None:
                # we are editing and replacing rephsh - no file prompt
                # using existing uid
                self.title = EDITEXISTING
                self.mode = 2
                # self.repinfo = rephsh['fileinfo']
                self.edithsh = self.rephsh
                text, msg = hsh2str(self.edithsh, self.options)
            else:  # neither is None
                # we are changing some instances of a repeating item
                # we will be writing but not editing rephsh using its fileinfo
                # and its existing uid
                # we will be editing and saving newhsh using self.initfile
                # we will need a new uid for newhsh
                self.mode = 3
                self.title = CREATENEW
                self.edithsh = self.newhsh
                self.edithsh['I'] = uniqueId()
                if 'fileinfo' in newhsh and newhsh['fileinfo'][0]:
                    initfile = self.newhsh['fileinfo'][0]
                text, msg = hsh2str(self.edithsh, self.options)
            self.initfile = initfile
            logger.debug('mode: {0}; initfile: {1}; edit: {2}'.format(self.mode, self.initfile, self.edithsh))
        if self.title is not None:
            self.wm_title(self.title)
        self.settext(text)

        # clear the undo buffer
        if not modified:
            self.text.edit_reset()
            self.setmodified(False)
        self.text.bind('<<Modified>>', self.updateSaveStatus)

        self.text.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.quit)
        if parent:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                      parent.winfo_rooty() + 50))
        self.configure(background=BGCOLOR)
        l, c = commandShortcut('f')
        self.bind(c, lambda e: self.e.focus_set())
        l, c = commandShortcut('g')
        self.bind(c, lambda e: self.onFind())
        if start:
            # self.text.tag_add("sel", "1.1", "1.{0}".format(len(start)))
            self.text.mark_set(INSERT, 0.0)
        elif line:
            self.text.mark_set(INSERT, "{0}.0".format(line))
        else:
            self.text.mark_set(INSERT, END)
        self.text.see(INSERT)
        # l, c = commandShortcut('/')
        logger.debug("/: {0}, {1}".format(l, c))
        self.text.bind("<Control-space>", self.showCompletions)
        self.grab_set()
        self.wait_window(self)

    def settext(self, text=''):
        self.text.delete('1.0', END)
        self.text.insert(INSERT, text)
        self.text.mark_set(INSERT, '1.0')
        self.text.focus()
        logger.debug("modified: {0}".format(self.checkmodified()))

    def gettext(self):
        return self.text.get('1.0', END + '-1c')

    def setCompletions(self, *args):
        match = self.filterValue.get()
        self.matches = matches = [x for x in self.completions if x and x.lower().startswith(match.lower())]
        self.listbox.delete(0, END)
        for item in matches:
            self.listbox.insert(END, item)
        self.listbox.select_set(0)
        self.listbox.see(0)
        self.fltr.focus_set()

    def showCompletions(self, e=None):
        if not self.completions:
            return "break"
        if self.autocompletewindow:
            return "break"
        line = self.text.get("insert linestart", INSERT)
        m = completion_regex.search(line)
        if not m:
            logger.debug("no match in {0}".format(line))
            return "break"

        # set self.match here since it determines the characters to be replaced
        self.match = match = m.groups()[0]
        logger.debug("found match '{0}' in line '{1}'".format(match, line))

        self.autocompletewindow = acw = Toplevel(master=self.text)
        acw.geometry("+%d+%d" % (self.text.winfo_rootx() + 50, self.text.winfo_rooty() + 50))

        self.autocompletewindow.wm_attributes("-topmost", 1)

        self.filterValue = StringVar(self)
        self.filterValue.set(match)
        self.filterValue.trace_variable("w", self.setCompletions)
        self.fltr = Entry(acw, textvariable=self.filterValue)
        self.fltr.pack(side="top", fill="x")
        self.fltr.icursor(END)

        self.listbox = listbox = Listbox(acw, exportselection=False, width=self.loop.options['completions_width'])
        listbox.pack(side="bottom", fill=BOTH, expand=True)

        self.autocompletewindow.bind("<Double-1>", self.completionSelected)
        self.autocompletewindow.bind("<Return>", self.completionSelected)
        self.autocompletewindow.bind("<Escape>", self.hideCompletions)
        self.autocompletewindow.bind("<Up>", self.cursorUp)
        self.autocompletewindow.bind("<Down>", self.cursorDown)
        self.fltr.bind("<Up>", self.cursorUp)
        self.fltr.bind("<Down>", self.cursorDown)
        self.setCompletions()

    def is_active(self):
        return self.autocompletewindow is not None

    def hideCompletions(self, e=None):
        if not self.is_active():
            return
        # destroy widgets
        self.listbox.destroy()
        self.listbox = None
        self.autocompletewindow.destroy()
        self.autocompletewindow = None

    def completionSelected(self, event):
        # Put the selected completion in the text, and close the list
        modified = False
        if self.matches:
            cursel = self.matches[int(self.listbox.curselection()[0])]
        else:
            cursel = self.filterValue.get()
            modified = True

        start = "insert-{0}c".format(len(self.match))
        end = "insert-1c wordend"
        logger.debug("cursel: {0}; match: {1}; start: {2}; insert: {3}".format(
            cursel, self.match, start, INSERT))
        self.text.delete(start, end)
        self.text.insert(INSERT, cursel)
        self.hideCompletions()
        if modified:
            file = FileChoice(self, "append completion to file", prefix=self.loop.options['etmdir'], list=self.loop.options['completion_files']).returnValue()
            if (file and os.path.isfile(file)):
                with codecs.open(file, 'r', self.loop.options['encoding']['file']) as fo:
                    lines = fo.readlines()
                lines.append(cursel)
                lines.sort()
                content = "\n".join([x.strip() for x in lines if x.strip()])
                with codecs.open(file, 'w', self.loop.options['encoding']['file']) as fo:
                    fo.write(content)
            self.completions.append(cursel)
            self.completions.sort()

    def cursorUp(self, event=None):
        cursel = int(self.listbox.curselection()[0])
        # newsel = max(0, cursel=1)
        newsel = max(0, cursel - 1)
        self.listbox.select_clear(cursel)
        self.listbox.select_set(newsel)
        self.listbox.see(newsel)
        return "break"

    def cursorDown(self, event=None):
        cursel = int(self.listbox.curselection()[0])
        newsel = min(len(self.matches) - 1, cursel + 1)
        self.listbox.select_clear(cursel)
        self.listbox.select_set(newsel)
        self.listbox.see(newsel)
        return "break"

    def setmodified(self, bool):
        if bool is not None:
            self.text.edit_modified(bool)

    def checkmodified(self):
        return self.text.edit_modified()

    def updateSaveStatus(self, event=None):
        # Called by <<Modified>>
        if self.checkmodified():
            self.wm_title("{0} (modified)".format(self.title))
        else:
            self.wm_title("{0}".format(self.title))

    def onFinish(self, e=None):
        if self.mode == 'file':
            self.onSave()
        else:
            self.onCheck()

    def onSave(self, e=None, v=0):
        if not self.checkmodified():
            self.quit()
        elif self.file is not None:
            # we are editing a file
            alltext = self.gettext()
            self.loop.safe_save(self.file, alltext)
            self.setmodified(False)
            self.changed = True
            self.quit()
        else:
            # we are editing an item
            if self.mode in [1, 3]:  # new
                dir = self.options['datadir']
                if 's' in self.edithsh and self.edithsh['s']:
                    dt = self.edithsh['s']
                    file = ensureMonthly(self.options, dt.date())
                else:
                    dt = None
                    file = ensureMonthly(self.options)
                dir, initfile = os.path.split(file)
                # we need a filename for the new item
                # make datadir the root
                prefix, tuples = getFileTuples(self.options['datadir'], include=r'*.txt')
                if v == 2:
                    filename = file
                else:
                    ret = FileChoice(self, "etm data files", prefix=prefix, list=tuples, start=file).returnValue()
                    if not ret:
                        return False
                    filename = os.path.join(prefix, ret)
                if not os.path.isfile(filename):
                    return False
                filename = os.path.normpath(filename)
                logger.debug('saving to: {0}'.format(filename))
                self.text.focus_set()
            logger.debug('edithsh: {0}'.format(self.edithsh))
            if self.mode == 1:
                if self.loop.append_item(self.edithsh, filename):
                    logger.debug('append mode: {0}'.format(self.mode))
            elif self.mode == 2:
                if self.loop.replace_item(self.edithsh):
                    logger.debug('replace mode: {0}'.format(self.mode))
            else:  # self.mode == 3
                if self.loop.append_item(self.edithsh, filename):
                    logger.debug('append mode: {0}'.format(self.mode))
                if self.loop.replace_item(self.rephsh):
                    logger.debug('replace mode: {0}'.format(self.mode))

            # update the return value so that when it is not null then modified
            # is false and when modified is true then it is null
            self.setmodified(False)
            self.changed = True
            self.quit()
            return "break"

    def onCheck(self, event=None, showreps=True, showres=True):
        # only called when editing an item and finish is pressed
        self.loop.messages = []
        text = self.gettext()
        msg = []
        reps = []
        if text.startswith("BEGIN:VCALENDAR"):
            text = import_ical(vcal=text)
        logger.debug("text: {0} '{01}'".format(type(text), text))
        if self.edithsh and 'i' in self.edithsh:
            uid = self.edithsh['i']
        else:
            uid = None
        hsh, msg = str2hsh(text, options=self.options, uid=uid)
        logger.debug('itemtype: "{0}"'.format(hsh.get('itemtype', 'none')))

        if not msg:
            # we have a good hsh
            pre = post = warn = ""
            if 'r' in hsh:
                pre = _("Repeating ")
            elif 's' in hsh:
                dt = hsh['s']
                if hsh['itemtype'] in ['*', '~']:
                    if self.options['early_hour'] and dt.hour < self.options['early_hour']:
                        warn = _("Is {0} the starting time you intended?".format(fmt_time(dt, options=self.options)))
                    dtfmt = fmt_shortdatetime(hsh['s'], self.options)
                else:
                    if not dt.hour and not dt.minute:
                        dtfmt = fmt_date(dt, short=True)
                    else:
                        dtfmt = fmt_shortdatetime(hsh['s'], self.options)
                post = _(" starting {0}.").format(dtfmt)
            else:  # unscheduled
                pre = _("Unscheduled ")

            prompt = "{0}{1}{2}".format(pre, type2Text[hsh['itemtype']], post)
            if warn:
                prompt = prompt + "\n\n" + warn

            if self.edithsh and 'fileinfo' in self.edithsh:
                fileinfo = self.edithsh['fileinfo']
                self.edithsh = hsh
                self.edithsh['fileinfo'] = fileinfo
            else:
                # we have a new item without fileinfo
                self.edithsh = hsh
            # update missing fields
            logger.debug('calling hsh2str with {0}'.format(hsh))
            str, msg = hsh2str(hsh, options=self.options)

        self.loop.messages.extend(msg)
        if self.loop.messages:
            messages = "{0}".format("\n".join(self.loop.messages))
            logger.debug("messages: {0}".format(messages))
            self.messageWindow(MESSAGES, messages, opts=self.options)
            return False

        logger.debug("back from hsh2str with: {0}".format(str))
        if 'r' in hsh:
            showing_all, reps = get_reps(self.loop.options['bef'], hsh)
            if reps:
                if showreps:
                    try:
                        repsfmt = [unicode(x.strftime(rrulefmt)) for x in reps]
                    except:
                        repsfmt = [unicode(x.strftime("%X %x")) for x in reps]
                    logger.debug("{0}: {1}".format(showing_all, repsfmt))
                    if showing_all:
                        reps = ALLREPS
                    else:
                        reps = SOMEREPS
                    prompt = "{0}, {1}:\n\n  {2}".format(prompt, reps, "\n  ".join(repsfmt))
            else:
                warn = "No repetitions were generated.\nConsider removing the @r entry."
                prompt = prompt + "\n\n" + warn
            if self.loop.messages:
                messages = "{0}".format("\n".join(self.loop.messages))
                logger.debug("messages: {0}".format(messages))
                self.messageWindow(MESSAGES, messages, opts=self.options)
                return False

        if self.checkmodified():
            prompt += "\n\n{0}".format(SAVEANDEXIT)
        else:
            prompt += "\n\n{0}".format(UNCHANGEDEXIT)

        if str != text:
            self.settext(str)
        ans, value = OptionsDialog(parent=self, title=self.title, prompt=prompt, yesno=False, list=True).getValue()
        if ans:
            self.onSave(v=value)
        return

    def clearFind(self, *args):
        self.text.tag_remove(FOUND, "0.0", END)
        self.find_text.set("")

    def onFind(self, *args):
        target = self.find_text.get()
        logger.debug('target: {0}'.format(target))
        if target:
            where = self.text.search(target, INSERT, nocase=1)
        if where:
            pastit = where + ('+%dc' % len(target))
            self.text.tag_add(FOUND, where, pastit)
            self.text.mark_set(INSERT, pastit)
            self.text.see(INSERT)
            self.text.focus()

    def cancel(self, e=None):
        t = self.find_text.get()
        if t.strip():
            self.clearFind()
            return "break"
        if self.autocompletewindow:
            self.hideCompletions()
            return "break"
        if self.text.tag_ranges("sel"):
            self.text.tag_remove('sel', "1.0", END)
            return
        logger.debug(('calling quit'))
        self.quit()

    def quit(self, e=None):
        if self.checkmodified():
            ans = self.confirm(parent=self, title=_('Quit'), prompt=_("There are unsaved changes.\nDo you really want to quit?"))
        else:
            ans = True
        if ans:
            if self.master:
                logger.debug('setting focus')
                self.master.focus()
                self.master.focus_set()
                logger.debug('focus set')
            self.destroy()
            logger.debug('done')

    def messageWindow(self, title, prompt, opts=None, height=8, width=52):
        win = Toplevel(self,
                highlightcolor=self.HLCOLOR,
                background=self.BGCOLOR,
                highlightbackground=self.BGCOLOR)
        win.title(title)
        win.geometry("+%d+%d" % (self.text.winfo_rootx() + 50, self.text.winfo_rooty() + 50))
        f = Frame(win)
        # pack the button first so that it doesn't disappear with resizing
        b = ttk.Button(win, text=_('OK'),style="bg.TButton", command=win.destroy)
        b.pack(side='bottom', fill=tkinter.NONE, expand=0, pady=0)
        win.bind('<Return>', (lambda e, b=b: b.invoke()))
        win.bind('<KP_Enter>', (lambda e, b=b: b.invoke()))
        win.bind('<Escape>', (lambda e, b=b: b.invoke()))
        tkfixedfont = tkFont.nametofont("TkFixedFont")
        if 'fontsize_fixed' in self.loop.options and self.loop.options['fontsize_fixed']:
            tkfixedfont.configure(size=self.loop.options['fontsize_fixed'])

        t = ReadOnlyText(
            f, wrap="word", padx=2, pady=2, bd=2, relief="sunken",
            font=tkfixedfont,
            height=height,
            background=self.BGCOLOR,
            highlightcolor=self.HLCOLOR,
            foreground=self.FGCOLOR,
            width=width,
            takefocus=False)
        t.insert("0.0", prompt)
        t.pack(side='left', fill=tkinter.BOTH, expand=1, padx=0, pady=0)
        if height > 1:
            ysb = ttk.Scrollbar(f, orient='vertical', command=t.yview)
            ysb.pack(side='right', fill=tkinter.Y, expand=0, padx=0, pady=0)
            t.configure(state="disabled", yscroll=ysb.set)
            t.configure(yscroll=ysb.set)
        f.pack(padx=2, pady=2, fill=tkinter.BOTH, expand=1)

        win.focus_set()
        win.grab_set()
        win.transient(self)
        win.wait_window(win)

    def confirm(self, parent=None, title="", prompt="", instance="xyz"):
        ok, value = OptionsDialog(parent=parent, title=_("confirm").format(instance), prompt=prompt).getValue()
        return ok


class OriginalCommand:

    def __init__(self, redir, operation):
        self.redir = redir
        self.operation = operation
        self.tk = redir.tk
        self.orig = redir.orig
        self.tk_call = self.tk.call
        self.orig_and_operation = (self.orig, self.operation)

    def __repr__(self):
        return "OriginalCommand(%r, %r)" % (self.redir, self.operation)

    def __call__(self, *args):
        return self.tk_call(self.orig_and_operation + args)


########################################################
# WidgetRedirector and OriginalCommand are from idlelib
########################################################

class WidgetRedirector:

    """Support for redirecting arbitrary widget subcommands.

    Some Tk operations don't normally pass through Tkinter.  For example, if a
    character is inserted into a Text widget by pressing a key, a default Tk
    binding to the widget's 'insert' operation is activated, and the Tk library
    processes the insert without calling back into Tkinter.

    Although a binding to <Key> could be made via Tkinter, what we really want
    to do is to hook the Tk 'insert' operation itself.

    When a widget is instantiated, a Tcl command is created whose name is the
    same as the pathname widget._w.  This command is used to invoke the various
    widget operations, e.g. insert (for a Text widget). We are going to hook
    this command and provide a facility ('register') to intercept the widget
    operation.

    In IDLE, the function being registered provides access to the top of a
    Percolator chain.  At the bottom of the chain is a call to the original
    Tk widget operation.

    """
    def __init__(self, widget):
        self._operations = {}
        self.widget = widget            # widget instance
        self.tk = tk = widget.tk        # widget's root
        w = widget._w                   # widget's (full) Tk pathname
        self.orig = w + "_orig"
        # Rename the Tcl command within Tcl:
        tk.call("rename", w, self.orig)
        # Create a new Tcl command whose name is the widget's pathname, and
        # whose action is to dispatch on the operation passed to the widget:
        tk.createcommand(w, self.dispatch)

    def __repr__(self):
        return "WidgetRedirector(%s<%s>)" % (self.widget.__class__.__name__,
                                             self.widget._w)

    def close(self):
        for operation in list(self._operations):
            self.unregister(operation)
        widget = self.widget
        del self.widget
        orig = self.orig
        del self.orig
        tk = widget.tk
        w = widget._w
        tk.deletecommand(w)
        # restore the original widget Tcl command:
        tk.call("rename", orig, w)

    def register(self, operation, function):
        self._operations[operation] = function
        setattr(self.widget, operation, function)
        return OriginalCommand(self, operation)

    def unregister(self, operation):
        if operation in self._operations:
            function = self._operations[operation]
            del self._operations[operation]
            if hasattr(self.widget, operation):
                delattr(self.widget, operation)
            return function
        else:
            return None

    def dispatch(self, operation, *args):
        '''Callback from Tcl which runs when the widget is referenced.

        If an operation has been registered in self._operations, apply the
        associated function to the args passed into Tcl. Otherwise, pass the
        operation through to Tk via the original Tcl function.

        Note that if a registered function is called, the operation is not
        passed through to Tk.  Apply the function returned by self.register()
        to *args to accomplish that.  For an example, see ColorDelegator.py.

        '''
        m = self._operations.get(operation)
        try:
            if m:
                return m(*args)
            else:
                return self.tk.call((self.orig, operation) + args)
        except TclError:
            return ""


class Node:

    def __init__(self, name, identifier=None, expanded=True):
        self.__identifier = (uuid.uuid1()) if identifier is None else sanitize_id(s2or3(identifier))
        self.name = name
        self.expanded = expanded
        self.__bpointer = None
        self.__fpointer = []

    @property
    def identifier(self):
        return self.__identifier

    @property
    def fpointer(self):
        return self.__fpointer

    def update_fpointer(self, identifier, mode=_ADD):
        if mode is _ADD:
            self.__fpointer.append(sanitize_id(identifier))
        elif mode is _DELETE:
            self.__fpointer.remove(sanitize_id(identifier))
        elif mode is _INSERT:
            self.__fpointer = [sanitize_id(identifier)]


class MenuTree:
    """
    Used for the shortcuts menu
    """

    def __init__(self):
        self.nodes = []
        self.lst = []

    def get_index(self, position):
        for index, node in enumerate(self.nodes):
            if node.identifier == position:
                break
        return index

    def create_node(self, name, identifier=None, parent=None):
        # logger.debug("name: {0}, identifier: {1}; parent: {2}".format(name, identifier, parent))

        node = Node(name, identifier)
        self.nodes.append(node)
        self.__update_fpointer(parent, node.identifier, _ADD)
        node.bpointer = parent
        return node

    def showMenu(self, position, level=_ROOT):
        queue = self[position].fpointer
        if level == _ROOT:
            self.lst = []
        else:
            name, key = self[position].name.split("::")
            name = "{0}{1}".format("    " * (level - 1), name.strip())
            s = "{0:<48} {1:^12}".format(name, key.strip())
            self.lst.append(s)
            logger.debug("position: {0}, level: {1}, name: {2}, key: {3}".format(position, level, name, key))
        if self[position].expanded:
            level += 1
            for element in queue:
                self.showMenu(element, level)  # recursive call
        return "\n".join(self.lst)

    def __update_fpointer(self, position, identifier, mode):
        if position is None:
            return
        else:
            self[position].update_fpointer(identifier, mode)

    def __getitem__(self, key):
        return self.nodes[self.get_index(key)]

class Timer():
    def __init__(self, parent=None, options={}):
        """
        Methods providing timers
        """
        self.parent = parent
        self.options = options
        self.loop = parent.loop
        self.idleactive = False
        self.showIdle = self.loop.options['display_idletime']
        BGCOLOR = self.loop.options['background_color']
        HLCOLOR = self.loop.options['highlight_color']
        FGCOLOR = self.loop.options['foreground_color']
        self.BGCOLOR = BGCOLOR
        self.HLCOLOR = HLCOLOR
        self.FGCOLOR = FGCOLOR
        self.timermenu = parent.timermenu
        self.match = ""
        self.etmtimers = os.path.normpath(os.path.join(options['etmdir'], ".etmtimers"))
        self.dfile_encoding = options['encoding']['file']

        self.resetTimers()

    def updateMenu(self, e=None):
        if self.activeTimers:
            self.timermenu.entryconfig(1, state="active")
            if self.currentTimer:
                self.timermenu.entryconfig(2, state="active")
            else:
                self.timermenu.entryconfig(2, state="disabled")
            self.timermenu.entryconfig(3, state="active")
            self.timermenu.entryconfig(4, state="active")
            self.timermenu.entryconfig(5, state="active")
            self.timermenu.entryconfig(6, state="active")
        elif self.idleactive:
            self.timermenu.entryconfig(1, state="disabled")
            self.timermenu.entryconfig(2, state="disabled")
            self.timermenu.entryconfig(3, state="disabled")
            self.timermenu.entryconfig(4, state="active")
            self.timermenu.entryconfig(5, state="active")
            self.timermenu.entryconfig(6, state="active")
        else:
            self.timermenu.entryconfig(1, state="disabled")
            self.timermenu.entryconfig(2, state="disabled")
            self.timermenu.entryconfig(3, state="disabled")
            self.timermenu.entryconfig(4, state="disabled")
            self.timermenu.entryconfig(5, state="disabled")
            self.timermenu.entryconfig(6, state="disabled")

    def resetTimers(self):
        try:
            self.loadTimers()
            logger.info("reloaded saved timer data")
        except:
            self.activeDate = datetime.now().date()
            self.activeTimers = {} # summary -> { total, start, stop }
            self.currentTimer = None # summary
            self.currentStatus = STOPPED
            self.currentMinutes = 0
            self.idletime = 0 * ONEMINUTE
            self.idlestart = None
            logger.info("reset timer data")

    def clearIdle(self, e=None):
        # reset idle
        self.idletime = 0 * ONEMINUTE
        if self.activeTimers:
            if self.currentStatus == RUNNING:
                self.idlestart = None
            else:
                self.idlestart = datetime.now()
        else:
            self.idlestart = None
            self.idleactive = False
        self.saveTimers()
        if self.parent:
            self.parent.updateTimerStatus()
            self.parent.update_idletasks()

    def toggleIdle(self, e=None):
        if not self.idleactive:
            return
        self.showIdle = not self.showIdle
        if self.parent:
            self.parent.updateTimerStatus()
            self.parent.update_idletasks()

    def selectTimer(self, e=None, new=True, title=None, name=None):
        """
        Combo box with list of active timer summaries and option to create a new, unique summary.
        """
        self.selected = None
        self.new = new
        now = datetime.now()
        if not self.activeTimers:
            if not new:
                return False
            self.completions = []
            if title is None:
                title = _("Create Timer")
        else:
            if title is None:
                title = _("Create or Choose Timer")
            self.completions = []
            tmp = [(self.activeTimers[x]['stop'], x) for x in self.activeTimers]
            # put the most recently stopped timers at the top
            sort = sorted(tmp, reverse=True)
            self.completions = []
            for x in sort:
                timer = x[1]
                h = self.activeTimers[timer]
                if timer == self.currentTimer and self.currentStatus == RUNNING:
                    t = fmt_period(h['total'] + now - h['start'])
                    s = '\u279c'
                else:
                    t = fmt_period(h['total'])
                    s = '\u2716'
                self.completions.append(" {0} {1} {2} {3} ".format(timer, '\u25aa', t, s))

        # return the focus to the right place
        if self.parent.weekly or self.parent.monthly:
            master = self.parent.canvas
        else:
            master = self.parent.tree
        master=self.parent
        self.timerswindow = win = Toplevel(master=master, highlightcolor=self.HLCOLOR, background=self.BGCOLOR, highlightbackground=self.BGCOLOR, bd=4)
        self.timerswindow.title(title)

        self.filterValue = StringVar(master)
        self.timerswindow.geometry("+%d+%d" % (master.winfo_rootx() + 50, master.winfo_rooty() + 50))
        self.timerswindow.minsize(240, 30)

        self.timerswindow.wm_attributes("-topmost", 1)

        self.filterValue = StringVar(master)
        self.filterValue.set("")
        self.filterValue.trace_variable("w", self.setCompletions)
        self.fltr = Entry(self.timerswindow,
                        highlightcolor=self.HLCOLOR,
                        highlightbackground=self.BGCOLOR,
                        background=self.BGCOLOR,
                        foreground=self.FGCOLOR,
                        highlightthickness=0,
                        selectbackground=self.FGCOLOR,
                        selectforeground=self.BGCOLOR,
                        textvariable=self.filterValue)
        self.fltr.pack(side="top", fill="x")
        self.fltr.icursor(END)

        self.listbox = listbox = Listbox(self.timerswindow,
                        highlightcolor=self.HLCOLOR,
                        highlightbackground=self.BGCOLOR,
                        background=self.BGCOLOR,
                        foreground=self.FGCOLOR,
                        selectbackground=self.FGCOLOR,
                        selectforeground=self.BGCOLOR,
                        highlightthickness=0,
                        exportselection=False)
        listbox.pack(side="bottom", fill=BOTH, expand=True)

        self.timerswindow.bind("<Double-1>", self.completionSelected)
        self.timerswindow.bind("<Return>", self.completionSelected)
        self.timerswindow.bind("<Escape>", self.hideCompletions)
        self.timerswindow.bind("<Up>", self.cursorUp)
        self.timerswindow.bind("<Down>", self.cursorDown)
        self.fltr.bind("<Up>", self.cursorUp)
        self.fltr.bind("<Down>", self.cursorDown)
        if name is not None:
            self.filterValue.set(name)
        self.setCompletions()
        win.wait_window(win)


    def setCompletions(self, *args):
        match = self.filterValue.get()
        self.matches = matches = [x for x in self.completions if x and x.lower().startswith(match.lower())]
        self.listbox.delete(0, END)
        for item in matches:
            self.listbox.insert(END, item)
        self.listbox.select_set(0)
        self.listbox.see(0)
        self.fltr.focus_set()

    def is_active(self):
        return self.timerswindow is not None

    def hideCompletions(self, e=None):
        # destroy widgets
        if not self.is_active():
            return
        self.fltr.destroy()
        self.fltr = None
        self.listbox.destroy()
        self.listbox = None
        self.timerswindow.destroy()
        self.timerswindow = None

    def completionSelected(self, event):
        # Put the selected completion in the text, and close the list
        cursel = None
        if self.matches:
            cursel = self.matches[int(self.listbox.curselection()[0])]
        else:
            tmp = self.filterValue.get()
            if tmp in self.activeTimers or self.new:
                cursel = tmp
        logger.debug("cursel: {0}; match: {1}".format(cursel, self.match))
        self.hideCompletions(e=event)
        if cursel is not None:
            self.selected = cursel.split('\u25aa')[0].strip()
            if self.new:
                self.startTimer()

    def cursorUp(self, event=None):
        cursel = int(self.listbox.curselection()[0])
        # newsel = max(0, cursel=1)
        newsel = max(0, cursel - 1)
        self.listbox.select_clear(cursel)
        self.listbox.select_set(newsel)
        self.listbox.see(newsel)
        return "break"

    def cursorDown(self, event=None):
        cursel = int(self.listbox.curselection()[0])
        newsel = min(len(self.matches) - 1, cursel + 1)
        self.listbox.select_clear(cursel)
        self.listbox.select_set(newsel)
        self.listbox.see(newsel)
        return "break"

    def saveTimers(self):
        """
        dump activeTimers, ...
        """
        tmp = (
            self.activeDate,
            self.activeTimers,
            self.currentTimer,
            self.currentStatus,
            self.currentMinutes,
            self.idlestart,
            self.idletime
        )
        fo = codecs.open(self.etmtimers, 'w', self.dfile_encoding)
        yaml.dump(tmp, fo)
        fo.close()
        self.updateMenu()

    def loadTimers(self):
        """
        load activeTimers
        """
        fo = codecs.open(self.etmtimers, 'r', self.dfile_encoding)
        tmp = yaml.safe_load(fo)
        fo.close()
        (self.activeDate, self.activeTimers, self.currentTimer, self.currentStatus, self.currentMinutes, self.idlestart, self.idletime) = tmp
        if self.idlestart or self.idletime:
            self.idleactive = True
        if self.activeDate != datetime.now().date():
            self.newDay()
        self.updateMenu()

    def startTimer(self, e=None):
        self.pauseTimer()
        self.idleactive = True
        if not self.selected:
            return

        if self.currentStatus == PAUSED:
            if self.idlestart:
                self.idletime += datetime.now() - self.idlestart
                self.idlestart = None

        summary = self.selected
        if summary not in self.activeTimers:
            # new timer
            hsh = {}
            hsh['total'] = 0 * ONEMINUTE
            hsh['stop'] = datetime.now()
        else:
            hsh = self.activeTimers[summary]

        hsh['start'] = datetime.now()
        self.activeTimers[summary] = hsh
        self.currentTimer = summary
        self.currentStatus = RUNNING

        self.saveTimers()

        if self.parent:
            self.parent.updateTimerStatus()
            self.parent.update_idletasks()

    def finishTimer(self, e=None):
        self.pauseTimer()
        self.selectTimer(new=False, title="Finish Timer")
        if not self.selected:
            return

        self.currentStatus = STOPPED
        self.currentTimer = None

        hsh = self.activeTimers[self.selected]
        hsh['summary'] = self.selected

        self.saveTimers()

        if self.parent:
            self.parent.updateTimerStatus()
            self.parent.update_idletasks()

        return hsh

    def deleteTimer(self, e=None, timer=None):
        if timer is None:
            self.selectTimer(new=False, title=_("Delete Timer"))
            timer = self.selected
        if not timer or timer not in self.activeTimers:
            return
        self.pauseTimer()
        if self.currentTimer == timer:
            self.currentTimer = None
            self.currentMinutes = 0
            self.currentStatus = STOPPED
        if self.idlestart:
            idle = (datetime.now() - self.idlestart) + self.idletime
        elif self.idletime:
            idle = self.idletime
        else:
            idle = 0 * ONEMINUTE
        self.idletime = idle + self.activeTimers[timer]['total']
        del self.activeTimers[timer]
        self.saveTimers()
        if self.parent:
            self.parent.updateTimerStatus()
            self.parent.update_idletasks()


    def newDay(self, e=None):
        now = datetime.now()
        self.activeDate = now.date()
        self.idlestart = None
        self.idletime = 0 * ONEMINUTE

        if not self.activeTimers:
            self.idleactive = False
            self.activeTimers = {} # summary -> { total, start, stop }
            self.currentTimer = None # summary
            self.currentStatus = STOPPED
            self.currentMinutes = 0

        running = (self.currentTimer and self.currentStatus == RUNNING)

        curfile = ensureMonthly(self.options, date=now.date())
        tmp = []
        for timer in self.activeTimers:
            # create inbox entries
            thsh = self.activeTimers[timer]
            hsh = {"itemtype": "$", "_summary": timer, "s": thsh['start'], "e": thsh['total']}
            tmp.append([timer, hsh])

        for timer, hsh in tmp:
            res = self.loop.append_item(hsh, curfile)
            if res:
                del self.activeTimers[timer]

        if running:
            # currentStatus == RUNNING
            hsh = {}
            hsh['total'] = 0 * ONEMINUTE
            hsh['start'] = hsh['stop'] = now
            self.activeTimers[self.currentTimer] = hsh
        else:
            self.currentTimer = None
            self.currentStatus = STOPPED

        self.currentMinutes = 0
        self.saveTimers()
        if self.parent:
            self.parent.updateTimerStatus()
            self.parent.update_idletasks()

    def toggleCurrent(self, e=None):
        """

        """
        if not self.activeTimers or not self.currentTimer:
            return

        hsh = self.activeTimers[self.currentTimer]

        if self.currentStatus == RUNNING:
            hsh['total'] += datetime.now() - hsh['start']
            hsh['stop'] = datetime.now()
            self.idlestart = datetime.now()
            self.currentStatus = PAUSED

        elif self.currentStatus == PAUSED:
            hsh['start'] = datetime.now()
            if self.idlestart:
                self.idletime += datetime.now() - self.idlestart
                self.idlestart = None
            self.currentStatus = RUNNING

        self.activeTimers[self.currentTimer] = hsh

        self.saveTimers()

        if self.parent:
            self.parent.updateTimerStatus()
            self.parent.update_idletasks()


    def pauseTimer(self):
        """
        Pause the running timer
        """
        if self.activeTimers and self.currentTimer and self.currentStatus == RUNNING:
            self.toggleCurrent()

        self.saveTimers()
        if self.parent:
            self.parent.updateTimerStatus()
            self.parent.update_idletasks()
        return False

    def getStatus(self):
        """
        Return the status of the timers for the status bar
        """
        if not self.activeTimers and not self.idlestart and not self.idletime:
            return "", ""
        idlestatus = ""
        now = datetime.now()
        if self.currentTimer and self.currentStatus:
            hsh = self.activeTimers[self.currentTimer]
            if self.currentStatus == RUNNING:
                status='\u279c'
                idlestatus='\u2716'
                hsh['total'] = hsh['total'] + (now - hsh['start'])
                hsh['start'] = now
            else:
                status='\u2716'
                idlestatus='\u279c'
            ret1 = "{0}: {1} {2}".format(self.currentTimer, fmt_period(hsh['total']), status)

            total = hsh['total']
            self.currentMinutes = total.seconds // 60

        elif self.activeTimers:
            ret1 = "{0}".format(_("all paused"))
        else:
            ret1 = ""

        if self.showIdle:
            if self.idlestart:
                idle = (now - self.idlestart) + self.idletime
            elif self.idletime:
                idle = self.idletime
            else:
                idle = 0 * ONEMINUTE
            ret2 = "{0}: {1} {2}".format(_("idle"), fmt_period(idle), idlestatus)
        else:
            ret2 = ""

        logger.debug("timer: {0} {1}".format(ret1, ret2))
        return ret1, ret2


class ReadOnlyText(Text):
    # noinspection PyShadowingNames
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        bg = kwargs.pop('background', None)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")
        self.configure(highlightthickness=0, insertwidth=0, takefocus=0, wrap="word", background=bg)


class MessageWindow():
    # noinspection PyShadowingNames
    def __init__(self, parent, title, prompt, opts={}):
        self.loop = parent.loop
        BGCOLOR = self.loop.options['background_color']
        HLCOLOR = self.loop.options['highlight_color']
        FGCOLOR = self.loop.options['foreground_color']
        self.win = Toplevel(parent, highlightcolor=HLCOLOR, background=BGCOLOR)
        self.win.protocol("WM_DELETE_WINDOW", self.cancel)
        self.parent = parent
        self.options = opts
        self.win.title(title)
        tkfixedfont = tkFont.nametofont("TkFixedFont")
        if 'fontsize_fixed' in self.options and self.options['fontsize_fixed']:
            tkfixedfont.configure(size=self.options['fontsize_fixed'])

        self.content = ReadOnlyText(self.win, wrap="word", padx=3, bd=2, height=10, relief="sunken", font=tkfixedfont, width=46, takefocus=False, background=BGCOLOR, highlightcolor=HLCOLOR, foreground=FGCOLOR)
        self.content.pack(fill=tkinter.BOTH, expand=1, padx=10, pady=10)
        self.content.insert("1.0", prompt)
        b = ttk.Button(self.win, text=_("OK"), style="bg.TButton",  command=self.cancel)
        # b = Button(self.win, text=_('OK'), width=10, command=self.cancel, default='active', pady=2)
        b.pack()
        self.win.bind('<Return>', (lambda e, b=b: b.invoke()))
        self.win.bind('<Escape>', (lambda e, b=b: b.invoke()))
        self.win.focus_set()
        self.win.grab_set()
        self.win.transient(parent)
        self.win.wait_window(self.win)
        return

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.win.destroy()


class FileChoice(object):
    def __init__(self, parent, title=None, prefix=None, list=[], start='', ext="txt", new=False):
        self.parent = parent
        self.loop = parent.loop
        BGCOLOR = self.loop.options['background_color']
        self.BGCOLOR = BGCOLOR
        HLCOLOR = self.loop.options['highlight_color']
        self.HLCOLOR = HLCOLOR
        FGCOLOR = self.loop.options['foreground_color']
        self.FGCOLOR = FGCOLOR
        self.value = None
        self.prefix = prefix
        self.list = list
        if prefix and start:
            self.start = relpath(start, prefix)
        else:
            self.start = start
        self.ext = ext
        self.new = new

        self.modalPane = Toplevel(self.parent, highlightcolor=HLCOLOR, background=BGCOLOR)
        logger.debug('winfo: {0}, {1}; {2}, {3}'.format(parent.winfo_rootx(), type(parent.winfo_rootx()), parent.winfo_rooty(), type(parent.winfo_rooty())))
        self.modalPane.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        self.modalPane.transient(self.parent)
        self.modalPane.grab_set()

        self.modalPane.bind("<Return>", self._choose)
        self.modalPane.bind("<Escape>", self._cancel)

        if title:
            self.modalPane.title(title)

        if new:
            nameFrame = Frame(self.modalPane, highlightcolor=HLCOLOR, background=BGCOLOR)
            nameFrame.pack(side="top", padx=18, pady=2, fill="x")

            nameLabel = Label(nameFrame, text=_("file:"), bd=1, relief="flat", anchor="w", padx=0, pady=0, highlightcolor=HLCOLOR, background=BGCOLOR, foreground=FGCOLOR)
            nameLabel.pack(side="left")

            self.fileName = StringVar(self.modalPane)
            self.fileName.set("untitled.{0}".format(ext))
            self.fileName.trace_variable("w", self.onSelect)
            self.fname = Entry(nameFrame, textvariable=self.fileName, bd=1, highlightcolor=HLCOLOR, background=BGCOLOR, foreground=FGCOLOR)
            self.fname.pack(side="left", fill="x", expand=1, padx=0, pady=0)
            self.fname.icursor(END)
            self.fname.bind("<Up>", self.cursorUp)
            self.fname.bind("<Down>", self.cursorDown)

        filterFrame = Frame(self.modalPane, highlightcolor=HLCOLOR, background=BGCOLOR)
        filterFrame.pack(side="top", padx=18, pady=4, fill="x")

        filterLabel = Label(filterFrame, text=_("filter:"), bd=1, relief="flat", anchor="w", padx=0, pady=0, highlightcolor=HLCOLOR, background=BGCOLOR, foreground=FGCOLOR)
        filterLabel.pack(side="left")

        self.filterValue = StringVar(self.modalPane)
        self.filterValue.set("")
        self.filterValue.trace_variable("w", self.setMatching)
        self.fltr = Entry(filterFrame, textvariable=self.filterValue, bd=1, highlightcolor=HLCOLOR, background=BGCOLOR, foreground=FGCOLOR)
        self.fltr.pack(side="left", fill="x", expand=1, padx=0, pady=0)
        self.fltr.icursor(END)

        prefixFrame = Frame(self.modalPane, highlightcolor=HLCOLOR, background=BGCOLOR)
        prefixFrame.pack(side="top", padx=8, pady=2, fill="x")

        self.prefixLabel = Label(prefixFrame, text=_("{0}:").format(prefix), bd=1, highlightcolor=BGCOLOR, background=BGCOLOR, foreground=FGCOLOR)
        self.prefixLabel.pack(side="left", expand=0, padx=0, pady=0)

        buttonFrame = Frame(self.modalPane, highlightcolor=HLCOLOR, background=BGCOLOR)
        buttonFrame.pack(side="bottom", padx=10, pady=2)

        chooseButton = ttk.Button(buttonFrame, text="Choose", style="bg.TButton", command=self._choose)
        chooseButton.pack(side="right", padx=10)

        cancelButton = ttk.Button(buttonFrame, text="Cancel", style="bg.TButton", command=self._cancel, )
        cancelButton.pack(side="left")

        selectionFrame = Frame(self.modalPane, highlightcolor=HLCOLOR, background=BGCOLOR)
        selectionFrame.pack(side="bottom", padx=8, pady=2, fill="x")

        self.selectionValue = StringVar(self.modalPane)
        self.selectionValue.set("")
        self.selection = Label(selectionFrame, textvariable=self.selectionValue, bd=1, highlightcolor=HLCOLOR, background=BGCOLOR, foreground=FGCOLOR)
        self.selection.pack(side="left", fill="x", expand=1, padx=0, pady=0)

        listFrame = Frame(self.modalPane, highlightcolor=HLCOLOR, background=BGCOLOR, width=40)
        listFrame.pack(side="top", fill="both", expand=1, padx=5, pady=2)

        scrollBar = Scrollbar(listFrame, width=8)
        scrollBar.pack(side="right", fill="y")
        self.listBox = Listbox(listFrame, selectmode=BROWSE, width=36, foreground=FGCOLOR, background=BGCOLOR, selectbackground=FGCOLOR, selectforeground=BGCOLOR)
        self.listBox.pack(side="left", fill="both", expand=1, ipadx=4, padx=2, pady=0)
        self.listBox.bind('<<ListboxSelect>>', self.onSelect)
        self.listBox.bind("<Double-1>", self._choose)
        self.modalPane.bind("<Return>", self._choose)
        self.modalPane.bind("<Escape>", self._cancel)
        # self.modalPane.bind("<Up>", self.cursorUp)
        # self.modalPane.bind("<Down>", self.cursorDown)
        self.fltr.bind("<Up>", self.cursorUp)
        self.fltr.bind("<Down>", self.cursorDown)
        scrollBar.config(command=self.listBox.yview)
        self.listBox.config(yscrollcommand=scrollBar.set)
        self.setMatching()

    def ignore(self, e=None):
        return "break"

    def onSelect(self, *args):
        # Note here that Tkinter passes an event object to onselect()

        if self.listBox.curselection():
            firstIndex = self.listBox.curselection()[0]
            value = self.matches[int(firstIndex)]
            r = value[1]
            p = os.path.join(self.prefix, r)
            if self.new:
                if os.path.isfile(p):
                    p = os.path.split(p)[0]
                    r = os.path.split(r)[0]
                f = self.fileName.get()
                r = os.path.join(r, f)
                p = os.path.join(p, f)

            self.selectionValue.set(r)
            self.value = p
        return "break"

    def cursorUp(self, event=None):
        cursel = int(self.listBox.curselection()[0])
        newsel = max(0, cursel - 1)
        self.listBox.select_clear(cursel)
        self.listBox.select_set(newsel)
        self.listBox.see(newsel)
        self.onSelect()
        return "break"

    def cursorDown(self, event=None):
        cursel = int(self.listBox.curselection()[0])
        newsel = min(len(self.list) - 1, cursel + 1)
        self.listBox.select_clear(cursel)
        self.listBox.select_set(newsel)
        self.listBox.see(newsel)
        self.onSelect()
        return "break"

    def setMatching(self, *args):
        # disabled = "#BADEC3"
        # disabled = "#91CC9E"
        disabled = "#62B374"
        match = self.filterValue.get()
        if match:
            self.matches = matches = [x for x in self.list if x and match.lower() in x[1].lower()]
        else:
            self.matches = matches = self.list
        self.listBox.delete(0, END)
        index = 0
        init_index = 0
        for item in matches:
            if type(item) is tuple:
                # only show the label
                self.listBox.insert(END, item[0])
                if self.new:
                    if not item[-1]:
                        self.listBox.itemconfig(index, fg=disabled)
                    else:
                        self.listBox.itemconfig(index, fg=self.FGCOLOR)
                        if self.start and item[1] == self.start:
                            init_index = index
                else:
                    if item[-1]:
                        self.listBox.itemconfig(index, fg=disabled)
                    else:
                        self.listBox.itemconfig(index, fg=self.FGCOLOR)
                        if self.start and item[1] == self.start:
                            init_index = index
            # elif files:
            else:
                self.listBox.insert(END, item)
            index += 1
        self.listBox.select_set(init_index)
        self.listBox.see(init_index)
        self.fltr.focus_set()
        self.onSelect()

    def _choose(self, event=None):
        try:
            if self.listBox.curselection():
                firstIndex = self.listBox.curselection()[0]
                if self.new:
                    if not self.value or os.path.isfile(self.value):
                        return
                else:
                    tup = self.matches[int(firstIndex)]
                    if tup[-1]:
                        return
                    self.value = os.path.join(self.prefix, tup[1])
            else:
                return
        except IndexError:
            self.value = None
        self.modalPane.destroy()

    def _cancel(self, event=None):
        self.value = None
        self.modalPane.destroy()

    def returnValue(self):
        if self.parent is not None:
            self.parent.wait_window(self.modalPane)
        return self.value


class Dialog(Toplevel):

    def __init__(self, parent, title=None, prompt=None, opts=None, default=None, modal=True, xoffset=50, yoffset=50, event=None, process=None, font=None, close=0):
        # global BGCOLOR, HLCOLOR, FGCOLOR
        self.parent = parent
        self.loop = parent.loop
        BGCOLOR = self.loop.options['background_color']
        self.BGCOLOR = BGCOLOR
        HLCOLOR = self.loop.options['highlight_color']
        self.HLCOLOR = HLCOLOR
        FGCOLOR = self.loop.options['foreground_color']
        self.FGCOLOR = FGCOLOR

        Toplevel.__init__(self, parent, highlightcolor=HLCOLOR, background=BGCOLOR)
        self.protocol("WM_DELETE_WINDOW", self.quit)
        if modal:
            logger.debug('modal')
            self.transient(parent)
        else:
            logger.debug('non modal')

        if title:
            self.title(title)

        self.event = event
        logger.debug("parent: {0}".format(self.parent))
        self.prompt = prompt
        self.options = opts
        self.font = font
        self.default = default
        self.value = ""
        self.process = process

        self.error_message = None

        # self.buttonbox()

        body = Frame(self, highlightcolor=HLCOLOR, background=BGCOLOR)
        # self.initial_focus = self.body(body)
        self.body(body).focus_set()

        self.buttonbox()
        # don't expand body or it will fill below the actual content
        body.pack(side="top", fill=tkinter.BOTH, padx=0, pady=0, expand=1)
        self.protocol("WM_DELETE_WINDOW", self.quit)
        if parent:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + xoffset, parent.winfo_rooty() + yoffset))
        if close:
            self.after(close, lambda: self.cancel())
        if modal:
            self.grab_set()
            self.wait_window(self)


    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden
        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = Frame(self, background=self.BGCOLOR, highlightcolor=self.HLCOLOR)
        w = ttk.Button(box, text="OK", style="bg.TButton",  command=self.ok, default=ACTIVE)
        w.pack(side="right", padx=5, pady=2)
        w = ttk.Button(box, text="Cancel", style="bg.TButton",  command=self.cancel)
        w.pack(side="right", padx=5, pady=2)
        self.bind("<Return>", self.ok)
        self.bind("<KP_Enter>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack(side='bottom')

    # standard button semantics

    def ok(self, event=None):
        res = self.validate()
        logger.debug('validate: {0}, value: "{1}"'.format(res, self.value))
        if not res:
            if self.error_message:
                self.messageWindow('error', self.error_message)

            # self.initial_focus.focus_set()  # put focus back
            return "break"

        self.withdraw()
        self.update_idletasks()

        self.apply()
        self.quit()

    def cancel(self, event=None):
        # return the focus to the tree view in the main window
        self.value = None
        logger.debug('value: "{0}"'.format(self.value))
        self.quit()

    def quit(self, event=None):
        if self.parent:
            logger.debug("returning focus to parent: {0}".format(self.parent))
            self.parent.focus()
            # self.parent.tree.focus_set()
            if self.parent.weekly or self.parent.monthly:
                self.parent.canvas.focus_set()
            else:
                self.parent.tree.focus_set()
        else:
            logger.debug("returning focus, no parent")
        self.destroy()

    # command hooks
    def validate(self):
        return 1  # override

    def apply(self):
        pass  # override

    def messageWindow(self, title, prompt):
        MessageWindow(self.parent, title, prompt)


class TextVariableWindow(Dialog):
    def body(self, master):
        if 'textvariable' not in self.options:
            return
        self.entry = Entry(master, textvariable=self.options['textvariable'])
        self.entry.pack(side="bottom", padx=5, pady=5)
        Label(master, text=self.prompt, justify='left', highlightcolor=HLCOLOR, background=BGCOLOR, foreground=FGCOLOR).pack(side="top", fill=tkinter.BOTH, expand=1, padx=10, pady=5)
        self.entry.focus_set()
        self.entry.bind('<Escape>', self.entry.delete(0, END))
        return self.entry

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = Frame(self, highlightcolor=self.HLCOLOR, background=self.BGCOLOR)

        w = ttk.Button(box, text=CLOSE, style="bg.TButton",  command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<KP_Enter>", self.ok)
        self.bind("<Escape>", self.ok)
        box.pack(side='bottom')

    def quit(self, event=None):
        if self.parent:
            logger.debug("returning focus to parent: {0}".format(self.parent))
            self.parent.focus()
            self.parent.focus_set()
        else:
            logger.debug("returning focus, no parent")
        self.entry.delete(0, END)
        self.options['textvariable'].set("")
        self.destroy()


class DialogWindow(Dialog):
    # master will be a frame in Dialog
    def body(self, master):
        self.entry = Entry(master,
            highlightthickness=0,
            highlightcolor=self.HLCOLOR,
            highlightbackground=self.BGCOLOR,
            selectbackground=self.FGCOLOR,
            selectforeground=self.BGCOLOR,
            background=self.BGCOLOR,
            foreground=self.FGCOLOR)
        self.entry.pack(side="bottom", padx=5, pady=2, fill=X)
        tkfixedfont = self.font
        lines = self.prompt.split('\n')
        height = min(20, len(lines) + 1)
        lengths = [len(line) for line in lines]
        width = min(70, max(lengths) + 2)
        self.text = ReadOnlyText(
            master, wrap="word", padx=2, pady=2, bd=2, relief="sunken",
            font=tkfixedfont,
            height=height,
            width=width,
            background=self.BGCOLOR,
            highlightcolor=self.HLCOLOR,
            highlightbackground=self.BGCOLOR,
            foreground=self.FGCOLOR,
            takefocus=False)
        self.text.insert("1.1", self.prompt)
        self.text.pack(side="top", fill=tkinter.BOTH, expand=1, padx=6, pady=2)
        if self.default is not None:
            self.entry.insert(0, self.default)
            self.entry.select_range(0, END)
        return self.entry


class TextDialog(Dialog):

    def body(self, master):
        tkfixedfont = self.font
        lines = self.prompt.split('\n')
        height = min(25, len(lines) + 1)
        lengths = [len(line) for line in lines]
        width = min(70, max(lengths) + 2)
        self.text = ReadOnlyText(
            master, wrap="word", padx=2, pady=2, bd=2, relief="sunken",
            # font=tkFont.Font(family="Lucida Sans Typewriter"),
            font=tkfixedfont,
            height=height,
            width=width,
            background=self.BGCOLOR,
            highlightbackground=self.BGCOLOR,
            highlightcolor=self.HLCOLOR,
            foreground=self.FGCOLOR,
            takefocus=False)
        self.text.insert("1.1", self.prompt)
        self.text.pack(side='left', fill=tkinter.BOTH, expand=1, padx=5, pady=2)
        return self.text

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self, highlightcolor=self.HLCOLOR, background=self.BGCOLOR)

        w = ttk.Button(box, text="OK", style="bg.TButton",  command=self.cancel, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=0)

        self.bind("<Return>", self.ok)
        self.bind("<KP_Enter>", self.ok)
        self.bind("<Escape>", self.ok)

        box.pack(side='bottom')


class OptionsDialog():

    def __init__(self, parent, master=None, title="", prompt="", opts=None, radio=True, yesno=True, list=False):
        if not opts:
            opts = []
        self.parent = parent
        self.loop = parent.loop
        BGCOLOR = self.loop.options['background_color']
        self.BGCOLOR = BGCOLOR
        HLCOLOR = self.loop.options['highlight_color']
        self.HLCOLOR = HLCOLOR
        FGCOLOR = self.loop.options['foreground_color']
        self.FGCOLOR = FGCOLOR
        self.win = Toplevel(parent, background=BGCOLOR, highlightcolor=HLCOLOR)
        self.win.protocol("WM_DELETE_WINDOW", self.quit)
        if parent:
            self.win.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        # self.parent = parent
        self.master = master
        self.options = opts
        self.radio = radio
        self.win.title(title)
        if list:
            self.win.configure(bg=BGCOLOR)
            tkfixedfont = tkFont.nametofont("TkFixedFont")
            if 'fontsize_fixed' in self.parent.options and self.parent.options['fontsize_fixed']:
                tkfixedfont.configure(size=self.parent.options['fontsize_fixed'])
            self.content = ReadOnlyText(self.win, wrap="word", padx=3, bd=2, height=10, relief="sunken", font=tkfixedfont, background=BGCOLOR, highlightcolor=HLCOLOR, foreground=FGCOLOR, width=46, takefocus=False)
            self.content.pack(fill=tkinter.BOTH, expand=1, padx=10, pady=5)
            self.content.insert("1.0", prompt)
        else:
            Label(self.win, text=prompt, justify='left', highlightcolor=HLCOLOR, background=BGCOLOR, foreground=FGCOLOR).pack(fill=tkinter.BOTH, expand=1, padx=10, pady=5)
            self.sv = StringVar(parent)
        self.sv = IntVar(parent)
        self.sv.set(1)
        if self.options:
            if radio:
                self.value = opts[0]
                for i in range(min(9, len(self.options))):
                    txt = self.options[i]
                    val = i + 1
                    # bind keyboard numbers 1-9 (at most) to options selection, i.e., press 1 to select option 1, 2 to select 2, etc.
                    self.win.bind(str(val), (lambda e, x=val: self.sv.set(x)))
                    Radiobutton(self.win, text="{0}: {1}".format(val, txt), padx=20, indicatoron=True, variable=self.sv, background=BGCOLOR, highlightcolor=HLCOLOR, foreground=FGCOLOR, command=self.getValue, value=val).pack(padx=10, anchor=W)
            else:
                self.check_values = {}
                # show 0, check 1, return 2
                for i in range(min(9, len(self.options))):
                    txt = self.options[i][0]
                    self.check_values[i] = BooleanVar(self.parent)
                    self.check_values[i].set(self.options[i][1])
                    Checkbutton(self.win, text=self.options[i][0], padx=20, variable=self.check_values[i]).pack(padx=10, anchor=W)
        box = Frame(self.win)
        box.configure(bg=BGCOLOR, highlightcolor=HLCOLOR)
        # if list:
        #     box.configure(bg=BGCOLOR)
        if yesno:
            YES = _("Yes")
            NO = _("No")
        else:
            YES = _("Ok")
            NO = _("Cancel")
        c = ttk.Button(box, text=NO, style="bg.TButton",  command=self.cancel)
        c.pack(side=LEFT, padx=5, pady=5)
        o = ttk.Button(box, text=YES, style="bg.TButton",  default='active', command=self.ok)
        o.pack(side=LEFT, padx=5, pady=5)
        box.pack()
        self.win.bind('<Return>', (lambda e, o=o: o.invoke()))
        self.win.bind('<KP_Enter>', (lambda e, o=o: o.invoke()))
        self.win.bind('<Control-w>', self.Ok)
        self.win.bind('<Escape>', (lambda e, c=c: c.invoke()))
        logger.debug('parent: {0}'.format(parent))
        self.win.focus_set()
        self.win.transient(parent)
        self.win.wait_window(self.win)

    def getValue(self, e=None):
        v = self.sv.get()
        logger.debug("sv: {0}".format(v))
        if self.options:
            if self.radio:
                if v - 1 in range(len(self.options)):
                    o = self.options[v - 1]
                    logger.debug(
                        'OptionsDialog returning {0}: {1}'.format(v, o))
                    return v, o
                    # return o, v
                else:
                    logger.debug(
                        'OptionsDialog returning {0}: {1}'.format(v, None))
                    return 0, None
            else:  # checkbutton
                values = []
                for i in range(len(self.options)):
                    bool = self.check_values[i].get() > 0
                    values.append([self.options[i][0], bool, self.options[i][2]])
                return values
        else:  # askokcancel type dialog
            logger.debug(
                'OptionsDialog returning {0}: {1}'.format(v, None))
            return v, v

    def ok(self, event=None):
        # self.parent.update_idletasks()
        self.quit()

    def Ok(self, event=None):
        # self.parent.update_idletasks()
        self.sv.set(2)
        self.quit()

    def cancel(self, event=None):
        self.sv.set(0)
        self.quit()

    def quit(self, event=None):
        # put focus back to the parent window
        if self.master:
            self.master.focus_set()
        elif self.parent:
            self.parent.focus_set()
        self.win.destroy()


class GetInteger(DialogWindow):

    def validate(self):
        minvalue = maxvalue = None
        if len(self.options) > 0:
            minvalue = self.options[0]
            if len(self.options) > 1:
                maxvalue = self.options[1]
        res = self.entry.get()
        try:
            val = int(res)
            ok = (minvalue is None or val >= minvalue) and (
                maxvalue is None or val <= maxvalue)
        except:
            val = None
            ok = False

        if ok:
            self.value = val
            return True
        else:
            self.value = None
            msg = [_('an integer')]
            conj = ""
            if minvalue is not None:
                msg.append(_("no less than {0}".format(minvalue)))
                conj = _("and ")
            if maxvalue is not None:
                msg.append(_("{0}no greater than {1}").format(conj, maxvalue))
            msg.append(_("is required"))
            self.error_message = "\n".join(msg)
            return False


class GetRepeat(GetInteger):

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = Frame(self, background=self.BGCOLOR, highlightcolor=self.HLCOLOR)
        w = ttk.Button(box, text=_("Repeat"), style="bg.TButton",  command=self.ok, default=ACTIVE)
        w.pack(side="right", padx=5, pady=2)
        w = ttk.Button(box, text=_("Close"), style="bg.TButton",  command=self.cancel)
        w.pack(side="right", padx=5, pady=2)
        self.bind("<Return>", self.ok)
        self.bind("<KP_Enter>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack(side='bottom')


class GetDateTime(DialogWindow):
    def validate(self):
        res = self.entry.get()
        logger.debug('res: {0}'.format(res))
        ok = False
        if not res.strip():
            # return the current date if ok is pressed with no entry
            # val = get_current_time().replace(hour=0, minute=0, second=0, microsecond=0)
            val = get_current_time()
            ok = True
        else:
            try:
                val = parse_str(res)
                ok = True
            except:
                val = None
        if ok:
            self.value = val
            return True
        else:
            self.value = False
            self.error_message = _('could not parse "{0}"').format(res)
            return False


class GetString(DialogWindow):
    def validate(self):
        nullok = False
        if 'nullok' in self.options and self.options['nullok']:
            nullok = True
            # an entry is required
        val = self.entry.get()
        if val.strip():
            self.value = val
            return True
        elif nullok:  # null and null is ok
            if self.value is None:
                return False
            else:
                self.value = val
                return True
        else:
            self.error_message = _('an entry is required')
            return False

    def ok(self, event=None):
        res = self.validate()
        logger.debug('validate: {0}, value: "{1}"'.format(res, self.value))
        if not res:
            if self.error_message:
                self.messageWindow('error', self.error_message)
            return "break"
        if self.process:
            res = self.process(self.value)
            self.text.delete("1.0", END)
            self.text.insert("1.0", res)
        else:
            self.withdraw()
            self.update_idletasks()
            self.apply()
            self.quit()
