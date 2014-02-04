import platform, sys

if platform.python_version() >= '3':
    import tkinter
    from tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, RIGHT, Text, PanedWindow, OptionMenu, StringVar, Menu, BooleanVar, ACTIVE, X, RIDGE, BOTH, SEL, SEL_FIRST, SEL_LAST
    from tkinter import ttk
    from tkinter import font as tkFont
    from tkinter import simpledialog as tkSimpleDialog
    from tkinter.simpledialog import askstring
    from tkinter.messagebox import askokcancel
    from tkinter.filedialog import asksaveasfilename
    from tkinter.filedialog import askopenfilename
else:
    import Tkinter as tkinter
    from Tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, RIGHT, Text, PanedWindow, OptionMenu, StringVar, Menu, BooleanVar, ACTIVE, X, RIDGE, BOTH, SEL, SEL_FIRST, SEL_LAST
    import ttk
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

import logging
import logging.config
logger = logging.getLogger()
from data import setup_logging


import gettext
_ = gettext.gettext

from data import hsh2str, str2hsh, get_reps, checkhsh

# class MessageWindow():
#     # noinspection PyShadowingNames
#     def __init__(self, parent, title, prompt):
#         self.win = Toplevel(parent)
#         self.parent = parent
#         self.win.title(title)
#         Label(self.win, text=prompt).pack(fill=tkinter.BOTH, expand=1, padx=10, pady=10)
#         b = Button(self.win, text=_('OK'), width=10, command=self.cancel,
#                    default='active')
#         b.pack()
#         self.win.bind('<Return>', (lambda e, b=b: b.invoke()))
#         self.win.bind('<Escape>', (lambda e, b=b: b.invoke()))
#         self.win.focus_set()
#         self.win.grab_set()
#         self.win.transient(parent)
#         self.win.wait_window(self.win)
#         return
#
#     def cancel(self, event=None):
#         # put focus back to the parent window
#         self.parent.focus_set()
#         self.win.destroy()

from idlelib.WidgetRedirector import WidgetRedirector

class ReadOnlyText(Text):
    # noinspection PyShadowingNames
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")


class ScrolledText(Frame):

    def __init__(self, parent=None, text='', file=None):
        Frame.__init__(self, parent, bd=2, relief=RIDGE)
        self.pack(expand=1, padx=0, pady=0, fill=BOTH)
        self.text = None
        self.makewidgets()
        # self.text_value = StringVar(self)
        # self.text_value.trace_variable("w", self.setSaveStatus)
        self.settext(text, file)
        self.text.focus()

    def makewidgets(self):
        # sbar = Scrollbar(self)
        text = Text(self, bd=0, padx=3, pady=2, font=tkFont.Font(family="Lucida Sans Typewriter"), undo=True, width=70)

        text.pack(side=LEFT, padx=0, pady=0, expand=1, fill=BOTH)
        self.text = text
        self.text.bind('<<Modified>>', self.updateSaveStatus)

    def settext(self, text='', file=None):
        if file:
            text = open(file, 'r').read()
        self.text.delete('1.0', END)
        self.text.insert('1.0', text)
        self.text.mark_set(INSERT, '1.0')
        # self.text.edit_modified(True)
        self.text.focus()

    def gettext(self):
        return self.text.get('1.0', END + '-1c')

    def setmodified(self, bool):
        if bool is not None:
            self.text.edit_modified(bool)
            self.updateSaveStatus()

    def checkmodified(self):
        return self.text.edit_modified()

    def updateSaveStatus(self, event=None):
        # we will override this in SimpleEditor
        pass


