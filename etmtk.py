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
        # win = Toplevel(self)
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

        # self.withdraw()
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
        self.minsize(400, 375)
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
        # self.columnconfigure(1, minsize=50, weight=0)
        # self.columnconfigure(2, minsize=10, weight=0)

        self.rowconfigure(1, weight=3)
        self.rowconfigure(2, weight=2)
        self.tree = ttk.Treeview(self, show='tree', columns=["#1"], selectmode='browse')
        self.tree.column("#0", minwidth=200, width=300, stretch=1)
        self.tree.column("#1", minwidth=80, width=140, stretch=0, anchor="center")
        # self.tree.column("#2", minwidth=30, width=40, stretch=0, anchor="e")
        self.tree.bind("<<TreeviewSelect>>", self.OnSelect)
        # self.tree.bind("<Button-1>", self.OnSingleClick)
        self.tree.bind("<Double-1>", self.OnDoubleClick)

        self.date2id = {}

        # abspath = os.path.abspath(path)
        # root_node = self.tree.insert(u'', 'end', text=abspath, open=True)
        self.root = (u'', u'_')

        self.e = Entry(self, text='?')

        self.e.bind('<Return>', self.process_input)
        self.e.bind('<Escape>', self.cleartext)
        self.e.bind('<Up>', self.prev_history)
        self.e.bind('<Down>', self.next_history)
        self.e.grid(row=0, column=0, sticky='ew')

        self.showTree(loop.do_a(''))
        self.tree.grid(row=1, column=0, sticky='nsew')

        # self.l = Label(self, text=text, anchor="nw", wraplength=400, justify='left', bd=5, font=tkFont.Font(family="Lucida Sans Typewriter"), fg="darkblue")
        # self.l = Label(self, textvariable=self.l_text, anchor="nw", justify='left', bd=2, padx=4, pady=4, relief="sunken", width=80)
        # self.l = Text(self, wrap="word", bd=2, relief="sunken", padx=4, pady=4, font=tkFont.Font(family="Lucida Sans"), height=6, width=50)
        self.l = Text(self, wrap="word", bd=2, relief="sunken", padx=4, pady=4, font=tkFont.Font(family="Lucida Sans"), height=6, width=50)
        # self.l.insert(INSERT, text)

        self.l.grid(row=2, column=0, sticky="nesw")
        self.grid()
        self.e.focus_set()
        self.update_clock()
        self.lift()

    def OnSelect(self, event=None):
        item = self.tree.selection()[0]
        instance = self.count2id[item]
        self.l.config(state="normal")
        self.l.delete("0.0", END)
        if instance is not None:
            uuid, dt = self.count2id[item].split("::")
            hsh = loop.uuid2hash[uuid]
            text = hsh['entry']
        else:
            text = ""
        self.l.insert(INSERT, text)
        self.l.config(state="disabled")

       # print("you selected", self.tree.item(item, "text"), item, self.count2id[item])

    # def OnSingleClick(self, event):
    #     # item = self.tree.selection()[0]
    #     item = self.tree.identify('item', event.x, event.y)
    #     print("you clicked on", self.tree.item(item, "text"), self.tree.item(item, "values"), self.tree.item(item), item)

    def OnDoubleClick(self, event):
        # item = self.tree.selection()[0]
        item = self.tree.identify('item', event.x, event.y)
        print("you clicked on", self.tree.item(item, "text"), self.tree.item(item, "values"), self.tree.item(item), item)

    def update_clock(self):
        self.now = get_current_time()
        nxt = (60*1000 - self.now.second*1000 - self.now.microsecond//1000)
        nowfmt = "{0} {1}".format(
            s2or3(self.now.strftime(loop.options['reprtimefmt']).lower()),
            s2or3(self.now.strftime("%a %b %d %Z")))
        nowfmt = leadingzero.sub("", nowfmt)

        print(self.now)
        self.title("{0}".format(nowfmt))
        # self.label.configure(text=now)
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
        # Label(win, text=prompt, width=54, wraplength=400, justify='left', font=tkFont.Font(family="Lucida Sans Typewriter"), fg="darkblue").pack(fill=tkinter.BOTH, expand=1)
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

        # if not cmd:
        #     return(True)

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

        # print('res', type(res), res)

        if not res:
            res = _('command "{0}" returned no output').format(cmd)
        if type(res) == dict:
            self.showTree(res)
        else:
            self.messageWindow(title='etm', prompt=res)
            # d = ETMDialog(self, title='etm', message=ress)
            # self.wait_window(d)
            # tkMessageBox.showinfo('etm', res, icon='info')
            return(0)

    def showTree(self, tree):
        self.deleteItems()
        self.count = 0
        self.count2id = {}
        self.addItems(u'', tree[self.root], tree)
        loop.count2id = self.count2id
        # self.tree.selection_set( 'I001' )
        # self.tree.focus_set()
        # self.tree.focus( 'I001' ) # this fixes a problem.
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
                item = text[1]  # this is the label of the parent
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

                col1 = "{0} ".format(id2Type[item_type]) + col1
                # col1 = "{0}  [{1}] {2}".format(id2Type[item_type], self.count, col1)

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


    # def process_directory(self, parent, path):
    #     for p in os.listdir(path):
    #         print(parent, path, p)
    #         abspath = os.path.join(path, p)
    #         isdir = os.path.isdir(abspath)
    #         if os.path.isfile(abspath):
    #             oid = self.tree.insert(parent, 'end', text=p, open=False, value=[os.path.getsize(abspath)])
    #         else:
    #             oid = self.tree.insert(parent, 'end', text=p, open=False)
    #         if isdir:
    #             self.process_directory(oid, abspath)


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


# #create a new window
# main = tkinter.Tk()
# main.geometry('520x420+100+100')
# main.title('etm')
# content = ttk.Frame(main)
# content['width'] = 520
# content['height'] = 420
# content.grid()
# # window.wm_iconbitmap('etmlogo_512x512x32.ico')
# #draw the window, and start the 'application'
# main.mainloop()
