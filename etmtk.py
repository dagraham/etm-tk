#!/usr/bin/env python3
#import the 'tkinter' module
import os
import platform
import sys
if platform.python_version() >= '3':
    import tkinter
    from tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, Text, PanedWindow, OptionMenu, StringVar
    from tkinter import messagebox as tkMessageBox
    from tkinter import ttk
    from tkinter import font as tkFont
    from tkinter import simpledialog as tkSimpleDialog
    # import tkFont
else:
    import Tkinter as tkinter
    from Tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, Text, PanedWindow, OptionMenu, StringVar
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
    def __init__(self, parent, title="", prompt="", maxvalue=0, minvalue=0):
        self.win = Toplevel(parent)
        self.parent = parent
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        self.error_message = ""
        self.value = None
        self.win.title(title)
        Label(self.win, text=prompt, justify='left').pack(fill=tkinter.BOTH, expand=1, padx=10, pady=5)
        self.entry = Entry(self.win)
        self.entry.pack(padx=5, pady=5)
        box = Frame(self.win)
        o = Button(box, text="OK", width=10, default='active', command=self.ok)
        o.pack(side=LEFT, padx=5, pady=5)
        c = Button(box, text="Cancel", width=10, command=self.cancel)
        c.pack(side=LEFT, padx=5, pady=5)
        box.pack()
        self.win.bind('<Return>', (lambda e, o=o: o.invoke()))
        self.win.bind('<Escape>', (lambda e, c=c: c.invoke()))
        self.entry.focus_set()
        # self.win.focus_set()
        self.win.grab_set()
        self.win.transient(parent)
        self.win.wait_window(self.win)

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
        self.error_message = ""

        return 1  # override

    def apply(self):

        pass  # override

    def messageWindow(self, title, prompt):
        MessageWindow(self.parent, title, prompt)


class GetInteger(DialogWindow):
    def validate(self):
        print(self.__dict__)
        res = self.entry.get()
        print('checking', res)
        try:
            val = int(res)
            ok = (val >= self.minvalue and val <= self.maxvalue)
            print('ok', ok)
        except:
            val = None
            ok = False

        if ok:
            print('setting value', val)
            self.value = val
            return True
        else:
            self.error_message = _("an integer between {0} and {1} is required").format(self.minvalue, self.maxvalue)
            return False

class GetDateTime(DialogWindow):
    def validate(self):
        res = self.entry.get()
        ok = False
        if not res.strip():
            # today
            val = get_current_time()
            ok = True
        else:
            try:
                x = parse_datetime(res)
                val = parse(parse_datetime(res))
                ok = True
            except:
                val = None

        if ok:
            self.value = val
            return True
        else:
            self.error_message = _('could not parse "{0}"').format(res)
            return False

