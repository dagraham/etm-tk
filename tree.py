import os
from Tkinter import *
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

# import os
# import Tkinter as tk
# import ttk


# class App(tk.Frame):
#     def __init__(self, master, path):
#         tk.Frame.__init__(self, master)
#         self.tree = ttk.Treeview(self)
#         ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
#         xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
#         self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
#         self.tree.heading('#0', text='Path', anchor='w')

#         abspath = os.path.abspath(path)
#         root_node = self.tree.insert('', 'end', text=abspath, open=True)
#         self.process_directory(root_node, abspath)

#         self.tree.grid(row=0, column=0)
#         ysb.grid(row=0, column=1, sticky='ns')
#         xsb.grid(row=1, column=0, sticky='ew')
#         self.grid()

#     def process_directory(self, parent, path):
#         for p in os.listdir(path):
#             abspath = os.path.join(path, p)
#             isdir = os.path.isdir(abspath)
#             oid = self.tree.insert(parent, 'end', text=p, open=False)
#             if isdir:
#                 self.process_directory(oid, abspath)

# root = tk.Tk()
# path_to_my_project = # ...
# app = App(root, path=path_to_my_project)
# app.mainloop()