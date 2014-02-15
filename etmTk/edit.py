#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import platform, sys
import codecs

from copy import deepcopy

if platform.python_version() >= '3':
    import tkinter
    from tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Frame, LEFT, RIGHT, Text, PanedWindow, OptionMenu, StringVar, Menu, BooleanVar, ACTIVE, X, RIDGE, BOTH, SEL, SEL_FIRST, SEL_LAST, Button, FLAT
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
    from Tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Frame, LEFT, RIGHT, Text, PanedWindow, OptionMenu, StringVar, Menu, BooleanVar, ACTIVE, X, RIDGE, BOTH, SEL, SEL_FIRST, SEL_LAST, Button, FLAT
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

import gettext
_ = gettext.gettext

import logging
import logging.config
logger = logging.getLogger()


SOMEREPS = _('Selected repetitions')
ALLREPS = _('Repetitions')
MESSAGES = _('Error messages')

from etmTk.data import hsh2str, str2hsh, get_reps, rrulefmt, ensureMonthly, commandShortcut, optionShortcut, bgclr, CMD, relpath


from idlelib.WidgetRedirector import WidgetRedirector

class ReadOnlyText(Text):
    # noinspection PyShadowingNames
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")


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
        self.geometry('440x400')
        self.transient(parent)
        self.parent = parent
        self.loop = parent.loop
        self.changed = False

        self.file = file
        self.initfile = None
        self.fileinfo = None
        self.repinfo = None
        self.title = title
        self.newhsh = newhsh
        self.rephsh = rephsh
        self.value = ''
        self.options = options
        # self.text_value.trace_variable("w", self.setSaveStatus)
        frame = Frame(self, bd=0, relief=FLAT)
        frame.pack(side="bottom", fill=X, padx=4, pady=3)
        frame.configure(background=bgclr)

        btnwdth = 5

        # ok will check, save and quit
        Button(frame, text=_("OK"), highlightbackground=bgclr, width=btnwdth, command=self.onSave).pack(side=RIGHT, padx=4)

        l, c = commandShortcut('w')
        self.bind(c, self.onSave)

        # cancel will quit with a warning prompt if modified
        Button(frame, text=_("Cancel"), highlightbackground=bgclr, width=btnwdth, command=self.quit).pack(side=RIGHT, padx=4)
        self.bind("<Escape>", self.quit)
        # check will evaluate the item entry and, if repeating, show reps
        inspect = Button(frame, text=_("Inspect"), highlightbackground=bgclr, width=btnwdth, command=self.onCheck)
        inspect.pack(side=LEFT, padx=4)


        # find
        Button(frame, text='<', command=self.clearFind, highlightbackground=bgclr, padx=8).pack(side=LEFT,
                                                                                                         padx=0)
        self.find_text = StringVar(frame)
        e = Entry(frame, textvariable=self.find_text, width=10, highlightbackground=bgclr)
        e.pack(side=LEFT, padx=0, expand=1, fill=X)
        e.bind("<Return>", self.onFind)
        e.bind("<Escape>", self.clearFind)
        Button(frame, text='>', command=self.onFind, highlightbackground=bgclr,  padx=8).pack(side=LEFT, padx=0)

        text = Text(self, bd=2, relief="sunken", padx=3, pady=2, font=tkFont.Font(family="Lucida Sans Typewriter"), undo=True, width=70)
        text.configure(highlightthickness=0)

        text.pack(side="bottom", padx=4, pady=4, expand=1, fill=BOTH)
        self.text = text
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
            logger.debug("newhsh: {0}".format(self.newhsh))
            logger.debug("rephsh: {0}".format(self.rephsh))
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
        self.grab_set()
        # if self.parent:
        #     self.initial_focus().focus_set = self.parent
        self.text.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.quit)
        if parent:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                      parent.winfo_rooty() + 50))
        self.configure(background=bgclr)
        self.wait_window(self)

    def settext(self, text=''):
        self.text.delete('1.0', END)
        self.text.insert(INSERT, text)
        self.text.mark_set(INSERT, '1.0')
        self.text.focus()
        logger.debug("modified: {0}".format(self.checkmodified()))

    def gettext(self):
        return self.text.get('1.0', END + '-1c')

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
                return False
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
            logger.debug("hsh: {0}".format(hsh))
        except Exception as e:
            logger.exception('could not process: {0}'.format(text))
            error = True
        if msg:
            messages = "{0}".format("\n".join(msg))
            logger.debug("messages: {0}".format(messages))
            self.messageWindow(MESSAGES, messages)
        if error or msg:
            self.newhsh = None
            return False, ''

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
                self.messageWindow(ALLREPS, repetitions)
            else:
                self.messageWindow(SOMEREPS, repetitions)
        logger.debug(('onCheck: Ok'))
        return True

    def clearFind(self, *args):
        self.find_text.set("")

    def onFind(self, *args):
        target = self.find_text.get()
        print('onFind')
        # target = askstring('SimpleEditor', 'Search String?')
        print('target', target)
        if target:
            where = self.text.search(target, INSERT, END)
            if not where:
                where = self.text.search(target, "0.0", INSERT)
            if where:
                print(where)
                pastit = where + ('+%dc' % len(target))
                # self.text.tag_remove(SEL, '1.0', END)
                self.text.tag_add(SEL, where, pastit)
                self.text.mark_set(INSERT, pastit)
                self.text.see(INSERT)
                self.text.focus()

    def quit(self, e=None):
        logger.debug(('quit'))
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

    def messageWindow(self, title, prompt):
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
            font=tkFont.Font(family="Lucida Sans Typewriter"),
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

if __name__ == '__main__':
    print('edit.py should only be imported. Run etm or view.py instead.')
