# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
# import time
import weakref

import os
import os.path
import codecs
encoding = codecs.lookup('utf-8').name

import platform
if platform.python_version() >= '3':
    python_version2 = False
    unicode = str
    u = lambda x: x
    QString = lambda x: x
    utf8 = lambda x: x
else:
    python_version2 = True

    def utf8(s):
        return(s)

from copy import deepcopy

from colorsys import hsv_to_rgb

from datetime import date, datetime, timedelta
from dateutil.tz import tzlocal, gettz
from dateutil.parser import parse

from etmQt.etmData import (
    fmt_weekday, fmt_dt, fmt_date, fmt_time, get_options, get_data,
    get_reps, getDoneAndTwo, getFiles, getPrevNext, getReportData,
    getViewData, group_regex, hsh2str, leadingzero, mail_report,
    makeTree, oneday, oneminute, parse_datetime, parse_dtstr, fmt_datetime,
    process_lines, relpath, rrulefmt, s2or3, send_mail, send_text,
    sfmt, str2hsh, timedelta2Str, tstr2SCI, uniqueId, fmt_period,
    updateCurrentFiles, get_changes, checkForNewerVersion, getAgenda,
    date_calculator, datetime2minutes, calyear, export_ical_item,
    import_ical, export_ical, has_icalendar, expand_template, ensureMonthly,
    python_version, qt_version)

from etmQt.v import version

import locale
import re
import platform
import csv
from dateutil import __version__ as dateutil_version


# 2: all, 1: red, 0: none
use_colors = 2

# these will be overruled in main get_options
term_encoding = file_encoding = locale.getdefaultlocale()[1]

# named colors:
# aliceblue antiquewhite aqua aquamarine azure beige bisque black
# blanchedalmond blue blueviolet brown burlywood cadetblue chartreuse
# chocolate coral cornflowerblue cornsilk crimson cyan darkblue
# darkcyan darkgoldenrod darkgray darkgreen darkgrey darkkhaki
# darkmagenta darkolivegreen darkorange darkorchid darkred darksalmon
# darkseagreen darkslateblue darkslategray darkslategrey darkturquoise
# darkviolet deeppink deepskyblue dimgray dimgrey dodgerblue firebrick
# floralwhite forestgreen fuchsia gainsboro ghostwhite gold goldenrod
# gray green greenyellow grey honeydew hotpink indianred indigo ivory
# khaki lavender lavenderblush lawngreen lemonchiffon lightblue
# lightcoral lightcyan lightgoldenrodyellow lightgray lightgreen
# lightgrey lightpink lightsalmon lightseagreen lightskyblue
# lightslategray lightslategrey lightsteelblue lightyellow lime
# limegreen linen magenta maroon mediumaquamarine mediumblue
# mediumorchid mediumpurple mediumseagreen mediumslateblue
# mediumspringgreen mediumturquoise mediumvioletred midnightblue
# mintcream mistyrose moccasin navajowhite navy oldlace olive
# olivedrab orange orangered orchid palegoldenrod palegreen
# paleturquoise palevioletred papayawhip peachpuff peru pink plum
# powderblue purple red rosybrown royalblue saddlebrown salmon
# sandybrown seagreen seashell sienna silver skyblue slateblue
# slategray slategrey snow springgreen steelblue tan teal thistle
# tomato transparent turquoise violet wheat white whitesmoke yellow
# yellowgreen

calheader_fg = 'forestgreen'
calheader_bg = 'whitesmoke'
todayColor = QColor(0, 0, 255, 20)
occasionColor = QColor(200, 200, 200, 40)
timebarColor = QColor(255, 0, 0, 255)

PageSize = (612, 792)
PointSize = 10

MagicNumber = 0x70616765
FileVersion = 1

Dirty = False

if qt_version == 5:
    from etmQt.ui5.ui_etmBrowser import Ui_Dialog as Browser_Dialog
else:
    from etmQt.ui4.ui_etmBrowser import Ui_Dialog as Browser_Dialog


class BrowserForm(QDialog, Browser_Dialog):
    def __init__(self, parent=None):
        super(BrowserForm, self).__init__(parent)
        self.setupUi(self)
        self.parent = weakref.ref(parent)
        self.setStyleSheet(
            'font-size: %dpt' % self.parent().options['fontsize'])
        QShortcut(QKeySequence(
            Qt.CTRL + Qt.Key_W), self, self.close)


if qt_version == 5:
    from etmQt.ui5.ui_etmCalendar import Ui_Dialog as Calendar_Dialog
else:
    from etmQt.ui4.ui_etmCalendar import Ui_Dialog as Calendar_Dialog


class CalendarYearForm(QDialog, Calendar_Dialog):
    def __init__(self, parent=None):
        super(CalendarYearForm, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_GroupLeader)
        self.setupUi(self)
        self.printer = None
        self.cal_year = 0
        self.resize(580, 600)
        self.parent = weakref.ref(parent)
        self.setStyleSheet(
            'font-size: %dpt' %
            self.parent().options['fontsize'])

        self.cal_fgcolor = 'BLACK'
        self.cal_pastcolor = '#FFCCCC'
        self.cal_currentcolor = '#FFFFCC'
        self.cal_futurecolor = '#99CCFF'
        QShortcut(QKeySequence(Qt.Key_Left), self, self.minusYear)
        QShortcut(QKeySequence(Qt.Key_Right), self, self.plusYear)
        QShortcut(QKeySequence(Qt.Key_Space), self, self.zeroYear)
        QShortcut(QKeySequence(
            Qt.CTRL + Qt.Key_P), self,
            self.printCalendar)

        self.showYear()

    def showYear(self):
        if self.cal_year < 0:
            bgcolor = self.cal_pastcolor
        elif self.cal_year == 0:
            bgcolor = self.cal_currentcolor
        else:
            bgcolor = self.cal_futurecolor

        self.calendar_page = """\
<pre>
%s</pre>
""" % "\n".join(calyear(int(self.cal_year), self.parent().options))

        self.html = """\
<title>etm calendar</title>
<body text="%s" bgcolor="%s">
%s
</body>
""" % (self.cal_fgcolor, bgcolor, self.calendar_page)
        self.calendarBrowser.setHtml(self.html)

    def minusYear(self):
        self.cal_year -= 1
        self.showYear()

    def plusYear(self):
        self.cal_year += 1
        self.showYear()

    def zeroYear(self):
        self.cal_year = 0
        self.showYear()

    def printCalendar(self):
        self.document = QTextDocument()
        font = QFont()
        font.setPointSize(11)
        self.document.setDefaultFont(font)
        self.document.setHtml(self.calendar_page)

        if self.printer is None:
            self.printer = QPrinter(QPrinter.HighResolution)
            self.printer.setPageSize(QPrinter.Letter)
        form = QPrintDialog(self.printer, self)
        if form.exec_():
            self.document.print_(self.printer)

if qt_version == 5:
    from etmQt.ui5.ui_etmHelp import Ui_Dialog as Help_Dialog
else:
    from etmQt.ui4.ui_etmHelp import Ui_Dialog as Help_Dialog


class HelpForm(QDialog, Help_Dialog):
    def __init__(self, parent=None, page=0):
        super(HelpForm, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_GroupLeader)
        self.setupUi(self)
        self.parent = weakref.ref(parent)
        self.inSearch = False
        self.setStyleSheet(
            'font-size: %dpt' % self.parent().options['fontsize'])
        self.printer = None
        self.browserpages = [
            (self.overviewBrowser, 'overview.html'),
            (self.dataBrowser, 'data.html'),
            (self.viewsBrowser, 'views.html'),
            (self.reportsBrowser, 'reports.html'),
            (self.shortcutsBrowser, 'shortcuts.html'),
            (self.preferencesBrowser, 'preferences.html')]
        self.setHtml()
        self.tabWidget.setCurrentIndex(int(page))
        self.resize(740, 500)
        self.next.clicked.connect(self.doFind)
        self.previous.clicked.connect(self.doFindBackwards)

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_P), self, self.printHelp)
        QShortcut(QKeySequence(
            Qt.CTRL + Qt.Key_O), self, self.parent().edit_config)
        self.closeButton.clicked.connect(self.close)
        self.search.returnPressed.connect(self.doFind)
        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_F), self, self.openSearch)
        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_G), self, self.doFind)
        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_W), self, self.close)
        QShortcut(QKeySequence(
            Qt.SHIFT + Qt.CTRL + Qt.Key_G), self, self.doFindBackwards)
        QShortcut(QKeySequence(Qt.Key_Return), self, self.findOrClose)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.closeSearch)

    def setHtml(self):
        for browser, page in self.browserpages:
            browser.setSearchPaths([":/"])
            browser.setSource(QUrl(page))

    def setText(self, text):
        self.textBrowser.setText(text)

    def printHelp(self):
        font = QFont()
        font.setPointSize(11)
        page = self.tabWidget.currentIndex()
        browser = self.browserpages[page][0]
        self.document = QTextDocument(browser)
        self.document.setDefaultFont(font)
        self.document.setHtml(browser.toHtml())

        if self.printer is None:
            self.printer = QPrinter(QPrinter.HighResolution)
            self.printer.setPageSize(QPrinter.Letter)
        form = QPrintDialog(self.printer, self)
        if form.exec_():
            self.document.print_(self.printer)

    def doFindBackwards(self):
        return self.doFind(backwards=True)

    def doFind(self, backwards=False):
        page = self.tabWidget.currentIndex()
        browser = self.browserpages[page][0]

        self.tabWidget.setFocus()
        self.inSearch = True
        flags = QTextDocument.FindFlags()
        if backwards:
            where = self.tr("backward")
            flags = QTextDocument.FindBackward
        else:
            where = self.tr("forward")

        text = unicode(self.search.text())
        if not text:
            self.closeSearch()
            return()

        r = browser.find(text, flags)
        if r:
            self.clearStatusMessage()
        else:
            self.showStatusMessage(
                "{0} {1}".format(self.tr("not found"), where))

    def openSearch(self):
        self.inSearch = True
        self.search.clear()
        self.search.setFocus()

    def closeSearch(self):
        if self.inSearch:
            self.inSearch = False
            self.search.clear()
            self.tabWidget.setFocus()
        else:
            self.close()

    def findOrClose(self):
        if self.search.hasFocus():
            self.doFind()
            self.tabWidget.setFocus()
        else:
            self.close()

    def showStatusMessage(self, message):
        self.status_message.setText(message)
        QTimer.singleShot(3000, self.clearStatusMessage)

    def clearStatusMessage(self):
        self.status_message.setText('')


