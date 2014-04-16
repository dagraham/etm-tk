#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import logging.config
import uuid

logger = logging.getLogger()

import platform

if platform.python_version() >= '3':
    import tkinter
    from tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, Text, PanedWindow, OptionMenu, StringVar, IntVar, Menu, BooleanVar, ACTIVE, Radiobutton, Checkbutton, W, X, LabelFrame, Canvas, CURRENT, TclError
    from tkinter import ttk
    from tkinter import font as tkFont
    from tkinter.messagebox import askokcancel
    from tkinter.filedialog import askopenfilename
    utf8 = lambda x: x
    # from tkinter import simpledialog as tkSimpleDialog
else:
    import Tkinter as tkinter
    from Tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, Text, PanedWindow, OptionMenu, StringVar, IntVar, Menu, BooleanVar, ACTIVE, Radiobutton, Checkbutton, W, X, LabelFrame, Canvas, CURRENT, TclError
    # import tkMessageBox
    import ttk
    import tkFont
    from tkMessageBox import askokcancel
    from tkFileDialog import askopenfilename
    # import tkSimpleDialog
    def utf8(s):
        return s

# from idlelib.WidgetRedirector import WidgetRedirector

from datetime import datetime, timedelta

from collections import OrderedDict

from etmTk.data import fmt_period, parse_dt, get_current_time

import gettext

_ = gettext.gettext

def sanitize_id(id):
    return id.strip().replace(" ", "")

(_ADD, _DELETE, _INSERT) = range(3)
(_ROOT, _DEPTH, _WIDTH) = range(3)


ONEMINUTE = timedelta(minutes=1)
ONEHOUR = timedelta(hours=1)

ONEDAY = timedelta(days=1)
ONEWEEK = timedelta(weeks=1)

STOPPED = _('stopped')
PAUSED = _('paused')
RUNNING = _('running')

FOUND = "found"

BGCOLOR = "#ebebeb"

class OriginalCommand:

    def __init__(self, redir, operation):
        self.redir = redir
        self.operation = operation
        self.tk = redir.tk
        self.orig = redir.orig
        self.tk_call = self.tk.call
        self.orig_and_operation = (self.orig, self.operation)

    def __repr__(self):
        return "OriginalCommand(%r, %r)" % (self.redir, self.operation)

    def __call__(self, *args):
        return self.tk_call(self.orig_and_operation + args)

########################################################
# WidgetRedirector and OriginalCommand are from idlelib
########################################################

class WidgetRedirector:

    """Support for redirecting arbitrary widget subcommands.

    Some Tk operations don't normally pass through Tkinter.  For example, if a
    character is inserted into a Text widget by pressing a key, a default Tk
    binding to the widget's 'insert' operation is activated, and the Tk library
    processes the insert without calling back into Tkinter.

    Although a binding to <Key> could be made via Tkinter, what we really want
    to do is to hook the Tk 'insert' operation itself.

    When a widget is instantiated, a Tcl command is created whose name is the
    same as the pathname widget._w.  This command is used to invoke the various
    widget operations, e.g. insert (for a Text widget). We are going to hook
    this command and provide a facility ('register') to intercept the widget
    operation.

    In IDLE, the function being registered provides access to the top of a
    Percolator chain.  At the bottom of the chain is a call to the original
    Tk widget operation.

    """
    def __init__(self, widget):
        self._operations = {}
        self.widget = widget            # widget instance
        self.tk = tk = widget.tk        # widget's root
        w = widget._w                   # widget's (full) Tk pathname
        self.orig = w + "_orig"
        # Rename the Tcl command within Tcl:
        tk.call("rename", w, self.orig)
        # Create a new Tcl command whose name is the widget's pathname, and
        # whose action is to dispatch on the operation passed to the widget:
        tk.createcommand(w, self.dispatch)

    def __repr__(self):
        return "WidgetRedirector(%s<%s>)" % (self.widget.__class__.__name__,
                                             self.widget._w)

    def close(self):
        for operation in list(self._operations):
            self.unregister(operation)
        widget = self.widget; del self.widget
        orig = self.orig; del self.orig
        tk = widget.tk
        w = widget._w
        tk.deletecommand(w)
        # restore the original widget Tcl command:
        tk.call("rename", orig, w)

    def register(self, operation, function):
        self._operations[operation] = function
        setattr(self.widget, operation, function)
        return OriginalCommand(self, operation)

    def unregister(self, operation):
        if operation in self._operations:
            function = self._operations[operation]
            del self._operations[operation]
            if hasattr(self.widget, operation):
                delattr(self.widget, operation)
            return function
        else:
            return None

    def dispatch(self, operation, *args):
        '''Callback from Tcl which runs when the widget is referenced.

        If an operation has been registered in self._operations, apply the
        associated function to the args passed into Tcl. Otherwise, pass the
        operation through to Tk via the original Tcl function.

        Note that if a registered function is called, the operation is not
        passed through to Tk.  Apply the function returned by self.register()
        to *args to accomplish that.  For an example, see ColorDelegator.py.

        '''
        m = self._operations.get(operation)
        try:
            if m:
                return m(*args)
            else:
                return self.tk.call((self.orig, operation) + args)
        except TclError:
            return ""

