#!/usr/bin/env python3
#import the 'tkinter' module
import os
import platform
import sys
if platform.python_version() >= '3':
    import tkinter
    from tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, Text
    from tkinter import messagebox as tkMessageBox
    from tkinter import ttk
    from tkinter import font as tkFont
    from tkinter import simpledialog as tkSimpleDialog
    # import tkFont
else:
    import Tkinter as tkinter
    from Tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, Text
    import tkMessageBox
    import ttk
    import tkFont
    import tkSimpleDialog

tkversion = tkinter.TkVersion

import etmTk.data as data
from etmTk.data import init_localization

from dateutil.parser import parse

from etmTk.data import (
    fmt_weekday, fmt_dt, fmt_time, get_options, get_data,
    get_reps, getDoneAndTwo, getFiles, getPrevNext, getReportData,
    getViewData, group_regex, hsh2str, leadingzero, mail_report,
    oneday, oneminute, parse_datetime, parse_dtstr, fmt_datetime,
    process_lines, relpath, rrulefmt, s2or3, send_mail, send_text,
    sfmt, str2hsh, timedelta2Str, tstr2SCI, fmt_period,
    updateCurrentFiles, get_changes, checkForNewerVersion, getAgenda,
    date_calculator, datetime2minutes, calyear, export_ical_item,
    import_ical, export_ical, has_icalendar, expand_template, ensureMonthly,
    sys_platform, id2Type, get_current_time)

import gettext
_ = gettext.gettext


class MessageWindow():
    def __init__(self, parent, title, prompt):
        self.win = Toplevel(parent)
        self.parent = parent
        self.win.title(title)
        Label(self.win, text=prompt).pack(fill=tkinter.BOTH, expand=1, padx=10, pady=10)
        b = Button(self.win, text=_('OK'), width=10, command=self.cancel, default='active')
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


class DialogWindow():
    def __init__(self, parent, title="", prompt=""):
        self.win = Toplevel(parent)
        self.parent = parent

        self.win.title(title)
        Label(self.win, text=prompt, justify='left').pack(fill=tkinter.BOTH, expand=1, padx=10, pady=5)
        self.e = Entry(self.win).pack(padx=5, pady=5)
        box = Frame(self.win)
        o = Button(box, text="OK", width=10, default='active', command=self.ok)
        o.pack(side=LEFT, padx=5, pady=5)
        c = Button(box, text="Cancel", width=10, command=self.cancel)
        c.pack(side=LEFT, padx=5, pady=5)
        box.pack()
        self.win.bind('<Return>', (lambda e, o=o: o.invoke()))
        self.win.bind('<Escape>', (lambda e, c=c: c.invoke()))
        self.win.focus_set()
        self.win.grab_set()
        self.win.transient(parent)
        self.win.wait_window(self.win)
        return(self.e)

    def ok(self, event=None):
        if not self.validate():
            self.messageWindow('error', self.error_message)
            self.parent.focus_set()
            return

        self.parent.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.win.destroy()

    #
    # command hooks

    def validate(self):
        self.error_message = "an integer between 1 and 4 is required"

        return 0  # override

    def apply(self):

        pass  # override

    def messageWindow(self, title, prompt):
        MessageWindow(self.parent, title, prompt)