class PHL(QSyntaxHighlighter):

    Rules = []
    Formats = {}

    at_keys = "abcdefgklmpstuvwxz"
    repeat_keys = "hiMmnstuWw"
    job_keys = "cdefklq"
    # unused & keys: "aegjoprvxyz"

    uuid_color = "#F0F0F0"
    error_color = "crimson"
    comment_color = "#A0A0A0"
    repeat_color = "olive"
    task_color = "#106CAC"
    job_color = "lightseagreen"
    at_color = "darkviolet"
    date_color = "orchid"
    text_color = "slategray"

    typeColor = {
        '\=': ("default_value", "orchid"),
        '\$': ("inbox_value", "fuchsia"),
        '\*': ("event_value", "green"),
        '\~': ("action_value", "darkmagenta"),
        '\!': ("note_value", "saddlebrown"),
        '\-': ("task_value", task_color),
        '\+': ("group_value", task_color),
        '\%': ("delegated_value", "deepskyblue"),
        '\^': ("allday_value", "darkgreen"),
        '\?': ("someday_value", "cornflowerblue"),
        '\#': ("hidden_value", "lightslategrey"),
    }

    ATKEYS = [x for x in at_keys]

    REPEATKEYS = [x for x in repeat_keys]

    JOBKEYS = [x for x in job_keys]

    TYPEKEYS = ['\=', '\*', '\-', '\+', '\%', '\~', '\$', '\?', '\!', '\#']

    ATREPEATKEYS = ['r', 'o', '\+', '\-']

    ATJOBKEYS = ['j']

    ATERROR = r"[^%ssdjro\+\-\s]" % at_keys

    AMPERROR = r"[^%s%s\s]" % (repeat_keys, job_keys)

    # b29bfdd4-1086-4c6f-9678-10b5c1514dd2
    UUIDREGEX = r"@i\s+[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\
\-[a-z0-9]{4}\-[a-z0-9]{12}\b"

    def __init__(self, parent=None):
        super(PHL, self).__init__(parent)

        self.normal_format = ''
        self.format_values = []
        self.initializeFormats()

        for key in PHL.TYPEKEYS:
            pattern = r"^{0}\s.*$".format(key)
            self.format_values.append(PHL.typeColor[key][0])
            PHL.Rules.append(
                (QRegExp(pattern), PHL.typeColor[key][0]))

        PHL.Rules.append((
            QRegExp("|".join([r"\s&{0}\s".format(repeat_key)
                    for repeat_key in PHL.REPEATKEYS])), "repeat_key"))

        PHL.Rules.append((
            QRegExp("|".join([r"\s@{0}\s".format(at_key)
                    for at_key in PHL.ATREPEATKEYS])), "repeat_key"))

        PHL.Rules.append(
            (QRegExp("|".join([r"\s&{0}\s".format(job_key)
                     for job_key in PHL.JOBKEYS])), "job_key"))

        PHL.Rules.append((
            QRegExp("|".join([r"\s@{0}\s".format(at_key)
                    for at_key in PHL.ATJOBKEYS])), "job_key"))

        PHL.Rules.append((
            QRegExp("|".join([r"\s@{0}\s".format(at_key)
                    for at_key in PHL.ATKEYS])), "at_key"))

        PHL.Rules.append((
            QRegExp(r"\s@{0}\s[^@&]*".format(PHL.ATERROR)), "error"))

        PHL.Rules.append((
            QRegExp(r"\s&{0}\s[^@&]*\b".format(PHL.AMPERROR)), "error"))

        PHL.Rules.append((QRegExp(PHL.UUIDREGEX), "uuid"))

        PHL.Rules.append((QRegExp(r"#.*"), "comment"))

    @staticmethod
    def initializeFormats():
        baseFormat = QTextCharFormat()
        for name, color, bold, italic in (
                ("normal", "#000000", False, False),
                ("at_key", PHL.at_color, False, True),
                ("at_value", PHL.at_color, False, False),
                ("date_key", PHL.date_color, False, True),
                ("date_value", PHL.date_color, False, False),
                ("text_key", PHL.text_color, False, True),
                ("text_value", PHL.text_color, False, False),
                ("repeat_key", PHL.repeat_color, False, True),
                ("repeat_value", PHL.repeat_color, False, False),
                ("job_key", PHL.job_color, False, True),
                ("job_value", PHL.job_color, False, False),
                ("uuid", PHL.uuid_color, False, False),
                ("comment", PHL.comment_color, False, True),
                ("error", PHL.error_color, True, False)):
            format = QTextCharFormat(baseFormat)
            format.setForeground(QColor(color))
            if bold:
                format.setFontWeight(QFont.Bold)
            format.setFontItalic(italic)
            PHL.Formats[name] = format
        for key in PHL.typeColor.keys():
            format = QTextCharFormat(baseFormat)
            format.setForeground(QColor(PHL.typeColor[key][1]))
            PHL.Formats[PHL.typeColor[key][0]] = format

    def highlightBlock(self, text):
        NORMAL, TRIPLESINGLE, TRIPLEDOUBLE, ERROR = range(4)

        textLength = len(text)
        prevState = self.previousBlockState()

        if self.normal_format:
            self.setFormat(
                0, textLength, PHL.Formats[self.normal_format])
        else:
            self.setFormat(
                0, textLength, PHL.Formats["normal"])

        if python_version2 and qt_version == 4:
            if text.startsWith("Traceback") or text.startsWith("Error: "):
                self.setCurrentBlockState(ERROR)
                self.setFormat(0, textLength,
                               PHL.Formats["error"])
                return
            if (
                prevState == ERROR and not (
                    text.startsWith(sys.ps1) or text.startsWith("#"))):
                self.setCurrentBlockState(ERROR)
                self.setFormat(0, textLength,
                               PHL.Formats["error"])
                return
        else:
            if text.startswith("Traceback") or text.startswith("Error: "):
                self.setCurrentBlockState(ERROR)
                self.setFormat(0, textLength,
                               PHL.Formats["error"])
                return
            if (
                prevState == ERROR and not (
                    text.startswith(sys.ps1) or text.startswith("#"))):
                self.setCurrentBlockState(ERROR)
                self.setFormat(0, textLength,
                               PHL.Formats["error"])
                return

        for regex, format in PHL.Rules:
            i = regex.indexIn(text)
            if i >= 0 and format in self.format_values:
                self.normal_format = format
            while i >= 0:
                length = regex.matchedLength()
                self.setFormat(i, length,
                               PHL.Formats[format])
                i = regex.indexIn(text, i + length)

        self.setCurrentBlockState(NORMAL)

    def rehighlight(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QSyntaxHighlighter.rehighlight(self)
        QApplication.restoreOverrideCursor()

STARTTEXT = (
    'This TextEdit provides autocompletions for words that have '
    + 'more than 3 characters.\nYou can trigger autocompletion'
    + ' using %s\n\n''' % (
        QKeySequence("Ctrl+E").toString(QKeySequence.NativeText)))


class DictionaryCompleter(QCompleter):
    def __init__(self, parent=None, words=[]):
        QCompleter.__init__(self, words, parent)


class CompletionTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(CompletionTextEdit, self).__init__(parent)
        self.setTabStopWidth(32)
        self.setPlainText(QString(""))
        self.parent = weakref.ref(parent)
        self.setStyleSheet(
            'font-size: %dpt' % self.parent().options['fontsize'])
        self.completer = None
        self.moveCursor(QTextCursor.End)
        self.setFocus(True)

    def setCompleter(self, completer):
        if self.completer:
            self.disconnect(self.completer, 0, self, 0)
        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        # completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer = completer
        self.completer.activated.connect(self.insertCompletion)

    def isempty(self, s):
        if python_version2 and qt_version == 4:
            return(s.isEmpty())
        else:
            return(not s)

    def length(self, s):
        if python_version2 and qt_version == 4:
            return(s.length())
        else:
            return(len(s))

    def right(self, s, n):
        if python_version2 and qt_version == 4:
            return(s.right(n))
        else:
            return(s[-n:])

    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = (
            self.length(completion) -
            self.length(self.completer.completionPrefix()))
        if self.right(self.completer.completionPrefix(), 1) == ' ':
            # add room for the ending space
            extra += 1
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(self.right(completion, extra))
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        w3 = tc.selectedText()
        tc.movePosition(QTextCursor.StartOfWord)
        tc.movePosition(QTextCursor.PreviousCharacter)
        tc.select(QTextCursor.WordUnderCursor)
        w2 = tc.selectedText()
        if w2 == QString(':') or w2 == QString('/'):
            # prepend the word before the colon and the colon to w3
            tc.movePosition(QTextCursor.PreviousWord)
            tc.movePosition(QTextCursor.WordLeft)
            tc.select(QTextCursor.WordUnderCursor)
            prev_word = tc.selectedText()
            w3 = prev_word + w2 + w3
            # set w2 to the word before the previous word
            tc.movePosition(QTextCursor.PreviousCharacter)
            tc.movePosition(QTextCursor.StartOfWord)
            tc.movePosition(QTextCursor.WordLeft)
            tc.select(QTextCursor.WordUnderCursor)
            w2 = tc.selectedText()
        if w2 == QString('@'):
            # e.g., w2+w3+" " = '@k '
            return(w2 + w3 + " ")
        # get the previous word
        tc.movePosition(QTextCursor.WordLeft)
        tc.movePosition(QTextCursor.Left)
        tc.select(QTextCursor.WordUnderCursor)
        w1 = tc.selectedText()
        if w1 == QString('@'):
            # e.g., w1+w2+" "+w3 = '@c o'
            return(w1 + w2 + " " + w3)
        return(w3)

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self)
        QTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (
                    Qt.Key_Enter,
                    Qt.Key_Return,
                    Qt.Key_Escape,
                    Qt.Key_Tab,
                    Qt.Key_Backtab):
                event.ignore()
                return

        ## has ctrl-E been pressed??
        isShortcut = (event.modifiers() == Qt.ControlModifier and
                      event.key() == Qt.Key_E)
        if (not self.completer or not isShortcut):
            QTextEdit.keyPressEvent(self, event)

        ## ctrl or shift key on it's own??
        ctrlOrShift = event.modifiers() in (Qt.ControlModifier,
                                            Qt.ShiftModifier)
        if ctrlOrShift and self.isempty(event.text()):
            # ctrl or shift key on it's own
            return

        eow = QString("\b(@[a-zA-Z/].*)\b")  # end of word

        hasModifier = (
            (event.modifiers() != Qt.NoModifier) and not ctrlOrShift)

        if self.completer:
            completionPrefix = self.textUnderCursor()
            # if (not isShortcut and (hasModifier or event.text().isEmpty() or
            if python_version2 and qt_version == 4:
                if (not isShortcut and
                    (hasModifier or event.text().isEmpty() or
                     completionPrefix.length() < 3 or
                     event.text().contains(eow))):
                    if self.completer:
                        self.completer.popup().hide()
                    return
            else:
                if (not isShortcut and (
                        hasModifier or
                        not event.text() or
                        len(completionPrefix) < 3 or
                        "eow" in event.text())):
                    if self.completer:
                        self.completer.popup().hide()
                    return

            if (completionPrefix != self.completer.completionPrefix()):
                self.completer.setCompletionPrefix(completionPrefix)
                popup = self.completer.popup()
                popup.setCurrentIndex(
                    self.completer.completionModel().index(0, 0))

            cr = self.cursorRect()
            cr.setWidth(
                self.completer.popup().sizeHintForColumn(0)
                + self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(cr)  # popup it up!

if qt_version == 5:
    from etmQt.ui5.ui_etmList import Ui_Dialog as List_Dialog
else:
    from etmQt.ui4.ui_etmList import Ui_Dialog as List_Dialog


class ListForm(QDialog, List_Dialog):
    def __init__(self, parent=None, title='', items=[],
                 tooltip=None):
        super(ListForm, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.parent = weakref.ref(parent)
        self.setStyleSheet(
            'font-size: %dpt' % self.parent().options['fontsize'])
        self.title = title
        self.items = items
        if tooltip:
            self.textLabel.setToolTip(tooltip)

        self.textLabel.setText(self.title)
        for item in self.items:
            item = QListWidgetItem("%s" % item)
            self.listWidget.addItem(item)

        QShortcut(QKeySequence(
            Qt.CTRL + Qt.Key_W), self, self.close)

        self.closeButton.clicked.connect(self.close)
        self.resize(460, 200)

if qt_version == 5:
    from etmQt.ui5.ui_etmWhich import Ui_whichDialog as Which_Dialog
else:
    from etmQt.ui4.ui_etmWhich import Ui_whichDialog as Which_Dialog


class WhichForm(QDialog, Which_Dialog):
    def __init__(self, parent, mode, instance):
        super(WhichForm, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.parent = weakref.ref(parent)
        self.mode = mode
        if mode == 'file':
            (self.datadir, suggested_file) = instance
            self.comboBox.setEditable(True)
            self.comboBox.setInsertPolicy(QComboBox.InsertAtBottom)
            if suggested_file:
                currfile = suggested_file
            else:
                currfile = ensureMonthly(self.parent().options)
            itemList = []
            self.fileList = []
            current = 0
            common_prefix, filelist = getFiles(self.datadir)
            for i in range(len(filelist)):
                fullfile, relfile = filelist[i]
                itemList.append(QString(relfile))
                self.fileList.append(fullfile)
                if currfile and fullfile == currfile:
                    current = i
                    # no need to check any more
                    currfile = None
            self.theQuestion.setText(self.tr('Append item to which file?'))
            self.parent().which_file = self.fileList[current]
        elif mode == 'recent':
            itemList = []
            self.fileList = []
            recent_edits = self.parent().recent_edits
            choices = ["%s: %s" % (x[0], x[1]) for x in recent_edits]
            self.comboBox.setEditable(False)
            self.comboBox.setInsertPolicy(QComboBox.InsertAtBottom)
            current = 0
            for i in range(len(choices)):
                itemList.append(QString(choices[i]))
                self.fileList.append(
                    os.path.join(self.parent().options['datadir'],
                                 recent_edits[i][0]))
            self.theQuestion.setText(self.tr('Edit which file?'))
            self.parent().which_file = self.fileList[current]
        else:
            self.comboBox.setEditable(False)
            current = 0
            itemList = [
                self.tr("only the datetime of this instance"),
                self.tr("this instance"),
                self.tr("this and all subsequent instances"),
                self.tr("all instances")
            ]
            q1 = self.tr("You have selected instance")
            if mode == 'remove':
                q2 = self.tr("of a repeating item. What do you want to delete?")
                itemList.pop(0)
            elif mode == 'export':
                q2 = self.tr("of a repeating item. What do you want to export?")
                itemList.pop(0)
            else:
                q2 = self.tr("of a repeating item. What do you want to change?")
            self.theQuestion.setText(QString(
                "%s %s.\n%s" % (q1, instance, q2)))
            self.parent().which_indx = 1

        self.comboBox.addItems(itemList)
        self.comboBox.setCurrentIndex(current)
        self.comboBox.currentIndexChanged.connect(self.setChoice)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_L), self, self.showList)

    def setChoice(self, txt):
        if self.mode == 'file':
            self.parent().which_file = \
                os.path.join(self.datadir, str(self.comboBox.currentText()))
        elif self.mode == 'recent':
            which_indx = self.comboBox.currentIndex()
            self.parent().which_file = self.fileList[which_indx]
        else:
            self.parent().which_indx = self.comboBox.currentIndex() + 1

    def showList(self):
        self.comboBox.setFocus()
        self.comboBox.showPopup()

if qt_version == 5:
    from etmQt.ui5.ui_etmDetails import Ui_detailDialog as Details_Dialog
else:
    from etmQt.ui4.ui_etmDetails import Ui_detailDialog as Details_Dialog


class DetailForm(QDialog, Details_Dialog):
    def __init__(self, parent=None, receiver=None):
        super(DetailForm, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.parent = weakref.ref(parent)
        self.setStyleSheet(
            'font-size: %dpt' % self.parent().options['fontsize'])
        self.options = self.parent().options
        self.receiver = receiver
        self.printer = None
        self.setupUi(self)
        self.detailLayout = QVBoxLayout(self.detailFrame)
        self.editor = QTextEdit()
        self.editor.setTabStopWidth(4)
        self.editor.setStyleSheet("QTextEdit {background: transparent}")
        self.detailLayout.addWidget(self.editor, 0)
        self.detailLayout.setContentsMargins(QMargins(0, 0, 0, 0))
        self.highlighter = PHL(self.editor.document())
        self.hsh = {}
        self.bef = None
        self.which_indx = 0
        self.which_file = ''

        if self.parent().timer_status == 'stopped':
            self.cloneActionButton.setToolTip(
                self.tr("""\
Click here or press Ctrl-T to start the timer
for an action based on this item."""))
        else:
            self.cloneActionButton.setToolTip(self.parent().timer_tooltip)

        self.uuid = None
        self.fileinfo = None
        self.linenum = None
        self.dt = None
        self.repeating = False
        self.editor.setReadOnly(True)

        self.closeButton.clicked.connect(self.close)
        self.historyButton.clicked.connect(self.show_history)
        self.repsButton.clicked.connect(self.show_repetitions)
        self.itemButton.clicked.connect(self.edit_item)
        self.fileButton.clicked.connect(self.edit_file)
        self.finishButton.clicked.connect(self.finish)
        self.cloneItemButton.clicked.connect(self.clone_item)
        self.cloneActionButton.clicked.connect(self.clone_action)
        self.minusButton.clicked.connect(self.remove)
        self.moveButton.clicked.connect(self.move)
        self.helpButton.clicked.connect(self.detailsHelp)
        QShortcut(QKeySequence(Qt.Key_F1), self, self.detailsHelp)
        QShortcut(QKeySequence(Qt.Key_Return), self, self.edit_item)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_D), self, self.remove)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_E), self, self.edit_file)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_C), self, self.clone_item)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_T), self, self.clone_action)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_F), self, self.finish)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_M), self, self.move)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_R), self, self.show_repetitions)
        QShortcut(
            QKeySequence(Qt.SHIFT + Qt.CTRL + Qt.Key_H),
            self, self.show_history)
        QShortcut(
            QKeySequence(Qt.SHIFT + Qt.CTRL + Qt.Key_S),
            self, self.schedule)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_G), self, self.openWithDefault)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_W), self, self.close)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_P), self, self.printText)
        QShortcut(QKeySequence(Qt.Key_F8), self, self.exportIcalItem)

        if self.parent().timer_status == 'stopped':
            self.cloneActionButton.setEnabled(True)
        else:
            self.cloneActionButton.setEnabled(False)

        self.resize(460, 200)

    def exportIcalItem(self):
        if not has_icalendar:
            QMessageBox.warning(
                self, "import error",
                "Could not import icalendar - aborted.")
            return()

        num = 0
        if not self.repeating:
            num = 4
        else:
            # indx = 0
            which = WhichForm(self.parent(), 'export', self.hsh['_dt'])
            which.setWindowTitle(self.hsh['_filetext'])
            if not which.exec_():
                self.parent().which_indx = 0
                return()
            num = self.parent().which_indx
        # 1: this instance, 2: this and subsequent, 3: all, 4: not repeating
        hsh = deepcopy(self.hsh)
        if num == 1:
            del hsh['_r'], hsh['r'], hsh['rrule']
            hsh['s'] = parse(parse_dtstr(hsh['_dt'], hsh['z']))
            m = 'this instance'
        elif num == 2:
            hsh['s'] = parse(parse_dtstr(hsh['_dt'], hsh['z']))
            m = 'this and subsequent instances'
        elif num == 3:
            # no need to modify hsh
            m = 'all instances'
        else:
            m = 'item'
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setText(self.tr("iCalendar Export"))
            msgBox.setInformativeText(
                self.tr(
                    "Save this item to the file\n\n{0}?".format(
                        self.options['icsitem_file'])))
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Ok)
            # must use exec_ here
            reply = msgBox.exec_()
            if reply != QMessageBox.Ok:
                return(False)

        ok, msg = export_ical_item(hsh, self.options['icsitem_file'])
        if ok:
            msg = "Exported {0} to {1}".format(m, self.options['icsitem_file'])
        mbox = QMessageBox(self)
        mbox.setText(self.tr('etm icalendar export'))
        mbox.setInformativeText(msg)
        mbox.resize(600, 200)
        mbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mbox.show()

    def printText(self):
        font = QFont(self.font())
        font.setPointSize(font.pointSize() - 3)

        self.document = QTextDocument()
        self.document.setDefaultFont(font)
        self.document.setPlainText(self.editor.toPlainText())

        if self.printer is None:
            self.printer = QPrinter(QPrinter.HighResolution)
            self.printer.setPageSize(QPrinter.Letter)

        form = QPrintDialog(self.printer, self)
        if form.exec_():
            self.document.print_(self.printer)

    def setHash(self, hsh):
        '''
            From hsh create detailsShow and detailsHide strings.
        '''
        self.finishButton.setEnabled(
            hsh['itemtype'] in [u'-', u'+', u'%'] and
            (u'_r' in hsh or u'f' not in hsh))
        # why not enable deleting hidden items?
        self.grouptask = (hsh['itemtype'] == '+')
        # list only with len @+ == 1 is not repeating
        self.repeating = False
        if '_r' in hsh:
            if hsh['_r'][0]['f'] != 'l':
                self.repeating = True
            elif len(hsh['+']) > 1:
                self.repeating = True
            else:
                self.repeating = False
        self.hsh = hsh

        if self.repeating:
            self.minusButton.setToolTip(
                self.tr("""\
Click here or press Ctrl-D to delete one or more repetitions of this item."""))
            self.minusButton.setIcon(QIcon(":/date_delete.png"))

            if self.grouptask:
                self.finishButton.setToolTip(
                    self.tr("""\
Click here or press Ctrl-F to set the completion datetime for this job."""))
            else:
                self.finishButton.setToolTip(
                    self.tr("""
Click here or press Ctrl-F when a task is selected
to update the latest completion datetime for the task."""))
        else:
            self.minusButton.setIcon(QIcon(":/item_delete.png"))

            if hsh['itemtype'] == u'~':
                self.minusButton.setToolTip(
                    self.tr("""\
Click here or press Ctrl-D to delete this action."""))
            else:
                self.minusButton.setToolTip(
                    self.tr("""\
Click here or press Ctrl-D to delete this item."""))
            if self.grouptask:
                self.finishButton.setToolTip(self.tr("""\
Click here or press Ctrl-F to set the completion datetime for this job."""))
            else:
                self.finishButton.setToolTip(
                    self.tr("""\
Click here or press Ctrl-F when a task is selected
to set the finish datetime for this item."""))
        self.repsButton.setEnabled(self.repeating)
        self.hsh['_filename'] = os.path.join(
            self.parent().options['datadir'], hsh['fileinfo'][0])
        self.hsh['_linenum'] = hsh['fileinfo'][1]
        filetext = "{0}".format(":".join([str(x) for x in hsh['fileinfo']]))
        hsh['_filetext'] = filetext
        self.statusBar.setText(filetext)
        self.editor.setPlainText(self.hsh['entry'])
        # self.editor.setFocus()

    def processCommand(self, command):
        """
        Process comand and return output.
        """
        process = QProcess()
        process.start(command)
        if process.waitForStarted():
            process.waitForFinished()
            result = process.readAllStandardOutput().data()
            error = process.readAllStandardError().data()
            if error:
                QMessageBox.warning(
                    self, "etm error", "{0}".format(str(error)))
                return((0, error))
            else:
                if python_version2 and qt_version == 4:
                    return((1, QString(result)))
                else:
                    return((1, unicode(result, encoding=encoding)))

    def openWithDefault(self):
        if 'g' not in self.hsh:
            return(False)
        path = self.hsh['g']

        from platform import system
        pf = system()
        if pf in ('Windows', 'Microsoft'):
            # TODO: check whether the solution for Darwin will work here
            os.startfile(path)
            return()
        if pf == 'Darwin':
            cmd = '/usr/bin/open' + " %s" % path
        else:
            cmd = 'xdg-open' + " %s" % path
        ok, msg = self.processCommand(cmd)
        if not ok:
            return(False)
        return(True)

    def show_history(self):
        command = self.parent().options['hg_history'].format(
            repo=self.parent().options['datadir'],
            file=self.hsh['_filename'], rev="{rev}", desc="{desc}")

        res, qstr = self.processCommand(command)
        lines = qstr.split('\n')
        self.form = ListForm(self.parent(), title="{0}: {1}".format(
            self.tr('change history'), self.hsh['fileinfo'][0]),
            items=lines)
        font = QFont(self.font())
        font.setPointSize(font.pointSize() - 1)
        self.form.setFont(font)
        self.form.resize(580, 240)
        self.form.infoButton.clicked.connect(self.showDiffInfo)
        self.form.show()

    def showDiffInfo(self):
        self.udiff_title = self.tr("The GNU Unified Diff Format")
        self.udiff_text = self.tr("""\
The format starts with a two-line header with the original file
preceded by "---" and the new file is preceded by "+++". Following
this are one or more change hunks that contain the line differences in
the file. The unchanged, contextual lines are preceded by a space
character, addition lines are preceded by a plus sign, and deletion
lines are preceded by a minus sign.

A hunk begins with range information and is immediately followed with
the line additions, line deletions, and any number of the contextual
lines. The range information is surrounded by double-at signs. The
format of the range information line is as follows:

@@ -l,s +l,s @@

The hunk range information contains two hunk ranges. The range for the
hunk of the original file is preceded by a minus symbol, and the range
for the new file is preceded by a plus symbol. Each hunk range is of
the format l,s where l is the starting line number and s is the number
of lines the change hunk applies to for each respective file.

If a line is modified, it is represented as a deletion and addition.
Since the hunks of the original and new file appear in the same hunk,
such changes would appear adjacent to one another. An example of this
is:

-check this dokument. On
+check this document. On
""")

        mbox = QMessageBox(self)
        mbox.setText(self.udiff_title)
        mbox.setInformativeText(self.udiff_text)
        mbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mbox.show()

    def detailsHelp(self):
        form = HelpForm(self.parent(), 0)
        form.setWindowTitle('etm')
        form.show()

    def show_repetitions(self):
        # self.emit(SIGNAL("repetitions"), self.editor)
        if 'rrule' not in self.hsh:
            return(False)
        gotall, lines = get_reps(self.bef, self.hsh)
        if gotall:
            self.txt = """All of this item's repetitions are listed."""
        else:
            self.txt = """\
Repetitions that fall on or after the item's starting date, {0}, and
before {1} plus the first repetition, if any, after this interval.\
""".format(fmt_date(self.hsh['s'], True), fmt_date(self.bef, True))
        self.form = ListForm(
            self.parent(), title='{0}: {1}   ({2} {3})'.format(
                self.tr('repetitions'), self.hsh['_summary'],
                self.tr("times are"), self.hsh['z']),
            items=[x.strftime(rrulefmt) for x in lines])
        self.form.infoButton.clicked.connect(self.showInterval)
        self.form.show()

    def showInterval(self):
        mbox = QMessageBox(self)
        mbox.setText(
            self.tr('repetitions for {0}'.format(self.hsh['_summary'])))
        mbox.setInformativeText(self.txt)
        mbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mbox.show()

    def finish(self):
        if self.hsh['itemtype'] not in [u'+', u'-', u'%']:
            return(False)

        done, next, following = getDoneAndTwo(self.hsh)
        if next:
            # undated tasks won't have a due date
            ddn = next.replace(
                tzinfo=tzlocal()).astimezone(
                gettz(self.hsh['z'])).replace(tzinfo=None)
            dds = ddn.strftime(self.parent().options['etmdatetimefmt'])
        else:
            ddn = dds = ''
        if self.hsh['itemtype'] == u'+':
            m = group_regex.match(self.hsh['_summary'])
            if m:
                group, num, tot, job = m.groups()
                prompt = "job %s/%s:\t%s\ngroup:\t%s\ndue:\t%s\nfinish date" % (
                    num, tot, job, group,
                    dds)
                dt = self.getDate(prompt)
                if not dt:
                    return()

                self.hsh['_j'][int(num) - 1]['f'] = [
                    (dt.replace(tzinfo=None), ddn)]
                finished = True
                # check to see if all jobs are finished
                for job in self.hsh['_j']:
                    if 'f' not in job:
                        finished = False
                        break
                if finished:
                    # remove the finish dates from the jobs
                    for job in self.hsh['_j']:
                        del job['f']
                    # and add the last finish date (this one) to the group
                    self.hsh['f'] = [(dt.replace(tzinfo=None), ddn)]
        else:
            prompt = "task:\t%s\ndue:\t%s\nfinish date and time" % (
                self.hsh['_summary'],
                dds)
            dt = self.getDate(prompt)
            if not dt:
                return()
            dtz = dt.replace(
                tzinfo=tzlocal()).astimezone(
                gettz(self.hsh['z'])).replace(tzinfo=None)
            if not ddn:
                ddn = dtz
            self.hsh.setdefault('f', []).append((dtz, ddn))
        content = hsh2str(self.hsh, self.parent().options)
        filename = self.hsh['_filename']
        fn, bl, el = self.hsh['fileinfo']
        lines = content.split('\n')
        form = EditForm(self.parent(), receiver=self.receiver)
        self.close()
        form.replaceLinesInFile(filename, bl, el, lines)
        form.close()

    def schedule(self):
        if 'r' in self.hsh or 's' in self.hsh:
            p = (self.tr("new date and time to replace\n%s" %
                         self.hsh['_dt']))
        else:
            p = self.tr("New datetime")
        dt = self.getDate(prompt=p)
        if not dt:
            return(None)
        dtz = dt.replace(
            tzinfo=tzlocal()).astimezone(
            gettz(self.hsh['z'])).replace(tzinfo=None)

        # repeating -> at current to @- and new to @+
        # not repeating -> @s new
        if 'r' in self.hsh:
            old_dt = parse(
                self.hsh['_dt']).replace(
                tzinfo=tzlocal()).astimezone(
                gettz(self.hsh['z']))
            self.hsh.setdefault('+', []).append(
                dtz.strftime(sfmt))
            self.hsh.setdefault('-', []).append(
                old_dt.strftime(sfmt))
        else:  # not repeating
            self.hsh['s'] = dtz
        content = hsh2str(self.hsh, self.parent().options)
        filename = self.hsh['_filename']
        fn, bl, el = self.hsh['fileinfo']
        lines = content.split('\n')
        form = EditForm(self.parent(), receiver=self.receiver)
        self.close()
        form.replaceLinesInFile(filename, bl, el, lines)
        form.close()

    def getDate(self, prompt):
        txt = datetime.now().strftime(self.parent().options['etmdatetimefmt'])
        ok = True
        dt = None
        while ok and not dt:
            fdate, ok = QInputDialog.getText(
                self,
                self.tr("datetime"), "%s:" % prompt,
                text=txt)
            if ok:
                try:
                    dt = parse(
                        parse_datetime(
                            str(fdate)),
                        dayfirst=self.options['dayfirst'],
                        yearfirst=self.options['yearfirst']).replace(
                        tzinfo=None)

                    return(dt)
                except:
                    dt = None
                    txt = fdate
        return(None)

    def move(self):
        form = getEditForm(
            self.parent(), instance='file', hsh=self.hsh,
            receiver=self.receiver)
        if form:
            newfile = form.getFileName(self.hsh)
            if not newfile:
                return(False)

            fn, begline, endline = self.hsh['fileinfo']
            oldfile = self.hsh['_filename']
            newlines = self.hsh['entry'].strip().split('\n')
            added = form.addLinesToFile(
                filename=newfile,
                newlines=newlines,
                senddone=False)
            if not added:
                # warn message
                QMessageBox.warning(
                    self, "etm", self.tr("""\
Adding item to {1} failed - aborted removing item from {2}""".format(
                    newfile, oldfile)))
                form.close()
                return(False)
            removed = form.removeLinesFromFile(
                filename=oldfile, begline=begline,
                endline=endline, senddone=True)
            if removed:
                self.close()
            form.close()

    def doRemove(self, ret):
        form = getEditForm(
            self.parent(), instance='file', receiver=self.receiver)
        if form:
            if ret == 3:
                # we're removing the item
                filename = self.hsh['_filename']
                fn, bl, el = self.hsh['fileinfo']
                form.removeLinesFromFile(filename, bl, el)
                self.close()
                self.accept()
                return(True)

            if self.rev_str:
                lines = self.rev_str.split('\n')
            else:
                contents = "# %s" % hsh2str(
                    self.hsh, self.parent().options)
                lines = contents.split('\n')
            filename = self.hsh['_filename']
            fn, bl, el = self.hsh['fileinfo']
            form.replaceLinesInFile(filename, bl, el, lines)

    def edit_file(self):
        form = getEditForm(
            self.parent(), instance='edit',
            filename=self.hsh['_filename'],
            hsh=self.hsh,
            receiver=self.receiver)
        if form:
            form.setWindowTitle("{0}".format(self.hsh['_filetext']))
            form.show()
            self.close()
            form.raise_()
            form.setFocus()

    def doIt(self, mode):
        edit_hsh = {}
        ret = self.hsh['_which']
        self.rev_str = ''
        if ret == 1:
            # ret for remove begins with 2
            # only the datetime of this instance
            # get the new datetime in localtime and convert it to zonetime
            # add the new datetime using @+
            # convert the old datetime in localtime to zonetime
            # remove the old datetime using @-
            # proceed as in ret = 4
            datestr, doit = QInputDialog.getText(
                self, self.tr("datetime"), "%s:" %
                (self.tr("new date and time to replace\n%s" %
                         self.hsh['_dt'])))
            if doit:
                new_dt = parse(
                    str(datestr)).replace(
                    tzinfo=tzlocal()).astimezone(
                    gettz(self.hsh['z']))
                if new_dt:
                    old_dt = parse(
                        self.hsh['_dt']).replace(
                        tzinfo=tzlocal()).astimezone(
                        gettz(self.hsh['z']))
                    self.hsh.setdefault('+', []).append(
                        new_dt.strftime(sfmt))
                    self.hsh.setdefault('-', []).append(
                        old_dt.strftime(sfmt))
                    self.rev_str = edit_str = hsh2str(
                        self.hsh, self.parent().options)
                    hsh_rev = edit_hsh = self.hsh
                    self.rev_id = self.new_id = self.hsh['i']
                    mode = 'remove'
                else:
                    return()

        elif ret == 2:
            # add this datetime to hsh['-']
            # make a copy without repetion entries and with this
            # date as hsh['s']
            # open copy for editing
            hsh_cpy = deepcopy(self.hsh)
            hsh_rev = deepcopy(self.hsh)
            hsh_cpy['i'] = uniqueId()
            self.rev_id = hsh_rev['i']
            self.new_id = hsh_cpy['i']
            dt = parse(
                self.hsh['_dt']).replace(
                tzinfo=tzlocal()).astimezone(
                gettz(self.hsh['z']))
            dtn = dt.replace(tzinfo=None)
            if '+' in hsh_rev and dtn in hsh_rev['+']:
                hsh_rev['+'].remove(dtn)
                if not hsh_rev['+'] and hsh_rev['r'] == 'l':
                    del hsh_rev['r']
                    del hsh_rev['_r']
            else:
                hsh_rev.setdefault('-', []).append(dt)
            for k in ['_r', 'o', '+', '-']:
                if k in hsh_cpy:
                    del hsh_cpy[k]
            hsh_cpy['s'] = dt
            self.rev_str = hsh2str(hsh_rev, self.parent().options)
            self.cpy_str = hsh2str(hsh_cpy, self.parent().options)
            edit_str = self.cpy_str
            edit_hsh = hsh_cpy

        elif ret == 3:
            # this and all future instances
            # TODO: &u -> @u to apply to all @r entries?
            # make a copy with hsh['s'] = this datetime
            # add hsh['u'] = this datetime (- oneminute?)
            # open copy for editing
            hsh_cpy = deepcopy(self.hsh)
            hsh_rev = deepcopy(self.hsh)
            hsh_cpy['i'] = uniqueId()
            self.rev_id = hsh_rev['i']
            self.new_id = hsh_cpy['i']
            dtstr = self.hsh['_dt']
            dt = parse(parse_dtstr(dtstr, self.hsh['z'])).replace(
                tzinfo=None)
            tmp = []
            for h in hsh_rev['_r']:
                if 'f' in h and h['f'] != u'l':
                    h['u'] = dt - oneminute
                tmp.append(h)
            hsh_rev['_r'] = tmp
            if u'+' in self.hsh:
                tmp_rev = []
                tmp_cpy = []
                for d in hsh_rev['+']:
                    if d < dt:
                        tmp_rev.append(d)
                    else:
                        tmp_cpy.append(d)
                hsh_rev['+'] = tmp_rev
                hsh_cpy['+'] = tmp_cpy
            if u'-' in self.hsh:
                tmp_rev = []
                tmp_cpy = []
                for d in hsh_rev['-']:
                    if d < dt:
                        tmp_rev.append(d)
                    else:
                        tmp_cpy.append(d)
                hsh_rev['-'] = tmp_rev
                hsh_cpy['-'] = tmp_cpy
            hsh_cpy['s'] = dt
            self.rev_str = hsh2str(hsh_rev, self.parent().options)
            self.cpy_str = hsh2str(hsh_cpy, self.parent().options)
            edit_str = self.cpy_str
            edit_hsh = hsh_cpy

        elif ret == 4:
            # all instances
            hsh_cpy = hsh_rev = deepcopy(self.hsh)
            self.rev_id = self.hsh['i']
            self.new_id = self.hsh['i']
            self.rev_str = ''
            self.cpy_str = hsh2str(self.hsh, self.parent().options)
            # self.cpy_str = ''
            edit_str = self.cpy_str
            edit_hsh = self.hsh

        if mode == 'remove':
            if self.hsh['_which'] == 4:
                filename = self.hsh['_filename']
                fn, bl, el = self.hsh['fileinfo']
                form = getEditForm(
                    self.parent(), instance='remove',
                    receiver=self.receiver)
                if form:
                    form.removeLinesFromFile(filename, bl, el)
                    form.close()
                    self.close()
                    self.accept()
                    return(True)

            if self.rev_str:
                lines = self.rev_str.split('\n')
            else:
                contents = "# %s" % hsh2str(
                    self.hsh, self.parent().options)
                lines = contents.split('\n')
            filename = self.hsh['_filename']
            fn, bl, el = self.hsh['fileinfo']
            form = getEditForm(
                self.parent(),
                instance='file',
                receiver=self.receiver)
            if form:
                form.replaceLinesInFile(filename, bl, el, lines)
                form.close()
                self.close()
                self.accept()

        elif 'fileinfo' in edit_hsh and edit_hsh['fileinfo']:
            form = getEditForm(
                self.parent(),
                instance='edit',
                hsh=edit_hsh,
                receiver=self.receiver)
            if form:
                form.setWindowTitle(self.hsh['_filetext'])
                form.fileinfo = edit_hsh['fileinfo']
                form.editor.setPlainText(edit_str)
                form.editor.new_id = edit_hsh['i']
                form.rev_hsh = hsh_rev
                form.setEditInfo(self.rev_id, self.rev_str, self.new_id)
                if self.hsh['itemtype'] == u'+':
                    m = group_regex.match(self.hsh['_summary'])
                    if m:
                        group, num, tot, job = m.groups()
                        form.editor.find(job)
                form.show()
                self.close()
                self.accept()
                form.raise_()
                form.setFocus()

    def edit_item(self):
        if not self.repeating:
            self.hsh['_which'] = 4
        else:
            which = WhichForm(self.parent(), 'edit', self.hsh['_dt'])
            which.setWindowTitle(self.hsh['_filetext'])
            if not which.exec_():
                self.parent().which_indx = 0
                return()
            self.hsh['_which'] = self.parent().which_indx
        self.doIt('edit')

    def remove(self):
        if not self.repeating:
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setText(self.tr("Delete"))
            msgBox.setInformativeText(
                self.tr("""\
Do you really want to delete this item?

This action cannot be undone."""))
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Ok)
            # must use exec_ here
            reply = msgBox.exec_()
            if reply != QMessageBox.Ok:
                return(False)
            # self.emit(SIGNAL("remove"), self.editor)
            filename = self.hsh['_filename']
            fn, bl, el = self.hsh['fileinfo']
            form = getEditForm(
                self.parent(),
                instance='file',
                receiver=self.receiver)
            if form:
                form.removeLinesFromFile(filename, bl, el)
                form.close()
                self.close()
        else:
            which = WhichForm(self.parent(), 'remove', self.hsh['_dt'])
            which.setWindowTitle(self.hsh['_filetext'])
            if not which.exec_():
                self.parent().which_indx = 0
            else:
                self.parent().which_indx += 1
            self.hsh['_which'] = self.parent().which_indx
            self.doIt('remove')

    def clone_item(self):
        hsh_cpy = deepcopy(self.hsh)
        # save to the same file as the original
        hsh_cpy['fileinfo'] = (self.hsh['fileinfo'][0], -1, -1)
        for key in [u'i']:
            if key in hsh_cpy:
                del hsh_cpy[key]
        form = getEditForm(
            self.parent(),
            instance='edit',
            hsh=hsh_cpy,
            receiver=self.receiver)
        if form:
            form.setWindowTitle(
                "{0}: {1}".format(
                    self.tr("copy"),
                    self.hsh['_filetext']))
            form.rev_hsh = {}
            form.rev_str = ''
            form.filename = None
            form.hsh = None
            # do this in editform
            form.editor.setPlainText(self.hsh['entry'])
            form.show()
            self.close()
            form.raise_()
            form.setFocus()

    def clone_action(self):
        if self.parent().timer_status != 'stopped':
            return(False)
        # action = 'copy'
        hsh_cpy = deepcopy(self.hsh)
        hsh_cpy['fileinfo'] = (self.hsh['fileinfo'][0], -1, -1)
        if u'i' in hsh_cpy:
            del hsh_cpy[u'i']
        hsh_cpy['itemtype'] = '~'
        hsh_cpy['s'] = datetime.now()
        hsh_cpy['e'] = timedelta(seconds=0)
        if self.hsh['itemtype'] == u'~':
            if self.hsh['s'].date() == datetime.now().date():
                # copy or restart
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Question)
                msgBox.setText(self.tr("action"))
                msgBox.setInformativeText("""\
Restart the timer for the existing action (yes) or create a new timer (no)?""")
                msgBox.setStandardButtons(
                    QMessageBox.Cancel | QMessageBox.No | QMessageBox.Yes)
                msgBox.setDefaultButton(QMessageBox.Yes)
                reply = msgBox.exec_()
                if reply == QMessageBox.Cancel:
                    return(False)
                if reply == QMessageBox.Yes:
                    # restore current values
                    for key in [u's', u'e', u'fileinfo']:
                        hsh_cpy[key] = self.hsh[key]
                    self.parent().timer_hsh = hsh_cpy
        else:  # not an action
            for key in [u'r', u'rrule', u'_r', u'p', u'q', u'+', u'-']:
                if key in hsh_cpy:
                    del hsh_cpy[key]
            self.parent().timer_subject = hsh2str(
                hsh_cpy, self.parent().options)
        self.parent().timer_hsh = hsh_cpy
        self.parent().timer_subject = hsh_cpy['_summary']
        self.parent().timer_status_hsh['summary'] = hsh_cpy['_summary']
        self.parent().timer_tooltip = "{0}: '{1}'".format(
            self.tr('active timer'), self.parent().timer_subject)
        self.parent().newActionButton.setToolTip(self.parent().timer_tooltip)
        self.cloneActionButton.setToolTip(self.parent().timer_tooltip)
        self.parent().timer_delta = hsh_cpy['e']
        self.parent().timer_status = 'paused'
        self.parent().newActionButton.setEnabled(False)
        self.parent().stopButton.show()
        self.parent().timerLabel.show()
        self.parent().pause_restartButton.show()
        self.parent().getTimer()
        self.parent().timer_toggle()
        self.close()

    def close(self):
        self.reject()

    def minimumSizeHint(self):
        font = QFont(self.font())
        font.setPointSize(font.pointSize())
        fm = QFontMetricsF(font)
        return QSize(300, (fm.height() * 3))