class Node:

    def __init__(self, name, identifier=None, expanded=True):
        self.__identifier = (str(uuid.uuid1()) if identifier is None else
                sanitize_id(str(identifier)))
        self.name = name
        self.expanded = expanded
        self.__bpointer = None
        self.__fpointer = []

    @property
    def identifier(self):
        return self.__identifier

    @property
    def fpointer(self):
        return self.__fpointer

    def update_fpointer(self, identifier, mode=_ADD):
        if mode is _ADD:
            self.__fpointer.append(sanitize_id(identifier))
        elif mode is _DELETE:
            self.__fpointer.remove(sanitize_id(identifier))
        elif mode is _INSERT:
            self.__fpointer = [sanitize_id(identifier)]

class MenuTree:

    def __init__(self):
        self.nodes = []
        self.lst = []

    def get_index(self, position):
        for index, node in enumerate(self.nodes):
            if node.identifier == position:
                break
        return index

    def create_node(self, name, identifier=None, parent=None):
        # logger.debug("name: {0}, identifier: {1}; parent: {2}".format(name, identifier, parent))

        node = Node(name, identifier)
        self.nodes.append(node)
        self.__update_fpointer(parent, node.identifier, _ADD)
        node.bpointer = parent
        return node

    def showMenu(self, position, level=_ROOT):
        queue = self[position].fpointer
        if level == _ROOT:
            self.lst = ["Note: Most dialogs can be closed by pressing Escape.", ""]
        else:
            name, key = self[position].name.split("::")
            name = "{0}{1}".format("    "*(level-1), name.strip())
            s = "{0:<49} {1:^11}".format(name, key.strip())
            self.lst.append(s)
            logger.debug("position: {0}, level: {1}, name: {2}, key: {3}".format(position, level, name, key))
        if self[position].expanded:
            level += 1
            for element in queue:
                self.showMenu(element, level)  # recursive call
        return "\n".join(self.lst)

    def __update_fpointer(self, position, identifier, mode):
        if position is None:
            return
        else:
            self[position].update_fpointer(identifier, mode)

    def __getitem__(self, key):
        return self.nodes[self.get_index(key)]


