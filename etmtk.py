#!/usr/bin/env python3
#import the 'tkinter' module
import os
import platform
if platform.python_version() >= '3':
    import tkinter
    from tkinter import Tk
else:
    import Tkinter as tkinter
    from Tkinter import Tk
# import Tkinter as tkinter

import ttk


class App(Tk):
    def __init__(self, path):
        Tk.__init__(self)
        self.minsize(500,400)
        self.title("etm")
        self.columnconfigure(0, minsize=300, weight=1)
        # self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(self, show='tree', columns="#1")
        self.tree.column("#0", stretch=1)
        self.tree.column("#1", stretch=0, anchor="center")
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)

        abspath = os.path.abspath(path)
        root_node = self.tree.insert('', 'end', text=abspath, open=True)
        self.process_directory(root_node, abspath)

        self.tree.grid(row=0, column=0, sticky='nsew')
        ysb.grid(row=0, column=1, sticky='ns')

        self.grid()

    def process_directory(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            if os.path.isfile(abspath):
                oid = self.tree.insert(parent, 'end', text=p, open=False, value=[os.path.getsize(abspath)])
            else:
                oid = self.tree.insert(parent, 'end', text=p, open=False)
            if isdir:
                self.process_directory(oid, abspath)

app = App(path='/Users/dag/etm-qt')
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