def tr(string):
    return(QApplication.translate('etmEditor', string))


def getEditForm(
    parent, instance=None, hsh=None, filename=None,
        receiver=None, highlight=True, use_completer=True, options={}):
    msg_hsh = {
        'scratch': tr('%s is already open' % filename),
        'config': tr('%s is already open' % filename),
        'complete': tr('%s is already open' % filename),
        'report': tr('%s is already open' % filename),
    }
    # 'file' will be set for finish, move, remove when the form will not
    # be opened
    # 'edit' will be set for edit item, edit file, and stop timer

    if instance in msg_hsh.keys() and instance in parent.editor_instances:
        QMessageBox.warning(parent, "etm", msg_hsh[instance])
        return(None)
    elif (instance in ['file', 'edit', 'recent'] and
            ('file' in parent.editor_instances or
                'edit' in parent.editor_instances or
                'recent' in parent.editor_instances)):
        if instance == 'file':
            if 'file' in parent.editor_instances:
                msg = tr("""\
Another file operation is in process and must be completed before
this can be done.""")
            else:  # edit
                msg = tr('The editor must be closed before this can be done.')
        else:  # edit
            if 'file' in parent.editor_instances:
                msg = tr("""\
A file operation is in process and must be completed before
the editor can be opened.""")
            else:  # edit
                msg = tr("""\
Only once instance of the editor can be open at one time.""")
        QMessageBox.warning(parent, "etm", msg)
        return(None)
    else:
        form = EditForm(
            parent=parent,
            instance=instance,
            filename=filename,
            hsh=hsh,
            receiver=receiver,
            highlight=highlight,
            use_completer=use_completer)
        form.resize(
            parent.options['window_width'],
            parent.options['window_height'] - 30)
        return(form)

if qt_version == 5:
    from etmQt.ui5.ui_etmEditor import Ui_editDialog as Edit_Dialog
else:
    from etmQt.ui4.ui_etmEditor import Ui_editDialog as Edit_Dialog