class Timer():
    def __init__(self, parent=None):
        """
            Methods providing the action timer
        """
        self.timer_clear()
        self.parent = parent
        # self.starttime = datetime.now()

    def timer_clear(self):
        self.timer_delta = 0 * ONEMINUTE
        self.timer_active = False
        self.timer_status = STOPPED
        self.stop_status = STOPPED
        self.timer_last = None
        self.timer_hsh = None
        self.timer_summary = None

    def timer_start(self, hsh=None, toggle=True):
        if not hsh: hsh = {}
        self.starttime = datetime.now()
        self.timer_hsh = hsh
        text = hsh['_summary']
        # self.timer_hsh['s'] = self.starttime
        if 'e' in hsh:
            self.timer_delta = hsh['e']
        if len(text) > 16:
            self.timer_summary = "{0}~".format(text[:15])
        else:
            self.timer_summary = text
        if toggle:
            self.timer_toggle(self.timer_hsh)
        else:
            self.timer_status = self.stop_status

    def timer_stop(self, create=True):
        if self.timer_status == STOPPED:
            return ()
        self.stop_status = self.timer_status
        if self.timer_status == RUNNING:
            self.timer_delta += datetime.now() - self.timer_last
            self.timer_status = PAUSED

        self.timer_delta = max(self.timer_delta, ONEMINUTE)
        self.timer_hsh['e'] = self.timer_delta
        self.timer_hsh['s'] = self.starttime
        self.timer_hsh['itemtype'] = '~'

    def timer_toggle(self, hsh=None):
        if not hsh: hsh = {}
        if self.timer_status == STOPPED:
            self.get_time()
            self.timer_last = datetime.now()
            self.timer_status = RUNNING
        elif self.timer_status == RUNNING:
            self.timer_delta += datetime.now() - self.timer_last
            self.timer_status = PAUSED
        elif self.timer_status == PAUSED:
            self.timer_status = RUNNING
            self.timer_last = datetime.now()
        if self.parent:
            self.parent.update_idletasks()


    def get_time(self):
        if self.timer_status == PAUSED:
            elapsed_time = self.timer_delta
        elif self.timer_status == RUNNING:
            elapsed_time = (self.timer_delta + datetime.now() -
                       self.timer_last)
        else:
            elapsed_time = self.timer_delta
        plus = " ({0})".format(_("paused"))
        self.timer_minutes = elapsed_time.seconds//60
        if self.timer_status == RUNNING:
            plus = " ({0})".format(_("running"))
        # ret = "{0}  {1}{2}".format(self.timer_summary, self.timer_time, s)
        ret = "{0}  {1}{2}".format(self.timer_summary, fmt_period(elapsed_time), plus)
        logger.debug("timer: {0}; {1}; {2}".format(ret, self.timer_last, elapsed_time))
        return ret


class ReadOnlyText(Text):
    # noinspection PyShadowingNames
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.redirector = WidgetRedirector(self)
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")
        self.configure(highlightthickness=0, wrap="word")


class MessageWindow():
    # noinspection PyShadowingNames
    def __init__(self, parent, title, prompt):
        self.win = Toplevel(parent)
        self.win.protocol("WM_DELETE_WINDOW", self.cancel)
        self.parent = parent
        self.win.title(title)
        Label(self.win, text=prompt).pack(fill=tkinter.BOTH, expand=1, padx=10, pady=10)
        b = Button(self.win, text=_('OK'), width=10, command=self.cancel,
                   default='active')
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


