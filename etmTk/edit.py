#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import platform, sys
import codecs
from datetime import datetime, timedelta, time

from copy import deepcopy
# from view import AFTER

if platform.python_version() >= '3':
    import tkinter
    from tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Frame, LEFT, RIGHT, Text, PanedWindow, OptionMenu, StringVar, Menu, BooleanVar, ACTIVE, X, RIDGE, BOTH, SEL, SEL_FIRST, SEL_LAST, Button, FLAT, Listbox
    from tkinter import ttk
    # from ttk import Button, Style
    from tkinter import font as tkFont
    # from tkinter import simpledialog as tkSimpleDialog
    # from tkinter.simpledialog import askstring
    # from tkinter.messagebox import askokcancel
    # from tkinter.filedialog import asksaveasfilename
    # from tkinter.filedialog import askopenfilename
else:
    import Tkinter as tkinter
    from Tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Frame, LEFT, RIGHT, Text, PanedWindow, OptionMenu, StringVar, Menu, BooleanVar, ACTIVE, X, RIDGE, BOTH, SEL, SEL_FIRST, SEL_LAST, Button, FLAT, Listbox
    import ttk
    # from ttk import Button, Style
    import tkFont
    # import tkSimpleDialog
    # from tkSimpleDialog import askstring
    # from tkFileDialog import asksaveasfilename
    # from tkFileDialog import askopenfilename
    # from tkMessageBox import askokcancel

# Also from messagebox:
# askquestion()
# askokcancel()
# askyesno ()
# askretrycancel ()

import string
ID_CHARS = string.ascii_letters + string.digits + "_@/"

import gettext
_ = gettext.gettext

import logging
import logging.config
logger = logging.getLogger()


SOMEREPS = _('Selected repetitions')
ALLREPS = _('Repetitions')
MESSAGES = _('Error messages')
FOUND = "found"  # for found text marking

MAKE = _("Make")
PRINT = _("Print")
EXPORTTEXT = _("Export report in text format ...")
EXPORTCSV = _("Export report in CSV format ...")
SAVESPECS = _("Save changes to report specifications")
CLOSE = _("Close")


from etmTk.data import hsh2str, str2hsh, get_reps, rrulefmt, ensureMonthly, commandShortcut, optionShortcut, CMD, relpath, completion_regex, getReportData, tree2Text, AFTER, get_current_time, getFileTuples