class EditForm(QMainWindow, Edit_Dialog):
    def __init__(
            self, parent=None, instance=None, filename=None, hsh=None,
            receiver=None, highlight=True, use_completer=True):
        super(EditForm, self).__init__(parent)
        self.setAttribute(Qt.WA_GroupLeader)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowIcon(QIcon(":/etmlogo.png"))
        self.parent = weakref.ref(parent)
        self.options = self.parent().options
        self.instance = instance
        self.parent().editor_instances.add(instance)
        self.recent_edits = self.parent().recent_edits
        self.now = self.parent().now
        self.setStyleSheet(
            'font-size: %dpt' % self.parent().options['fontsize'])
        self.receiver = receiver
        self.highlight = highlight  # turn this off for scratchpad
        self.setupUi(self)
        self.hsh = hsh
        self.rev_hsh = {}
        self.rev_id = ''
        self.rev_str = ''
        self.new_id = ''
        self.new_str = ''
        self.mode = ''
        self.filename = filename
        self.helpPage = 1
        self.printer = None

        self.suggested_file = None
        self.editLayout = QVBoxLayout(self.editFrame)

        self.helpButton.clicked.connect(self.editHelp)
        self.search.returnPressed.connect(self.doFind)

        QShortcut(QKeySequence(Qt.Key_F1), self, self.editHelp)
        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_I), self, self.insertScratchPad)
        multiple_whitespace_regex = re.compile(r' {2,}|\t+')

        self.editor = CompletionTextEdit(self.parent())
        if ('auto_completions' in self.parent().options and
                self.parent().options['auto_completions'] and
                os.path.isfile(self.parent().options[
                    'auto_completions'])):
            try:
                words = []
                f = open(self.parent().options['auto_completions'], "r")
                for word in f.readlines():
                    if word[0] == '#':
                        continue
                    word = multiple_whitespace_regex.sub(' ', word).strip()
                    if python_version2 and qt_version == 4:
                        words.append(u'%s' % word.decode(encoding))
                    else:
                        words.append(word)

                f.close()
            except IOError:
                print("dictionary not in anticipated location")
        else:
            words = []
            self.showStatusMessage(
                self.tr("'auto_completions' not found or empty"))

        if words:
            completer = DictionaryCompleter(words=words)
            self.editor.setCompleter(completer)

        if highlight:
            self.highlighter = PHL(self.editor.document())

        self.editor.setTabStopWidth(4)
        self.editLayout.addWidget(self.editor, 0)
        self.editLayout.setContentsMargins(QMargins(0, 0, 0, 0))

        self.next.clicked.connect(self.doFind)
        self.previous.clicked.connect(self.doFindBackwards)

        self.saveButton.clicked.connect(self.fileSave)
        self.quitButton.clicked.connect(self.close)

        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_W), self, self.close)
        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_Return), self, self.fileSaveAndClose)
        self.copyButton.clicked.connect(self.editor.copy)
        self.cutButton.clicked.connect(self.editor.cut)
        self.pasteButton.clicked.connect(self.editor.paste)

        self.editor.selectionChanged.connect(self.updateUi)
        self.editor.document().modificationChanged.connect(self.updateUi)
        QApplication.clipboard().dataChanged.connect(self.updateUi)

        QShortcut(QKeySequence(
            Qt.CTRL + Qt.Key_S), self, self.fileSave)
        QShortcut(QKeySequence(
            Qt.CTRL + Qt.Key_R), self, self.reloadFile)

        QShortcut(QKeySequence(
            Qt.CTRL + Qt.Key_F), self, self.openSearch)
        QShortcut(QKeySequence(
            Qt.Key_Escape), self, self.closeSearch)

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Z), self, self.updateUi)

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_G), self, self.doFind)

        QShortcut(QKeySequence(
            Qt.SHIFT + Qt.CTRL + Qt.Key_G), self, self.doFindBackwards)

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_P), self, self.printText)

        self.resize(460, 420)

        if self.hsh and '_linenum' in self.hsh:
            self.linenum = self.hsh['_linenum']
        else:
            self.linenum = 1
        if self.filename is not None:
            self.loadFile()
            if self.linenum:
                cursor = self.editor.textCursor()
                cursor.movePosition(
                    QTextCursor.Down, QTextCursor.MoveAnchor,
                    self.linenum - 1)
                self.editor.setTextCursor(cursor)
        self.updateUi()
        self.inSearch = False
        self.editor.setFocus(True)

    def insertScratchPad(self):
        lines = []
        try:
            fh = QFile(self.parent().options['scratchfile'])
            if not fh.open(QIODevice.ReadOnly):
                raise IOError  # as unicode(fh.errorString())
            stream = QTextStream(fh)
            stream.setCodec(encoding)
            contents = stream.readAll()
        except (IOError, OSError) as e:
            QMessageBox.warning(
                self, "etm -- read Error",
                "Failed to read {0}: {1}".format(self.filename, e))
        finally:
            if fh is not None:
                fh.close()
        if contents:
            lines = [unicode(x) for x in contents.split('\n')]
        self.editor.insertPlainText("\n".join(lines))

    def printText(self):
        font = QFont(self.font())
        font.setPointSize(font.pointSize() - 3)

        self.document = QTextDocument()
        self.document.setDefaultFont(font)
        self.document.setPlainText(self.editor.toPlainText())

        if self.printer is None:
            self.printer = QPrinter(QPrinter.HighResolution)
            self.printer.setPageSize(QPrinter.Letter)

        form = QPrintDialog(self.printer, self)
        if form.exec_():
            self.document.print_(self.printer)

    def copy(self):
        print("copy")

    def cut(self):
        print("cut")

    def paste(self):
        print("paste")

    def setEditInfo(self, rev_id, rev_str, new_id):
        self.rev_id = rev_id
        self.rev_str = rev_str
        self.new_id = new_id

    def openSearch(self):
        self.inSearch = True
        self.search.clear()
        self.search.setFocus()

    def closeSearch(self):
        if self.inSearch:
            self.inSearch = False
            self.search.clear()
            self.editor.setFocus()

    def doFindBackwards(self):
        return self.doFind(backwards=True)

    def doFind(self, backwards=False):
        self.editor.setFocus()
        self.inSearch = True
        flags = QTextDocument.FindFlags()
        if backwards:
            where = self.tr("backward")
            flags = QTextDocument.FindBackward
        else:
            where = self.tr("forward")

        text = unicode(self.search.text())
        if not text:
            self.closeSearch()
            return()

        r = self.editor.find(text, flags)
        if r:
            self.clearStatusMessage()
        else:
            self.showStatusMessage(
                "{0} {1}".format(self.tr("not found"), where))

    def showStatusMessage(self, message):
        self.statusBar.showMessage(message, 2000)

    def clearStatusMessage(self):
        self.statusBar.clearMessage()

    def updateUi(self, arg=None):
        # FIXME: self has no attribute editor
        modified = self.editor.document().isModified()
        self.saveButton.setEnabled(modified)
        enable = self.editor.textCursor().hasSelection()
        self.copyButton.setEnabled(enable)
        self.cutButton.setEnabled(enable)
        self.pasteButton.setEnabled(self.editor.canPaste())

    def closeEvent(self, event):
        if not self.okToContinue():
            event.ignore()
        self.parent().editor_instances.discard(self.instance)

    def okToContinue(self):
        if self.editor.document().isModified():
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setWindowModality(Qt.ApplicationModal)
            msgBox.setText(self.tr("The document has been modified."))
            msgBox.setInformativeText(
                self.tr("Do you want to verify and save your changes?"))
            msgBox.setStandardButtons(
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Save)
            reply = msgBox.exec_()
            if reply == QMessageBox.Save:
                return self.fileSave()
            elif reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Discard:
                return True
        return True

    def fileNew(self):
        if not self.okToContinue():
            return
        document = self.editor.document()
        document.clear()
        document.setModified(False)
        self.filename = None
        self.setWindowTitle("etm - new item")
        self.updateUi()

    def getLinesFromFile(self, filename):
        if not os.path.isfile(filename):
            # this is a new file
            return([])
        fh = None
        contents = None
        try:
            fh = QFile(filename)
            if not fh.open(QIODevice.ReadOnly):
                raise IOError  # as unicode(fh.errorString())
            stream = QTextStream(fh)
            stream.setCodec(encoding)
            contents = stream.readAll()
        except (IOError, OSError) as e:
            QMessageBox.warning(
                self, "etm -- read Error",
                "Failed to read {0}: {1}".format(filename, e))
        finally:
            if fh is not None:
                fh.close()
        if not contents:
            return([])
        lines = [unicode(x) for x in contents.split('\n')]
        return(lines)

    def writeLinesToFile(self, filename, lines, senddone=True):
        filename = str(filename)
        fh = None
        filestr = "\n".join(lines)  # \n's are already appended to each line
        # make sure the file has a trailing newline
        filestr = "%s\n" % filestr.strip()
        try:
            # then update the file
            fh = QFile(filename)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError  # unicode(fh.errorString())
            stream = QTextStream(fh)
            stream.setCodec(encoding)
            stream << filestr
            self.editor.document().setModified(False)
            # ret = [self.filename]
            tup = (relpath(
                filename,
                self.parent().options['datadir']),
                self.now.strftime(self.parent().options['etmdatetimefmt']))
            if tup not in self.recent_edits:
                self.recent_edits.insert(0, tup)
                del self.recent_edits[10:]
        except (IOError, OSError) as e:
            QMessageBox.warning(
                self, "etm -- Save Error",
                "Failed to save {0}: {1}".format(self.filename, e))
            return False
        finally:
            if fh is not None:
                fh.flush()
                fh.close()
        # update etmView
        if senddone and self.receiver:
            self.receiver(filename)

        if 'hg_commit' in self.parent().options:
            # hack to avoid unicode in .format() for python 2
            mesg = u"{0}: {1}".format(self.mode, filename)
            if python_version == 2 and type(mesg) == unicode:
                command = self.parent().options['hg_commit'].format(
                    repo=self.parent().options['datadir'], mesg="XXX")
                command = command.replace("XXX", mesg)
            else:
                command = self.parent().options['hg_commit'].format(
                    repo=self.parent().options['datadir'],
                    mesg=mesg)
            process = QProcess()
            process.startDetached(command)
        self.showStatusMessage(self.tr("changes saved"))
        return True

    def replaceLinesInFile(
            self, filename=None, begline=None, endline=None,
            newlines=None, senddone=True):
        lines = self.getLinesFromFile(filename)
        del lines[begline - 1:endline]
        newlines.reverse()
        for x in newlines:
            lines.insert(begline - 1, x)
        self.mode = self.tr("replaced lines")
        return self.writeLinesToFile(filename, lines, senddone)

    def addLinesToFile(self, filename=None, newlines=None, senddone=True):
        lines = self.getLinesFromFile(filename)
        if len(lines) > 1:
            while len(lines) > 1 and not lines[-1]:
                lines.pop(-1)
            lastline = len(lines)
        else:
            lastline = 0
        newlines.reverse()
        for x in newlines:
            lines.insert(lastline, x)
        self.hsh['fileinfo'] = (relpath(filename), lastline + 1, len(lines))

        self.mode = self.tr("added lines")
        return self.writeLinesToFile(filename, lines, senddone)

    def removeLinesFromFile(
            self, filename=None, begline=None, endline=None, senddone=True):
        orig_lines = self.getLinesFromFile(filename)
        del orig_lines[begline - 1:endline]
        self.mode = self.tr("removed lines")
        return self.writeLinesToFile(filename, orig_lines, senddone)

    def loadFile(self):
        if not self.filename or not os.path.isfile(self.filename):
            return(False)
        fh = None
        try:
            fh = QFile(self.filename)
            if not fh.open(QIODevice.ReadOnly):
                raise IOError  # unicode(fh.errorString())
            stream = QTextStream(fh)
            stream.setCodec(encoding)
            contents = stream.readAll()
            self.editor.setPlainText(contents)
            self.editor.document().setModified(False)
        except (IOError, OSError) as e:
            QMessageBox.warning(
                self, "etm -- Load Error",
                "Failed to load {0}: {1}".format(self.filename, e))
        finally:
            if fh is not None:
                fh.close()
        self.setWindowTitle("editor - {0}".format(
            QFileInfo(self.filename).fileName()))

    def reloadFile(self):
        if not self.filename or not os.path.isfile(self.filename):
            return(False)
        fh = None
        try:
            fh = QFile(self.filename)
            if not fh.open(QIODevice.ReadOnly):
                raise IOError  # unicode(fh.errorString())
            stream = QTextStream(fh)
            stream.setCodec(encoding)
            contents = stream.readAll()
            self.editor.setPlainText(contents)
            self.editor.document().setModified(False)
        except (IOError, OSError) as e:
            QMessageBox.warning(
                self, "etm -- Load Error",
                "Failed to load {0}: {1}".format(self.filename, e))
        finally:
            if fh is not None:
                fh.close()

    def fileSaveAndClose(self):
        self.fileSave()
        self.close()

    def fileSave(self):
        if self.filename is None and self.hsh is None:
            # return the result from calling fileSaveAs
            return self.fileSaveAs()

        if self.filename is None:
            # we're editing an item not a file
            new_str = unicode(self.editor.toPlainText())
            new_hsh, msg = str2hsh(new_str, options=self.parent().options)
            if msg:
                QMessageBox.warning(
                    self, 'etm -- error', "\n".join(msg))
                return(False)

            if 's' in new_hsh and new_hsh['itemtype'] in ['*']:
                h = new_hsh['s'].hour
                m = new_hsh['s'].minute
                if 0 <= h <= 6 and not (h == 0 and m == 0):
                    msgBox = QMessageBox()
                    msgBox.setIcon(QMessageBox.Question)
                    msgBox.setText(self.tr("Please verify"))
                    msgBox.setInformativeText(
                        "Do you really want to schedule this for %s?" %
                        fmt_time(new_hsh['s'], options=self.parent().options))
                    msgBox.setStandardButtons(
                        QMessageBox.Save | QMessageBox.Cancel)
                    msgBox.setDefaultButton(QMessageBox.Save)
                    reply = msgBox.exec_()
                    if reply == QMessageBox.Cancel:
                        return(False)

            new_str = hsh2str(new_hsh, self.parent().options)
            self.editor.setPlainText(new_str)
            self.new_str = new_str
            fn, begline, endline = self.hsh['fileinfo']
            filename = self.hsh['_filename']
            editlines = [unicode(x) for x in self.new_str.split('\n')]
            newlines = editlines
            if begline >= 0:
                rev_str = str(self.rev_str).strip()
                if rev_str:
                    # revlines = map(str, self.rev_str.split('\n'))
                    revlines = [str(x) for x in self.rev_str.split('\n')]
                else:
                    revlines = []
                return self.replaceLinesInFile(
                    filename, begline, endline, revlines + newlines)
            else:
                return self.addLinesToFile(filename, newlines)
        else:  # we are editing the entire file
            self.mode = self.tr("edited file")
            filename = self.filename
            contents = self.editor.toPlainText()
            lines = [unicode(u'%s') % x for x in contents.split('\n')]
            if self.highlight:
                messages = process_lines(lines, self.parent().options)
            else:
                messages = []
            if messages:
                QMessageBox.warning(
                    self, 'etm -- error', "\n".join(messages))
            else:
                return self.writeLinesToFile(filename, lines)

    def getFileName(self, hsh={}):
        datadir = self.parent().options['datadir']
        if hsh and 's' in hsh and hsh['s']:
            # make sure the relevant monthly file exists
            currfile = ensureMonthly(self.parent().options, hsh['s'])
        else:
            currfile = self.suggested_file
        which = WhichForm(self, 'file', (datadir, currfile))
        which.setWindowTitle(self.tr('select file'))
        if not which.exec_():
            self.which_file = ''
            return('')
        return(self.which_file)

    def fileSaveAs(self):
        new_str = unicode(self.editor.toPlainText())
        new_hsh, msg = str2hsh(
            new_str, options=self.parent().options)
        if msg:
            print('msg', type(msg), msg)
            QMessageBox.warning(
                self, 'etm -- error', "\n".join(msg))
            return(False)
        new_str = hsh2str(new_hsh, self.parent().options)
        self.editor.setPlainText(new_str)
        self.new_str = new_str
        filename = self.getFileName(new_hsh)
        if not filename:
            return(False)
        self.hsh = {}
        self.filename = None
        self.hsh['_filename'] = filename
        self.hsh['fileinfo'] = (filename, -1, -1)
        self.setWindowTitle("etm - {0}".format(
            QFileInfo(filename).fileName()))
        fn, begline, endline = self.hsh['fileinfo']
        filename = self.hsh['_filename']
        editlines = [unicode(x) for x in self.new_str.split('\n')]
        newlines = editlines
        return self.addLinesToFile(filename, newlines)

    def editHelp(self):
        form = HelpForm(self.parent(), self.helpPage)
        form.setWindowTitle('etm')
        form.show()

    def setFocus(self):
        self.editor.setFocus(True)


class TreeFilter(QSortFilterProxyModel):
    '''
        Show the entire path to a match and all children.
    '''

    def __init__(self, parent=None):
        super(TreeFilter, self).__init__(parent)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        model = self.sourceModel()
        sourceIndex = model.index(sourceRow, 0, sourceParent)

        if self.filterAcceptsRowItself(sourceRow, sourceParent):
            return True

        parent = sourceIndex
        while parent.isValid():
            if self.filterAcceptsRowItself(parent.row(), parent.parent()):
                return(True)
            parent = parent.parent()
        return self.hasAcceptedChildren(sourceRow, sourceParent)

    def filterAcceptsRowItself(self, sourceRow, sourceParent):
        return(super(
            TreeFilter, self).filterAcceptsRow(sourceRow, sourceParent))

    def hasAcceptedChildren(self, sourceRow, sourceParent):
        model = self.sourceModel()
        sourceIndex = model.index(sourceRow, 0, sourceParent)
        if not sourceIndex.isValid():
            return False
        indexes = model.rowCount(sourceIndex)
        for i in range(indexes):
            if self.filterAcceptsRow(i, sourceIndex):
                return True
        return False

if qt_version == 5:
    from etmQt.ui5.ui_etmReport import Ui_reportDialog as Report_Dialog
else:
    from etmQt.ui4.ui_etmReport import Ui_reportDialog as Report_Dialog


class ReportForm(QDialog, Report_Dialog):
    def __init__(self, parent=None, colors=2):
        super(ReportForm, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_GroupLeader)
        self.parent = weakref.ref(parent)
        self.setStyleSheet(
            'font-size: %dpt' % self.parent().options['fontsize'])
        self.colors = colors
        self.printer = None
        self.inSearch = False
        self.setupUi(self)
        self.modified = False
        self.saveButton.setEnabled(False)
        self.resize(520, 340)
        reports = []
        if ('report_specifications' in self.parent().options and
                self.parent().options['report_specifications'] and
                os.path.isfile(self.parent().options['report_specifications'])):
            try:
                fo = codecs.open(
                    self.parent().options['report_specifications'],
                    'r', file_encoding)
                for line in fo.readlines():
                    if line[0] != "#":
                        reports.append(QString(line.strip()))
            except IOError:
                print("reports file not in anticipated location")
            finally:
                if fo:
                    fo.close()

        self.reportBox.lineEdit().setTextMargins(4, 0, 4, 0)
        # add a filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel(self.reportBox)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseSensitive)
        self.pFilterModel.setSourceModel(self.reportBox.model())

        # add a completer, which uses the filter model
        self.completer = QCompleter(self.pFilterModel)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.reportBox.setCompleter(self.completer)

        # connect signals
        self.reportBox.lineEdit().textEdited[unicode].connect(
            self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

        # self.reportBox.currentIndexChanged.connect(self.indexChanged)
        # self.connect(self.reportBox, SIGNAL(
        #     "currentIndexChanged(int)"), self.indexChanged)

        self.reportBox.editTextChanged.connect(self.textChanged)
        # self.connect(self.reportBox, SIGNAL(
        #     "editTextChanged(QString)"), self.textChanged)

        self.reportBox.activated.connect(self.activated)
        # self.connect(self.reportBox, SIGNAL(
        #     "activated(QString)"), self.activated)
        self.search.returnPressed.connect(self.doFind)
        # self.connect(self.search, SIGNAL(
        #     "returnPressed()"), self.doFind)

        self.closeButton.clicked.connect(self.close)
        # self.connect(
        #     self.closeButton, SIGNAL("clicked()"), self.close)
        self.printButton.clicked.connect(self.printReport)
        # self.connect(
        #     self.printButton, SIGNAL("clicked()"), self.printReport)
        self.exportButton.clicked.connect(self.exportReport)
        # self.connect(
        #     self.exportButton, SIGNAL("clicked()"), self.exportReport)
        self.reportButton.clicked.connect(self.createReport)
        # self.connect(
        #     self.reportButton, SIGNAL("clicked()"), self.createReport)
        self.saveButton.clicked.connect(self.saveReports)
        # self.connect(
        #     self.saveButton, SIGNAL("clicked()"), self.saveReports)
        self.minusButton.clicked.connect(self.reportRemove)
        # self.connect(
        #     self.minusButton, SIGNAL("clicked()"), self.reportRemove)
        self.mailButton.clicked.connect(self.mailReport)
        # self.connect(
        #     self.mailButton, SIGNAL("clicked()"), self.mailReport)

        self.helpButton.clicked.connect(self.helpReport)
        # self.connect(self.helpButton, SIGNAL("clicked()"), self.helpReport)

        self.next.clicked.connect(self.doFind)
        self.previous.clicked.connect(self.doFindBackwards)

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_P), self, self.printReport)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_R), self, self.createReport)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_S), self, self.saveReports)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_L), self, self.showPopup)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_D), self, self.reportRemove)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_E), self, self.exportReport)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_M), self, self.mailReport)
        QShortcut(QKeySequence(
            Qt.SHIFT + Qt.CTRL + Qt.Key_R), self,
            self.parent().editReportSpecs)

        QShortcut(QKeySequence(Qt.Key_F1), self, self.helpReport)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_W), self, self.close)

        self.closeButton.clicked.connect(self.close)
        # QObject.connect(self.closeButton, SIGNAL("clicked()"), self.close)
        self.reportBox.addItems(reports)
        self.reportCount = self.reportBox.count()

        # self.reportBox.lineEdit().selectAll()

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_F), self, self.openSearch)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_G), self, self.doFind)
        QShortcut(QKeySequence(
            Qt.SHIFT + Qt.CTRL + Qt.Key_G), self, self.doFindBackwards)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.closeSearch)
        self.reportBox.setFocus()

    def showPopup(self):
        self.reportBox.showPopup()

    def createReport(self):
        opstr = self.reportBox.lineEdit().text()
        try:
            self.html, count2id = getReportData(
                opstr, self.parent().file2uuids,
                self.parent().uuid2hash, self.parent().options)
        except:
            self.html = ['<font color="red">Could not process &ldquo;%s&rdquo;</quote></font>.' % opstr]
        self.setHtml("<pre>%s</pre>" % "\n".join(self.html))
        self.showStatusMessage(self.tr('done'))

    def exportReport(self):
        opstr = self.reportBox.lineEdit().text()
        rows, count2id = getReportData(
            opstr, self.parent().file2uuids,
            self.parent().uuid2hash, self.parent().options, True)
        filename, pat = QFileDialog.getSaveFileNameAndFilter(
            self, 'Save File', '.', filter=self.tr("CSV files (*.csv)"),
            options=QFileDialog.DontUseNativeDialog)
        if filename:
            fname = open(filename, 'w')
            w = csv.writer(fname)
            w.writerows(rows)
            fname.close()

    def closeEvent(self, event):
        if self.okToContinue():
            self.modified = False
        else:
            event.ignore()

    def on_completer_activated(self, text):
        if text:
            index = self.reportBox.findText(text)
            self.reportBox.setCurrentIndex(index)
            self.reportBox.activated[str].emit(self.reportBox.itemText(index))

    def activated(self, text=''):
        if self.reportBox.lineEdit().isModified():
            self.reportBox.lineEdit().setModified(False)
            self.reportBox.lineEdit().setStyleSheet(QString(""))
            self.reportBox.setToolTip(
                self.tr('Press Ctrl-R to\ncreate report.'))
        if self.reportBox.count() != self.reportCount:
            self.modified = True
            self.saveButton.setEnabled(True)
            # self.createReport()

    def textChanged(self, text):
        if self.reportBox.lineEdit().isModified():
            self.reportBox.lineEdit().setStyleSheet(
                QString("""\
background: lightgoldenrodyellow; font-size: 14pt; font-family: \
CourierNewPSMT"""))
            self.reportBox.setToolTip(
                self.tr("""\
Press return to make modification\ntemporarily available."""))
        else:
            self.reportBox.lineEdit().setStyleSheet(
                QString("""\
background: transparent; font-size: 14pt; font-family: CourierNewPSMT"""))
            self.reportBox.setToolTip(
                self.tr('Press Ctrl-R to\ncreate report.'))
        return(True)

    def okToContinue(self):
        if self.modified:
            msgBox = QMessageBox(self)
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setWindowModality(Qt.ApplicationModal)
            msgBox.setText(self.tr("The list of reports has been modified."))
            msgBox.setInformativeText(
                self.tr("Do you want to save the changes?"))
            msgBox.setStandardButtons(
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Save)
            reply = msgBox.exec_()
            # reply = msgBox.show()
            if reply == QMessageBox.Cancel:
                return(False)
            elif reply == QMessageBox.Save:
                self.modified = False
                return(self.saveReports())
            else:
                return(True)
        return True

    def saveReports(self):
        res = False
        if self.modified:
            items = [str(
                self.reportBox.itemText(i)) for
                i in range(self.reportBox.count())]
            try:
                fo = codecs.open(
                    self.parent().options['report_specifications'],
                    'w', file_encoding)
                for item in items:
                    fo.write("%s\n" % item)
                self.saveButton.setEnabled(False)
                self.modified = False
                res = True
            except IOError:
                print("reports file not in anticipated location")
            finally:
                if fo:
                    fo.close()
            return(res)

    def reportRemove(self):
        index = self.reportBox.currentIndex()
        text = self.reportBox.itemText(index)
        curr_text = self.reportBox.lineEdit().text()
        if text == curr_text:
            # only remove the item is the displayed value is the same as
            # the stored value
            self.reportBox.removeItem(index)
            self.modified = True
        else:
            # restore the stored value
            self.reportBox.lineEdit().setText(text)

    def setHtml(self, html):
        self.html = html
        htmlfont = self.parent().options['fontsize'] + 1
        self.reportBrowser.setStyleSheet('font-size: %dpt' % htmlfont)
        self.reportBrowser.setHtml(html)

    def helpReport(self):
        form = HelpForm(parent=self.parent(), page=3)
        form.setWindowTitle('etm')
        form.show()

    def printReport(self):
        self.document = QTextDocument()
        font = QFont()
        font.setPointSize(10)
        self.document.setDefaultFont(font)
        self.document.setHtml(self.html)

        if self.printer is None:
            self.printer = QPrinter(QPrinter.HighResolution)
            self.printer.setPageSize(QPrinter.Letter)
        form = QPrintDialog(self.printer, self)
        if form.exec_():
            self.document.print_(self.printer)

    def mailReport(self):
        to, ok = QInputDialog.getText(
            self, self.tr("send email"),
            "%s" % self.tr("comma separated email addresses:"),
            QLineEdit.Normal,
            self.parent().options['smtp_to'])
        if ok:
            self.to = str(to).rsplit(',\s*')
            self.showStatusMessage(self.tr('sending ...'))
            QTimer.singleShot(1000, self.send)

    def send(self):
        mail_report(
            self.html,
            smtp_from=self.parent().options['smtp_from'],
            smtp_server=self.parent().options['smtp_server'],
            smtp_id=self.parent().options['smtp_id'],
            smtp_pw=self.parent().options['smtp_pw'],
            smtp_to=self.to)
        self.status_message.setText(self.tr('sent'))
        QTimer.singleShot(3000, self.clearStatusMessage)
        return(True)

    def showStatusMessage(self, message):
        self.status_message.setText(message)
        QTimer.singleShot(3000, self.clearStatusMessage)

    def clearStatusMessage(self):
        self.status_message.setText('')

    def doFindBackwards(self):
        return self.doFind(backwards=True)

    def doFind(self, backwards=False):
        self.inSearch = True
        flags = QTextDocument.FindFlags()
        if backwards:
            where = self.tr("backward")
            flags = QTextDocument.FindBackward
        else:
            where = self.tr("forward")

        text = unicode(self.search.text())
        if not text:
            self.closeSearch()
            return()

        r = self.reportBrowser.find(text, flags)
        if r:
            self.clearStatusMessage()
        else:
            self.showStatusMessage(
                "{0} {1}".format(self.tr("not found"), where))

    def openSearch(self):
        self.inSearch = True
        self.search.clear()
        self.search.setFocus()

    def closeSearch(self):
        if self.inSearch:
            self.inSearch = False
            self.search.clear()
            self.reportBox.setFocus()

    def find(self):
        if self.search.hasFocus():
            self.doFind()
        # elif self.reportBox.hasFocus():

