# -*- coding: utf-8 -*-

# A simple setup script to create an executable using Tkinter. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# SimpleTkApp.py is a very simple type of Tkinter application
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

import sys
from cx_Freeze import setup, Executable
from etmTk.v import version

import platform
if platform.python_version() >= '3':
    import tkinter
    from tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, Text, PanedWindow, OptionMenu, StringVar, IntVar, Menu, BooleanVar, ACTIVE, Radiobutton, W
    # from tkinter import messagebox as tkMessageBox
    from tkinter import ttk
    from tkinter import font as tkFont
    from tkinter.messagebox import askokcancel
    from tkinter.filedialog import askopenfilename
    # from tkinter import simpledialog as tkSimpleDialog
    # import tkFont
else:
    import Tkinter as tkinter
    from Tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, Text, PanedWindow, OptionMenu, StringVar, IntVar, Menu, BooleanVar, ACTIVE, Radiobutton, W
    # import tkMessageBox
    import ttk
    import tkFont
    from tkMessageBox import askokcancel
    from tkFileDialog import askopenfilename
    # import tkSimpleDialog


BASE = None
if sys.platform == 'win32':
    BASE = 'Win32GUI'

EXECUTABLES = [
    Executable('etm', base=BASE)
]

OPTIONS = {
    'build': {'build_exe': 'releases/etmtk-{0}'.format(version)},
    'build_exe': {'icon':'etmTk/etmlogo.icns', 'optimize':'2', 'compressed': 1},
    'build_mac': {'iconfile':'etmTk/etmlogo.icns', 'bundle_name':'etm'},
    'Executable': {'targetDir':'releases/etmtk-{0}'.format(version)}
}

setup(name='etm',
    version=version,
    executables=EXECUTABLES,
    options=OPTIONS,
    url='http://people.duke.edu/~dgraham/etmtk',
    description='event and task manager',
    long_description='manage events and tasks using simple text files',
    platforms='Any',
    license='License :: OSI Approved :: GNU General Public License (GPL)',
    author='Daniel A Graham',
    author_email='daniel.graham@duke.edu',
      )