from etmTk.dialog import BGCOLOR, OptionsDialog, ReadOnlyText, FileChoice


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
        self.configure(background=BGCOLOR, highlightbackground=BGCOLOR)
        self.parent = parent
        self.loop = parent.loop
        self.messages = self.loop.messages
        self.messages = []
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
        self.newhsh = newhsh
        self.rephsh = rephsh
        self.value = ''
        self.options = options
        self.tkfixedfont = tkFont.nametofont("TkFixedFont")
        self.tkfixedfont.configure(size=self.options['fontsize_fixed'])
        # self.text_value.trace_variable("w", self.setSaveStatus)
        frame = Frame(self, bd=0, relief=FLAT)
        frame.pack(side="bottom", fill=X, padx=4, pady=0)
        frame.configure(background=BGCOLOR, highlightbackground=BGCOLOR)

        btnwdth = 5

        # ok will check, save and quit
        Button(frame, text=_("Save and Exit"), highlightbackground=BGCOLOR, command=self.onSave, pady=2).pack(side=RIGHT, padx=4)

        l, c = commandShortcut('w')
        self.bind(c, self.onSave)

        # quit with a warning prompt if modified
        Button(frame, text=_("Cancel"), highlightbackground=BGCOLOR, pady=2, command=self.quit).pack(side=LEFT, padx=4)
        # self.bind("<Escape>", self.quit)

        l, c = commandShortcut('q')
        self.bind(c, self.quit)
        self.bind("<Escape>", self.cancel)
        # check will evaluate the item entry and, if repeating, show reps
        inspect = Button(frame, text=_("Validate"), highlightbackground=BGCOLOR,  command=self.onCheck, pady=2)
        self.bind("<Control-question>", self.onCheck)
        inspect.pack(side=RIGHT, padx=4)

        # find
        Button(frame, text='x', command=self.clearFind, highlightbackground=BGCOLOR, padx=8, pady=2).pack(side=LEFT, padx=0)
        self.find_text = StringVar(frame)
        self.e = Entry(frame, textvariable=self.find_text, width=10, highlightbackground=BGCOLOR)
        self.e.pack(side=LEFT, padx=0, expand=1, fill=X)
        self.e.bind("<Return>", self.onFind)
        Button(frame, text='>', command=self.onFind, highlightbackground=BGCOLOR, padx=8, pady=2).pack(side=LEFT, padx=0)

        text = Text(self, wrap="word", bd=2, relief="sunken", padx=3, pady=2, font=self.tkfixedfont, undo=True, width=70)
        text.configure(highlightthickness=0)
        text.tag_configure(FOUND, background="lightskyblue")

        text.pack(side="bottom", padx=4, pady=3, expand=1, fill=BOTH)
        self.text = text

        self.completions = self.loop.options['completions']

        if title is not None:
            self.wm_title(title)
        if start is not None:
            # we have the starting text
            text = start
            self.edithsh = {}
            self.mode = 1
        elif file is not None:
            # we're editing a file
            self.mode = 'file'
            inspect.configure(state="disabled")
            if not os.path.isfile(file):
                logger.warn('could not open: {0}'.format(file))
                text = ""
            else:
                with codecs.open(file, 'r',
                             self.options['encoding']['file']) as f:
                    text = f.read()
        else:
            # we are creating a new item and/or replacing an item
            # mode:
            #   1: new
            #   2: replace
            #   3: new and replace
            self.initfile = initfile = ensureMonthly(options=self.options, date=datetime.now())
            # logger.debug("newhsh: {0}".format(self.newhsh))
            # logger.debug("rephsh: {0}".format(self.rephsh))
            # set the mode
            if newhsh is None and rephsh is None:
                # we are creating a new item from scratch
                self.mode = 1
                self.edithsh = self.newhsh
                text = ''
            elif rephsh is None:  # newhsh is not None
                # we are creating a new item as a copy
                self.mode = 1
                self.edithsh = self.newhsh
                if ('fileinfo' in newhsh and newhsh['fileinfo']):
                    initfile = newhsh['fileinfo'][0]
                text, msg = hsh2str(self.edithsh, self.options)
            elif newhsh is None: # rephsh
                # we are editing and replacing rephsh - no file prompt
                self.mode = 2
                # self.repinfo = rephsh['fileinfo']
                self.edithsh = self.rephsh
                text, msg = hsh2str(self.edithsh, self.options)
            else:  # neither is None
                # we are changing some instances of a repeating item
                # we will be writing but not editing rephsh using its fileinfo
                # we will be editing and saving newhsh using self.initfile
                self.mode = 3
                self.edithsh = self.newhsh
                # self.repinfo = rephsh['fileinfo']
                if 'fileinfo' in newhsh and newhsh['fileinfo'][0]:
                    initfile = self.newhsh['fileinfo'][0]
                text, msg = hsh2str(self.edithsh, self.options)

            logger.debug('mode: {0}; initfile: {1}; edit: {2}'.format(self.mode,  self.initfile,  self.edithsh))
        # logger.debug("setting text {0}:\n{1}".format(type(text), text))
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
            self.text.tag_add("sel", "1.1", "1.{0}".format(len(start)))
            self.text.mark_set(INSERT, END)
        elif line:
            self.text.mark_set(INSERT, "{0}.0".format(line))
        else:
            self.text.mark_set(INSERT, END)
        self.text.see(INSERT)
        # l, c = commandShortcut('/')
        logger.debug("/: {0}, {1}".format(l, c))
        # self.text.bind("<Control-slash>", self.showCompletions)
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
        acw.geometry("+%d+%d" % (self.text.winfo_rootx() + 50,
                          self.text.winfo_rooty() + 50))

        self.autocompletewindow.wm_attributes("-topmost", 1)

        self.filterValue = StringVar(self)
        self.filterValue.set(match)
        self.filterValue.trace_variable("w", self.setCompletions)
        self.fltr = fltr = Entry(acw, textvariable=self.filterValue)
        self.fltr.pack(side="top", fill="x") #, expand=1, fill=X)
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
        # self.match = None
        # self.autocompletewindow.destroy()
        # self.scrollbar.destroy()
        # self.scrollbar = None
        self.listbox.destroy()
        self.listbox = None
        self.autocompletewindow.destroy()
        self.autocompletewindow = None

    def completionSelected(self, event):
        # Put the selected completion in the text, and close the list
        cursel = self.matches[int(self.listbox.curselection()[0])]
        start = "insert-{0}c".format(len(self.match))
        end = "insert-1c wordend"
        logger.debug("cursel: {0}; match: {1}; start: {2}; insert: {3}".format(
            cursel, self.match, start, INSERT))
        self.text.delete(start, end)
        self.text.insert(INSERT, cursel)
        self.hideCompletions()

    def cursorUp(self, event=None):
        cursel = int(self.listbox.curselection()[0])
        # newsel = max(0, cursel=1)
        newsel = max(0, cursel-1)
        self.listbox.select_clear(cursel)
        self.listbox.select_set(newsel)
        self.listbox.see(newsel)
        return "break"

    def cursorDown(self, event=None):
        cursel = int(self.listbox.curselection()[0])
        newsel = min(len(self.matches)-1, cursel+1)
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
        if self.checkmodified():
            self.wm_title("{0} *".format(self.title))
        else:
            self.wm_title(self.title)

    def onSave(self, e=None):
        e = None
        if not self.checkmodified():
            self.quit()
        elif self.file is not None:
            # we are editing a file
            alltext = self.gettext()
            self.loop.safe_save(self.file, alltext)
            # with codecs.open(self.file, 'w',
            #                  self.options['encoding']['file']) as f:
            #     f.write(alltext)
            self.setmodified(False)
            self.changed = True
            self.quit()
        else:
            # we are editing an item
            ok = self.onCheck(showreps=False, showres=False)
            if not ok:
                return "break"
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
                # logger.info('prefix: {0}; files: {1}'.format(prefix, filelist))
                lst = []
                ret = FileChoice(self, "etm data files", prefix=prefix, list=tuples, start=file).returnValue()
                if not ret: return False
                filename = os.path.join(prefix, ret)
                if not os.path.isfile(filename): return False
                filename = os.path.normpath(filename)
                logger.debug('saving to: {0}'.format(filename))
                self.text.focus_set()
            logger.debug('edithsh: {0}'.format(self.edithsh))
            ok = True
            if self.mode == 1:
                if self.loop.append_item(self.edithsh, filename):
                    logger.debug('append mode: {0}'.format(self.mode))
                else:
                    ok = False
            elif self.mode == 2:
                if self.loop.replace_item(self.edithsh):
                    logger.debug('replace mode: {0}'.format(self.mode))
                else:
                    ok = False
            else:  # self.mode == 3
                if self.loop.append_item(self.edithsh, filename):
                    logger.debug('append mode: {0}'.format(self.mode))
                else:
                    ok = False
                if self.loop.replace_item(self.rephsh):
                    logger.debug('replace mode: {0}'.format(self.mode))
                else:
                    ok = False

            # update the return value so that when it is not null then modified
            # is false and when modified is true then it is null
            self.setmodified(False)
            self.changed = True
            self.quit()
            return "break"

    def onCheck(self, event=None, showreps=True, showres=True):
        self.loop.messages = []
        text = self.gettext()
        logger.debug("text: {0}".format(text))
        msg = []
        reps = []
        error = False
        hsh, msg = str2hsh(text, options=self.options)

        if not msg:
            # we have a good hsh

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
        if str != text:
            self.settext(str)
        if 'r' in hsh:
            showing_all, reps =  get_reps(self.options['bef'], hsh)
            if reps:
                if showreps:
                    repsfmt = [x.strftime(rrulefmt) for x in reps]
                    logger.debug("{0}: {1}".format(showing_all, repsfmt))
                    repetitions = "{0}".format("\n".join(repsfmt))
                    if showing_all:
                        self.messageWindow(ALLREPS, repetitions, opts=self.options, width=24)
                    else:
                        self.messageWindow(SOMEREPS, repetitions, opts=self.options, width=24)
            else:
                repetitions = "No repetitions were generated."
                self.loop.messages.append(repetitions)
            if self.loop.messages:
                messages = "{0}".format("\n".join(self.loop.messages))
                logger.debug("messages: {0}".format(messages))
                self.messageWindow(MESSAGES, messages, opts=self.options)
                return False


        elif showres:
            self.messageWindow(MESSAGES, _("valid entry"), opts=self.options, height=1, width=14)
        logger.debug(('Ok: {0}'.format(True)))
        return True

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
            # self.text.tag_remove(SEL, '1.0', END)
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
        # if self.checkmodified():
        #     return "break"
        logger.debug(('calling quit'))
        self.quit()

    def quit(self, e=None):
        if self.checkmodified():
            ans = self.confirm(parent=self,
                title=_('Quit'),
                prompt=_("There are unsaved changes.\nDo you really want to quit?"))
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

    def messageWindow(self, title, prompt, opts=None, height=14, width=52):
        win = Toplevel(self)
        win.title(title)
        win.geometry("+%d+%d" % (self.text.winfo_rootx() + 50,
                          self.text.winfo_rooty() + 50))
        # win.minsize(444, 430)
        # win.minsize(450, 450)
        f = Frame(win)
        # pack the button first so that it doesn't disappear with resizing
        b = Button(win, text=_('OK'), width=10, command=win.destroy, default='active', pady=2)
        b.pack(side='bottom', fill=tkinter.NONE, expand=0, pady=0)
        win.bind('<Return>', (lambda e, b=b: b.invoke()))
        win.bind('<Escape>', (lambda e, b=b: b.invoke()))

        t = ReadOnlyText(
            f, wrap="word", padx=2, pady=2, bd=2, relief="sunken",
            font=self.tkfixedfont,
            height=height,
            width=width,
            takefocus=False)
        t.insert("0.0", prompt)
        t.pack(side='left', fill=tkinter.BOTH, expand=1, padx=0, pady=0)
        # ysb = ttk.Scrollbar(f, orient='vertical', command=t.yview)
        # ysb.pack(side='right', fill=tkinter.Y, expand=0, padx=0, pady=0)
        # t.configure(state="disabled", yscroll=ysb.set)
        # t.configure(yscroll=ysb.set)
        f.pack(padx=2, pady=2, fill=tkinter.BOTH, expand=1)

        win.focus_set()
        win.grab_set()
        win.transient(self)
        win.wait_window(win)

    def confirm(self, parent=None, title="", prompt="", instance="xyz"):
        ok, value = OptionsDialog(parent=parent, title=_("confirm").format(instance), prompt=prompt).getValue()
        return ok


if __name__ == '__main__':
    print('edit.py should only be imported. Run etm or view.py instead.')