if qt_version == 5:
    from etmQt.ui5.ui_etmCalendars import Ui_Dialog as Calendars_Dialog
else:
    from etmQt.ui4.ui_etmCalendars import Ui_Dialog as Calendars_Dialog


class CalendarsForm(QDialog, Calendars_Dialog):
    def __init__(self, parent=None):
        super(CalendarsForm, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.parent = weakref.ref(parent)
        self.setStyleSheet(
            'font-size: %dpt' % self.parent().options['fontsize'])
        self.setupUi(self)
        vbox = QVBoxLayout()
        self.labelChecked = []

        for label, checked, path in self.parent().calendars:
            checkbox = QCheckBox("%s" % label)
            checkbox.setChecked(checked)
            self.labelChecked.append((label, checkbox))
            vbox.addWidget(checkbox)
        vbox.addStretch(1)
        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_W), self, self.close)

        self.calendarBox.setLayout(vbox)

    def accept(self):
        calendars = self.parent().calendars
        for i in range(len(self.labelChecked)):
            checked = self.labelChecked[i][1].isChecked()
            calendars[i][1] = checked
        self.parent().calendars = calendars
        self.done(1)


class WeekView(QWidget):
    XMARGIN = 8
    YMARGIN = 4
    WSTRING = " 99 MMM "
    INDENT = "999999"
    DFLTCOLOR = QColor(0, 0, 255, 60)
    OTHRCOLOR = QColor(0, 140, 0, 60)

    doubleclicked = pyqtSignal(str, str)

    def __init__(self, parent=None, uuid2hash=None):
        super(WeekView, self).__init__(parent)
        self.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.parent = weakref.ref(parent)
        self.uuid2hash = uuid2hash
        self.indent_width = 0
        self.font_delta = 1
        self.day = None
        self.time = None
        self.uuid = None
        self.setMouseTracking(1)
        self.printer = QPrinter()

        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_B), self, self.showBusyTimes)

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        font = QFont(self.font())
        font.setPointSize(font.pointSize() - self.font_delta)
        fm = QFontMetricsF(font)
        self.fm = fm
        self.indent_width = fm.boundingRect(WeekView.INDENT).width()
        return QSize(fm.width(WeekView.WSTRING) * 7, (fm.height() * 16))

    def getDetails(self, event):
        x = event.x()
        segHeight = self.height() / 17
        y = event.y() - segHeight
        y = max(0.0, min(y, 16 * segHeight))
        minutes = 420 + round(60 * y / segHeight)
        fivemins = round(minutes / 5.0)
        minutes = int(fivemins * 5)
        hours = minutes // 60
        mins = minutes % 60
        # y_mins = round(((minutes - 420)*18*segHeight)/16.0 * 60.0)
        span = self.width() - (WeekView.XMARGIN * 2 + self.indent_width)
        # offset = span - x + WeekView.XMARGIN
        numerator = int(
            round(.5 + (7 * (x - WeekView.XMARGIN - self.indent_width) / span)))
        day = max(1, min(numerator, 7)) - 1
        self.dayhourmin = '%s:%s:%s' % (day, hours, mins)
        id = ''
        summary = ''
        occasions = "\n".join([xx[1] for xx in self.occasion_lst[day]])
        for (s, e, i, summary, f, mtch) in self.busy_lst[day]:
            if minutes >= s and minutes <= e:
                id = i
                hours = s // 60
                mins = s % 60
                self.dayhourmin = '%s:%s:%s' % (day, hours, mins)
                break
            # id = ''
        self.day = day
        self.time = "%s:%02d" % (hours, mins)
        self.uuid = id
        return(id, summary, occasions)

    def mouseMoveEvent(self, event):
        id, summary, occasions = self.getDetails(event)
        if id and id in self.uuid2hash:
            QToolTip.showText(event.globalPos(), summary)
        elif occasions:
            QToolTip.showText(event.globalPos(), occasions)
        else:
            # TODO: maybe insert occasion info here?
            QToolTip.showText(event.globalPos(), '')

    def mouseDoubleClickEvent(self, event):
        if event.button() != Qt.LeftButton:
            event.accept()
        else:
            self.doubleclicked.emit(self.dayhourmin, self.uuid)

    def keyPressEvent(self, event):
        QWidget.keyPressEvent(self, event)

    def setWeekdays(
            self, day_lst, busy_lst, occasion_lst, today_col=0,
            curr_minutes=0):
        self.weekdays = day_lst
        self.busy_lst = busy_lst
        self.occasion_lst = occasion_lst
        self.today_col = today_col
        self.curr_minutes = curr_minutes
        self.update()

    def paintEvent(self, event=None):
        font = QFont(self.font())
        font.setPointSize(font.pointSize() - self.font_delta)
        # fm = QFontMetricsF(font)
        span = self.width() - (WeekView.XMARGIN * 2 + self.indent_width)
        painter = QPainter(self)
        painter.setFont(font)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setPen(self.palette().color(QPalette.Mid))
        segColor = QColor(Qt.blue).darker(120)
        segLineColor = segColor.darker()
        lineColor = QColor(Qt.gray).darker(90)
        painter.setPen(segLineColor)
        segWidth = span / 7
        num_hours = 16
        segHeight = self.height() / (num_hours + 1)
        y = segHeight
        painter.drawRect(WeekView.XMARGIN + self.indent_width,
                         segHeight, span, (num_hours) * segHeight)
        textColor = self.palette().color(QPalette.Text)
        rect = QRectF(0, 0, span, segHeight)
        x = WeekView.XMARGIN + self.indent_width
        nRect = QRectF(0, 0, segWidth, segHeight)
        x = WeekView.XMARGIN + self.indent_width
        painter.setBrush(segColor)
        x = WeekView.XMARGIN + self.indent_width
        for i in range(1, 7 + 1):
            painter.setPen(textColor)
            rect = QRectF(nRect)
            rect.moveCenter(QPointF(x + segWidth / 2.0, segHeight / 2.0))
            painter.drawText(rect, Qt.AlignCenter, QString(self.weekdays[i - 1]))
            painter.setPen(lineColor)
            painter.drawLine(x, y, x, y + num_hours * segHeight)
            x += segWidth
        rect = QRectF(0, 0, self.indent_width, segHeight)
        for i in range(1, num_hours + 1):
            y += segHeight
            painter.setPen(lineColor)
            painter.drawLine(
                WeekView.XMARGIN + self.indent_width, y,
                WeekView.XMARGIN + self.indent_width + span, y)
            rect.moveCenter(QPointF(self.indent_width / 2.0, y))
            painter.setPen(textColor)
            h = i + 7
            if h % 2 == 0:
                if ('ampm' in self.parent().options and
                        self.parent().options['ampm']):
                    h
                    if h < 12:
                        t = '%dam' % h
                    elif h == 12:
                        t = '%dpm' % h
                    else:
                        t = '%dpm' % (h - 12)
                    painter.drawText(
                        rect, Qt.AlignRight | Qt.AlignVCenter,
                        QString(t))
                else:
                    painter.drawText(
                        rect, Qt.AlignRight | Qt.AlignVCenter,
                        QString('%02d:00' % (i + 7)))
        x = WeekView.XMARGIN + self.indent_width
        painter.setBrush(segColor)
        for i in range(7):
            if self.today_col and self.today_col - 1 == i:
                t1 = 7 * 60
                t2 = 23 * 60
                start_y = ((t1 - 360) * segHeight) / 60.0
                end_y = ((t2 - t1) * segHeight) / 60.0
                painter.fillRect(
                    x + i * segWidth, start_y,
                    segWidth, end_y, todayColor)

                if self.curr_minutes < 7 * 60:
                    minutes = 7 * 60
                elif self.curr_minutes > 23 * 60:
                    minutes = 23 * 60
                else:
                    minutes = self.curr_minutes
                y = ((minutes - 360) * segHeight) / 60.0

                painter.fillRect(x + i * segWidth, y - 1, segWidth, 2, timebarColor)
            elif self.occasion_lst[i]:
                # highlight = True
                t1 = 7 * 60
                t2 = 23 * 60
                start_y = ((t1 - 360) * segHeight) / 60.0
                end_y = ((t2 - t1) * segHeight) / 60.0
                painter.fillRect(
                    x + i * segWidth, start_y,
                    segWidth, end_y, occasionColor)

            for tup in self.busy_lst[i]:
                # id = tup[2]
                t1 = max(7 * 60, tup[0])
                t2 = min(23 * 60, max(420, tup[1]))
                mtch = tup[5]
                if mtch:
                    busyColor = WeekView.DFLTCOLOR
                else:
                    busyColor = WeekView.OTHRCOLOR
                # last_end = t2
                start_y = ((t1 - 360) * segHeight) / 60.0
                end_y = ((t2 - t1) * segHeight) / 60.0
                painter.fillRect(
                    x + i * segWidth, start_y, segWidth, end_y, busyColor)

    def showBusyTimes(self):
        lines = ["<pre>%s %s" % (self.tr(
            "Scheduled times for"), str(self.parent().busyLabel.text()))]
        ampm = False
        s1 = s2 = ''
        if 'ampm' in self.parent().options and self.parent().options['ampm']:
            ampm = True
        for i in range(7):
            times = []
            for tup in self.busy_lst[i]:
                t1 = max(7 * 60, tup[0])
                t2 = min(23 * 60, max(420, tup[1]))
                if t1 != t2:
                    t1h, t1m = (t1 // 60, t1 % 60)
                    t2h, t2m = (t2 // 60, t2 % 60)
                    if ampm:
                        if t1h == 12:
                            s1 = 'pm'
                        elif t1h > 12:
                            t1h -= 12
                            s1 = 'pm'
                        else:
                            s1 = 'am'
                        if t2h == 12:
                            s2 = 'pm'
                        elif t2h > 12:
                            t2h -= 12
                            s2 = 'pm'
                        else:
                            s2 = 'am'

                    T1 = "%d:%02d%s" % (t1h, t1m, s1)
                    T2 = "%d:%02d%s" % (t2h, t2m, s2)

                    times.append("%s-%s" % (T1, T2))
            if times:
                lines.append("   %s: %s" % (self.weekdays[i], "; ".join(times)))

        self.form = BrowserForm(self.parent())
        self.form.resize(580, 240)
        self.form.setWindowTitle("busy times")
        self.form.browserWindow.setHtml("%s</pre>" % "\n".join(lines))
        self.form.show()

    def handlePreview(self):
        dialog = QPrintPreviewDialog()
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()

    def handlePaintRequest(self, printer):
        painter = QPainter(printer)
        pageRect = printer.pageRect()
        self.render(painter, pageRect.topLeft(), QRegion(pageRect))

if qt_version == 5:
    from etmQt.ui5.ui_etmView import Ui_uiMainWindow as MainWindow_Dialog
else:
    from etmQt.ui4.ui_etmView import Ui_uiMainWindow as MainWindow_Dialog


class UiWindow(QMainWindow, MainWindow_Dialog):
    def __init__(self, parent=None, options={}):
        super(UiWindow, self).__init__(parent)
        self.setupUi(self)
        self.printer = QPrinter()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.options = options
        self.scratch_text = ''
        self.editor_instances = set([])
        self.recent_edits = []
        self.printer = None
        self.etmdir = options['etmdir']
        self.qlcl = None
        self.timer_summary = ''
        self.timer_hsh = {}

        if self.options['window_width']:
            width = self.options['window_width']
            self.widths = (int(.65 * width), int(.3 * width))
        else:
            self.widths = ()

        self.setStyleSheet('font-size: %dpt' % self.options['fontsize'])
        if 'calendars' in options and options['calendars']:
            calendars = options['calendars']
            self.default_calendars = calendars
            self.calendars = deepcopy(calendars)
            default_pattern = r'^%s' % '|'.join(
                [x[2] for x in self.default_calendars if x[1]])
            self.default_regex = re.compile(default_pattern)
            self.cal_pattern = r'^%s' % '|'.join([
                x[2] for x in self.calendars if x[1]])
            self.cal_regex = re.compile(self.cal_pattern)
        else:
            self.calendars = {}
            self.cal_pattern = ''
            self.cal_regex = None
            self.default_regex = None
            self.calendarButton.hide()

        if 'weather_location' in options and options['weather_location']:
            from etmQt.etmWeather import Weather
            myweather = Weather(options['weather_location'])
            self.getWeather = myweather.getWeather
        else:
            self.getWeather = None
        QShortcut(QKeySequence(Qt.Key_F6), self, self.showWeather)
        if 'sunmoon_location' in options and options['sunmoon_location']:
            from etmQt.etmWeather import getSunMoon
            self.getSunMoon = getSunMoon
        else:
            self.getSunMoon = None
        QShortcut(QKeySequence(Qt.Key_F7), self, self.showSunMoon)

        QShortcut(QKeySequence(Qt.Key_F8), self, self.exportIcal)
        QShortcut(QKeySequence(Qt.SHIFT + Qt.Key_F8), self, self.importIcal)

        self.scratch_file = self.options['scratchfile']
        if not os.path.isfile(self.scratch_file):
            f = open(self.scratch_file, 'w')
            f.write('')
            f.close()

        self.smallfont = QFont(self.font())
        self.smallfont.setPointSize(self.smallfont.pointSize() - 1)

        self.uiView.addItems([
            self.tr('Day'), self.tr('Week'), self.tr('Month'),
            self.tr('Now'), self.tr('Next'),
            self.tr('Folder'), self.tr('Keyword'), self.tr('Tag')])
        self.comboxItem = {
            0: 0, 1: 1, 2: 2, 4: 3, 5: 4, 7: 5, 8: 6, 9: 7}
        self.indexHsh = {
            0: 'day',
            1: 'week',
            2: 'month',
            4: 'now',
            5: 'next',
            7: 'folder',
            8: 'keyword',
            9: 'tag',
        }

        self.indexTree = {
            'day': self.dayTree,
            'now': self.nowTree,
            'next': self.nextTree,
            'folder': self.folderTree,
            'keyword': self.keywordTree,
            'tag': self.tagTree,
        }

        self.current_expansions = {
            'day': 0,
            'now': 0,
            'next': 0,
            'folder': 2,
            'keyword': 1,
            'tag': 1
        }

        self.uiView.insertSeparator(3)
        self.uiView.insertSeparator(6)

        self.uiView.activated.connect(self.viewChanged)
        # if qt_version == 4:
        #     self.connect(
        #         self.uiView, SIGNAL("activated(int)"), self.viewChanged)
        # else:
        #     self.uiView.activated.connect(self.viewChanged)
        # spacer = QLabel(QString("\t\t"))
        self.date2row = {}
        self.aft = None
        self.bef = None

        self.now = datetime.now(tzlocal())
        self.today = self.now.date()
        self.active_date = self.now.date()

        self.prev_day = None
        self.curr_day = self.today
        self.next_day = None

        self.prev_week = None
        self.curr_week = self.today
        self.next_week = None

        self.prev_month = None
        self.curr_month = self.today
        self.next_month = None

        self.timer_minutes = 0

        self.today_col = 0

        self.timer_status_hsh = {}
        self.timer_status = 'stopped'
        self.index2uuid = {}
        self.index2datetime = {}
        self.index2uuid['day'] = {}
        self.index2uuid['now'] = {}
        self.index2uuid['next'] = {}
        self.index2uuid['folder'] = {}
        self.index2uuid['keyword'] = {}
        self.index2uuid['tag'] = {}
        self.index2item = {}

        self.yScroll = 0

        self.now_tree = None
        self.next_tree = None
        self.day_tree = None
        self.folder_tree = None
        self.keyword_tree = None
        self.tag_tree = None

        self.filter_pattern = ''

        self.now_model = QStandardItemModel()
        self.now_model.setColumnCount(2)

        self.next_model = QStandardItemModel()
        self.next_model.setColumnCount(2)

        self.day_model = QStandardItemModel()
        self.day_model.setColumnCount(2)

        self.folder_model = QStandardItemModel()
        self.folder_model.setColumnCount(2)

        self.keyword_model = QStandardItemModel()
        self.keyword_model.setColumnCount(2)

        self.tag_model = QStandardItemModel()
        self.tag_model.setColumnCount(2)

        self._nowProxy = TreeFilter()
        self._nowProxy.setSourceModel(self.now_model)
        self._nowProxy.setDynamicSortFilter(True)
        self._nowProxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.nowTree.setModel(self._nowProxy)

        self._nextProxy = TreeFilter()
        self._nextProxy.setSourceModel(self.next_model)
        self._nextProxy.setDynamicSortFilter(True)
        self._nextProxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.nextTree.setModel(self._nextProxy)

        self._dayProxy = TreeFilter()
        self._dayProxy.setSourceModel(self.day_model)
        self._dayProxy.setDynamicSortFilter(True)
        self._dayProxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.dayTree.setModel(self._dayProxy)

        self._folderProxy = TreeFilter()
        self._folderProxy.setSourceModel(self.folder_model)
        self._folderProxy.setDynamicSortFilter(True)
        self._folderProxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.folderTree.setModel(self._folderProxy)

        self._keywordProxy = TreeFilter()
        self._keywordProxy.setSourceModel(self.keyword_model)
        self._keywordProxy.setDynamicSortFilter(True)
        self._keywordProxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.keywordTree.setModel(self._keywordProxy)

        self._tagProxy = TreeFilter()
        self._tagProxy.setSourceModel(self.tag_model)
        self._tagProxy.setDynamicSortFilter(True)
        self._tagProxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.tagTree.setModel(self._tagProxy)

        self.indexModel = {
            'day': self.day_model,
            'now': self.now_model,
            'next': self.next_model,
            'folder': self.folder_model,
            'keyword': self.keyword_model,
            'tag': self.tag_model,
        }

        self.indexProxy = {
            'day': self._dayProxy,
            'now': self._nowProxy,
            'next': self._nextProxy,
            'folder': self._folderProxy,
            'keyword': self._keywordProxy,
            'tag': self._tagProxy,
        }

        self.weekWidget = QDialog()
        weeklayout = QGridLayout()
        weeklayout.setSpacing(4)
        # if qt_version == 4:
        #     weeklayout.setMargin(7)
        weeklayout.setContentsMargins(QMargins(7, 7, 7, 7))

        self.prevWeekButton = QToolButton()
        self.prevWeekButton.setStyleSheet('border: 0px black')
        self.prevWeekButton.setIcon(QIcon(":/{0}.png".format("previous")))
        self.nextWeekButton = QToolButton()
        self.nextWeekButton.setStyleSheet('border: 0px black')
        self.nextWeekButton.setIcon(QIcon(":/{0}.png".format("next")))
        # self.weekview = WeekView(self, uuid2hash = self.uuid2hash)
        self.weekview = WeekView(self)
        self.busyLabel = QLabel('now is the time')
        weeklayout.addWidget(self.prevWeekButton, 0, 0, Qt.AlignLeft)
        weeklayout.addWidget(self.busyLabel, 0, 1, Qt.AlignCenter)
        weeklayout.addWidget(self.nextWeekButton, 0, 2, Qt.AlignRight)
        weeklayout.addWidget(self.weekview, 1, 0, 1, 3)
        self.weekPage.setLayout(weeklayout)

        monthlayout = QGridLayout()
        monthlayout.setSpacing(4)
        # if qt_version == 4:
        #     monthlayout.setMargin(4)
        monthlayout.setContentsMargins(QMargins(7, 7, 7, 7))
        self.calendarWidget = QCalendarWidget()
        # self.calendarWidget.setLocale(self.qlcl)
        self.calendarWidget.setStyleSheet('background: white; color: black')
        self.calendarWidget.setGridVisible(True)
        if qt_version == 4:
            self.calendarWidget.setHeaderVisible(True)
        self.calendarWidget.setFirstDayOfWeek(Qt.Monday)
        headerText = QTextCharFormat()
        headerText.setForeground(QColor(calheader_fg))
        headerText.setBackground(QColor(calheader_bg))
        self.calendarWidget.setHeaderTextFormat(headerText)
        weekendText = QTextCharFormat()
        weekdayText = QTextCharFormat()
        self.calendarWidget.setWeekdayTextFormat(Qt.Saturday, weekendText)
        self.calendarWidget.setWeekdayTextFormat(Qt.Sunday, weekendText)
        self.calendarWidget.setWeekdayTextFormat(Qt.Monday, weekdayText)
        self.calendarWidget.setWeekdayTextFormat(Qt.Tuesday, weekdayText)
        self.calendarWidget.setWeekdayTextFormat(Qt.Wednesday, weekdayText)
        self.calendarWidget.setWeekdayTextFormat(Qt.Thursday, weekdayText)
        self.calendarWidget.setWeekdayTextFormat(Qt.Friday, weekdayText)

        monthlayout.addWidget(self.calendarWidget, 1, 0)
        self.monthPage.setLayout(monthlayout)

        self.uiFilter.textChanged.connect(self.filter)
        # start with day view
        self.dayView()

        # timer will fire on the minute to update current time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timeout)

        self.newActionButton.clicked.connect(self.timer_toggle)
        self.pause_restartButton.clicked.connect(self.timer_toggle)
        self.stopButton.clicked.connect(self.timer_finish)
        self.reportButton.clicked.connect(self.createReport)
        self.prevWeekButton.clicked.connect(self.prevPeriod)
        self.nextWeekButton.clicked.connect(self.nextPeriod)
        self.alertsButton.clicked.connect(self.showAlerts)
        self.todayButton.clicked.connect(self.setNowView)
        self.errorButton.clicked.connect(self.showMessages)
        self.newItemButton.clicked.connect(self.createItem)
        self.mainHelpButton.clicked.connect(self.mainHelp)
        self.calendarButton.clicked.connect(self.selectCalendars)

        QShortcut(QKeySequence(Qt.Key_F1), self, self.mainHelp)
        QShortcut(QKeySequence(Qt.Key_F2), self, self.aboutHelp)
        QShortcut(QKeySequence(Qt.Key_F3), self, self.checkNewer)
        QShortcut(QKeySequence(Qt.Key_F4), self, self.showCalendar)
        QShortcut(QKeySequence(Qt.Key_F5), self, self.dateCalculator)
        QShortcut(QKeySequence(Qt.Key_Space), self, self.scrollToDate)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.clearFilter)

        self.calendarWidget.activated.connect(self.setMonthDay)

        if qt_version == 4:
            self.connect(self, SIGNAL("itemChanged"), self.itemChanged)

        self.weekview.doubleclicked.connect(self.clickedWeek)

        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_L), self, self.viewMenu)
        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_E), self, self.showMessages)
        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_F), self, self.filterFocus)
        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_N), self, self.createItem)
        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_T), self, self.timer_toggle)
        QShortcut(
            QKeySequence(Qt.SHIFT + Qt.CTRL + Qt.Key_T),
            self, self.timer_finish)
        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_R), self, self.createReport)
        QShortcut(
            QKeySequence(Qt.SHIFT + Qt.CTRL + Qt.Key_O), self, self.edit_config)
        QShortcut(
            QKeySequence(Qt.SHIFT + Qt.CTRL + Qt.Key_C), self,
            self.edit_completions)
        QShortcut(
            QKeySequence(Qt.SHIFT + Qt.CTRL + Qt.Key_R), self,
            self.editReportSpecs)
        QShortcut(
            QKeySequence(Qt.SHIFT + Qt.CTRL + Qt.Key_H), self,
            self.edit_recent)

        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_C), self, self.selectCalendars)

        QShortcut(
            QKeySequence(Qt.Key_Comma), self, self.dayView)
        QShortcut(
            QKeySequence(Qt.Key_Period), self, self.weekView)
        QShortcut(
            QKeySequence(Qt.Key_Slash), self, self.monthView)
        QShortcut(
            QKeySequence(Qt.Key_Semicolon), self, self.nowView)
        QShortcut(
            QKeySequence(Qt.Key_Apostrophe), self, self.nextView)
        QShortcut(
            QKeySequence(Qt.Key_BracketLeft), self, self.folderView)
        QShortcut(
            QKeySequence(Qt.Key_BracketRight), self, self.keywordView)
        QShortcut(
            QKeySequence(Qt.Key_Backslash), self, self.tagView)

        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_A), self, self.showAlerts)
        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_J), self, self.jumpToDate)
        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_P), self, self.openScratchPad)
        QShortcut(
            QKeySequence(Qt.CTRL + Qt.Key_S), self, self.showAgenda)

        QShortcut(QKeySequence(Qt.Key_Left), self.dayPage, self.prevPeriod)
        QShortcut(QKeySequence(Qt.Key_Right), self.dayPage, self.nextPeriod)
        QShortcut(QKeySequence(Qt.Key_Left), self.weekPage, self.prevPeriod)
        QShortcut(QKeySequence(Qt.Key_Right), self.weekPage, self.nextPeriod)
        QShortcut(QKeySequence(Qt.Key_Left), self.monthPage, self.prevPeriod)
        QShortcut(QKeySequence(Qt.Key_Right), self.monthPage, self.nextPeriod)

        # start with the timer inactive and the buttons hidden
        self.timerLabel.hide()
        self.stopButton.hide()
        self.pause_restartButton.hide()

        self.dayTree.doubleClicked.connect(self.clickedSlot)
        self.nowTree.doubleClicked.connect(self.clickedSlot)
        self.nextTree.doubleClicked.connect(self.clickedSlot)
        self.folderTree.doubleClicked.connect(self.clickedSlot)
        self.keywordTree.doubleClicked.connect(self.clickedSlot)
        self.tagTree.doubleClicked.connect(self.clickedSlot)
        self.dayTree.activated.connect(self.activated)
        self.tagTree.activated.connect(self.activated)

        for tree in [self.nowTree, self.nextTree, self.dayTree,
                     self.folderTree, self.keywordTree, self.tagTree]:
            QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Slash), tree,
                      self.expandTo)
            QShortcut(QKeySequence(Qt.Key_Return), tree,
                      self.keyReturn)

        self.alerts = []
        self.nowTree.expandAll()
        self.nextTree.expandAll()
        self.dayTree.expandAll()
        self.folderTree.expandToDepth(0)
        self.keywordTree.expandToDepth(0)
        self.tagTree.collapseAll()

    def loadFileData(self, dirty=False):
        (self.uuid2hash, self.file2uuids, self.file2lastmodified,
         self.bad_datafiles, self.messages) = get_data(self.options, dirty)
        return True

    def loadViewData(self):
        weeks_after = self.options['weeks_after']
        now = datetime.now()
        curr_minutes = datetime2minutes(now)
        year, wn, dn = now.isocalendar()
        if dn > 1:
            days = dn - 1
        else:
            days = 0
        week_beg = now.replace(hour=0, minute=0, second=0) - days * oneday
        bef = (week_beg + (7 * (weeks_after + 1)) * oneday)
        self.bef = bef
        (self.all_rows, self.all_busytimes, self.all_busydays,
            self.all_alerts, self.all_dates, self.occasions) = \
            getViewData(
                bef, self.file2uuids, self.uuid2hash, options=self.options)
        updateCurrentFiles(
            self.all_rows, self.file2uuids, self.uuid2hash, self.options)
        self.all_alerts = [x for x in self.all_alerts if x[0] >= curr_minutes]
        return(self.applyCalendarsFilter())

    def showMessages(self, force=True):
        if self.messages:
            html = "<pre>%s</pre>" % ("\n".join(self.messages))
        else:
            html = self.tr("""\
No error messages were generated when data files were last loaded.""")
        if self.messages or force:
            self.form = BrowserForm(self)
            self.form.setWindowTitle(self.tr("data errors"))
            self.form.browserWindow.setHtml(html)
            self.form.resize(500, 400)
            self.form.show()

    def applyCalendarsFilter(self):
        if self.all_rows:
            if self.cal_pattern:
                self.cal_regex = re.compile(self.cal_pattern)
                my_alerts = deepcopy(self.all_alerts)
                self.alerts = [x for x in my_alerts if
                               self.cal_regex.match(x[2])]
                self.busytimes = deepcopy(self.all_busytimes)
                my_dates = deepcopy(self.all_dates)
                self.dates = [x[0] for x in my_dates if
                              self.cal_regex.match(x[1])]
                self.busydays = deepcopy(self.all_busydays)
                my_rows = deepcopy(self.all_rows)
                rows = [x for x in my_rows if
                        self.cal_regex.match(x[0][-1])]
            else:
                self.cal_regex = None
                self.alerts = deepcopy(self.all_alerts)
                self.busytimes = deepcopy(self.all_busytimes)
                my_dates = deepcopy(self.all_dates)
                self.dates = [x[0] for x in my_dates]
                self.busydays = deepcopy(self.all_busydays)
                rows = deepcopy(self.all_rows)
            if self.dates:
                self.prevnext = getPrevNext(self.dates)
                self.first_day = self.dates[0]
                self.last_day = self.dates[-1]
            else:
                self.prevnext = {}
                self.busydays = {}
                self.busytimes = {}

            if self.alerts:
                self.alertsButton.setToolTip(self.tr("""\
Click here or press <em>Ctrl-A</em> to see the remaining alerts for today."""))
                self.alertsButton.show()
            else:
                self.alertsButton.hide()
        else:
            self.prevnext = {}
            self.busydays = {}
            self.busytimes = {}
            self.dates = {}
            self.alerts = {}
            rows = []

        self.now_tree = makeTree(rows, 'now')
        self.next_tree = makeTree(rows, 'next')
        self.day_tree = makeTree(rows, 'day')
        self.folder_tree = makeTree(rows, 'folder')
        self.keyword_tree = makeTree(rows, 'keyword')
        self.tag_tree = makeTree(rows, 'tag')
        return True

    # def showsize(self):
    #     print('SHOWSIZE', self.width())

    def refreshViews(self):
        root_key = tuple(['', '_'])

        self.next_model.clear()
        if self.next_tree and root_key in self.next_tree:
            self.next_model.setColumnCount(2)
            self.index2uuid['next'] = {}
            self.index2item['next'] = {}
            self.addItems(
                'next', self.next_model, self.next_tree[root_key],
                self.next_tree)

        self.now_model.clear()
        if self.now_tree and root_key in self.now_tree:
            self.now_model.setColumnCount(2)
            self.index2uuid['now'] = {}
            self.index2item['now'] = {}
            self.addItems(
                'now', self.now_model, self.now_tree[root_key],
                self.now_tree)

        self.day_model.clear()
        if self.day_tree and root_key in self.day_tree:
            self.day_model.setColumnCount(2)
            self.index2uuid['day'] = {}
            self.index2item['day'] = {}
            self.addItems(
                'day', self.day_model, self.day_tree[root_key],
                self.day_tree)

        self.folder_model.clear()
        if self.folder_tree and root_key in self.folder_tree:
            self.folder_model.setColumnCount(2)
            self.index2uuid['folder'] = {}
            self.index2item['folder'] = {}
            self.addItems(
                'folder', self.folder_model, self.folder_tree[root_key],
                self.folder_tree)

        self.keyword_model.clear()
        if self.keyword_tree and root_key in self.keyword_tree:
            self.keyword_model.setColumnCount(2)
            self.index2uuid['keyword'] = {}
            self.index2item['keyword'] = {}
            self.addItems(
                'keyword', self.keyword_model, self.keyword_tree[root_key],
                self.keyword_tree)

        self.tag_model.clear()
        if self.tag_tree and root_key in self.tag_tree:
            self.tag_model.setColumnCount(2)
            self.index2uuid['tag'] = {}
            self.index2item['tag'] = {}
            self.addItems(
                'tag', self.tag_model, self.tag_tree[root_key],
                self.tag_tree)

        self.nowTree.expandAll()
        self.nextTree.expandAll()
        self.dayTree.expandAll()
        self.scrollToDate(self.active_date)

        # we need these expanded to resize the 2nd column and let the first
        # take the remaining space
        self.folderTree.expandAll()
        self.keywordTree.expandAll()
        self.tagTree.expandAll()

        if self.filter_pattern:
            self.filter(self.filter_pattern)

        # resize the last column (2) and let the first column (1) take the
        # remaining space when the window is resized. Too cool!
        for tree in [self.dayTree, self.nowTree, self.nextTree, self.dayTree,
                     self.folderTree, self.keywordTree, self.tagTree]:
            if qt_version == 4:
                tree.header().setStretchLastSection(False)
                tree.resizeColumnToContents(1)
                tree.header().setResizeMode(0, QHeaderView.Stretch)
            else:
                # print('size', tree.frameGeometry())
                if self.widths:
                    tree.setColumnWidth(1, self.widths[1])
                    tree.setColumnWidth(0, self.widths[0])
                else:
                    tree.resizeColumnToContents(1)
                    tree.resizeColumnToContents(0)

        # now we can set the expansions that we want
        for key, depth in self.current_expansions.items():
            tree = self.indexTree[key]
            if depth == 0:
                tree.expandAll()
            elif depth == 1:
                tree.collapseAll()
            else:
                tree.expandToDepth(depth - 2)

        if self.now_tree:
            tip = []
            for key in self.now_tree:
                if key == (u'', u'_'):
                    continue
                tip.append((key[-1], len(self.now_tree[key])))
            tip.sort()
            tipstr = "\n".join(["  {1}: {0}".format(
                x[1], x[0]) for x in tip])
            tipstr = "{0}\n{1}".format(self.tr('Now'), tipstr)
            self.todayButton.show()
            self.todayButton.setToolTip(tipstr)
        else:
            self.todayButton.hide()

        if self.messages:
            self.errorButton.show()
        else:
            self.errorButton.hide()

        self.setMonthDayColors()
        self.setTodayColors()
        self.setWeek(self.curr_week)
        return True

    def edit_recent(self):
        if not self.recent_edits:
            QMessageBox.warning(
                self, "etm",
                self.tr("No files have been changed in this session."))
            return()
        which = WhichForm(self, 'recent', '')
        if which.exec_():
            form = getEditForm(
                self, instance='recent',
                filename=self.which_file,
                receiver=self.itemChanged)
            if form:
                form.setWindowTitle(
                    "{0}".format(
                        relpath(self.which_file, self.options['datadir'])))
                form.show()
                form.helpPage = 1
                form.show()

    def edit_config(self):
        form = getEditForm(
            self, instance='config',
            filename=self.options['config'],
            receiver=self.configChanged,
            highlight=False,
            use_completer=False)
        if form:
            form.setWindowTitle("{0}".format(self.options['config']))
            form.helpPage = 5
            form.show()

    def edit_completions(self):
        form = getEditForm(
            self, instance='complete',
            filename=self.options['auto_completions'],
            receiver=self.configChanged,
            highlight=False,
            use_completer=False)
        if form:
            form.setWindowTitle("{0}".format(self.options['auto_completions']))
            form.helpPage = 5
            form.show()

    def editReportSpecs(self):
        form = getEditForm(
            self, instance='report',
            filename=self.options['report_specifications'],
            receiver=self.configChanged,
            highlight=False,
            use_completer=False)
        if form:
            form.setWindowTitle(
                "{0}".format(self.options['report_specifications']))
            form.helpPage = 3
            form.show()

    def whichPrinter(self):
        # call the correct handlePreview
        indx = self.stackedWidget.currentIndex()
        if indx == 1:  # week view
            self.weekview.handlePreview()

    def selectCalendars(self):
        form = CalendarsForm(self)
        ok = form.exec_()
        if ok:
            if self.calendars == self.default_calendars:
                self.calendarButton.setIcon(QIcon(":/folders_blue.png"))
                self.showStatusMessage(self.tr("using default calendars"))
            else:
                self.calendarButton.setIcon(QIcon(":/folders_green.png"))
                self.showStatusMessage(self.tr("not using default calendars"))
            selections = False
            for calendar in self.calendars:
                if calendar[1]:
                    selections = True
                    break
            if selections:
                self.cal_pattern = r'^%s' % '|'.join(
                    [x[2] for x in self.calendars if x[1]])
            else:
                self.cal_pattern = ''
            self.options['calendars'] = self.calendars
            self.applyCalendarsFilter()
            self.refreshViews()

    def scrollToDate(self, curr_day=None):
        if not curr_day:
            curr_day = datetime.today().date()
        self.setWeek(curr_day)
        self.setMonth(curr_day)
        self.active_date = curr_day
        if not self.prevnext:
            if self.stackedWidget.currentIndex() == 0:
                self.showStatusMessage(self.tr('Nothing to show in day view.'))
            return()
        if curr_day in self.prevnext:
            prev, curr, next = self.prevnext[curr_day]
        elif curr_day <= self.first_day:
            prev, curr, next = self.prevnext[self.first_day]
            prev = curr = self.first_day
        else:
            prev, curr, next = self.prevnext[self.last_day]
            curr = next = self.last_day
        if curr_day != curr and self.stackedWidget.currentIndex() == 0:
            self.showStatusMessage(self.tr('Nothing for %s.' % curr_day))
        df = fmt_date(curr)
        if df not in self.date2row:
            print("error: missing date2row key '%s'" % df)
            return()
        self.prev_day = prev
        self.curr_day = curr
        self.next_day = next
        self.prev_week = curr - 7 * oneday
        self.curr_week = curr
        self.next_week = curr + 7 * oneday
        row = self.date2row[df]
        index = self._dayProxy.index(row, 0)
        self.dayTree.setCurrentIndex(index)
        self.dayTree.scrollTo(
            self.dayTree.currentIndex(),
            hint=QAbstractItemView.PositionAtTop)

    def setWeek(self, curr_day=datetime.today()):
        yn, wn, dn = curr_day.isocalendar()
        iso_today = datetime.today().isocalendar()
        curr_minutes = datetime2minutes(datetime.now(tzlocal()))
        self.prev_week = curr_day - 7 * oneday
        self.next_week = curr_day + 7 * oneday
        self.curr_week = curr_day
        if dn > 1:
            days = dn - 1
        else:
            days = 0
        self.week_beg = weekbeg = curr_day - days * oneday
        weekend = curr_day + (6 - days) * oneday
        weekdays = []
        day = weekbeg
        busy_lst = []
        occasion_lst = []
        col_num = 1
        self.today_col = 0
        matching = self.cal_regex is not None and self.default_regex is not None
        while day <= weekend:
            weekdays.append(fmt_weekday(day))
            isokey = day.isocalendar()
            if isokey == iso_today:
                self.today_col = col_num

            if isokey in self.occasions:
                bt = []
                for item in self.occasions[isokey]:
                    it = list(item)
                    if matching:
                        if not self.cal_regex.match(item[-1]):
                            continue
                        mtch = (
                            self.default_regex.match(it[-1]) is not None)
                    else:
                        mtch = True
                    it.append(mtch)
                    item = tuple(it)
                    bt.append(item)
                occasion_lst.append(bt)
            else:
                occasion_lst.append([])

            if isokey in self.busytimes:
                bt = []
                for item in self.busytimes[isokey][1]:
                    it = list(item)
                    if matching:
                        if not self.cal_regex.match(item[-1]):
                            continue
                        mtch = (
                            self.default_regex.match(it[-1]) is not None)
                    else:
                        mtch = True
                    it.append(mtch)
                    item = tuple(it)
                    bt.append(item)
                busy_lst.append(bt)
            else:
                busy_lst.append([])
            day = day + oneday
            col_num += 1

        ybeg = weekbeg.year
        yend = weekend.year
        mbeg = weekbeg.month
        mend = weekend.month
        if mbeg == mend:
            header = "{0} - {1}".format(
                fmt_dt(weekbeg, '%b %d'), fmt_dt(weekend, '%d, %Y'))
        elif ybeg == yend:
            header = "{0} - {1}".format(
                fmt_dt(weekbeg, '%b %d'), fmt_dt(weekend, '%b %d, %Y'))
        else:
            header = "{0} - {1}".format(
                fmt_dt(weekbeg, '%b %d, %Y'), fmt_dt(weekend, '%b %d, %Y'))
        header = leadingzero.sub('', header)
        self.busyLabel.setText(
            "{0} {1}:  {2}".format(self.tr("Week"), wn, header))
        self.weekview.setWeekdays(
            weekdays, busy_lst, occasion_lst, self.today_col, curr_minutes)
        self.weekview.uuid2hash = self.uuid2hash

    def setMonth(self, curr_day=None):
        if curr_day:
            self.calendarWidget.setSelectedDate(curr_day)

    def setTodayColors(self):
        today = datetime.today().date()
        if today not in self.busydays:
            self.busydays[today] = 0
        v = self.busydays[today]
        date_fmt = QTextCharFormat()
        dte = QDate(today)
        color = self.getDayColor(v)
        date_fmt.setForeground(color)
        date_fmt.setBackground(todayColor)
        self.calendarWidget.setDateTextFormat(dte, date_fmt)

    def setMonthDayColors(self):
        for dt, v in self.busydays.items():
            date_fmt = QTextCharFormat()
            dte = QDate(dt)
            color = self.getDayColor(v)
            # rgba = color.getRgb()
            if color.isValid():
                date_fmt.setForeground(color)
                self.calendarWidget.setDateTextFormat(dte, date_fmt)
            else:
                print("bad color", dt, v, color)

    def getDayColor(self, num_minutes):
        # green = 120/355.0
        # blue = 240/355.0
        red = 10
        hue = red
        saturation = 1
        min_b = .3
        max_b = 1           # must be <= 1
        max_minutes = 480
        brightness = min(
            max_b, min_b + (max_b - min_b) * num_minutes / float(max_minutes))
        r, g, b = hsv_to_rgb(
            hue, saturation, brightness)
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        try:
            color = QColor(r, g, b)
        except:
            print('failed setting dayColor', r, g, b)
            color = QColor(0, 0, 0)
        return(color)

    def setMonthDay(self, d):
        pydate = d.getDate()
        dt = date(pydate[0], pydate[1], pydate[2])
        # df = d.toString('ddd MMM d, yyyy')
        self.scrollToDate(dt)
        self.viewChanged(1)

    def setSelectedDate(self, d):
        pydate = d.getDate()
        dt = date(pydate[0], pydate[1], pydate[2])
        # df = d.toString('ddd MMM d, yyyy')
        self.scrollToDate(dt)

    def prevPeriod(self):
        index = self.stackedWidget.currentIndex()
        day = None
        if index == 0:
            if not self.prev_day:
                return()
            day = self.prev_day
            self.scrollToDate(day)
            # self.setWeek(day)
        elif index == 1:
            day = self.prev_week
            self.scrollToDate(day)
            # self.setWeek(day)

        elif index == 2:
            self.calendarWidget.showPreviousMonth()
            self.setMonth()

    def nextPeriod(self):
        index = self.stackedWidget.currentIndex()
        day = None
        if index == 0:
            if not self.next_day:
                return()
            day = self.next_day
            self.scrollToDate(day)

        elif index == 1:
            day = self.next_week
            self.scrollToDate(day)
            # self.setWeek(day)
        elif index == 2:
            self.calendarWidget.showNextMonth()
            self.setMonth()

    def getAncestors(self, p, pr=-1):
        indx = []
        while pr >= 0:
            indx.append(pr)
            p = p.parent()
            if not p:
                break
            pr = p.row()
        return(indx)

    def clickedWeek(self, dayhourmin, uuid):
        days, hours, mins = map(int, dayhourmin.split(':'))
        y, m, d = (self.week_beg.year, self.week_beg.month, self.week_beg.day)
        self.parent_index = None
        if uuid:
            uuid = unicode(uuid)
            dt = datetime(y, m, d, hours, mins)
            dt += days * oneday
            if uuid not in self.uuid2hash:
                return()
            hsh = self.uuid2hash[uuid]
            hsh['_dt'] = fmt_datetime(dt, options=self.options)
            form = DetailForm(self, self.itemChanged)
            form.setHash(hsh)
            form.aft = self.aft
            form.bef = self.bef
            form.show()
        else:
            # round mins off to the nearest quarter hour
            mins15 = int(round(mins / 15.0)) * 15
            if mins15 == 60:
                mins15 = 0
                hours += 1
            dt = datetime(y, m, d, hours, mins15)
            dt += days * oneday
            self.createItem(
                self.tr("new event"), text="*  @s %s" %
                fmt_datetime(dt, options=self.options), modified=False)
        self.scrollToDate(dt.date())

    def keyReturn(self):
        if self.current_view in self.indexTree:
            tree = self.indexTree[self.current_view]
            self.clickedSlot(tree.currentIndex())
        else:
            return(False)

    def expandTo(self):
        if self.current_view in self.indexTree:
            depth, ok = QInputDialog.getInt(
                self, self.tr("expand to depth"),
                "%s:" % self.tr("depth (0 expands all)"), value=0,
                min=0, max=9)
            if ok:
                self.current_expansions[self.current_view] = depth
                tree = self.indexTree[self.current_view]
                if depth == 0:
                    tree.expandAll()
                elif depth == 1:
                    tree.collapseAll()
                else:
                    tree.expandToDepth(depth - 2)
        else:
            return(False)

    def clickedSlot(self, modelIndex):
        model = modelIndex.model()
        if hasattr(model, 'mapToSource'):
            # We are a proxy model
            modelIndex = model.mapToSource(modelIndex)
        p = modelIndex.parent()
        pr = p.row()
        indx = self.getAncestors(p, pr)
        indx.append(modelIndex.row())
        indx = tuple(indx)

        view_indx = self.uiView.currentIndex()
        view = self.indexHsh[view_indx]
        tree = self.indexTree[view]
        bar = tree.verticalScrollBar()
        self.yScroll = bar.value()

        hsh = {}
        # summary = ''
        if indx in self.index2uuid[self.current_view]:
            uuid = unicode(self.index2uuid[self.current_view][indx])
            if uuid in self.uuid2hash:
                hsh = self.uuid2hash[uuid]
                # summary = hsh['_summary']
        else:
            uuid = -1
            return()
        dt = None
        if indx in self.index2datetime:
            dt = self.index2datetime[indx]

        hsh = self.uuid2hash[uuid]
        hsh['_dt'] = dt
        if ':' in uuid:
            uuid = uuid.split(':')[0]

        form = DetailForm(self, self.itemChanged)
        form.setHash(hsh)
        form.aft = self.aft
        form.bef = self.bef
        form.show()

    def itemChanged(self, filename):
        res = self.loadFileData(dirty=True)
        if res:
            res = self.loadViewData()
            # loadViewData updates self.all_alerts and through call to
            # applyCalendarsFilter, updates self.alerts and
            # show/hide todayButt
            if res:
                self.refreshViews()
        self.showStatusMessage(self.tr('changes saved'))
        if self.yScroll:
            view_indx = self.uiView.currentIndex()
            view = self.indexHsh[view_indx]
            if view in self.indexTree:
                tree = self.indexTree[view]
                bar = tree.verticalScrollBar()
                bar.setValue(self.yScroll)

    def configChanged(self, filename):
        current_options = deepcopy(self.options)
        (user_options, options, use_locale) = get_options(self.etmdir)
        self.options = options
        if (options['datadir'] != current_options['datadir']
                or options['calendars'] != current_options['calendars']):
            self.loadFileData(dirty=True)
        self.loadViewData()
        self.refreshViews()
        return(True)

    def activated(self, modelIndex):
        model = modelIndex.model()
        if hasattr(model, 'mapToSource'):
            # We are a proxy model
            modelIndex = model.mapToSource(modelIndex)

    def viewMenu(self):
        self.uiView.setFocus()
        self.uiView.showPopup()

    def filterFocus(self):
        self.uiFilter.setFocus()

    def dayView(self):
        self.viewChanged(0)

    def weekView(self):
        self.viewChanged(1)

    def monthView(self):
        self.viewChanged(2)

    def nowView(self):
        self.viewChanged(4)

    def nextView(self):
        self.viewChanged(5)

    def folderView(self):
        self.viewChanged(7)

    def keywordView(self):
        self.viewChanged(8)

    def tagView(self):
        self.viewChanged(9)

    def setNowView(self):
        self.viewChanged(4)

    def viewChanged(self, v):
        self.uiView.setCurrentIndex(v)
        if v in self.indexHsh:
            self.current_view = self.indexHsh[v]
        self.stackedWidget.setCurrentIndex(self.comboxItem[v])

        if v in [1, 2]:
            self.uiFilter.hide()
        else:
            self.uiFilter.show()
        self.uiView.setFocus()

    def setLabel(self, text):
        item = QStandardItem(text)
        item.setEditable(False)
        # item.setSizeHint(QSize(600, -1))
        # print(item.sizeHint())
        return(item)

    def setLeaf(self, text, type_key, tooltip='', col3=''):
        item = QStandardItem(text)
        item.setEditable(False)
        if type_key and type_key in tstr2SCI:
            if self.options['report_colors']:
                if (self.options['report_colors'] == 2
                        or type_key[1] in [13, 14, 15]):
                    item.setForeground(QColor(tstr2SCI[type_key][1]))
            item.setIcon(QIcon(":/{0}.png".format(tstr2SCI[type_key][2])))
            item.setFont(self.smallfont)
            # item.setSizeHint(QSize(600, -1))
            # print(item.sizeHint())
            if tooltip:
                item.setToolTip(tooltip)
        else:
            print('bad type_key', type_key)

        return(item)

    def filter(self, pattern=''):
        self.filter_pattern = pattern
        self._nowProxy.setFilterRegExp(pattern)
        self._nextProxy.setFilterRegExp(pattern)
        self._dayProxy.setFilterRegExp(pattern)
        self._folderProxy.setFilterRegExp(pattern)
        self._keywordProxy.setFilterRegExp(pattern)
        self._tagProxy.setFilterRegExp(pattern)
        self.nowTree.expandAll()
        self.nextTree.expandAll()
        self.dayTree.expandAll()
        self.folderTree.expandAll()
        self.keywordTree.expandAll()
        self.tagTree.expandAll()

    def clearFilter(self):
        self.filter_pattern = ''
        self.uiFilter.clear()
        self.uiView.setFocus()
        self.scrollToDate(self.curr_day)

    def addItems(self, view, parent, elements, tree):
        row_count = 0
        leaf_count = 0
        for text in elements:
            if text in tree:
                # this is a branch
                item = self.setLabel(text[1])
                # modelIndex = item.index()
                children = tree[text]
                if 'rowsize' in self.options and self.options['rowsize']:
                    item.setSizeHint(QSize(1, self.options['rowsize']))
                parent.appendRow([item])
                self.addItems(view, item, children, tree)
                if view == 'day':
                    self.date2row[text[1]] = row_count
                    row_count += 1
            else:
                # this is a leaf
                lst = self.getAncestors(parent, parent.row())
                lst.append(leaf_count)
                indx = tuple(lst)
                if type(text[1]) != tuple:
                    # this shouldn't happen
                    print('error: leaf should be a tuple', text)
                if len(text[1]) == 4:
                    uuid, item_type, col0, col2 = text[1]
                    dt = ''
                else:  # len 5 day view with datetime appended
                    uuid, item_type, col0, col2, dt = text[1]
                    self.index2datetime[tuple(indx)] = dt
                uuid_unicode = unicode(uuid)
                if uuid_unicode in self.uuid2hash:
                    hsh = self.uuid2hash[uuid_unicode]
                    tooltip = hsh['_tooltip']
                else:
                    tooltip = 'none'
                item0 = self.setLeaf(col0, item_type, tooltip, dt)
                self.index2item[view][tuple(indx)] = item0
                self.index2uuid[view][tuple(indx)] = uuid
                if type(col2) == int:
                    col2 = '%s' % col2
                item2 = QStandardItem(col2)
                if item_type and item_type in tstr2SCI:
                    if self.options['report_colors']:
                        if (self.options['report_colors'] == 2 or
                                item_type[1] in [13, 14, 15]):
                            item2.setForeground(
                                QColor(tstr2SCI[item_type][1]))
                    item2.setFont(self.smallfont)
                else:
                    print("bad item_type", item_type)
                item2.setTextAlignment(Qt.AlignHCenter)
                parent.appendRow([item0, item2])
                leaf_count += 1

    def timeout(self):
        self.now = datetime.now(tzlocal())
        today = self.now.date()
        newday = (today != self.today)
        self.today = today
        process = QProcess()

        curr_minutes = datetime2minutes(self.now)
        if self.today_col:
            self.setWeek(self.curr_week)

        new, modified, deleted = get_changes(
            self.options, self.file2lastmodified)
        if new or modified or deleted:
            if ('filechange_alert' in self.options and
                    self.options['filechange_alert']):
                scmd = self.options['filechange_alert']
                process = QProcess()
                process.startDetached(scmd)

            self.loadFileData(dirty=True)
            # this updates self.alerts and show/hide todayButton
            self.loadViewData()
            self.refreshViews()
        elif newday:
            self.loadViewData()
            self.refreshViews()
            self.scrollToDate(self.today)

        if self.alerts:
            td = -1
            while td < 0 and self.alerts:
                td = self.alerts[0][0] - curr_minutes
                if td < 0:
                    self.alerts.pop(0)
            if td == 0:
                if ('alert_wakecmd' in self.options and
                        self.options['alert_wakecmd']):
                    process.execute(self.options['alert_wakecmd'])
                while td == 0:
                    hsh = self.alerts[0][1]
                    self.alerts.pop(0)
                    actions = hsh['_alert_action']
                    if 's' in actions:
                        if ('alert_soundcmd' in self.options and
                                self.options['alert_soundcmd']):
                            scmd = expand_template(
                                self.options['alert_soundcmd'], hsh)
                            process.startDetached(scmd)
                        else:
                            QMessageBox.warning(
                                self, "etm", self.tr("""\
A sound alert failed. The setting for 'alert_soundcmd' is missing from \
your etm.cfg."""))
                    if 'd' in actions:
                        if ('alert_displaycmd' in self.options and
                                self.options['alert_displaycmd']):
                            dcmd = expand_template(
                                self.options['alert_displaycmd'], hsh)
                            process.startDetached(dcmd)
                        else:
                            QMessageBox.warning(
                                self, "etm", self.tr("""\
A display alert failed. The setting for 'alert_displaycmd' is missing \
from your etm.cfg."""))
                    if 'v' in actions:
                        if ('alert_voicecmd' in self.options and
                                self.options['alert_voicecmd']):
                            vcmd = expand_template(
                                self.options['alert_voicecmd'], hsh)
                            process.startDetached(vcmd)
                        else:
                            QMessageBox.warning(
                                self, "etm", self.tr("""\
An email alert failed. The setting for 'alert_voicecmd' is missing from \
your etm.cfg."""))
                    if 'e' in actions:
                        missing = []
                        for field in [
                                'smtp_from',
                                'smtp_id',
                                'smtp_pw',
                                'smtp_server',
                                'smtp_to']:
                            if not self.options[field]:
                                missing.append(field)
                        if missing:
                            QMessageBox.warning(
                                self, "etm", self.tr("""\
An email alert failed. Settings for the following variables are missing \
from your etm.cfg: %s.""" % ", ".join(["'%s'" % x for x in missing])))
                        else:
                            subject = hsh['summary']
                            message = expand_template(
                                self.options['email_template'], hsh)
                            arguments = hsh['_alert_argument']
                            recipients = [str(x).strip() for x in arguments[0]]
                            if len(arguments) > 1:
                                attachments = [str(x).strip()
                                               for x in arguments[1]]
                            else:
                                attachments = []
                            if subject and message and recipients:
                                send_mail(
                                    smtp_to=recipients,
                                    subject=subject,
                                    message=message,
                                    files=attachments,
                                    smtp_from=self.options['smtp_from'],
                                    smtp_server=self.options['smtp_server'],
                                    smtp_id=self.options['smtp_id'],
                                    smtp_pw=self.options['smtp_pw'])
                    if 'm' in actions:

                        mbox = QMessageBox(self)
                        mbox.setWindowTitle("etm")  # ignored in os x
                        mbox.setIconPixmap(
                            QPixmap(":/etm.png").scaledToWidth(60))
                        mbox.setText(expand_template('!summary!', hsh))
                        mbox.setInformativeText(
                            expand_template(
                                self.options['alert_template'], hsh))
                        mbox.show()

                    if 't' in actions:
                        missing = []
                        for field in [
                                'sms_from',
                                'sms_message',
                                'sms_phone',
                                'sms_pw',
                                'sms_server',
                                'sms_subject']:
                            if not self.options[field]:
                                missing.append(field)
                        if missing:
                            QMessageBox.warning(
                                self, "etm", self.tr("""\
A text alert failed. Settings for the following variables are missing \
from your 'emt.cfg': %s.""" % ", ".join(["'%s'" % x for x in missing])))
                        else:
                            message = expand_template(
                                self.options['sms_message'], hsh)
                            subject = expand_template(
                                self.options['sms_subject'], hsh)
                            arguments = hsh['_alert_argument']
                            if arguments:
                                sms_phone = ",".join([str(x).strip() for x in
                                            arguments[0]])
                            else:
                                sms_phone = self.options['sms_phone']
                            if message:
                                send_text(
                                    sms_phone=sms_phone,
                                    subject=subject,
                                    message=message,
                                    sms_from=self.options['sms_from'],
                                    sms_server=self.options['sms_server'],
                                    sms_pw=self.options['sms_pw'])
                    if 'p' in actions:
                        arguments = hsh['_alert_argument']
                        proc = str(arguments[0][0]).strip()
                        cmd = expand_template(proc, hsh)
                        process.startDetached(cmd)

                    if not self.alerts:
                        break
                    td = self.alerts[0][0] - curr_minutes

        if self.alerts:
            self.alertsButton.setToolTip("{1} {0}".format(self.tr("remaining alerts for today"), len(self.alerts)))
            self.alertsButton.show()
        else:
            self.alertsButton.hide()

        if self.now_tree:
            self.todayButton.show()
        else:
            self.todayButton.hide()
        if self.messages:
            self.errorButton.show()
        else:
            self.errorButton.hide()

        self.getTimer()

        # update status every minute
        if self.timer_status == 'running':
            if ('running' in self.options['action_status'] and
                    self.options['action_status']['running']):
                tcmd = expand_template(
                    self.options['action_status']['running'],
                    self.timer_status_hsh)
                os.system(tcmd)
        elif self.timer_status == 'paused':
            if ('paused' in self.options['action_status'] and
                    self.options['action_status']['paused']):
                tcmd = expand_template(
                    self.options['action_status']['paused'],
                    self.timer_status_hsh)
                os.system(tcmd)

        # update timer every action_interval minutes
        if (self.options['action_interval'] and self.timer_minutes > 0
                and self.timer_minutes % self.options['action_interval'] == 0):
            if self.timer_status == 'running':
                if ('running' in self.options['action_timer'] and
                        self.options['action_timer']['running']):
                    tcmd = self.options['action_timer']['running']
                    process.startDetached(tcmd)
            elif self.timer_status == 'paused':
                if ('paused' in self.options['action_timer'] and
                        self.options['action_timer']['paused']):
                    tcmd = self.options['action_timer']['paused']
                    process.startDetached(tcmd)

        # now that the work is done, calculate seconds remaining
        # until the next timeout
        self.now = datetime.now(tzlocal())
        nxt = (60 - self.now.second) * 1000
        nowfmt = " {0} {1}".format(
            s2or3(self.now.strftime(self.options['reprtimefmt']).lower()),
            s2or3(self.now.strftime("%a %b %d %Z")))
        nowfmt = leadingzero.sub("", nowfmt)

        self.currentTime.setText(nowfmt)
        self.timer.start(nxt)

    def jumpToDate(self):
        datestr, ok = QInputDialog.getText(
            self, self.tr("jump to date"), "%s:" % self.tr("date"))
        if ok:
            dt = parse(
                parse_datetime(
                    str(datestr)), dayfirst=self.options['dayfirst'],
                yearfirst=self.options['yearfirst']).replace(tzinfo=None)
            if dt:
                self.scrollToDate(dt.date())
                return(True)
        return(False)

    def openScratchPad(self, modified=False):
        if 'scratchpad' in self.editor_instances:
            QMessageBox.warning(
                self, "etm", self.tr('scratchpad is already open'))
        else:
            form = getEditForm(
                self, instance='scratch',
                filename=self.scratch_file,
                highlight=False, use_completer=False)
            if form:
                form.setWindowTitle(self.tr("scratch pad"))
                cursor = form.editor.textCursor()
                cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
                form.editor.setTextCursor(cursor)
                form.show()

    def dateCalculator(self):
        datestr, ok = QInputDialog.getText(
            self, self.tr("datetime calculator"),
            "%s" % self.tr("""\
Enter an expression of the form "x [+-] y" where x is a date
and y is either a date or a time period if "-" is used and
a time period if "+" is used. """))
        if ok:
            dt = date_calculator(str(datestr))
            if type(dt) == datetime:
                res = fmt_datetime(dt, self.options)
            elif type(dt) == timedelta:
                res = timedelta2Str(dt)
            else:
                res = dt
            mbox = QMessageBox(self)
            mbox.setText(self.tr('etm date calculator'))
            mbox.setInformativeText("""\
<em>
%s:
<p><center>%s</center>
</em>
""" % (datestr, res))
            mbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            mbox.open()

            return(True)
        return(False)

    def timer_finish(self, create=True):
        if self.timer_status == 'stopped':
            return()
        self.timer_delta = max(self.timer_delta, oneminute)
        self.timer_status = 'stopped'
        if ('stopped' in self.options['action_status'] and
                self.options['action_status']['stopped']):
            tcmd = expand_template(
                self.options['action_status']['stopped'],
                self.timer_status_hsh)
            os.system(tcmd)

        if self.timer_hsh:
            # hsh = self.timer_hsh
            form = getEditForm(
                self, instance='edit', hsh=self.timer_hsh,
                receiver=self.itemChanged)
            if form:
                form.setWindowTitle(self.timer_hsh['_filetext'])
                # we're editing an item not a file
                form.filename = None
                if self.timer_hsh['e'] == timedelta(seconds=0):
                    # this is a copy, setup for fileSaveAs
                    form.hsh = None
                    form.suggested_file = self.timer_hsh['_filename']
                else:
                    # we are restarting, setup for fileSave
                    form.hsh = self.timer_hsh
                # self.timer_hsh['e'] = self.timer_delta
                self.timer_hsh['e'] = self.timer_minutes * oneminute
                inital_entry = hsh2str(self.timer_hsh, self.options)
                form.fileinfo = self.timer_hsh['fileinfo']
                form.rev_hsh = {}
                form.rev_str = ''
                # do this in editform
                form.editor.setPlainText(hsh2str(self.timer_hsh, self.options))
                form.editor.setModified()
                form.editor.suggested_file = self.timer_hsh['_filename']
                form.show()
            else:
                return()
        else:
            inital_entry = "~ %s @s %s @e %s" % (
                self.timer_summary,
                fmt_datetime(datetime.now(), self.options),
                fmt_period(self.timer_minutes * oneminute))
            res = self.createItem(
                title=self.tr("action"), text=inital_entry, modified=True)
            if not res:
                return()
        self.newActionButton.setEnabled(True)
        self.newActionButton.setToolTip(
            "Click here or press 'a' to create a new action timer.")
        self.pause_restartButton.hide()
        self.timerLabel.hide()
        self.stopButton.hide()
        if self.timer_status == 'running':
            self.timer_delta += datetime.now() - self.timer_last

        self.timer_last = None

    def timer_start(self, hsh={}):
        text = ''
        if hsh:
            text = hsh2str(hsh, self.options)
        summary, ok = QInputDialog.getText(
            self, self.tr("new action"), "%s:" % self.tr("summary"),
            text=text)
        if ok:
            self.timer_summary = summary
            self.timer_description = ''
            self.timer_status_hsh['summary'] = str(summary)
            self.timer_status_hsh['time'] = "0:00"
            if ('running' in self.options['action_status'] and
                    self.options['action_status']['running']):
                tcmd = expand_template(
                    self.options['action_status']['running'],
                    self.timer_status_hsh)
                os.system(tcmd)
            return(True)

        return(False)

    def timer_toggle(self, hsh={}):
        if self.timer_status == 'stopped':
            if not self.timer_start():
                return()
            self.timer_delta = timedelta(seconds=0)
            self.timer_last = datetime.now()
            self.timer_status = 'running'
            self.newActionButton.setEnabled(False)
            self.timer_tooltip = "{0}: '{1}'".format(
                self.tr('active timer'), self.timer_summary)
            self.newActionButton.setToolTip(self.timer_tooltip)
            self.stopButton.show()
            self.timerLabel.setText('0:00')
            if ('running' in self.options['action_timer'] and
                    self.options['action_timer']['running']):
                tcmd = self.options['action_timer']['running']
                process = QProcess()
                process.startDetached(tcmd)
            if ('running' in self.options['action_status'] and
                    self.options['action_status']['running']):
                tcmd = expand_template(
                    self.options['action_status']['running'],
                    self.timer_status_hsh)
                os.system(tcmd)
            self.timerLabel.show()
            self.pause_restartButton.show()
            self.pause_restartButton.setIcon(QIcon(":/action_pause.png"))
            self.pause_restartButton.setToolTip(
                self.tr(
                    "Click here or press Ctrl-T to pause the action timer."))
            self.stopButton.setToolTip(
                self.tr("""\
Click here or press Shift Ctrl-T to stop the timer and record the action."""))
            self.timerLabel.setStyleSheet('color: green')
            self.timerLabel.setToolTip(
                "'{0}': {1}".format(self.timer_summary, self.tr('running')))
        elif self.timer_status == 'running':
            self.timer_delta += datetime.now() - self.timer_last
            self.timer_status = 'paused'
            self.pause_restartButton.setToolTip(
                "Click here or press Ctrl-T to restart the action timer.")
            self.pause_restartButton.setIcon(QIcon(":/action_restart.png"))
            self.timerLabel.setStyleSheet('color: red')
            self.timerLabel.setToolTip(
                "'{0}': {1}".format(self.timer_summary, self.tr('paused')))
            if ('paused' in self.options['action_timer'] and
                    self.options['action_timer']['paused']):
                tcmd = self.options['action_timer']['paused']
                process = QProcess()
                process.startDetached(tcmd)
            if ('paused' in self.options['action_status'] and
                    self.options['action_status']['paused']):
                tcmd = expand_template(
                    self.options['action_status']['paused'],
                    self.timer_status_hsh)
                os.system(tcmd)
        elif self.timer_status == 'paused':
            self.timer_status = 'running'
            self.timer_last = datetime.now()
            self.pause_restartButton.setIcon(QIcon(":/action_pause.png"))
            self.pause_restartButton.setToolTip(
                self.tr(
                    "Click here or press Ctrl-T to pause the action timer."))
            self.timerLabel.setStyleSheet('color: green')
            self.timerLabel.setToolTip(
                "'{0}': {1}".format(self.timer_summary, self.tr('running')))
            if ('running' in self.options['action_timer'] and
                    self.options['action_timer']['running']):
                tcmd = self.options['action_timer']['running']
                process = QProcess()
                process.startDetached(tcmd)
            if ('running' in self.options['action_status'] and
                    self.options['action_status']['running']):
                tcmd = expand_template(
                    self.options['action_status']['running'],
                    self.timer_status_hsh)
                os.system(tcmd)

    def getTimer(self):
        m = 0
        h = 0
        if self.timer_status == 'paused':
            seconds = self.timer_delta.seconds
        elif self.timer_status == 'running':
            seconds = (self.timer_delta + datetime.now() -
                       self.timer_last).seconds
        else:
            seconds = 0
            self.timer_minutes = 0
        if seconds > 0:
            if seconds % (60 * 60) % 60 >= 30:
                seconds += 60 - seconds % (60 * 60) % 60
            h = seconds // (60 * 60)
            m = seconds % (60 * 60) // 60
            self.timer_minutes = h * 60 + m
        self.timerLabel.setText('%d:%02d' % (h, m))
        self.timer_status_hsh['time'] = '%d:%02d' % (h, m)

    def showStatusMessage(self, message):
        self.status_message.setText(message)
        QTimer.singleShot(3000, self.clearStatusMessage)

    def clearStatusMessage(self):
        self.status_message.setText('')

    def createItem(self, title=None, text="", modified=False):
        if not title:
            title = self.tr("new item")
        form = getEditForm(
            self, instance='edit', receiver=self.itemChanged)
        if form:
            form.setWindowTitle(title)
            uuid = uniqueId()
            form.editor.setPlainText('%s\n' % (text))
            #                    rev_id, rev_str, new_id
            form.setEditInfo(None, '', uuid)
            form.filename = None
            form.rev_hsh = {}
            form.rev_str = ''
            if modified:
                form.editor.setModified()
            form.show()
            return(True)
        return(False)

    def createReport(self):
        form = ReportForm(self)
        form.raise_()
        form.show()
        return(True)

    def showAgenda(self):
        html, count2id = getAgenda(
            self.all_rows,
            colors=self.options['agenda_colors'],
            days=self.options['agenda_days'],
            indent=self.options['agenda_indent'],
            width1=self.options['agenda_width1'],
            width2=self.options['agenda_width2'],
            calendars=self.options['calendars'],
            html=True)
        form = ReportForm(self)
        form.setHtml("<pre>%s</pre>" % "\n".join(html))
        form.minusButton.hide()
        form.reportBox.hide()
        form.saveButton.hide()
        form.reportButton.hide()
        form.setWindowTitle(self.tr("Schedule"))
        form.resize(
            (self.options['agenda_width1'] + self.options['agenda_width2'])
            * 10 + 16, 380)
        form.show()
        return(True)

    def mainHelp(self):
        form = HelpForm(self, 0)
        form.setWindowTitle('etm')
        form.show()

    def aboutHelp(self):
        d = {
            'copyright': '2009-%s' % datetime.today().strftime("%Y"),
            'home': '<a href="http://www.duke.edu/~dgraham/etmqt">home</a>',
            'dev': '<a href="mailto:daniel.graham@duke.edu">Daniel Graham</a>',
            'group': """<a href="http://groups.google.com/group/eventandtaskmanager/topics"> forum</a>""",
            'gpl': '<a href="http://www.gnu.org/licenses/gpl.html">license</a>',
            'version': version,
            'platform': platform.system(),
            'python': platform.python_version(),
            'dateutil': dateutil_version,
            'qt': QT_VERSION_STR,
            'pyqt': PYQT_VERSION_STR,
            'sip': SIP_VERSION_STR}

        QMessageBox.about(
            self, "About etm",
            """\
<b>Event and Task Manager</b> v {0[version]}
<p>This application provides a format for using plain text
files to store actions, events, notes, and tasks and a PyQt
based GUI for creating and modifying items as well as viewing
them.
<p>Copyright &copy; {0[copyright]} {0[dev]}. All rights
reserved. This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at your
option) any later version.
<p>Python {0[python]}, dateutil {0[dateutil]}, Qt {0[qt]}, SIP {0[sip]},
PyQt {0[pyqt]} on {0[platform]}.
<center>
{0[home]} &nbsp;&nbsp; {0[group]} &nbsp;&nbsp; {0[gpl]} &nbsp;&nbsp;</center>
""".format(d))

    def showAlerts(self):
        header = "{0:^7}\t{1:^7}\t{2:<8}{3:<30}".format(
            self.tr('alert'),
            self.tr('event'),
            self.tr('type'),
            self.tr('summary'))
        divider = '-' * 60
        if self.alerts:
            for alert in self.alerts:
                s = '%s\n%s\n%s' % (
                    header, divider, "\n".join(
                        ["{0:^7}\t{1:^7}\t{2:<8}{3:<30}".format(
                            x[1]['alert_time'], x[1]['_event_time'],
                            ", ".join(x[1]['_alert_action']),
                            utf8(x[1]['summary'][:30])) for x in self.alerts]))

        else:
            s = self.tr("none")
        mbox = QMessageBox(self)
        mbox.setText(self.tr('remaining alerts for today'))
        mbox.setInformativeText(QString(s))
        mbox.setTextFormat(Qt.RichText)
        mbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mbox.open()

    def checkNewer(self):
        ok, msg = checkForNewerVersion()
        mbox = QMessageBox(self)
        mbox.setText(self.tr('etm update information'))
        mbox.setInformativeText(msg)
        mbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mbox.open()

    def importIcal(self):
        if not has_icalendar:
            QMessageBox.warning(
                self, "import error",
                "Could not import icalendar - aborted.")
            return()

        d = self.options['icsimport_dir']
        fname = unicode(
            QFileDialog.getOpenFileName(
                self, 'Import ICS File', d,
                filter=self.tr("ICS files (*.ics)"),
                options=QFileDialog.DontUseNativeDialog))
        if not fname:
            return()
        newlines = import_ical(fname)
        while len(newlines) > 0 and not newlines[-1]:
            newlines.pop(-1)
        d = self.options['datadir']
        fname = unicode(
            QFileDialog.getSaveFileName(
                self, '', d, filter=self.tr("etm data files (*.txt)"),
                options=QFileDialog.DontUseNativeDialog |
                QFileDialog.DontConfirmOverwrite))
        if not fname:
            return()
        fname = "%s.txt" % os.path.splitext(fname)[0]

        if os.path.exists(fname):
            fo = codecs.open(fname, 'r', file_encoding)
            lines = [x.rstrip() for x in fo.readlines()]
            fo.close()
            while len(lines) > 0 and not lines[-1]:
                lines.pop(-1)
        else:
            lines = []
        lastline = len(lines)
        lines.extend(newlines)
        fo = codecs.open(fname, 'w', file_encoding)
        fo.writelines("\n".join(lines))
        fo.close()

        # count lines again since items may be multiline
        fo = codecs.open(fname, 'r', file_encoding)
        alllines = fo.readlines()
        fo.close()
        addedlines = len(alllines) - lastline
        # print('added lines', addedlines, lastline, len(alllines))

        form = EditForm(
            parent=self,
            instance='import',
            filename=fname,
            hsh=None,
            receiver=self.itemChanged,
            highlight=True,
            use_completer=True)

        if form:
            form.resize(
                self.options['window_width'],
                self.options['window_height'] - 30)
            form.setWindowTitle("{0}".format(self.options['auto_completions']))
            form.helpPage = 1
            # set the cursor at the end and then move it back to the
            # beginning of the addition to leave the addition selected
            cursor = form.editor.textCursor()
            cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            cursor.movePosition(
                QTextCursor.Up, QTextCursor.KeepAnchor, addedlines - 1)

            form.editor.setTextCursor(cursor)

            form.show()

    def exportIcal(self):
        if not has_icalendar:
            QMessageBox.warning(
                self, "import error",
                "Could not import icalendar - aborted.")
            return()

        msgBox = QMessageBox(self)
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText(self.tr("iCalendar Export"))
        msgBox.setInformativeText(
            self.tr(
                "Save items in selected calendars to the file\n\n{0}?".format(
                    self.options['icscal_file'])))
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Ok)
        # must use exec_ here
        reply = msgBox.exec_()
        if reply != QMessageBox.Ok:
            return(False)

        ok, msg = export_ical(
            self.uuid2hash, self.options['icscal_file'], self.calendars)
        if ok:
            if self.calendars:
                calendars = "items in calendars:\n      {0}".format(
                    ", ".join(["'{0}'".format(x[0]) for x in
                            self.calendars if x[1]]))
            else:
                calendars = "all items"
            msg = "Exported {0}\nto {1}".format(
                calendars, self.options['icscal_file'])

        mbox = QMessageBox(self)
        mbox.setText(self.tr('etm vcalendar export'))
        mbox.setInformativeText(msg)
        mbox.resize(600, 200)
        mbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mbox.show()

    def showCalendar(self):
        form = CalendarYearForm(self)
        form.setWindowTitle('etm')
        # lst = calyear(0, self.options)
        form.show()

    def showWeather(self):
        if self.getWeather:
            ok, weather = self.getWeather()
            html = ""
            if ok:
                html = "\n".join([str(x) for x in weather])
            else:
                html += "%s" % str(weather)
            mbox = QMessageBox(self)
            mbox.setText(self.tr('yahoo weather information'))
            mbox.setInformativeText(html)
            mbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            mbox.open()
        else:
            QMessageBox.information(
                self, "etm", self.tr("""\
The setting for 'weather_location' in etm.cfg is required for this \
operation."""))

    def showSunMoon(self, enabled=True):
        if self.getSunMoon:
            ok, sunmoon = self.getSunMoon(self.options['sunmoon_location'])
            if ok:
                html = "%s" % "\n".join(sunmoon)
            else:
                html = "%s" % sunmoon
            mbox = QMessageBox(self)
            mbox.setText(self.tr('USNO sunmoon information'))
            mbox.setInformativeText(html)
            mbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            mbox.open()
        else:
            QMessageBox.information(
                self, "etm",
                self.tr("""\
The setting for 'sunmoon_location' in etm.cfg is required for this \
operation."""))

    def closeEvent(self, event):
        self.timer_finish()
        self.timer.stop()
        self.update()
        QApplication.closeAllWindows()