class SimpleEditor(ScrolledText):

    def __init__(self, parent=None, file=None, hsh=None):
        """
        If file is given, set file mode and open file for editing.
        If hsh is given we are editing an item. If the item has fileinfo line numbers
        then we will be replacing the item, else it is a copy that we will be
        appending.

        :param parent:
        :param file: path to file to be edited
        :param hsh: hsh of the item to be edited
        """
        self.frm = frm = Frame(parent)
        self.parent = parent
        self.file = file
        self.hsh = hsh
        self.ret_value = ''
        self.options = loop.options
        # self.text_value.trace_variable("w", self.setSaveStatus)
        frm.pack(fill=X, pady=2)
        btnwdth = 5
        Button(frm, text=_('Quit'), width=btnwdth, command=self.quit).pack(side=LEFT, padx=2)
        self.sb = Button(frm, text=_('Save'), width=btnwdth, command=self.onSave)
        self.sb.pack(side=LEFT, padx=2)
        Button(frm, text='X', command=self.clearFind).pack(side=RIGHT, padx=2)
        self.find_text = StringVar(frm)
        e = Entry(frm, textvariable=self.find_text, width=20)
        e.pack(side=RIGHT, padx=2)
        e.bind("<Return>", self.onFind)
        e.bind("<Escape>", self.clearFind)
        Button(frm, text=_('Find'), width=btnwdth, command=self.onFind).pack(side=RIGHT, padx=2)
        if file is not None:
            # we're editing a file
            self.mode = 'file'
            self.st = ScrolledText.__init__(self, parent, file=file)
        else:
            # we are editing an item
            Button(frm, text=_('Check'), width=btnwdth, command=self.onCheck).pack(side=LEFT, padx=2)
            if hsh is not None:
                self.st = ScrolledText.__init__(self, parent, text=hsh2str((hsh)))
                if hsh['fileinfo'][2]:
                    # we have line numbers and are will be replacing an item
                    self.setmodified(False)
                else:
                    # without line numbers we will be appending an item
                    self.setmodified(True)
            else:
                # we will be appending a new item
                self.mode = "newitem"
                self.hsh = {}
                self.st = ScrolledText.__init__(self, parent)
                self.setmodified(False)

    def updateSaveStatus(self, event=None):
        if self.checkmodified():
            logger.debug('normal: "{0}"'.format(self.ret_value))
            self.sb.configure(state='normal')
            # update the return value so that when it is not null then modified
            # is false and when modified is true then it is null
            self.ret_value = ""
        else:
            logger.debug('disabled: "{0}"'.format(self.ret_value))
            self.sb.configure(state='disabled')

    def onSave(self):
        # fixme: sometimes replacing lines, adding lines, overwriting file
        if self.file is not None:
            # handle saving the file here
            alltext = self.gettext()
            open(self.file, 'w').write(alltext)
        elif self.hsh is not None:
            # we will be returning a string version of the edited item
            ok, str = self.onCheck()
            if ok and str:
                self.settext(str)
                # update the return value so that when it is not null then modified
                # is false and when modified is true then it is null
                self.ret_value = str
                self.setmodified(False)

            # # get filename
            # options = {'defaultextension': '.txt',
            #            'filetypes': [('text files', '.txt')],
            #            'initialdir': '~/.etm/data',
            #            'initialfile': "",
            #            'title': 'etmtk data files'}
            # # options['parent'] = self.frm
            # filename = askopenfilename(**options)
            # print(filename)

        # if filename:

    def onCheck(self, event=None):
        text = self.gettext()
        msg = []
        reps = []
        str = ''
        try:
            hsh, msg = str2hsh(text, options=self.options)
            logger.debug("hsh: {0}".format(hsh))
        except Exception as e:
            print('bad', e)
        if msg:
            messages = "messages:\n  {0}".format("\n  ".join(msg))
            logger.debug(messages)
            self.messageWindow('errors', messages)
            return False, ''
        str = hsh2str(hsh, options=self.options)
        logger.debug("str: {0}".format(str))
        self.settext(str)
        if 'r' in hsh:
            ok, reps =  get_reps(self.options['bef'], hsh)
            repsfmt = [x.strftime("%x %X") for x in reps]
            logger.debug("{0}: {1}".format(ok, repsfmt))

            repetitons = "repetitions:\n  {0}".format("\n  ".join(repsfmt))
            self.messageWindow('repetitions', repetitons)
        return True, str

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

    def quit(self):
        if self.checkmodified():
            ans = askokcancel('Verify exit', "Really quit?")
        else:
            ans = True
        if ans:
            Frame.quit(self)

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
    setup_logging(default_level=logging.DEBUG)
    etmdir = ''
    # For testing override etmdir:
    etmdir = '/Users/dag/etm-tk/etm-sample'
    import data
    (user_options, options, use_locale) = data.get_options(etmdir)
    loop = data.ETMCmd(options=options)
    try:
        SimpleEditor(file=sys.argv[1]).mainloop()
    except IndexError:
        SimpleEditor().mainloop()
