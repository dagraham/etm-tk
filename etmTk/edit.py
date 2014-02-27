#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import platform, sys
import codecs

from copy import deepcopy
# from view import AFTER

if platform.python_version() >= '3':
    import tkinter
    from tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Frame, LEFT, RIGHT, Text, PanedWindow, OptionMenu, StringVar, Menu, BooleanVar, ACTIVE, X, RIDGE, BOTH, SEL, SEL_FIRST, SEL_LAST, Button, FLAT, Listbox
    from tkinter import ttk
    # from ttk import Button, Style
    from tkinter import font as tkFont
    from tkinter import simpledialog as tkSimpleDialog
    from tkinter.simpledialog import askstring
    from tkinter.messagebox import askokcancel
    from tkinter.filedialog import asksaveasfilename
    from tkinter.filedialog import askopenfilename
else:
    import Tkinter as tkinter
    from Tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Frame, LEFT, RIGHT, Text, PanedWindow, OptionMenu, StringVar, Menu, BooleanVar, ACTIVE, X, RIDGE, BOTH, SEL, SEL_FIRST, SEL_LAST, Button, FLAT, Listbox
    import ttk
    # from ttk import Button, Style
    import tkFont
    import tkSimpleDialog
    from tkSimpleDialog import askstring
    from tkFileDialog import asksaveasfilename
    from tkFileDialog import askopenfilename
    from tkMessageBox import askokcancel

# Also from messagebox:
# askquestion()
# askokcancel()
# askyesno ()
# askretrycancel ()

import string
ID_CHARS = string.ascii_letters + string.digits + "_@/"
from idlelib.AutoComplete import AutoComplete
from idlelib.AutoCompleteWindow import AutoCompleteWindow

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
SAVEAS = _("Save as ...")
EXPORTCSV = _("Export in CSV format ...")
EMAILREPORT = _("Email ...")
SAVESPECS = _("Save changes to report specifications")
CLOSE = _("Close")


from etmTk.data import hsh2str, str2hsh, get_reps, rrulefmt, ensureMonthly, commandShortcut, optionShortcut, BGCOLOR, CMD, relpath, completion_regex, getReportData, tree2Text, AFTER


from idlelib.WidgetRedirector import WidgetRedirector

class ReadOnlyText(Text):
    # noinspection PyShadowingNames
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")