class App(Tk):
    def __init__(self, path=None):
        Tk.__init__(self)
        # print(tkFont.names())
        self.minsize(400, 380)
        self.history = []
        self.index = 0
        self.count2id = {}
        self.now = None
        self.options = {}
        self.popup = ''
        self.value = ''
        self.firsttime = True
        self.mode = 'command'   # or edit or delete
        self.item_hsh = {}

        self.title("etm tk")
        if sys_platform == 'Linux':
            self.wm_iconbitmap('@' + 'etmlogo-4.xbm')
        # self.wm_iconbitmap('etmlogo-4.xbm')
        # self.call('wm', 'iconbitmap', self._w, '/Users/dag/etm-tk/etmlogo_128x128x32.ico')
            # self.iconbitmap(ICON_PATH)

        self.columnconfigure(0, minsize=300, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=1)

        self.tree = ttk.Treeview(self, show='tree', columns=["#1"], selectmode='browse')
        self.tree.column("#0", minwidth=200, width=300, stretch=1)
        self.tree.column("#1", minwidth=80, width=140, stretch=0, anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self.OnSelect)
        self.tree.bind("<Double-1>", self.OnDoubleClick)
        self.tree.bind("<Return>", self.OnActivate)

        self.date2id = {}
        padx = 2

        # abspath = os.path.abspath(path)
        # root_node = self.tree.insert(u'', 'end', text=abspath, open=True)
        self.root = (u'', u'_')

        self.e = Entry(self, text='?')

        self.e.bind('<Return>', self.process_input)
        self.e.bind('<Escape>', self.cleartext)
        self.e.bind('<Up>', self.prev_history)
        self.e.bind('<Down>', self.next_history)
        self.e.grid(row=0, column=0, sticky='ew')

        for t in (self.e, self.tree):
            t.bind('<Tab>', lambda e, t=t: self.focusNext(t))
            t.bind('<Shift-Tab>', lambda e, t=t: self.focusPrev(t))

        self.tree.grid(row=1, column=0, sticky='nsew', padx=padx)

        self.l = Text(self, wrap="word", bd=1, relief="sunken", padx=padx, pady=4, font=tkFont.Font(family="Lucida Sans"), height=6, width=50)
        self.l.configure(state="disabled")

        self.l.grid(row=2, column=0, sticky="nesw")
        self.grid()
        self.update_clock()
        self.showTree(loop.do_a(''))
        self.lift()

    def focusNext(self, widget):
        print('focus next')
        widget.tk_focusNext().focus_set()
        return 'break'

    def focusPrev(self, widget):
        print('focus prev')
        widget.tk_focusPrev().focus_set()
        return 'break'

    def OnSelect(self, event=None):
        """
        Tree row has gained selection.
        """
        item = self.tree.selection()[0]
        uuid, dt, hsh = self.getInstance(item)
        self.l.configure(state="normal")
        self.l.delete("0.0", END)
        if uuid is not None:
            if 'r' in hsh and dt:
                item = "{0} {1}".format(_('selected'), dt)
            else:
                item = _('selected')
            l1 = hsh['fileinfo'][1]
            l2 = hsh['fileinfo'][2]
            if l1 == l2:
                lines = "{0} {1}".format(_('line'), l1)
            else:
                lines = "{0} {1}-{2}".format(_('lines'), l1, l2)
            filetext = "{0}, {1}".format(hsh['fileinfo'][0], lines)
            text = "=== {0} ===\n{1}\n\n=== {2} ===\n{3}".format(item, hsh['entry'].lstrip(), _("file"), filetext)
        else:
            text = ""
        self.l.insert(INSERT, text)
        self.l.configure(state="disabled")

    def OnActivate(self, event):
        """
        Return pressed with tree row selected
        """
        item = self.tree.selection()[0]
        uuid, dt, hsh = self.getInstance(item)
        print("you pressed <Return> on", item, uuid, dt, hsh['entry'])

    def OnDoubleClick(self, event):
        """
        Double click on tree row
        """
        item = self.tree.identify('item', event.x, event.y)
        uuid, dt, hsh = self.getInstance(item)
        print("you double clicked on", item, uuid, dt, hsh)

    def getInstance(self, item):
        instance = self.count2id[item]
        if instance is None:
            return(None, None, None)
        uuid, dt = self.count2id[item].split("::")
        hsh = loop.uuid2hash[uuid]
        return(uuid, dt, hsh)


    def update_clock(self):
        self.now = get_current_time()
        nxt = (60*1000 - self.now.second*1000 - self.now.microsecond//1000)
        nowfmt = "{0} {1}".format(
            s2or3(self.now.strftime(loop.options['reprtimefmt']).lower()),
            s2or3(self.now.strftime("%a %b %d %Z")))
        nowfmt = leadingzero.sub("", nowfmt)

        print(self.now)
        self.title("{0}".format(nowfmt))
        self.after(nxt, self.update_clock)

    def prev_history(self, event):
        """
        Replace input with the previous history item.
        """
        print('up')
        if self.index >= 1:
            self.index -= 1
            self.e.delete(0, END)
            self.e.insert(0, self.history[self.index])
        return 'break'

    def next_history(self, event):
        """
        Replace input with the next history item.
        """
        print('down')
        if self.index + 1 < len(self.history):
            self.index += 1
            self.e.delete(0, END)
            self.e.insert(0, self.history[self.index])
        return 'break'

    def messageWindow(self, title, prompt):
        win = Toplevel()
        win.title(title)
        Label(win, text=prompt, wraplength=400, justify='left', font=tkFont.Font(family="Lucida Sans Typewriter"), fg="darkblue").pack(fill=tkinter.BOTH, expand=1, padx=10)
        b = Button(win, text=_('OK'), width=10, command=win.destroy, default='active')
        b.pack()
        win.bind('<Return>', (lambda e, b=b: b.invoke()))
        win.bind('<Escape>', (lambda e, b=b: b.invoke()))
        win.focus_set()
        win.grab_set()
        win.transient(self)
        win.wait_window(win)

    def getInteger(self, title, prompt):
        DialogWindow(self, title, prompt)

    def editWhich(self, instance="xyz"):
        prompt = "\n".join([
            _("You have selected instance"),
            "    {0}".format(instance),
            _("of a repeating item. What do you want to change?"),
            "  1. {0}".format(_("only the datetime of this instance")),
            "  2. {0}".format(_("this instance")),
            "  3. {0}".format(_("this and all subsequent instances")),
            "  4. {0}".format(_("all instances")),
            "{0}".format(_('Choice [1-4] or 0 to cancel?'))])
        self.getInteger(title='which instance', prompt=prompt)


    def gettext(self, event=None):
        self.string = self.e.get()
        print(self.string)

    def cleartext(self, event=None):
        self.e.delete(0, END)

    def process_input(self, event=None):
        """
        This is called whenever enter is pressed in the input field.
        Action depends upon comand_mode.
        Append input to history, process it and show the result in output.
        """
        cmd = self.e.get().strip()

        if not cmd:
            return(True)

        if self.mode == 'command':
            cmd = cmd.strip()
            if cmd[0] == 'w':
                self.editWhich()
                return()
            elif cmd[0] in ['a', 'r', 't']:
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

            # select everything in input to make it easy to clear
            self.e.select_range(0, END)
            try:
                res = loop.do_command(cmd)
            except:
                return _('could not process command "{0}"').format(cmd)

        elif self.mode == 'edit':
            print('edit', cmd)
            res = loop._do_edit(cmd)

        elif self.mode == 'delete':
            print('deleted', cmd)
            loop._do_delete(cmd)
            res = ''

        elif self.mode == 'finish':
            print('finish', cmd)
            loop._do_finish(cmd)
            res = ''

        elif self.mode == 'new_date':
            print('date', cmd)
            res = loop._new_date(cmd)

        if not res:
            res = _('command "{0}" returned no output').format(cmd)
        if type(res) == dict:
            self.showTree(res)
        else:
            # not a hash => not a tree
            self.messageWindow(title='etm', prompt=res)
            return(0)

    def showTree(self, tree):
        self.deleteItems()
        self.count = 0
        self.count2id = {}
        self.addItems(u'', tree[self.root], tree)
        loop.count2id = self.count2id
        self.l.configure(state="normal")
        self.l.delete("0.0", END)
        self.l.configure(state="disabled")
        top = self.tree.get_children()[0]
        self.tree.focus_set()
        self.tree.focus(top)
        self.tree.selection_set(top)
        self.tree.yview(0)  # this is a line number

    def deleteItems(self):
        for child in self.tree.get_children():
            self.tree.delete(child)

    def addItems(self, parent, elements, tree):
        for text in elements:
            # print('text', text)
            # text is a key in the element (tree) hash
            # these keys are (parent, item) tuples
            if text in tree:
                # this is a branch
                item = " " + text[1]  # this is the label of the parent
                children = tree[text]  # this are the children tuples of item
                oid = self.tree.insert(parent, 'end', text=item, open=True)
                # recurse to get children
                self.count2id[oid] = None
                self.addItems(oid, children, tree)
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

                oid = self.tree.insert(parent, 'end', text=col1, open=True, value=[col2])
                self.count2id[oid] = "{0}::{1}".format(uuid, dt)
                if dt:
                    d = parse(dt[:10]).date()
                    if d not in self.date2id:
                        self.date2id[d] = parent

if __name__ == "__main__":
    etmdir = ''
    etm = sys.argv[0]
    if (len(sys.argv) > 1 and os.path.isdir(sys.argv[1])):
        etmdir = sys.argv.pop(1)
    init_localization()
    if len(sys.argv) > 1:
        etmdir = sys.argv.pop(1)
    (user_options, options, use_locale) = data.get_options(etmdir)
    loop = data.ETMCmd(options)
    loop.tkversion = tkversion
    # app = App(path='/Users/dag/etm-tk')
    app = App()
    app.mainloop()