class App(Tk):
    def __init__(self, path=None):
        Tk.__init__(self)
        # print(tkFont.names())
        self.minsize(400, 450)
        # self.configure(background="lightgrey")
        self.history = []
        self.index = 0
        self.count = 0
        self.count2id = {}
        self.now = None
        self.dayview = False
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

        ef = Frame(self)

        pw = PanedWindow(self, orient="vertical",
                         # showhandle=True,
                         sashwidth=3, sashrelief='flat',
                         )
        # pw.pack(fill="both", expand=1)

        self.tree = ttk.Treeview(pw, show='tree', columns=["#1"], selectmode='browse', padding=(3, 2, 3, 2))
        self.tree.column("#0", minwidth=200, width=300, stretch=1)
        self.tree.column("#1", minwidth=80, width=140, stretch=0, anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self.OnSelect)
        self.tree.bind("<Double-1>", self.OnDoubleClick)
        self.tree.bind("<Return>", self.OnActivate)
        self.tree.bind('<Escape>', self.cleartext)
        self.tree.bind('<space>', self.goHome)
        self.tree.bind('<j>', self.jumpToDate)
        self.tree.bind('<,>', self.agendaView)
        self.tree.bind('<.>', self.scheduleView)
        self.tree.bind('</>', self.pathView)
        self.tree.bind('<;>', self.keywordView)
        self.tree.bind("<'>", self.tagView)

        self.date2id = {}
        # padx = 2

        self.root = (u'', u'_')

        ef.grid(row=0, column=0, sticky='ew', padx=3, pady=2)

        menuwidth = 8

        self.vm_options = [[_('agenda'), 'a'],
                           [_('schedule'), 's'],
                           [_('paths'), 'p'],
                           [_('keywords'), 'k'],
                           [_('tags'), 't']]

        self.vm_opts = [x[0] for x in self.vm_options]
        self.viewLabel = _("show")
        self.view = self.vm_options[0][0]
        self.viewValue = StringVar(self)
        self.currentView = StringVar(self)
        self.currentView.set("{0} {1}".format(_("showing"), self.view))
        self.viewValue.set(self.viewLabel)
        self.vm = OptionMenu(ef, self.viewValue, *self.vm_opts, command=self.setView)
        self.vm.configure(width=menuwidth)
        self.vm.pack(side="left")

        self.newValue = StringVar(self)
        self.newLabel = _("make")
        self.newValue.set(self.newLabel)
        self.nm_options = [[_('item'), 'n'],
                           [_('action timer'), '?']
                           ]
        self.nm_opts = [x[0] for x in self.nm_options]
        self.nm = OptionMenu(ef, self.newValue, *self.nm_opts, command=self.newCommand)
        self.nm.configure(width=menuwidth)
        self.nm.pack(side="left")

        self.editValue = StringVar(self)
        self.editLabel = _("edit")
        self.editValue.set(self.editLabel)
        self.em_options = [[_('edit selected item'), ''],
                           [_('clone selected item'), ''],
                           [_('delete selected item'), ''],
                           [_('finish selected task'), ''],
                           [_('action timer for selected item'), ''],
                           ]
        self.em_opts = [x[0] for x in self.em_options]
        self.em = OptionMenu(ef, self.editValue, *self.em_opts, command=self.editCommand)
        self.em.configure(width=menuwidth)
        self.em.pack(side="left")

        self.filterValue = StringVar(self)
        self.filterValue.set('')
        self.e = Entry(ef, textvariable=self.filterValue, bd=2)
        self.e.bind('<Return>', self.showView)
        self.e.bind('<Escape>', self.cleartext)
        self.e.bind('<Up>', self.prev_history)
        self.e.bind('<Down>', self.next_history)
        self.e.pack(side="left",fill=tkinter.BOTH, expand=1)

        self.b = Button(ef, text=_('?'), command=self.help, takefocus=False)
        self.b.pack(side="right", expand=0)

        pw.add(self.tree, padx=3, pady=0, stretch="first")

        # ysb.grid(row=1, column=1, rowspan=2, sticky='ns')

        self.l = Text(pw, wrap="word", bd=2, relief="sunken", padx=2, pady=2, font=tkFont.Font(family="Lucida Sans"), height=6, width=50, state="disabled", takefocus=False)

        pw.add(self.l, padx=0, pady=0, stretch="never")

        pw.grid(row=1, column=0, sticky="nsew", padx=2, pady=0)

        sf = Frame(self)

        showing = Label(sf, textvariable=self.currentView, bd=1, relief="flat", anchor="w", padx=0, pady=0)
        showing.pack(side="left")

        self.currentTime = StringVar(self)
        currenttime = Label(sf, textvariable=self.currentTime, bd=1, relief="flat", anchor="e", padx=0, pady=0)
        currenttime.pack(side="right")

        sf.grid(row=2, column=0, sticky="ew", padx=8, pady=4)

        self.grid()

        self.e.select_range(0, END)

        self.update_clock()

        self.showTree(loop.do_a(''))

    def agendaView(self, e=None):
        self.setView(self.vm_options[0][0])

    def scheduleView(self, e=None):
        self.setView(self.vm_options[1][0])

    def pathView(self, e=None):
        self.setView(self.vm_options[2][0])

    def keywordView(self, e=None):
        self.setView(self.vm_options[3][0])

    def tagView(self, e=None):
        self.setView(self.vm_options[4][0])

    def setView(self, view):
        self.view = view
        self.showView()

    def showView(self, e=None):
        # print('showView', self.view)
        self.currentView.set("{0} {1}".format(_("showing"), self.view))
        self.viewValue.set(self.viewLabel)
        fltr = self.filterValue.get()
        cmd = "{0} {1}".format(
            self.vm_options[self.vm_opts.index(self.view)][1], fltr)
        self.mode = 'command'
        self.process_input(cmd=cmd)

    def newCommand(self, e=None):
        newcommand = self.newValue.get()
        self.newValue.set(self.newLabel)
        print('newCommand', newcommand)

    def editCommand(self, e=None):
        editcommand = self.editValue.get()
        self.editValue.set(self.editLabel)
        print('editCommand', editcommand)

    def help(self, event=None):
        res = loop.help_help()
        self.messageWindow(title='etm', prompt=res)

    def goHome(self, event=None):
        if self.dayview:
            today = get_current_time().date()
            self.scrollToDate(today)
        else:
            self.tree.focus_set()
            self.tree.focus(1)
            self.tree.selection_set(1)
            self.tree.yview(0)
        return('break')

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
            self.em.configure(state="normal")
        else:
            text = ""
            self.em.configure(state="disabled")
        self.l.insert(INSERT, text)
        self.l.configure(state="disabled")

    def OnActivate(self, event):
        """
        Return pressed with tree row selected
        """
        item = self.tree.selection()[0]
        uuid, dt, hsh = self.getInstance(item)
        if uuid is not None:
            print("you pressed <Return> on", item, uuid, dt, hsh['_summary'])
        else:
            print("you pressed <Return> on", item)
        return("break")

    def OnDoubleClick(self, event):
        """
        Double click on tree row
        """
        item = self.tree.identify('item', event.x, event.y)
        uuid, dt, hsh = self.getInstance(item)
        if uuid is not None:
            print("you double clicked on", item, uuid, dt, hsh['_summary'])
        else:
            print("you double clicked on", item)
        return("break")

    def getInstance(self, item):
        instance = self.count2id[item]
        if instance is None:
            return(None, None, None)
        uuid, dt = self.count2id[item].split("::")
        hsh = loop.uuid2hash[uuid]
        return(uuid, dt, hsh)

    def update_clock(self):
        self.now = get_current_time()
        nxt = (60 - self.now.second) * 1000 - self.now.microsecond // 1000
        nowfmt = "{0} {1}".format(
            s2or3(self.now.strftime(loop.options['reprtimefmt']).lower()),
            s2or3(self.now.strftime("%a %b %d %Z")))
        nowfmt = leadingzero.sub("", nowfmt)

        print(self.now)
        # self.bell()
        self.currentTime.set("{0}".format(nowfmt))
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
        win.minsize(400, 400)
        f = Frame(win)
        t = Text(f, wrap="word", padx=2, pady=2, bd=2, relief="sunken", font=tkFont.Font(family="Lucida Sans Typewriter"), height=20, width=52, takefocus=False)
        t.insert("0.0", prompt)
        t.pack(side='left', fill=tkinter.BOTH, expand=1, padx=0, pady=0)
        ysb = ttk.Scrollbar(f, orient='vertical', command=t.yview, width=8)
        ysb.pack(side='right', fill=tkinter.Y, expand=1, padx=0, pady=0)
        t.configure(state="disabled", yscroll=ysb.set)
        f.pack(padx=2, pady=2, fill=tkinter.BOTH, expand=1)

        b = Button(win, text=_('OK'), width=10, command=win.destroy, default='active')
        b.pack(side='bottom', pady=0)
        win.bind('<Return>', (lambda e, b=b: b.invoke()))
        win.bind('<Escape>', (lambda e, b=b: b.invoke()))
        win.focus_set()
        win.grab_set()
        win.transient(self)
        win.wait_window(win)

    def editWhich(self, instance="xyz"):
        prompt = "\n".join([
            _("You have selected instance"),
            "    {0}".format(instance),
            _("of a repeating item. What do you want to do?"),
            "  1. {0}".format(_("change the datetime of this instance")),
            "  2. {0}".format(_("edit this instance")),
            "  3. {0}".format(_("edit this and all subsequent instances")),
            "  4. {0}".format(_("edit all instances")),
            "{0}".format(_('Choice [1-4]?'))])
        value = GetInteger(parent=self, title='which instance', prompt=prompt, minvalue=1, maxvalue=4).value
        print('got integer result', value)

    def jumpToDate(self, event=None):
        if not self.dayview:
            return()
        prompt = _("""\
Return an empty string for the current date or a date to be parsed.
Relative dates and fuzzy parsing are supported.""")
        value = GetDateTime(parent=self, title='date', prompt=prompt).value
        self.scrollToDate(value.date())
        # return("break")

    def gettext(self, event=None):
        s = self.e.get()
        if s is not None:
            return(s)
        else:
            return('')

    def cleartext(self, event=None):
        self.e.delete(0, END)
        self.showView()
        return('break')

    def process_input(self, event=None, cmd=None):
        """
        This is called whenever enter is pressed in the input field.
        Action depends upon comand_mode.
        Append input to history, process it and show the result in output.
        """
        # if not cmd:
        #     cmd = self.e.get().strip()

        if not cmd:
            return(True)

        if self.mode == 'command':
            self.dayview = False
            cmd = cmd.strip()
            if cmd[0] == 'w':
                self.editWhich()
                return()
            elif cmd[0] == 's':
                self.dayview = True
            elif cmd[0] in ['r', 't']:
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
            # MessageWindow(self, 'info', res)
            self.deleteItems()
            return()

        if type(res) == dict:
            self.showTree(res)
        else:
            # not a hash => not a tree
            self.messageWindow(title='etm', prompt=res)
            return(0)

    def scrollToDate(self, date):
        # only makes sense for dayview
        if not self.dayview or date not in loop.prevnext:
            return()
        active_date = loop.prevnext[date][1]
        if active_date not in self.date2id:
            return()
        id = self.date2id[active_date]
        self.scrollToId(id)

    def scrollToId(self, id):
        self.update_idletasks()
        self.tree.focus_set()
        self.tree.focus(id)
        self.tree.selection_set(id)
        self.tree.yview(int(id) - 1)
        # self.tree.see(id)

    def showTree(self, tree):
        self.date2id = {}
        self.deleteItems()
        self.count = 0
        self.count2id = {}
        self.addItems(u'', tree[self.root], tree)
        loop.count2id = self.count2id
        self.l.configure(state="normal")
        self.l.delete("0.0", END)
        self.l.configure(state="disabled")
        self.goHome()

    def deleteItems(self):
        """
        Remove all items from the tree
        """
        for child in self.tree.get_children():
            self.tree.delete(child)

    def addItems(self, parent, elements, tree):
        for text in elements:
            self.count += 1
            # print('text', text)
            # text is a key in the element (tree) hash
            # these keys are (parent, item) tuples
            if text in tree:
                # this is a branch
                item = " " + text[1]  # this is the label of the parent
                children = tree[text]  # this are the children tuples of item
                oid = self.tree.insert(parent, 'end', iid=self.count, text=item, open=True)
                # oid = self.tree.insert(parent, 'end', text=item, open=True)
                # print(self.count, oid)
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

                oid = self.tree.insert(parent, 'end', iid=self.count, text=col1, open=True, value=[col2])
                # oid = self.tree.insert(parent, 'end', text=col1, open=True, value=[col2])
                # print(self.count, oid)
                self.count2id[oid] = "{0}::{1}".format(uuid, dt)
                if dt:
                    d = parse(dt[:10]).date()
                    if d not in self.date2id:
                        self.date2id[d] = parent

if __name__ == "__main__":
    # For production:
    etmdir = ''
    # For testing override etmdir:
    # etmdir = '/Users/dag/etm-tk/etm-sample'
    init_localization()
    (user_options, options, use_locale) = data.get_options(etmdir)
    loop = data.ETMCmd(options)
    loop.tkversion = tkversion
    # app = App(path='/Users/dag/etm-tk')
    app = App()
    app.mainloop()