class Dialog(Toplevel):

    def __init__(self, parent, title=None, prompt=None, opts=None, default=None, modal=True, xoffset=50, yoffset=50, event=None):

        Toplevel.__init__(self, parent, highlightbackground=BGCOLOR,
                    background=BGCOLOR)
        self.protocol("WM_DELETE_WINDOW", self.quit)
        if modal:
            logger.debug('modal')
            self.transient(parent)
        else:
            logger.debug('non modal')

        if title:
            self.title(title)

        self.parent = parent

        self.event = event
        logger.debug("parent: {0}".format(self.parent))
        self.prompt = prompt
        self.options = opts
        self.default = default
        self.value = ""

        self.error_message = None

        # self.buttonbox()

        body = Frame(self, highlightbackground=BGCOLOR, background=BGCOLOR)
        # self.initial_focus = self.body(body)
        self.body(body).focus_set()

        self.buttonbox()
        # don't expand body or it will fill below the actual content
        body.pack(side="top", fill=tkinter.BOTH, padx=0, pady=0, expand=1)


        self.protocol("WM_DELETE_WINDOW", self.quit)

        if parent:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + xoffset,
                                  parent.winfo_rooty() + yoffset))

        if modal:
            self.grab_set()
            self.wait_window(self)
        # return "break"

    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self, background=BGCOLOR, highlightbackground=BGCOLOR)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE,  highlightbackground=BGCOLOR)
        w.pack(side="right", padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel, highlightbackground=BGCOLOR)
        w.pack(side="right", padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack(side='bottom')

    # standard button semantics

    def ok(self, event=None):
        res = self.validate()
        logger.debug('validate: {0}, value: "{1}"'.format(res, self.value))
        if not res:
            if self.error_message:
                self.messageWindow('error', self.error_message)

            # self.initial_focus.focus_set()  # put focus back
            return "break"

        self.withdraw()
        self.update_idletasks()

        self.apply()
        self.quit()

    def cancel(self, event=None):
        # return the focus to the tree view in the main window
        self.value = None
        logger.debug('value: "{0}"'.format(self.value))
        self.quit()

    def quit(self, event=None):
        if self.parent:
            logger.debug("returning focus to parent: {0}".format(self.parent))
            self.parent.focus()
            # self.parent.tree.focus_set()
            if self.parent.weekly:
                self.parent.canvas.focus_set()
            else:
                self.parent.tree.focus_set()
        else:
            logger.debug("returning focus, no parent")
        self.destroy()
        # return "break"

    # command hooks

    def validate(self):

        return 1 # override

    def apply(self):

        pass # override

    def messageWindow(self, title, prompt):
        MessageWindow(self.parent, title, prompt)

class HelpWindow(Dialog):

    def body(self, master):
        PADY = 2

        toolbar = Frame(self, highlightbackground=BGCOLOR, background=BGCOLOR)
        # self.options = list of label, content pairs
        self.vm_dict = OrderedDict(self.options['help_opts'])
        vm_labels = [x[0] for x in self.options['help_opts']]
        self.view = StringVar(self)

        self.vm = vm = OptionMenu(toolbar, self.view, *vm_labels, command=self.showHelp)
        vm.configure(width=10, height=1, highlightbackground=BGCOLOR, background=BGCOLOR, pady=PADY)
        vm.pack(side="left", pady=0, padx=6)
        self.view.set(vm_labels[0])

        # find
        Button(toolbar, text='x', command=self.clearFind, highlightbackground=BGCOLOR, pady=PADY).pack(side=LEFT, padx=0)
        self.find_text = StringVar(toolbar)
        self.e = Entry(toolbar, textvariable=self.find_text, width=16, highlightbackground=BGCOLOR)
        self.e.pack(side=LEFT, padx=0)
        self.e.bind("<Return>", self.onFind)
        Button(toolbar, text='>', command=self.onFind, highlightbackground=BGCOLOR, pady=PADY).pack(side=LEFT, padx=0)

        Button(toolbar, text=_("OK"), highlightbackground=BGCOLOR, pady=PADY, command=self.cancel).pack(side="right", padx=6)
        # self.bind("<Escape>", self.quit)
        self.bind("<Escape>", self.cancel)

        toolbar.pack(side="top", padx=6, pady=0, expand="no", fill="x")

        textwindow = Frame(self, highlightbackground=BGCOLOR, background=BGCOLOR)

        text = ReadOnlyText(textwindow, bd=2, relief="sunken", padx=3, pady=2,
                            # font=self.tkfixedfont,
                            width=70)
        text.configure(highlightthickness=0)
        text.tag_configure(FOUND, background="lightskyblue")

        text.pack(side="top", padx=4, pady=4,
                  expand=1, fill="both"
        )
        self.text = text
        textwindow.pack(side="top",
                        expand=1, fill="both"
        )
        self.showHelp()
        return self.vm

    def showHelp(self, e=None):
        label = self.view.get()
        self.text.delete("1.0", END)
        self.text.insert("1.0", self.vm_dict[label])
        logger.debug("label: {0}".format(label))

    def clearFind(self, *args):
        self.text.tag_remove(FOUND, "0.0", END)
        self.find_text.set("")

    def onFind(self, *args):
        target = self.find_text.get()
        logger.debug('target {0}: {1}'.format(target, self.text))
        if target:
            where = self.text.search(target, INSERT, nocase=1)
            if where:
                pastit = where + ('+%dc' % len(target))
                logger.debug('pastit: {0}'.format(pastit))
                # self.text.tag_remove(SEL, '1.0', END)
                self.text.tag_add(FOUND, where, pastit)
                self.text.mark_set(INSERT, pastit)
                self.text.see(INSERT)
                self.text.focus()

    def buttonbox(self):
        box = Frame(self, background=BGCOLOR, highlightbackground=BGCOLOR)
        box.pack(side='bottom', fill=X, expand=0)

class TextVariableWindow(Dialog):
    def body(self, master):
        if 'textvariable' not in self.options:
            return
        self.entry = entry = Entry(master, textvariable=self.options['textvariable'])
        self.entry.pack(side="bottom", padx=5, pady=5)
        Label(master, text=self.prompt, justify='left', highlightbackground=BGCOLOR, background=BGCOLOR).pack(side="top", fill=tkinter.BOTH, expand=1, padx=10, pady=5)
        self.entry.focus_set()
        self.entry.bind('<Escape>', self.entry.delete(0, END))
        return self.entry

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self, highlightbackground=BGCOLOR, background=BGCOLOR)

        w = Button(box, text=CLOSE, width=10, command=self.ok,
                   default=ACTIVE, highlightbackground=BGCOLOR)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)
        box.pack(side='bottom')

    # def apply(self, e=None):
    #     logger.debug("got here")
    #     self.options['textvariable'].set("")
    #     self.entry.delete(0, END)
    #     self.parent.goHome()

    def quit(self, event=None):
        if self.parent:
            logger.debug("returning focus to parent: {0}".format(self.parent))
            self.parent.focus()
            # self.parent.tree.focus_set()
            self.parent.focus_set()
            # self.parent.focus_set()
        else:
            logger.debug("returning focus, no parent")
        self.entry.delete(0, END)
        self.options['textvariable'].set("")
        self.destroy()

