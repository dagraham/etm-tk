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
import glob

import platform
plat = platform.uname()[0]
if platform.python_version() >= '3':
    import tkinter
    from tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, Text, PanedWindow, OptionMenu, StringVar, IntVar, Menu, BooleanVar, ACTIVE, Radiobutton, W, X, LabelFrame, Canvas, CURRENT
    from tkinter import ttk
    from tkinter import font as tkFont
    from tkinter.messagebox import askokcancel
    from tkinter.filedialog import askopenfilename
    utf8 = lambda x: x
    # from tkinter import simpledialog as tkSimpleDialog
else:
    import Tkinter as tkinter
    from Tkinter import Tk, Entry, INSERT, END, Label, Toplevel, Button, Frame, LEFT, Text, PanedWindow, OptionMenu, StringVar, IntVar, Menu, BooleanVar, ACTIVE, Radiobutton, W, X, LabelFrame, Canvas, CURRENT
    # import tkMessageBox
    import ttk
    import tkFont
    from tkMessageBox import askokcancel
    from tkFileDialog import askopenfilename
    # import tkSimpleDialog
    def utf8(s):
        return(s)


BASE = None
if sys.platform == 'win32':
    BASE = 'Win32GUI'

EXECUTABLES = [
    # Executable(script='etm', base=BASE, targetDir="dist-{0}/etmtk-{1}-freeze-{0}".format(plat, version), icon='etmTk/etmlogo.icns')
    Executable(script='etm', base=BASE, targetDir="dist-{0}/etmtk-{1}-freeze-{0}".format(plat, version))
]

OPTIONS = {
    'build': {'build_exe': 'dist-{0}/etmtk-{1}-freeze-{0}'.format(plat, version)},
    'build_exe': {'optimize':'2', 'compressed': 1},
    'build_mac': {'bundle_name':'etm'},
    'Executable': {'targetDir':'dist-{0}/etmtk-{1}-freeze-{0}'.format(plat, version)}
}

setup(name='etm',
    version=version,
    executables=EXECUTABLES,
    url='http://people.duke.edu/~dgraham/etmtk',
    description='event and task manager',
    long_description='manage events and tasks using simple text files',
    platforms='Any',
    license='License :: OSI Approved :: GNU General Public License (GPL)',
    author='Daniel A Graham',
    author_email='daniel.graham@duke.edu',
    options=OPTIONS,
    # package_data={'etmTk': ['etmlogo.*', 'etmtk.xpm', 'version.txt', 'CHANGES', 'logging.yaml']},
    package_data={'etmTk': ['etmtk.xpm', 'version.txt', 'CHANGES', 'logging.yaml']},
)
