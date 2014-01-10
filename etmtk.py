#!/usr/bin/env python3
#import the 'tkinter' module
import os
import platform
import sys
if platform.python_version() >= '3':
    import tkinter
    from tkinter import Tk, Entry, END, Label, Toplevel, Button
    from tkinter import messagebox as tkMessageBox
    from tkinter import ttk
    from tkinter import font as tkFont
    # import tkFont
else:
    import Tkinter as tkinter
    from Tkinter import Tk, Entry, END, Label, Toplevel, Button
    import tkMessageBox
    import ttk
    import tkFont

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
    sys_platform, id2Type)

# import tkSimpleDialog


class App(Tk):
    def __init__(self, path=None):
        Tk.__init__(self)
        # print(tkFont.names())
        self.minsize(400, 370)
        self.title("etm tk")
        if sys_platform == 'Linux':
            self.wm_iconbitmap('@'+'etmlogo-4.xbm')
        # self.wm_iconbitmap('etmlogo-4.xbm')
        # self.call('wm', 'iconbitmap', self._w, '/Users/dag/etm-tk/etmlogo_128x128x32.ico')
            # self.iconbitmap(ICON_PATH)
        self.columnconfigure(0, minsize=300, weight=1)
        # self.columnconfigure(1, minsize=50, weight=0)
        # self.columnconfigure(2, minsize=10, weight=0)

        self.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(self, show='tree', columns=["#1", "#2"], selectmode='browse')
        self.tree.column("#0", minwidth=200, width=300, stretch=1)
        self.tree.column("#1", minwidth=80, width=140, stretch=0, anchor="center")
        self.tree.column("#2", minwidth=30, width=40, stretch=0, anchor="e")
        self.date2id = {}

        # abspath = os.path.abspath(path)
        # root_node = self.tree.insert(u'', 'end', text=abspath, open=True)
        self.root = (u'', u'_')

        self.e = Entry(self, text='?')

        self.e.bind('<Return>', self.process_input)
        self.e.bind('<Escape>', self.cleartext)

        self.showTree(loop.do_a(''))

        self.tree.grid(row=0, column=0, sticky='nsew')
        self.e.grid(row=1, column=0, sticky='ew')

        self.grid()
        self.history = []
        self.index = 0
        self.count = 0
        self.count2id = {}
        self.now = None
        self.options = {}
        self.popup = ''
        self.value = ''
        self.firsttime = True
        self.mode = 'command'   # or edit or delete
        self.item_hsh = {}
        self.e.focus_set()
        self.lift()

    def messageWindow(self, title, message):
        win = Toplevel()
        # win = Toplevel(self)
        win.title(title)
        # Label(win, text=message, width=50, wraplength=350, justify='left', font=tkFont.Font(family='TkFixedFont')).pack()
        # Label(win, text=message, width=50, wraplength=350, justify='left', font=('TkFixedFont', 13)).pack()
        Label(win, text=message, width=54, wraplength=400, justify='left', font=tkFont.Font(family="Lucida Sans Typewriter"), fg="darkblue").pack(fill=tkinter.BOTH, expand=1)
        b = Button(win, text='Ok', command=win.destroy, default='active')
        b.pack()
        # b.focus_set()
        win.bind('<Return>', (lambda e, b=b: b.invoke()))
        win.bind('<Escape>', (lambda e, b=b: b.invoke()))
        win.focus_set()
        win.grab_set()
        win.transient(self)
        # win.wait_window(self)
        win.wait_window(win)


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
            if cmd[0] in ['a', 'r', 't']:
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
            return(True)
        if type(res) == dict:
            self.showTree(res)
        else:
            self.messageWindow(title='etm', message=res)
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
                self.addItems(oid, children, tree)
            else:
                # this is a leaf
                self.count += 1
                if len(text[1]) == 4:
                    uuid, item_type, col1, col2 = text[1]
                    dt = ''
                else:  # len 5 day view with datetime appended
                    uuid, item_type, col1, col2, dt = text[1]

                col1 = "{0} {1}     ".format(id2Type[item_type], col1)
                # col1 = "{0}  [{1}] {2}".format(id2Type[item_type], self.count, col1)

                if type(col2) == int:
                    col2 = '%s' % col2

                oid = self.tree.insert(parent, 'end', text=col1, open=True, value=[col2, self.count])
                self.count2id[self.count] = "{0}::{1}".format(uuid, dt)
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