class ReportWindow(Toplevel):
    def __init__(self, parent=None, options=None, title=None):
        Toplevel.__init__(self, parent)
        self.configure(background=BGCOLOR)
        self.minsize(400, 300)
        self.geometry('500x200')
        self.transient(parent)
        self.parent = parent
        self.loop = parent.loop
        self.changed = False
        self.options = options
        self.modified = False
        self.tkfixedfont = tkFont.nametofont("TkFixedFont")
        self.tkfixedfont.configure(size=self.options['fontsize'])
        # self.text_value.trace_variable("w", self.setSaveStatus)
        btnwdth = 5
        topbar = Frame(self, bd=0, relief=FLAT)
        PADY = 2
        topbar.pack(side="top", fill=X, padx=0, pady=4)
        topbar.configure(background=BGCOLOR)

        botbar = Frame(self, bd=0, relief=FLAT, highlightbackground=BGCOLOR, background=BGCOLOR)
        botbar.pack(side="bottom", fill=X, padx=0, pady=4)

        text = ReadOnlyText(self, bd=2, relief="sunken", padx=3, pady=2, font=self.tkfixedfont, width=70, takefocus=False)
        text.configure(highlightthickness=0)
        text.tag_configure(FOUND, background="lightskyblue")

        text.pack(side="top", padx=4, pady=0, expand=1, fill=BOTH)
        self.text = text

        # botbar.configure(background=BGCOLOR)

        # topbar components
        # report menu
        self.reportLabel = _("Report")
        self.rm_options = [[MAKE, 'm'],
                           [SAVEAS, 's'],
                           [EXPORTCSV, 'x'],
                           [EMAILREPORT, 'e'],
                           [SAVESPECS, 'w'],
                           [CLOSE, 'q'],
        ]

        self.rm2cmd = {'m': self.makeReport,
                         's': self.saveReportAs,
                         'x': self.exportCSV,
                         'e': self.emailReport,
                         'w': self.saveSpecs,
                         'q': self.quit}
        self.rm_opts = [x[0] for x in self.rm_options]
        self.report = self.rm_options[0][0]
        self.reportValue = StringVar(self)
        self.currentReport = StringVar(self)
        self.currentReport.set(self.report)
        self.reportValue.set(self.reportLabel)
        self.rm = OptionMenu(topbar, self.reportValue, *self.rm_opts)


        for i in range(len(self.rm_options)):
            label = self.rm_options[i][0]
            k = self.rm_options[i][1]
            if i == 0:
                l = "Return"
                c = "<Return>"
            else:
                l, c = commandShortcut(k)
                logger.debug("k: {0}; l: {1}; c: {2}".format(k, l, c))
                print("rm2cmd", k, self.rm2cmd[k])
                self.bind(c, lambda e, x=k: self.after(AFTER, self.rm2cmd[x]))
            self.rm["menu"].entryconfig(i, accelerator=l, command=lambda x=k: self.after(AFTER, self.rm2cmd[x]))
        self.rm.pack(side="left", padx=2)
        self.rm.configure(background=BGCOLOR, takefocus=False)

        # find group
        Button(topbar, text='x', command=self.clearFind, highlightbackground=BGCOLOR, padx=8).pack(side=LEFT, padx=0)
        self.find_text = StringVar(topbar)
        self.e = Entry(topbar, textvariable=self.find_text, width=10, highlightbackground=BGCOLOR)
        self.e.pack(side=LEFT, padx=0, expand=1, fill=X)
        self.e.bind("<Return>", self.onFind)
        Button(topbar, text='>', command=self.onFind, highlightbackground=BGCOLOR,  padx=8).pack(side=LEFT, padx=0)

        # help
        Button(topbar, text="?", command=self.reportHelp, highlightbackground=BGCOLOR).pack(side=LEFT, padx=4)

        # botbar components
        # Button(botbar, text=CLOSE, highlightbackground=BGCOLOR, width=btnwdth, command=self.cancel).pack(side=LEFT, padx=4)
        # # self.bind("<Escape>", self.quit)
        # self.bind("<Escape>", self.cancel)
        #
        # # ok will check, save and quit
        # Button(botbar, text=_("Process"), highlightbackground=BGCOLOR, width=btnwdth, command=self.makeReport).pack(side=RIGHT, padx=4)

        # reportspec

        self.box_value = StringVar()
        self.box = ttk.Combobox(botbar, textvariable=self.box_value, font=tkFont.Font(family="Lucida Sans Typewriter"))
        self.box.bind("<<ComboboxSelected>>", self.newselection)
        self.bind("<Return>", self.makeReport)
        self.specs = ['']
        if ('report_specifications' in self.options and os.path.isfile(self.options['report_specifications'])):
            with open(self.options['report_specifications']) as fo:
                tmp = fo.readlines()
            self.specs = [str(x).rstrip() for x in tmp if x[0] != "#"]
        logger.debug('specs: {0}'.format(self.specs))
        self.value_of_combo = self.specs[0]
        self.box['values'] = self.specs
        self.box.current(0)
        self.box.configure(width=30, background=BGCOLOR, takefocus=False)
        self.box.pack(side="left", padx=2, fill=X, expand=1)
        self.box.focus_set()


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
        logger.debug(('calling quit'))
        self.quit()

    def quit(self, e=None):
        if self.modified:
            ans = askokcancel(
                _('Quit'),
                _("There are unsaved changes to your report specifications.\nDo you really want to quit?"),
                parent=self)
        else:
            ans = True
        if ans:
            if self.parent:
                logger.debug('focus set')
                self.parent.focus()
                self.parent.tree.focus_set()
            self.destroy()
        return "break"

    def messageWindow(self, title, prompt):
        win = Toplevel()
        win.title(title)
        tkfixedfont = tkFont.nametofont("TkFixedFont")
        tkfixedfont.configure(size=self.options['fontsize'])
        # win.minsize(444, 430)
        # win.minsize(450, 450)
        f = Frame(win)
        # pack the button first so that it doesn't disappear with resizing
        b = Button(win, text=_('OK'), width=10, command=win.destroy, default='active')
        b.pack(side='bottom', fill=tkinter.NONE, expand=0, pady=0)
        win.bind('<Return>', (lambda e, b=b: b.invoke()))
        win.bind('<Escape>', (lambda e, b=b: b.invoke()))

        t = ReadOnlyText(
            f, wrap="word", padx=2, pady=2, bd=2, relief="sunken",
            # font=tkFont.Font(family="Lucida Sans Typewriter"),
            font=self.tkfixedfont,
            height=14,
            width=52,
            takefocus=False)
        t.insert("0.0", prompt)
        t.pack(side='left', fill=tkinter.BOTH, expand=1, padx=0, pady=0)
        ysb = ttk.Scrollbar(f, orient='vertical', command=t.yview, width=8)
        ysb.pack(side='right', fill=tkinter.Y, expand=0, padx=0, pady=0)
        # t.configure(state="disabled", yscroll=ysb.set)
        t.configure(yscroll=ysb.set)
        f.pack(padx=2, pady=2, fill=tkinter.BOTH, expand=1)

        win.focus_set()
        win.grab_set()
        win.transient(self)
        win.wait_window(win)


    def makeReport(self, event=None):
        self.value_of_combo = self.box.get()
        if self.value_of_combo not in self.specs:
            self.specs.append(self.value_of_combo)
            self.specs.sort()
            self.box["values"] = self.specs
            self.modified = True
        logger.debug("spec: {0}".format(self.value_of_combo))
        self.all_text = text = getReportData(
            self.value_of_combo,
            self.loop.file2uuids,
            self.loop.uuid2hash,
            self.loop.options)
        # logger.debug("res: {0}".format(text))
        if not self.all_text:
            text = _("Report contains no output.")
        self.text.delete('1.0', END)
        self.text.insert(INSERT, text)
        self.text.mark_set(INSERT, '1.0')

    def newselection(self, event=None):
        self.value_of_combo = self.box.get()

    def reportHelp(self):
        logger.debug("not implemented")
        pass

    def saveReportAs(self):
        logger.debug("not implemented")
        pass

    def exportCSV(self):
        logger.debug("spec: {0}".format(self.value_of_combo))
        self.csv = text = getReportData(
            self.value_of_combo,
            self.loop.file2uuids,
            self.loop.uuid2hash,
            self.loop.options,
            export=True)
        fileops = {'defaultextension': '.csv',
                   'filetypes': [('text files', '.csv')],
                   'initialdir': self.options['etmdir'],
                   'title': 'CSV data files',
                   'parent': self}
        filename = asksaveasfilename(**fileops)
        if not filename:
            return False
        fo = codecs.open(filename, 'w', self.options['encoding']['file'])
        for row in self.csv:
            fo.write("{0}\n".format(",".join(row)))
        fo.close()
        # print(self.csv)

    def emailReport(self):
        logger.debug("not implemented")
        pass

    def saveSpecs(self):
        logger.debug("not implemented")
        pass