class DialogWindow(Dialog):
    # master will be a frame in Dialog
    # noinspection PyAttributeOutsideInit
    def body(self, master):
        self.entry = Entry(master)
        self.entry.pack(side="bottom", padx=5, pady=5)
        Label(master, text=self.prompt, justify='left', highlightbackground=BGCOLOR, background=BGCOLOR).pack(side="top", fill=tkinter.BOTH, expand=1, padx=10, pady=5)
        if self.default is not None:
            self.entry.insert(0, self.default)
            self.entry.select_range(0, END)
            # self.entry.pack(padx=5, pady=5)
        return self.entry

class TextDialog(Dialog):

    def body(self, master):
        tkfixedfont = tkFont.nametofont("TkFixedFont")
        tkfixedfont.configure(size=self.options['fontsize'])
        lines = self.prompt.split('\n')
        height = min(25, len(lines) + 1)
        lengths = [len(line) for line in lines]
        width = min(70, max(lengths) + 2)
        self.text = ReadOnlyText(
            master, wrap="word", padx=2, pady=2, bd=2, relief="sunken",
            # font=tkFont.Font(family="Lucida Sans Typewriter"),
            font=tkfixedfont,
            height=height,
            width=width,
            takefocus=False)
        self.text.insert("1.1", self.prompt)
        self.text.pack(side='left', fill=tkinter.BOTH, expand=1, padx=0,
                       pady=0)
        ysb = ttk.Scrollbar(master, orient='vertical', command=self.text
                            .yview)
        ysb.pack(side='right', fill=tkinter.Y, expand=0, padx=0, pady=0)
        # t.configure(state="disabled", yscroll=ysb.set)
        self.text.configure(yscroll=ysb.set)
        return self.text

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self, highlightbackground=BGCOLOR, background=BGCOLOR)

        w = Button(box, text="OK", width=6, command=self.cancel,
                   default=ACTIVE, highlightbackground=BGCOLOR, pady=2)
        w.pack(side=LEFT, padx=5, pady=0)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)

        box.pack(side='bottom')