def main(etmdir=''):
    app = QApplication(sys.argv)
    global use_locale, file_encoding, term_encoding, gui_encoding
    use_locale = ()
    (user_options, options, use_locale) = get_options(etmdir=etmdir)
    file_encoding = options['encoding']['file']
    term_encoding = options['encoding']['term']
    gui_encoding = options['encoding']['gui']
    if use_locale:
        locale.setlocale(locale.LC_ALL, map(str, use_locale[0]))
        qlcl = options['qlcl']
        Qlcl = QLocale()
        Qlcl.setDefault(qlcl)
    else:
        Qlcl = QLocale()
        qlcl = Qlcl.system()

    QLocale.setDefault(qlcl)
    qtTranslator = QTranslator()
    if qtTranslator.load("qt_" + qlcl.name(), ":/"):
        app.installTranslator(qtTranslator)
    appTranslator = QTranslator()
    if appTranslator.load("etm_" + qlcl.name(), ":/"):
        app.installTranslator(appTranslator)
    if qt_version == 5:
        app.setApplicationDisplayName("etm")
    else:
        app.setApplicationName("etm")
    app.setWindowIcon(QIcon(":/etm.png"))

    window = UiWindow(options=options)
    window.resize(options['window_width'], options['window_height'])
    window.options = options
    window.calendarWidget.setLocale(qlcl)

    window.loadFileData()
    window.loadViewData()
    window.refreshViews()
    if etmdir:
        window.eg = etmdir
    window.show()
    window.raise_()
    window.showMessages(force=False)
    window.timeout()
    res = app.exec_()
    sys.exit(res)

if __name__ == "__main__":
    etmdir = ''
    if len(sys.argv) > 1:
        etmdir = sys.argv[1]
    main(etmdir)