class SimpleEditor(Toplevel):

    def __init__(self, parent=None, file=None, newhsh=None, rephsh=None, options=None, title=None):
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
        Toplevel.__init__(self, parent)
        self.minsize(400, 300)
        self.geometry('500x200')
        self.transient(parent)
        self.configure(background=BGCOLOR, highlightbackground=BGCOLOR)
        self.parent = parent
        self.loop = parent.loop
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
        self.tkfixedfont.configure(size=self.options['fontsize'])
        # self.text_value.trace_variable("w", self.setSaveStatus)
        frame = Frame(self, bd=0, relief=FLAT)
        frame.pack(side="bottom", fill=X, padx=4, pady=0)
        frame.configure(background=BGCOLOR, highlightbackground=BGCOLOR)

        btnwdth = 5

        # ok will check, save and quit
        Button(frame, text=_("OK"), highlightbackground=BGCOLOR, width=btnwdth, command=self.onSave, pady=2).pack(side=RIGHT, padx=4)

        l, c = commandShortcut('w')
        self.bind(c, self.onSave)

        # cancel will quit with a warning prompt if modified
        Button(frame, text=_("Cancel"), highlightbackground=BGCOLOR, pady=2, width=btnwdth, command=self.cancel).pack(side=RIGHT, padx=4)
        # self.bind("<Escape>", self.quit)
        self.bind("<Escape>", self.cancel)
        # check will evaluate the item entry and, if repeating, show reps
        inspect = Button(frame, text=_("Validate"), highlightbackground=BGCOLOR,  command=self.onCheck, pady=2)
        inspect.pack(side=LEFT, padx=4)


        # find
        Button(frame, text='x', command=self.clearFind, highlightbackground=BGCOLOR, padx=8, pady=2).pack(side=LEFT, padx=0)
        self.find_text = StringVar(frame)
        self.e = Entry(frame, textvariable=self.find_text, width=10, highlightbackground=BGCOLOR)
        self.e.pack(side=LEFT, padx=0, expand=1, fill=X)
        self.e.bind("<Return>", self.onFind)
        Button(frame, text='>', command=self.onFind, highlightbackground=BGCOLOR, padx=8, pady=2).pack(side=LEFT, padx=0)

        text = Text(self, bd=2, relief="sunken", padx=3, pady=2, font=self.tkfixedfont, undo=True, width=70)
        text.configure(highlightthickness=0)
        text.tag_configure(FOUND, background="lightskyblue")

        text.pack(side="bottom", padx=4, pady=3, expand=1, fill=BOTH)
        self.text = text

        if self.options['auto_completions']:
            cf = self.options['auto_completions']
            logger.debug("auto_completions: {0}".format(cf))
            fe = self.options['encoding']['file']
            completions = []
            with codecs.open(cf, 'r', fe) as fo:
                self.completions = [x.rstrip() for x in fo.readlines() if x
                    .rstrip()]
            logger.debug('completions: {0}'.format(self.completions))


        if title is not None:
            self.wm_title(title)
        if file is not None:
            # we're editing a file
            self.mode = 'file'
            inspect.configure(state="disabled")
            logger.debug('file: {0}'.format(file))
            with codecs.open(file, 'r',
                             self.options['encoding']['file']) as f:
                text = f.read()
        else:
            # we are creating a new item and/or replacing an item
            # mode:
            #   1: new
            #   2: replace
            #   3: new and replace
            initfile = None
            # logger.debug("newhsh: {0}".format(self.newhsh))
            # logger.debug("rephsh: {0}".format(self.rephsh))
            # set the mode
            if newhsh is None and rephsh is None:
                # we are creating a new item from scratch
                self.mode = 1
                self.edithsh = self.newhsh
                initfile = ensureMonthly(options=self.options)
                text = ''
            elif rephsh is None:  # newhsh
                # we are creating a new item as a copy
                self.mode = 1
                self.edithsh = self.newhsh
                if ('fileinfo' in newhsh and newhsh['fileinfo']):
                    initfile = newhsh['fileinfo'][0]
                else:
                    initfile = ensureMonthly(options=self.options)
                text = hsh2str(self.edithsh, self.options)
            elif newhsh is None: # rephsh
                # we are editing and replacing rephsh - no file prompt
                self.mode = 2
                # self.repinfo = rephsh['fileinfo']
                self.edithsh = self.rephsh
                text = hsh2str(self.edithsh, self.options)
            else:  # neither is None
                # we are changing some instances of a repeating item
                # we will be writing but not editing rephsh using its fileinfo
                # we will be editing and saving newhsh using self.initfile
                self.mode = 3
                self.edithsh = self.newhsh
                # self.repinfo = rephsh['fileinfo']
                if 'fileinfo' in newhsh and newhsh['fileinfo'][0]:
                    initfile = self.newhsh['fileinfo'][0]
                else:
                    initfile = ensureMonthly(options=self.options)
                text = hsh2str(self.edithsh, self.options)

            if initfile:
                self.initfile = os.path.join(self.options['datadir'], initfile)

            logger.debug('mode: {0}; initfile: {1}; edit: {2}'.format(self.mode,  self.initfile,  self.edithsh))
        # logger.debug("setting text {0}:\n{1}".format(type(text), text))
        self.settext(text)

        # clear the undo buffer
        self.text.edit_reset()
        self.setmodified(False)
        self.text.bind('<<Modified>>', self.updateSaveStatus)

        # if self.parent:
        #     self.initial_focus().focus_set = self.parent
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

    def showCompletions(self, e=None):
        # print(self.text.get("insert -1c wordstart", INSERT))
        line = self.text.get("insert linestart", INSERT)
        m = completion_regex.search(line)
        if m:
            match = m.groups()[0]
            logger.debug("found match '{0}' in line '{1}'".format(match, line))
            self.matches = matches = [x for x in self.completions if x.lower()
                .startswith(match.lower())]
            if len(matches) >= 1:
                logger.debug("{0} items in completions matching '{1}'".format(len(matches), match))
                # self.line = line
                self.match = match
                self.autocompletewindow = acw = Toplevel(self)
                self.scrollbar = scrollbar = ttk.Scrollbar(acw,
                                                           orient="vertical",
                                                           width=8)
                self.listbox = listbox = Listbox(acw, yscrollcommand=scrollbar.set, exportselection=False, bg="white")
                for item in matches:
                    listbox.insert(END, item)
                scrollbar.config(command=listbox.yview)
                scrollbar.pack(side=RIGHT, fill="y")
                listbox.pack(side=LEFT, fill=BOTH, expand=True)
                self.listbox.select_set(0)
                self.listbox.see(0)
                self.listbox.focus_set()
                self.listbox.bind("<Return>", self.completionSelected)
                self.listbox.bind("<Escape>", self.hideCompletions)
                self.listbox.bind("Up", self.cursorUp)
                self.listbox.bind("Down", self.cursorDown)

            else:
                relfile = relpath(self.options['auto_completions'], self.options['etmdir'])
                self.messageWindow(title=_('etm'), prompt=_("No matches for '{0}'\nin '{1}'.").format(match, relfile), opts=self.options)
                # logger.debug("nothing in completions matching '{0}'.".format(match))
                return "break"
        else:
            # return
            logger.debug("no match in {0}".format(line))
        return "break"

    def is_active(self):
        return self.autocompletewindow is not None

    def hideCompletions(self, e=None):
        if not self.is_active():
            return
        # destroy widgets
        # self.match = None
        self.scrollbar.destroy()
        self.scrollbar = None
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

    def cursorUp(self):
        cursel = int(self.listbox.curselection()[0])
        newsel = max(0, cursel=1)
        self.listbox.select_clear(cursel)
        self.listbox.select_set(newsel)
        self.listbox.see(newsel)

    def cursorDown(self):
        cursel = int(self.listbox.curselection()[0])
        newsel = min(len(self.matches)-1, cursel+1)
        self.listbox.select_clear(cursel)
        self.listbox.select_set(newsel)
        self.listbox.see(newsel)

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
        logger.debug('modified: {0}'.format(self.checkmodified()))
        e = None
        if not self.checkmodified():
            self.quit()
        elif self.file is not None:
            # we are editing a file
            alltext = self.gettext()
            with codecs.open(self.file, 'w',
                             self.options['encoding']['file']) as f:
                f.write(alltext)
            self.setmodified(False)
            self.changed = True
            self.quit()
        else:
            # we are editing an item
            ok = self.onCheck(showreps=False)
            if not ok:
                logger.debug('not ok')
                return "break"
            if self.mode in [1, 3]:  # new
                if 's' in self.edithsh and self.edithsh['s']:
                    dt = self.edithsh['s']
                else:
                    dt = None
            if self.mode in [1, 3]:
                # we need a filename for the new item
                # make datadir the root
                dir = self.options['datadir']
                file = relpath(self.initfile, dir)
                logger.debug('initial dir and file: "{0}"; "{1}"'.format(dir, file))
                fileops = {'defaultextension': '.txt',
                           'filetypes': [('text files', '.txt')],
                           'initialdir': dir,
                           'initialfile': file,
                           'title': 'etmtk data files',
                           'parent': self}
                filename = askopenfilename(**fileops)
                if not (filename and os.path.isfile(filename)):
                    return False
            logger.debug('edithsh: {0}'.format(self.edithsh))
            ok = True
            if self.mode == 1:
                if self.loop.append_item(self.edithsh, filename):
                    self.update_idletasks()
                    logger.debug('added: {0}'.format(self.edithsh))
                else:
                    ok = False
            elif self.mode == 2:
                if self.loop.replace_item(self.edithsh):
                    logger.debug('replaced: {0}'.format(self.edithsh))
                else:
                    ok = False
            else:  # self.mode == 3
                if self.loop.append_item(self.edithsh, filename):
                    self.update_idletasks()
                    logger.debug('added: {0}'.format(self.edithsh))
                else:
                    ok = False
                if self.loop.replace_item(self.rephsh):
                    logger.debug('replaced: {0}'.format(self.rephsh))
                else:
                    ok = False

            logger.debug('ok: {0}'.format(ok))
            # update the return value so that when it is not null then modified
            # is false and when modified is true then it is null
            self.setmodified(False)
            self.changed = True
            self.quit()
            return "break"

    def onCheck(self, event=None, showreps=True):
        text = self.gettext()
        logger.debug("text: {0}".format(text))
        msg = []
        reps = []
        error = False
        try:
            hsh, msg = str2hsh(text, options=self.options)
        except Exception as e:
            logger.exception('could not process: {0}'.format(text))
            error = True
        if msg:
            messages = "{0}".format("\n".join(msg))
            logger.debug("messages: {0}".format(messages))
            self.messageWindow(MESSAGES, messages, opts=self.options)
        if error or msg:
            self.newhsh = None
            logger.debug('returning ok False')
            return False

        # we have a good hsh
        if self.edithsh and 'fileinfo' in self.edithsh:
            fileinfo = self.edithsh['fileinfo']
            self.edithsh = hsh
            self.edithsh['fileinfo'] = fileinfo
        else:
            # we have a new item without fileinfo
            self.edithsh = hsh
        # update missing fields
        str = hsh2str(hsh, options=self.options)
        logger.debug("str: {0}".format(str))
        if str != text:
            self.settext(str)
        if 'r' in hsh and showreps:
            showing_all, reps =  get_reps(self.options['bef'], hsh)
            repsfmt = [x.strftime(rrulefmt) for x in reps]
            logger.debug("{0}: {1}".format(showing_all, repsfmt))

            repetitions = "{0}".format("\n".join(repsfmt))
            if showing_all:
                self.messageWindow(ALLREPS, repetitions, opts=self.options)
            else:
                self.messageWindow(SOMEREPS, repetitions, opts=self.options)
        logger.debug(('onCheck: Ok'))
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
        logger.debug(('calling quit'))
        self.quit()

    def quit(self, e=None):
        if self.checkmodified():
            ans = askokcancel(
                _('Quit'),
                _("There are unsaved changes.\nDo you really want to quit?"),
                parent=self)
        else:
            ans = True
        if ans:
            if self.parent:
                logger.debug('focus set')
                self.parent.focus()
                self.parent.tree.focus_set()
            self.destroy()
        return "break"

    def messageWindow(self, title, prompt, opts=None):
        win = Toplevel()
        win.title(title)
        # win.minsize(444, 430)
        # win.minsize(450, 450)
        f = Frame(win)
        # pack the button first so that it doesn't disappear with resizing
        b = Button(win, text=_('OK'), width=10, command=win.destroy, default='active')
        b.pack(side='bottom', fill=tkinter.NONE, expand=0, pady=0)
        win.bind('<Return>', (lambda e, b=b: b.invoke()))
        win.bind('<Escape>', (lambda e, b=b: b.invoke()))

        t = ReadOnlyText(
            f, wrap="word", padx=2, pady=2, bd=2, relief="sunken",
            font=self.tkfixedfont,
            height=14,
            width=52,
            takefocus=False)
        t.insert("0.0", prompt)
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

if __name__ == '__main__':
    print('edit.py should only be imported. Run etm or view.py instead.')