class OptionsDialog():
    # noinspection PyShadowingNames
    def __init__(self, parent, master=None, title="", prompt="", opts=None, radio=True, yesno=True):
        if not opts: opts = []
        self.win = Toplevel(parent)
        self.win.protocol("WM_DELETE_WINDOW", self.quit)
        if parent:
            self.win.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                  parent.winfo_rooty() + 50))
        self.parent = parent
        self.master = master
        self.options = opts
        self.radio = radio
        self.win.title(title)
        Label(self.win, text=prompt, justify='left').pack(fill=tkinter.BOTH, expand=1, padx=10, pady=5)
        # self.sv = StringVar(parent)
        self.sv = IntVar(parent)
        # self.sv.set(opts[0])
        self.sv.set(1)
        # logger.debug('sv: {0}'.format(self.sv.get()))
        if self.options:
            if radio:
                self.value = opts[0]
                for i in range(min(9, len(self.options))):
                    txt = self.options[i]
                    val = i + 1
                    # bind keyboard numbers 1-9 (at most) to options selection, i.e., press 1
                    # to select option 1, 2 to select 2, etc.
                    self.win.bind(str(val), (lambda e, x=val: self.sv.set(x)))
                    Radiobutton(self.win,
                        text="{0}: {1}".format(val, txt),
                        padx=20,
                        indicatoron=True,
                        variable=self.sv,
                        command=self.getValue,
                        value=val).pack(padx=10, anchor=W)
            else:
                self.check_values = {}
                # show 0, check 1, return 2
                for i in range(min(9, len(self.options))):
                    txt = self.options[i][0]
                    self.check_values[i] = BooleanVar(self.parent)
                    self.check_values[i].set(self.options[i][1])
                    Checkbutton(self.win,
                        text=self.options[i][0],
                        padx=20,
                        variable=self.check_values[i]).pack(padx=10, anchor=W)
        box = Frame(self.win)
        if yesno:
            YES = _("Yes")
            NO = _("No")
        else:
            YES = _("Ok")
            NO = _("Cancel")
        c = Button(box, text=NO, width=10, command=self.cancel)
        c.pack(side=LEFT, padx=5, pady=5)
        o = Button(box, text=YES, width=10, default='active', command=self.ok)
        o.pack(side=LEFT, padx=5, pady=5)
        box.pack()
        self.win.bind('<Return>', (lambda e, o=o: o.invoke()))
        self.win.bind('<Escape>', (lambda e, c=c: c.invoke()))
        # self.choice.focus_set()
        self.win.focus_set()
        self.win.grab_set()
        # self.choice.focus()
        self.win.transient(parent)
        self.win.wait_window(self.win)

    def getValue(self, e=None):
        v = self.sv.get()
        logger.debug("sv: {0}".format(v))
        if self.options:
            if self.radio:
                if v-1 in range(len(self.options)):
                    o = self.options[v-1]
                    logger.debug(
                        'OptionsDialog returning {0}: {1}'.format(v, o))
                    return v, o
                    # return o, v
                else:
                    logger.debug(
                        'OptionsDialog returning {0}: {1}'.format(v,  None))
                    return 0, None
            else: # checkbutton
                values = []
                for i in range(len(self.options)):
                    bool = self.check_values[i].get() > 0
                    values.append([self.options[i][0], bool, self.options[i][2]])
                return values
        else: # askokcancel type dialog
            logger.debug(
                'OptionsDialog returning {0}: {1}'.format(v, None))
            return v, None

    def ok(self, event=None):
        # self.parent.update_idletasks()
        self.quit()

    def cancel(self, event=None):
        self.sv.set(0)
        self.quit()

    def quit(self, event=None):
        # put focus back to the parent window
        if self.master:
            self.master.focus_set()
        elif self.parent:
            self.parent.focus_set()
        self.win.destroy()


class GetInteger(DialogWindow):
    def validate(self):
        minvalue = maxvalue = None
        if len(self.options) > 0:
            minvalue = self.options[0]
            if len(self.options) > 1:
                maxvalue = self.options[1]
        res = self.entry.get()
        try:
            val = int(res)
            ok = (minvalue is None or val >= minvalue) and (
                maxvalue is None or val <= maxvalue)
        except:
            val = None
            ok = False

        if ok:
            self.value = val
            return True
        else:
            self.value = None
            msg = [_('an integer')]
            conj = ""
            if minvalue is not None:
                msg.append(_("no less than {0}".format(minvalue)))
                conj = _("and ")
            if maxvalue is not None:
                msg.append(_("{0}no greater than {0}").format(conj, maxvalue))
            msg.append(_("is required"))
            self.error_message = "\n".join(msg)
            return False


class GetDateTime(DialogWindow):
    def validate(self):
        res = self.entry.get()
        logger.debug('res: {0}'.format(res))
        ok = False
        if not res.strip():
            # return the current time if ok is pressed with no entry
            val = get_current_time()
            ok = True
        else:
            try:
                # val = parse(parse_datetime(res))
                val = parse_dt(res)
                ok = True
            except:
                val = None
        if ok:
            self.value = val
            return True
        else:
            self.value = False
            self.error_message = _('could not parse "{0}"').format(res)
            return False


class GetString(DialogWindow):
    def validate(self):
        nullok = False
        if 'nullok' in self.options and self.options['nullok']:
            nullok = True
            # an entry is required
        val = self.entry.get()
        ok = False
        if val.strip():
            self.value = val
            return True
        elif nullok:  # null and null is ok
            if self.value is None:
                return False
            else:
                self.value = val
                return True
        else:
            self.error_message = _('an entry is required')
            return False
