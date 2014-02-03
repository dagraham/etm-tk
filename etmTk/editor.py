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

# FIXME: remove this when imported by etmtk
# from etmtk import setup_logging
# setup_logging(default_level=logging.DEBUG)

import gettext
_ = gettext.gettext

from data import ensureMonthly

class ScrolledText(Frame):

    def __init__(self, parent=None, text='', file=None):
        Frame.__init__(self, parent, bd=2, relief=RIDGE)
        self.pack(expand=1, padx=0, pady=0, fill=BOTH)
        self.text = None
        self.makewidgets()
        self.text_value = StringVar(self)
        self.settext(text, file)
        self.text.focus()

    def makewidgets(self):
        # sbar = Scrollbar(self)
        text = Text(self, bd=0, padx=3, pady=2, font=tkFont.Font(family="Lucida Sans Typewriter"), undo=True, width=70)

        text.pack(side=LEFT, padx=0, pady=0, expand=1, fill=BOTH)
        self.text = text

    def settext(self, text='', file=None):
        if file:
            text = open(file, 'r').read()
        self.text.delete('1.0', END)
        self.text.insert('1.0', text)
        self.text.mark_set(INSERT, '1.0')
        self.text.edit_modified(False)
        self.text.focus()

    def gettext(self):
        return self.text.get('1.0', END + '-1c')

    def check_modified(self):
        return self.text.edit_modified()


class SimpleEditor(ScrolledText):

    def __init__(self, parent=None, file=None, item=None):
        """
        If file is given, set file mode and open file for editing

        :param parent:
        :param file:
        :param item:
        """
        self.frm = frm = Frame(parent)
        frm.pack(fill=X, pady=2)
        btnwdth = 5
        Button(frm, text=_('Quit'), width=btnwdth, command=self.quit).pack(side=LEFT, padx=2)
        Button(frm, text=_('Save'), width=btnwdth, command=self.onSave).pack(side=LEFT, padx=2)
        Button(frm, text='X', command=self.clearFind).pack(side=RIGHT, padx=2)
        self.find_text = StringVar(frm)
        e = Entry(frm, textvariable=self.find_text, width=20)
        e.pack(side=RIGHT, padx=2)
        e.bind("<Return>", self.onFind)
        e.bind("<Escape>", self.clearFind)
        Button(frm, text=_('Find'), width=btnwdth, command=self.onFind).pack(side=RIGHT, padx=2)
        if file is not None:
            # we're editing a file
            self.file = file
            self.mode = 'oldfile'
            self.item = None
            self.st = ScrolledText.__init__(self, parent, file=file)
        elif item is not None:
            Button(frm, text=_('Check'), width=btnwdth, command=self.onCheck).pack(side=LEFT, padx=2)
            self.item = item
            # we're editing an item hash.
            # item['fileinfo'] = (filename, beginning line num, ending line num)
            # if both beginning and ending line numbers are given, we are editing an existing item
            if item['fileinfo'][2]:
                self.mode = 'edititem'
            # if only a beginning line number is given, this is a clone
            elif item['fileinfo'][1]:
                self.mode = 'editclone'
            # with only a filename, this is a new item
            else:
                self.mode = 'editnew'
        else:
            # new file
            self.mode = "newfile"
            self.st = ScrolledText.__init__(self, parent)


    def onSave(self):
        # fixme: sometimes replacing lines, adding lines, overwriting file
        if self.mode == 'oldfile':
            alltext = self.gettext()
            open(self.file, 'w').write(alltext)
        elif self.mode == 'edititem':
            # replace lines
            pass
        elif self.mode == 'editclone':
            # replace lines
            pass
        elif self.mode == 'editnew':
            # replace lines
            pass
        else:  # clone or new
            # get filename
            options = {'defaultextension': '.txt',
                       'filetypes': [('text files', '.txt')],
                       'initialdir': '~/.etm/data',
                       'initialfile': "",
                       'title': 'etmtk data files'}
            # options['parent'] = self.frm
            filename = askopenfilename(**options)
            print(filename)

        # if filename:

    def onCheck(self):
        text = self.gettext()
        print(text)

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
        if self.check_modified():
            ans = askokcancel('Verify exit', "Really quit?")
        else:
            ans = True
        if ans:
            Frame.quit(self)


if __name__ == '__main__':
    try:
        SimpleEditor(file=sys.argv[1]).mainloop()
    except IndexError:
        SimpleEditor().mainloop()
