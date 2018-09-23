#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import os.path
# import pwd
from copy import deepcopy
from textwrap import wrap
import platform
import json

import logging
import logging.config
logger = logging.getLogger()

this_dir, this_filename = os.path.split(__file__)
LANGUAGES = os.path.normpath(os.path.join(this_dir, "locale"))

BGCOLOR = HLCOLOR = FGCOLOR = CALENDAR_COLORS = None


def _(x):
    return(x)


def setup_logging(level, etmdir=None):
    """
    Setup logging configuration. Override root:level in
    logging.yaml with default_level.
    """
    if etmdir:
        etmdir = os.path.normpath(etmdir)
    else:
        etmdir = os.path.normpath(os.path.join(os.path.expanduser("~/.etm")))
    log_levels = {
        '1': logging.DEBUG,
        '2': logging.INFO,
        '3': logging.WARN,
        '4': logging.ERROR,
        '5': logging.CRITICAL
    }

    if level in log_levels:
        loglevel = log_levels[level]
    else:
        loglevel = log_levels['3']

    if os.path.isdir(etmdir):
        logfile = os.path.normpath(os.path.abspath(os.path.join(etmdir, "etmtk_log.txt")))
        if not os.path.isfile(logfile):
            open(logfile, 'a').close()

        config = {'disable_existing_loggers': False,
                  'formatters': {'simple': {
                      'format': '--- %(asctime)s - %(levelname)s - %(module)s.%(funcName)s\n    %(message)s'}},
                  'handlers': {'console': {'class': 'logging.StreamHandler',
                                           'formatter': 'simple',
                                           'level': loglevel,
                                           'stream': 'ext://sys.stdout'},
                               'file': {'backupCount': 5,
                                        'class': 'logging.handlers.RotatingFileHandler',
                                        'encoding': 'utf8',
                                        'filename': logfile,
                                        'formatter': 'simple',
                                        'level': 'WARN',
                                        'maxBytes': 1048576}},
                  'loggers': {'etmtk': {'handlers': ['console'],
                                        'level': 'DEBUG',
                                        'propagate': False}},
                  'root': {'handlers': ['console', 'file'], 'level': 'DEBUG'},
                  'version': 1}
        logging.config.dictConfig(config)
        logger.info('logging at level: {0}\n    writing exceptions to: {1}'.format(loglevel, logfile))
    else:  # no etmdir - first use
        config = {'disable_existing_loggers': False,
                  'formatters': {'simple': {
                      'format': '--- %(asctime)s - %(levelname)s - %(module)s.%(funcName)s\n    %(message)s'}},
                  'handlers': {'console': {'class': 'logging.StreamHandler',
                                           'formatter': 'simple',
                                           'level': loglevel,
                                           'stream': 'ext://sys.stdout'}},
                  'loggers': {'etmtk': {'handlers': ['console'],
                                        'level': 'DEBUG',
                                        'propagate': False}},
                  'root': {'handlers': ['console'], 'level': 'DEBUG'},
                  'version': 1}
        logging.config.dictConfig(config)
        logger.info('logging at level: {0}'.format(loglevel))

import subprocess

# setup gettext in get_options once locale is known
import gettext

if platform.python_version() >= '3':
    python_version = 3
    python_version2 = False
    from io import StringIO
    unicode = str
    u = lambda x: x
    raw_input = input
    from urllib.parse import quote
else:
    python_version = 2
    python_version2 = True
    from cStringIO import StringIO
    from urllib2 import quote

def s2or3(s):
    if python_version == 2:
        if type(s) is unicode:
            return s
        elif type(s) is str:
            try:
                return unicode(s, term_encoding)
            except ValueError:
                logger.error('s2or3 exception: {0}'.format(s))
        else:
            return s
    else:
        return s

from random import random, uniform
from math import log


class Node(object):
    __slots__ = 'value', 'next', 'width'

    def __init__(self, value, next, width):
        self.value, self.next, self.width = value, next, width


class End(object):
    """
    Sentinel object that always compares greater than another object.
    Replaced __cmp__ to work with python3.x
    """

    def __eq__(self, other):
        return 0

    def __ne__(self, other):
        return 1

    def __gt__(self, other):
        return 1

    def __ge__(self, other):
        return 1

    def __le__(self, other):
        return 0

    def __lt__(self, other):
        return 0

# Singleton terminator node
NIL = Node(End(), [], [])


class IndexableSkiplist:
    """Sorted collection supporting O(lg n) insertion, removal, and lookup by rank."""

    def __init__(self, expected_size=100, type=""):
        self.size = 0
        self.type = type
        self.maxlevels = int(1 + log(expected_size, 2))
        self.head = Node('HEAD', [NIL] * self.maxlevels, [1] * self.maxlevels)

    def __len__(self):
        return self.size

    def __getitem__(self, i):
        node = self.head
        i += 1
        for level in reversed(range(self.maxlevels)):
            while node.width[level] <= i:
                i -= node.width[level]
                node = node.next[level]
        return node.value

    def insert(self, value):
        # find first node on each level where node.next[levels].value > value
        chain = [None] * self.maxlevels
        steps_at_level = [0] * self.maxlevels
        node = self.head
        for level in reversed(range(self.maxlevels)):
            try:
                while node.next[level].value <= value:
                    steps_at_level[level] += node.width[level]
                    node = node.next[level]
                chain[level] = node
            except:
                logger.exception('Error comparing {0}:\n    {1}\n    with the value to be inserted\n    {2}'.format(self.type, node.next[level].value, value))
                return

        # insert a link to the newnode at each level
        d = min(self.maxlevels, 1 - int(log(random(), 2.0)))
        newnode = Node(value, [None] * d, [None] * d)
        steps = 0
        for level in range(d):
            prevnode = chain[level]
            newnode.next[level] = prevnode.next[level]
            prevnode.next[level] = newnode
            newnode.width[level] = prevnode.width[level] - steps
            prevnode.width[level] = steps + 1
            steps += steps_at_level[level]
        for level in range(d, self.maxlevels):
            chain[level].width[level] += 1
        self.size += 1

    def remove(self, value):
        # find first node on each level where node.next[levels].value >= value
        chain = [None] * self.maxlevels
        node = self.head
        for level in reversed(range(self.maxlevels)):
            try:
                while node.next[level].value < value:
                    node = node.next[level]
                chain[level] = node
            except:
                logger.exception('Error comparing {0}:\n    {1}\n    with the value to be removed\n    {2}'.format(self.type, node.next[level].value, value))
        if value != chain[0].next[0].value:
            raise KeyError('Not Found')

        # remove one link at each level
        d = len(chain[0].next[0].next)
        for level in range(d):
            prevnode = chain[level]
            prevnode.width[level] += prevnode.next[level].width[level] - 1
            prevnode.next[level] = prevnode.next[level].next[level]
        for level in range(d, self.maxlevels):
            chain[level].width[level] -= 1
        self.size -= 1

    def __iter__(self):
        'Iterate over values in sorted order'
        node = self.head.next[0]
        while node is not NIL:
            yield node.value
            node = node.next[0]

# initial instances

itemsSL = IndexableSkiplist(5000, "items")
alertsSL = IndexableSkiplist(100, "alerts")
datetimesSL = IndexableSkiplist(1000, "datetimes")
datesSL = IndexableSkiplist(1000, "dates")
busytimesSL = {}
occasionsSL = {}
items = []
alerts = []
datetimes = []
busytimes = {}
occasions = {}
file2uuids = {}
uuid2hash = {}
file2data = {}

name2list = {
    "items": items,
    "alerts": alerts,
    "datetimes": datetimes
}
name2SL = {
    "items": itemsSL,
    "alerts": alertsSL,
    "datetimes": datetimesSL
}


def clear_all_data():
    global itemsSL, alertsSL, datetimesSL, datesSL, busytimesSL, occasionsSL, items, alerts, datetimes, busytimes, occasions, file2uuids, uuid2hash, file2data, name2list, name2SL
    itemsSL = IndexableSkiplist(5000, "items")
    alertsSL = IndexableSkiplist(100, "alerts")
    datetimesSL = IndexableSkiplist(1000, "datetimes")
    datesSL = IndexableSkiplist(1000, "dates")
    busytimesSL = {}
    occasionsSL = {}
    items = []
    alerts = []
    datetimes = []
    busytimes = {}
    occasions = {}
    file2uuids = {}
    uuid2hash = {}
    file2data = {}

    name2list = {
        "items": items,
        "alerts": alerts,
        "datetimes": datetimes
    }
    name2SL = {
        "items": itemsSL,
        "alerts": alertsSL,
        "datetimes": datetimesSL
    }


dayfirst = False
yearfirst = True

IGNORE = """\
syntax: glob
.*
"""

from datetime import datetime, timedelta, time
from dateutil.tz import (tzlocal, tzutc)
from dateutil.easter import easter


def get_current_time():
    return datetime.now(tzlocal())

# this task will be created for first time users
SAMPLE = """\
# Sample entries - edit or delete at your pleasure
= @t sample, tasks
? lose weight and exercise more
- milk and eggs @c errands
- reservation for Saturday dinner @c phone
- hair cut @s -1 @r w &i 2 &o r @c errands
- put out trash @s 1 @r w &w MO @o s

= @t sample, occasions
^ etm's !2009! birthday @s 2010-02-27 @r y @d initial release 2009-02-27
^ payday @s 1/1 @r m &w MO, TU, WE, TH, FR &m -1, -2, -3 &s -1 @d the last weekday of each month

= @t sample, events
* sales meeting @s +7 9a @e 1h @a 5 @a 2d: e; who@when.com, what@where.org @u jsmith
* stationary bike @s 1 5:30p @e 30 @r d @a 0
* Tête-à-têtes @s 1 3p @e 90 @r w &w fri @l conference room @t meetings
* Book club @s -1/1 7pm @e 2h @z US/Eastern @r w &w TH
* Tennis @s -1/1 9am @e 1h30m @z US/Eastern @r w &w SA
* Dinner @s -1/1 7:30pm @e 2h30m @z US/Eastern @a 1h, 40m: m @u dag @r w &w SA
* Appt with Dr Burns @s 2014-05-15 10am @e 1h @r m &i 9 &w 1TU &t 2
"""

HOLIDAYS = """\
^ Martin Luther King Day @s 2010-01-18 @r y &w 3MO &M 1
^ Valentine's Day @s 2010-02-14 @r y &M 2 &m 14
^ President's Day @s 2010-02-15 @c holiday @r y &w 3MO &M 2
^ Daylight saving time begins @s 2010-03-14 @r y &w 2SU &M 3
^ St Patrick's Day @s 2010-03-17 @r y &M 3 &m 17
^ Easter Sunday @s 2010-01-01 @r y &E 0
^ Mother's Day @s 2010-05-09 @r y &w 2SU &M 5
^ Memorial Day @s 2010-05-31 @r y &w -1MO &M 5
^ Father's Day @s 2010-06-20 @r y &w 3SU &M 6
^ The !1776! Independence Day @s 2010-07-04 @r y &M 7 &m 4
^ Labor Day @s 2010-09-06 @r y &w 1MO &M 9
^ Daylight saving time ends @s 2010-11-01 @r y &w 1SU &M 11
^ Thanksgiving @s 2010-11-26 @r y &w 4TH &M 11
^ Christmas @s 2010-12-25 @r y &M 12 &m 25
^ Presidential election day @s 2004-11-01 12am @r y &i 4 &m 2, 3, 4, 5, 6, 7, 8 &M 11 &w TU
"""

JOIN = "- join the etm discussion group @s +14 @b 10 @c computer @g http://groups.google.com/group/eventandtaskmanager/topics"

COMPETIONS = """\
# put completion phrases here, one per line. E.g.:
@z US/Eastern
@z US/Central
@z US/Mountain
@z US/Pacific

@c errands
@c phone
@c home
@c office

# empty lines and lines that begin with '#' are ignored.
"""

USERS = """\
jsmith:
    - Smith, John
    - jsmth@whatever.com
    - wife Rebecca
    - children Tom, Dick and Harry
"""

REPORTS = """\
# put report specifications here, one per line. E.g.:

# scheduled items this week:
c ddd, MMM dd yyyy -b mon - 7d -e +7

# this and next week:
c ddd, MMM dd yyyy -b mon - 7d -e +14

# this month:
c ddd, MMM dd yyyy -b 1 -e +1/1

# this and next month:
c ddd, MMM dd yyyy -b 1 -e +2/1

# last month's actions:
a MMM yyyy; u; k[0]; k[1:] -b -1/1 -e 1

# this month's actions:
a MMM yyyy; u; k[0]; k[1:] -b 1 -e +1/1

# this week's actions:
a w; u; k[0]; k[1:] -b sun - 6d -e sun

# all items by folder:
c f

# all items by keyword:
c k

# all items by tag:
c t

# all items by user:
c u

# empty lines and lines that begin with '#' are ignored.
"""

# command line usage
USAGE = """\
Usage:

    etm [logging level] [path] [?] [acmsv]

With no arguments, etm will set logging level 3 (warn), use settings from
the configuration file ~/.etm/etmtk.cfg, and open the GUI.

If the first argument is an integer not less than 1 (debug) and not greater
than 5 (critical), then set that logging level and remove the argument.

If the first (remaining) argument is the path to a directory that contains
a file named etmtk.cfg, then use that configuration file and remove the
argument.

If the first (remaining) argument is one of the commands listed below, then
execute the remaining arguments without opening the GUI.

    a ARG   display the agenda view using ARG, if given, as a filter.
    c ARGS  display a custom view using the remaining arguments as the
            specification. (Enclose ARGS in single quotes to prevent shell
            expansion.)
    d ARG   display the day view using ARG, if given, as a filter.
    k ARG   display the keywords view using ARG, if given, as a filter.
    m INT   display a report using the remaining argument, which must be a
            positive integer, to display a report using the corresponding
            entry from the file given by report_specifications in etmtk.cfg.
            Use ? m to display the numbered list of entries from this file.
    n ARG   display the notes view using ARG, if given, as a filter.
    N ARGS  Create a new item using the remaining arguments as the item
            specification. (Enclose ARGS in single quotes to prevent shell
            expansion.)
    p ARG   display the path view using ARG, if given, as a filter.
    t ARG   display the tags view using ARG, if given, as a filter.
    v       display information about etm and the operating system.
    ? ARG   display (this) command line help information if ARGS = '' or,
            if ARGS = X where X is one of the above commands, then display
            details about command X. 'X ?' is equivalent to '? X'.\
"""

import re
import sys
import locale

# term_encoding = locale.getdefaultlocale()[1]
term_locale = locale.getdefaultlocale()[0]

qt2dt = [
    ('a', '%p'),
    ('dddd', '%A'),
    ('ddd', '%a'),
    ('dd', '%d'),
    ('MMMM', '%B'),
    ('MMM', '%b'),
    ('MM', '%m'),
    ('yyyy', '%Y'),
    ('yy', '%y'),
    ('hh', '%H'),
    ('h', '%I'),
    ('mm', '%M'),
    ('w', 'WEEK')
]


def commandShortcut(s):
    """
    Produce label, command pairs from s based on Command for OSX
    and Control otherwise.
    """
    if s.upper() == s and s.lower() != s:
        shift = "Shift-"
    else:
        shift = ""
    if mac:
        # return "{0}Cmd-{1}".format(shift, s), "<{0}Command-{1}>".format(shift, s)
        return "{0}Ctrl-{1}".format(shift, s.upper()), "<{0}Control-{1}>".format(shift, s)
    else:
        return "{0}Ctrl-{1}".format(shift, s.upper()), "<{0}Control-{1}>".format(shift, s)


def optionShortcut(s):
    """
    Produce label, command pairs from s based on Command for OSX
    and Control otherwise.
    """
    if s.upper() == s and s.lower() != s:
        shift = "Shift-"
    else:
        shift = ""
    if mac:
        return "{0}Alt-{1}".format(shift, s.upper()), "<{0}Option-{1}>".format(shift, s)
    else:
        return "{0}Alt-{1}".format(shift, s.upper()), "<{0}Alt-{1}>".format(shift, s)


def d_to_str(d, s):
    for key, val in qt2dt:
        s = s.replace(key, val)
    ret = s2or3(d.strftime(s))
    if 'WEEK' in ret:
        theweek = get_week(d)
        ret = ret.replace('WEEK', theweek)
    return ret


def dt_to_str(dt, s):
    for key, val in qt2dt:
        s = s.replace(key, val)
    ret = s2or3(dt.strftime(s))
    if 'WEEK' in ret:
        theweek = get_week(dt)
        ret = ret.replace('WEEK', theweek)
    return ret


def get_week(dt):
    yn, wn, dn = dt.isocalendar()
    if dn > 1:
        days = dn - 1
    else:
        days = 0
    weekbeg = dt - days * ONEDAY
    weekend = dt + (6 - days) * ONEDAY
    ybeg = weekbeg.year
    yend = weekend.year
    mbeg = weekbeg.month
    mend = weekend.month
    if mbeg == mend:
        header = "{0} - {1}".format(
            fmt_dt(weekbeg, '%b %d'), fmt_dt(weekend, '%d'))
    elif ybeg == yend:
        header = "{0} - {1}".format(
            fmt_dt(weekbeg, '%b %d'), fmt_dt(weekend, '%b %d'))
    else:
        header = "{0} - {1}".format(
            fmt_dt(weekbeg, '%b %d, %Y'), fmt_dt(weekend, '%b %d, %Y'))
    header = leadingzero.sub('', header)
    theweek = "{0} {1}: {2}".format(_("Week"), "{0:02d}".format(wn), header)
    return theweek


from etmTk.v import version
from etmTk.version import version as fullversion

last_version = version

from re import split as rsplit

sys_platform = platform.system()
if sys_platform in ('Windows', 'Microsoft'):
    windoz = True
    from time import clock as timer
else:
    windoz = False
    from time import time as timer

if sys.platform == 'darwin':
    mac = True
    CMD = "Command"
    default_style = 'aqua'
else:
    mac = False
    CMD = "Control"
    default_style = 'default'

# used in hack to prevent dialog from hanging under os x
if mac:
    AFTER = 200
else:
    AFTER = 1


class TimeIt(object):
    def __init__(self, loglevel=1, label=""):
        self.loglevel = loglevel
        self.label = label
        msg = "{0} timer started".format(self.label)
        if self.loglevel == 1:
            logger.debug(msg)
        elif self.loglevel == 2:
            logger.info(msg)
        self.start = timer()

    def stop(self, *args):
        self.end = timer()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        msg = "{0} timer stopped; elapsed time: {1} milliseconds".format(self.label, self.msecs)
        if self.loglevel == 1:
            logger.debug(msg)
        elif self.loglevel == 2:
            logger.info(msg)

has_icalendar = False
try:
    from icalendar import Calendar, Event, Todo, Journal
    from icalendar.caselessdict import CaselessDict
    from icalendar.prop import vDate, vDatetime
    has_icalendar = True
    import pytz
except ImportError:
    if has_icalendar:
        logger.info('Could not import pytz')
    else:
        logger.info('Could not import icalendar and/or pytz')
    has_icalendar = False

from time import sleep
import dateutil.rrule as dtR
from dateutil.parser import parse as dparse
from dateutil import __version__ as dateutil_version
# noinspection PyPep8Naming
from dateutil.tz import gettz as getTz


def memoize(fn):
    memo = {}

    def memoizer(*param_tuple, **kwds_dict):
        if kwds_dict:
            memoizer.namedargs += 1
            return fn(*param_tuple, **kwds_dict)
        try:
            memoizer.cacheable += 1
            try:
                return memo[param_tuple]
            except KeyError:
                memoizer.misses += 1
                memo[param_tuple] = result = fn(*param_tuple)
                return result
        except TypeError:
            memoizer.cacheable -= 1
            memoizer.noncacheable += 1
            return fn(*param_tuple)

    memoizer.namedargs = memoizer.cacheable = memoizer.noncacheable = 0
    memoizer.misses = 0
    return memoizer


@memoize
def gettz(z=None):
    return getTz(z)


import calendar

# import yaml
import ruamel.yaml as yaml
from itertools import groupby
# from dateutil.rrule import *
from dateutil.rrule import (DAILY, rrule)

import bisect
import uuid
import codecs
import shutil
import fnmatch


def term_print(s):
    if python_version2:
        try:
            print(unicode(s).encode(term_encoding))
        except Exception:
            logger.exception("error printing: '{0}', {1}".format(s, type(s)))
    else:
        print(s)


parse = None


def setup_parse(day_first, year_first):
    global parse

    # noinspection PyRedeclaration
    def parse(s):
        """
        Return a datetime object
        """
        try:
            res = dparse(str(s), dayfirst=day_first, yearfirst=year_first)
        except:
            return 'Could not parse: {0}'.format(s)

        return res


try:
    from os.path import relpath
except ImportError:  # python < 2.6
    from os.path import curdir, abspath, sep, commonprefix, pardir, join

    def relpath(path, start=curdir):
        """Return a relative version of a path"""
        if not path:
            raise ValueError("no path specified")
        start_list = abspath(start).split(sep)
        path_list = abspath(path).split(sep)
        # Work out how much of the filepath is shared by start and path.
        i = len(commonprefix([start_list, path_list]))
        rel_list = [pardir] * (len(start_list) - i) + path_list[i:]
        if not rel_list:
            return curdir
        return join(*rel_list)

cwd = os.getcwd()


def pathSearch(filename):
    search_path = os.getenv('PATH').split(os.pathsep)
    for path in search_path:
        candidate = os.path.normpath(os.path.join(path, filename))
        # logger.debug('checking for: {0}'.format(candidate))
        if os.path.isfile(candidate):
            # return os.path.abspath(candidate)
            return candidate
    return ''


def getMercurial():
    if windoz:
        hg = pathSearch('hg.exe')
    else:
        hg = pathSearch('hg')
    if hg:
        logger.debug('found hg: {0}'.format(hg))
        base_command = "hg -R {work}"
        history_command = 'hg log --style compact --template "{desc}\\n" -R {work} -p {numchanges} {file}'
        commit_command = 'hg commit -q -A -R {work} -m "{mesg}"'
        init = 'hg init {work}'
        init_command = "%s && %s" % (init, commit_command)
        logger.debug('hg base_command: {0}; history_command: {1}; commit_command: {2}; init_command: {3}'.format(base_command, history_command, commit_command, init_command))
    else:
        logger.debug('could not find hg in path')
        base_command = history_command = commit_command = init_command = ''
    return base_command, history_command, commit_command, init_command


def getGit():
    if windoz:
        git = pathSearch('git.exe')
    else:
        git = pathSearch('git')
    if git:
        logger.debug('found git: {0}'.format(git))
        base_command = "git --git-dir {repo} --work-tree {work}"
        history_command = "git --git-dir {repo} --work-tree {work} log --pretty=format:'- %ai %an: %s' -U0 {numchanges} {file}"
        init = 'git init {work}'
        add = 'git --git-dir {repo} --work-tree {work} add */\*.txt > /dev/null'
        commit = 'git --git-dir {repo} --work-tree {work} commit -a -m "{mesg}" > /dev/null'
        commit_command = '%s && %s' % (add, commit)
        init_command = '%s && %s && %s' % (init, add, commit)
        logger.debug('git base_command: {0}; history_command: {1}; commit_command: {2}; init_command: {3}'.format(base_command, history_command, commit_command, init_command))
    else:
        logger.debug('could not find git in path')
        base_command = history_command = commit_command = init_command = ''
    return base_command, history_command, commit_command, init_command


zonelist = [
    'Africa/Cairo',
    'Africa/Casablanca',
    'Africa/Johannesburg',
    'Africa/Mogadishu',
    'Africa/Nairobi',
    'America/Belize',
    'America/Buenos_Aires',
    'America/Edmonton',
    'America/Mexico_City',
    'America/Monterrey',
    'America/Montreal',
    'America/Toronto',
    'America/Vancouver',
    'America/Winnipeg',
    'Asia/Baghdad',
    'Asia/Bahrain',
    'Asia/Calcutta',
    'Asia/Damascus',
    'Asia/Dubai',
    'Asia/Hong_Kong',
    'Asia/Istanbul',
    'Asia/Jakarta',
    'Asia/Jerusalem',
    'Asia/Katmandu',
    'Asia/Kuwait',
    'Asia/Macao',
    'Asia/Pyongyang',
    'Asia/Saigon',
    'Asia/Seoul',
    'Asia/Shanghai',
    'Asia/Singapore',
    'Asia/Tehran',
    'Asia/Tokyo',
    'Asia/Vladivostok',
    'Atlantic/Azores',
    'Atlantic/Bermuda',
    'Atlantic/Reykjavik',
    'Australia/Sydney',
    'Europe/Amsterdam',
    'Europe/Berlin',
    'Europe/Lisbon',
    'Europe/London',
    'Europe/Madrid',
    'Europe/Minsk',
    'Europe/Monaco',
    'Europe/Moscow',
    'Europe/Oslo',
    'Europe/Paris',
    'Europe/Prague',
    'Europe/Rome',
    'Europe/Stockholm',
    'Europe/Vienna',
    'Pacific/Auckland',
    'Pacific/Fiji',
    'Pacific/Samoa',
    'Pacific/Tahiti',
    'Turkey',
    'US/Alaska',
    'US/Aleutian',
    'US/Arizona',
    'US/Central',
    'US/East-Indiana',
    'US/Eastern',
    'US/Hawaii',
    'US/Indiana-Starke',
    'US/Michigan',
    'US/Mountain',
    'US/Pacific']


def get_localtz(zones=zonelist):
    """

    :param zones: list of timezone strings
    :return: timezone string
    """
    linfo = gettz()
    now = get_current_time()
    # get the abbreviation for the local timezone, e.g, EDT
    possible = []
    # try the zone list first unless windows system
    if not windoz:
        for i in range(len(zones)):
            z = zones[i]
            zinfo = gettz(z)
            if zinfo and zinfo == linfo:
                possible.append(i)
                break
    if not possible:
        for i in range(len(zones)):
            z = zones[i]
            zinfo = gettz(z)
            if zinfo and zinfo.utcoffset(now) == linfo.utcoffset(now):
                possible.append(i)
    if not possible:
        # the local zone needs to be added to timezones
        return ['']
    return [zonelist[i] for i in possible]


def calyear(advance=0, options=None):
    """
    """
    if not options:
        options = {}
    lcl = options['lcl']
    if 'sundayfirst' in options and options['sundayfirst']:
        week_begin = 6
    else:
        week_begin = 0
        # hack to set locale on darwin, windoz and linux
    try:
        if mac:
            # locale test
            c = calendar.LocaleTextCalendar(week_begin, lcl[0])
        elif windoz:
            locale.setlocale(locale.LC_ALL, '')
            lcl = locale.getlocale()
            c = calendar.LocaleTextCalendar(week_begin, lcl)
        else:
            lcl = locale.getdefaultlocale()
            c = calendar.LocaleTextCalendar(week_begin, lcl)
    except:
        logger.exception('Could not set locale: {0}'.format(lcl))
        c = calendar.LocaleTextCalendar(week_begin)
    cal = []
    y = int(today.strftime("%Y"))
    m = 1
    # d = 1
    y += advance
    for i in range(12):
        cal.append(c.formatmonth(y, m).split('\n'))
        m += 1
        if m > 12:
            y += 1
            m = 1
    ret = []
    for r in range(0, 12, 3):
        l = max(len(cal[r]), len(cal[r + 1]), len(cal[r + 2]))
        for i in range(3):
            if len(cal[r + i]) < l:
                for j in range(len(cal[r + i]), l + 1):
                    cal[r + i].append('')
        for j in range(l):
            if python_version2:
                ret.append(s2or3(u'  %-20s    %-20s    %-20s' % (cal[r][j], cal[r + 1][j], cal[r + 2][j])))
            else:
                ret.append((u'  %-20s    %-20s    %-20s' % (cal[r][j], cal[r + 1][j], cal[r + 2][j])))
    return ret


def date_calculator(s, options=None):
    """
        x [+-] y
        where x is a datetime and y is either a datetime or a timeperiod
    :param s:
    """
    estr = estr_regex.search(s)
    if estr:
        y = estr.group(1)
        e = easter(int(y))
        E = e.strftime("%Y-%m-%d")
        s = estr_regex.sub(E, s)

    m = date_calc_regex.match(s)
    if not m:
        return 'Could not parse "%s"' % s
    x, pm, y = [z.strip() for z in m.groups()]
    xzs = None
    nx = timezone_regex.match(x)
    if nx:
        x, xzs = nx.groups()
    yz = tzlocal()
    yzs = None
    ny = timezone_regex.match(y)
    if ny:
        y, yzs = ny.groups()
        yz = gettz(yzs)
    windoz_epoch = _("Warning: any timezone information in dates prior to 1970 is ignored under Windows.")
    warn = ""
    try:
        dt_x = parse_str(x, timezone=xzs)
        pmy = "%s%s" % (pm, y)
        if period_string_regex.match(pmy):
            dt = (dt_x + parse_period(pmy, minutes=False))
            if windoz and (dt_x.year < 1970 or dt.year < 1970):
                warn = "\n\n{0}".format(windoz_epoch)
            else:
                dt.astimezone(yz)

            res = dt.strftime("%Y-%m-%d %H:%M%z")
            prompt = "{0}:\n\n{1}{2}".format(s.strip(), res.strip(), warn)
            return prompt
        else:
            dt_y = parse_str(y, timezone=yzs)
            if windoz and (dt_x.year < 1970 or dt_y.year < 1970):
                warn = "\n\n{0}".format(windoz_epoch)
                dt_x = dt_x.replace(tzinfo=None)
                dt_y = dt_y.replace(tzinfo=None)
            if pm == '-':
                res = fmt_period(dt_x - dt_y)
                prompt = "{0}:\n\n{1}{2}".format(s.strip(), res.strip(), warn)
                return prompt
            else:
                return 'error: datetimes cannot be added'
    except ValueError:
        return 'error parsing "%s"' % s


def mail_report(message, smtp_from=None, smtp_server=None,
                smtp_id=None, smtp_pw=None, smtp_to=None):
    """
    """
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    from email.Utils import COMMASPACE, formatdate
    # from email import Encoders

    assert type(smtp_to) == list

    msg = MIMEMultipart()
    msg['From'] = smtp_from
    msg['To'] = COMMASPACE.join(smtp_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "etm agenda"

    msg.attach(MIMEText(message, 'html'))

    smtp = smtplib.SMTP_SSL(smtp_server)
    smtp.login(smtp_id, smtp_pw)
    smtp.sendmail(smtp_from, smtp_to, msg.as_string())
    smtp.close()


def send_mail(smtp_to, subject, message, files=None, smtp_from=None, smtp_server=None,
              smtp_id=None, smtp_pw=None):
    """
    """
    if not files:
        files = []
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email.utils import COMMASPACE, formatdate
    from email import encoders as Encoders
    assert type(smtp_to) == list
    assert type(files) == list
    msg = MIMEMultipart()
    msg['From'] = smtp_from
    msg['To'] = COMMASPACE.join(smtp_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(message))
    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        Encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)
    smtp = smtplib.SMTP_SSL(smtp_server)
    smtp.login(smtp_id, smtp_pw)
    smtp.sendmail(smtp_from, smtp_to, msg.as_string())
    smtp.close()


def send_text(sms_phone, subject, message, sms_from, sms_server, sms_pw):
    sms_phone = "%s" % sms_phone
    import smtplib
    from email.mime.text import MIMEText

    sms = smtplib.SMTP(sms_server)
    sms.starttls()
    sms.login(sms_from, sms_pw)
    for num in sms_phone.split(','):
        msg = MIMEText(message)
        msg["From"] = sms_from
        msg["Subject"] = subject
        msg['To'] = num
        sms.sendmail(sms_from, sms_phone, msg.as_string())
    sms.quit()


item_regex = re.compile(r'^([\$\^\*~!%\?#=\+\-])\s')
email_regex = re.compile('([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)')
sign_regex = re.compile(r'(^\s*([+-])?)')
week_regex = re.compile(r'[+-]?(\d+)w', flags=re.I)
estr_regex = re.compile(r'easter\((\d{4,4})\)', flags=re.I)
day_regex = re.compile(r'[+-]?(\d+)d', flags=re.I)
hour_regex = re.compile(r'[+-]?(\d+)h', flags=re.I)
minute_regex = re.compile(r'[+-]?(\d+)m', flags=re.I)
date_calc_regex = re.compile(r'^\s*(.+)\s+([+-])\s+(.+)\s*$')
period_string_regex = re.compile(r'^\s*([+-]?(\d+[wWdDhHmM])+\s*$)')
timezone_regex = re.compile(r'^(.+)\s+([A-Za-z]+/[A-Za-z]+)$')
int_regex = re.compile(r'^\s*([+-]?\d+)\s*$')
leadingzero = re.compile(r'(?<!(:|\d|-))0+(?=\d)')
trailingzeros = re.compile(r'(:00)')
at_regex = re.compile(r'\s+@', re.MULTILINE)
minus_regex = re.compile(r'\s+\-(?=[a-zA-Z])')
amp_regex = re.compile(r'\s+&')
comma_regex = re.compile(r',\s*')
range_regex = re.compile(r'range\((\d+)(\s*,\s*(\d+))?\)')
id_regex = re.compile(r'^\s*@i')
anniversary_regex = re.compile(r'!(\d{4})!')
group_regex = re.compile(r'^\s*(.*)\s+(\d+)/(\d+):\s*(.*)')
groupdate_regex = re.compile(r'\by{2}\b|\by{4}\b|\b[dM]{1,4}\b|\bw\b')
options_regex = re.compile(r'^\s*(!?[fk](\[[:\d]+\])?)|(!?[clostu])\s*$')
# completion_regex = re.compile(r'(?:^.*?)((?:\@[a-zA-Z] ?)?\b\S*)$')
completion_regex = re.compile(r'((?:[@&][a-zA-Z]? ?)?(?:\b[a-zA-Z0-9_/:]+)?)$')

# what about other languages?
# lun mar mer jeu ven sam dim
# we'll use this to reduce abbrevs to 2 letters for weekdays in rrule
threeday_regex = re.compile(r'(MON|TUE|WED|THU|FRI|SAT|SUN)',
                            re.IGNORECASE)

ONEMINUTE = timedelta(minutes=1)
ONEHOUR = timedelta(hours=1)
ONEDAY = timedelta(days=1)
ONEWEEK = timedelta(weeks=1)

rel_date_regex = re.compile(r'(?<![0-9])([-+][0-9]+)')
rel_month_regex = re.compile(r'(?<![0-9])([-+][0-9]+)/([0-9]+)')
blank_lines_regex = re.compile(r'^(\s*$){2,}', re.MULTILINE)

fmt = "%a %Y-%m-%d %H:%M %Z"

rfmt = "%Y-%m-%d %H:%M%z"
efmt = "%H:%M %a %b %d"

sfmt = "%Y%m%dT%H%M"

# finish and due dates
zfmt = "%Y%m%dT%H%M"

sortdatefmt = "%Y%m%d"
reprdatefmt = "%a %b %d, %Y"
shortdatefmt = "%a %b %d %Y"
shortyearlessfmt = "%a %b %d"
weekdayfmt = "%a %d"
sorttimefmt = "%H%M"
etmdatefmt = "%Y-%m-%d"
etmtimefmt = "%H:%M"
rrulefmt = "%a %b %d %Y %H:%M %Z %z"

today = datetime.now(tzlocal()).replace(
    hour=0, minute=0, second=0, microsecond=0)
yesterday = today - ONEDAY
tomorrow = today + ONEDAY

day_begin = time(0, 0)
day_end = time(23, 59)
day_end_minutes = 23 * 60 + 59
actions = ["s", "d", "e", "p", "v"]


def setConfig(options):
    dfile_encoding = options['encoding']['file']
    cal_regex = None
    if 'calendars' in options:
        cal_pattern = r'^%s' % '|'.join(
            [x[2] for x in options['calendars'] if x[1]])
        cal_regex = re.compile(cal_pattern)

    options['user_data'] = {}
    options['completions'] = []
    options['reports'] = []
    completions = set([])
    reports = set([])
    completion_files = []
    report_files = []
    user_files = []

    # get info from files in datadir
    prefix, filelist = getFiles(options['datadir'], include=r'*.cfg')
    for rp in ['completions.cfg', 'users.cfg', 'reports.cfg']:
        fp = os.path.join(options['etmdir'], rp)
        if os.path.isfile(fp):
            filelist.append((fp, rp))
    logger.info('prefix: {0}; files: {1}'.format(prefix, filelist))
    for fp, rp in filelist:
        if os.path.split(rp)[0] and cal_regex and not cal_regex.match(rp):
            continue
        np = relpath(fp, options['etmdir'])
        drive, parts = os_path_splitall(fp)
        n, e = os.path.splitext(parts[-1])
        # skip etmtk and any other .cfg files other than the following
        if n == "completions":
            completion_files.append((np, fp, False))
            with codecs.open(fp, 'r', dfile_encoding) as fo:
                for x in fo.readlines():
                    x = x.rstrip()
                    if x and x[0] != "#":
                        completions.add(x)

        elif n == "reports":
            report_files.append((np, fp, False))
            with codecs.open(fp, 'r', dfile_encoding) as fo:
                for x in fo.readlines():
                    x = x.rstrip()
                    if x and x[0] != "#":
                        reports.add(x)

        elif n == "users":
            user_files.append((np, fp, False))
            fo = codecs.open(fp, 'r', dfile_encoding)
            tmp = yaml.safe_load(fo)
            fo.close()
            try:
                # if a key already exists, use the tmp value
                options['user_data'].update(tmp)
                for x in tmp.keys():
                    completions.add("@u {0}".format(x))
                    completions.add("&u {0}".format(x))
            except:
                logger.exception("Error loading {0}".format(fp))

    # get info from cfg_files
    if 'cfg_files' in options and options['cfg_files']:
        if 'completions' in options['cfg_files'] and options['cfg_files']['completions']:
            for fp in options['cfg_files']['completions']:
                completion_files.append((relpath(fp, options['etmdir']), fp, False))
                with codecs.open(fp, 'r', dfile_encoding) as fo:
                    for x in fo.readlines():
                        x = x.rstrip()
                        if x and x[0] != "#":
                            completions.add(x)
        if 'reports' in options['cfg_files'] and options['cfg_files']['reports']:
            for fp in options['cfg_files']['reports']:
                report_files.append((relpath(fp, options['etmdir']), fp, False))
                with codecs.open(fp, 'r', dfile_encoding) as fo:
                    for x in fo.readlines():
                        x = x.rstrip()
                        if x and x[0] != "#":
                            reports.add(x)
        if 'users' in options['cfg_files'] and options['cfg_files']['users']:
            for fp in options['cfg_files']['users']:
                user_files.append((relpath(fp, options['etmdir']), fp, False))
                fo = codecs.open(fp, 'r', dfile_encoding)
                tmp = yaml.safe_load(fo)
                fo.close()
                # if a key already exists, use this value
                options['user_data'].update(tmp)
                for x in tmp.keys():
                    completions.add("@u {0}".format(x))
                    completions.add("&u {0}".format(x))

    if completions:
        completions = list(completions)
        completions.sort()
        options['completions'] = completions
        options['keywords'] = [x[3:] for x in completions if x.startswith('@k')]
    else:
        logger.info('no completions')
    if reports:
        reports = list(reports)
        reports.sort()
        options['reports'] = reports
    else:
        logger.info('no reports')

    options['completion_files'] = completion_files
    options['report_files'] = report_files
    options['user_files'] = user_files


# noinspection PyGlobalUndefined
term_encoding = None
file_encoding = None
gui_encoding = None
local_timezone = None

NONE = YESTERDAY = TODAY = TOMORROW = ""
trans = lang = None

def get_options(d=''):
    """
    """
    logger.debug('starting get_options with directory: "{0}"'.format(d))
    global parse, lang, trans, s2or3, term_encoding, file_encoding, gui_encoding, local_timezone, NONE, YESTERDAY, TODAY, TOMORROW, BGCOLOR, FGCOLOR, tstr2SCI, CALENDAR_COLORS

    from locale import getpreferredencoding
    from sys import stdout
    try:
        dterm_encoding = stdout.term_encoding
    except AttributeError:
        dterm_encoding = None
    if not dterm_encoding:
        dterm_encoding = getpreferredencoding()

    term_encoding = dterm_encoding = dfile_encoding = codecs.lookup(dterm_encoding).name

    use_locale = ()
    etmdir = ''
    NEWCFG = "etmtk.cfg"
    OLDCFG = "etm.cfg"
    using_oldcfg = False
    if d and os.path.isdir(d):
        etmdir = os.path.abspath(d)
    else:
        homedir = os.path.expanduser("~")
        etmdir = os.path.normpath(os.path.join(homedir, ".etm"))
    newconfig = os.path.normpath(os.path.join(etmdir, NEWCFG))
    oldconfig = os.path.normpath(os.path.join(etmdir, OLDCFG))
    default_datadir = os.path.normpath(os.path.join(etmdir, 'data'))
    logger.debug('checking first for: {0}; then: {1}'.format(newconfig, oldconfig))

    colors_cfg = os.path.normpath(os.path.join(etmdir, 'colors.cfg'))
    # the default colors
    FGCOLOR = BASE_COLORS['foreground']
    HLCOLOR = BASE_COLORS['highlight']
    BGCOLOR = BASE_COLORS['background']
    item_colors = ITEM_COLORS
    if os.path.isfile(colors_cfg):
        logger.info('using colors file: {0}'.format(colors_cfg))
        fo = codecs.open(colors_cfg, 'r', dfile_encoding)
        use_colors = yaml.safe_load(fo)
        fo.close()

        if use_colors:
            FGCOLOR = use_colors['base']['foreground']
            HLCOLOR = use_colors['base']['highlight']
            BGCOLOR = use_colors['base']['background']
            CALENDAR_COLORS = use_colors['calendar']
            item_colors = use_colors['item']
    elif os.path.isdir(etmdir):
        fo = codecs.open(colors_cfg, 'w', dfile_encoding)
        fo.writelines(colors_light)
        fo.close()

    for key in tstr2SCI:
        # update the item colors
        tstr2SCI[key][1] = item_colors[key]

    locale_cfg = os.path.normpath(os.path.join(etmdir, 'locale.cfg'))
    if os.path.isfile(locale_cfg):
        logger.info('using locale file: {0}'.format(locale_cfg))
        fo = codecs.open(locale_cfg, 'r', dfile_encoding)
        use_locale = yaml.safe_load(fo)
        fo.close()
        if use_locale:
            dgui_encoding = use_locale[0][1]
        else:
            use_locale = ()
            tmp = locale.getdefaultlocale()
            dgui_encoding = tmp[1]
    else:
        use_locale = ()
        tmp = locale.getdefaultlocale()
        dgui_encoding = tmp[1]

    if use_locale:
        locale.setlocale(locale.LC_ALL, map(str, use_locale[0]))
        lcl = locale.getlocale()
        lang = use_locale[0][0]
    else:
        lcl = locale.getdefaultlocale()


    NONE = '~ {0} ~'.format(_("none"))
    YESTERDAY = _('Yesterday')
    TODAY = _('Today')
    TOMORROW = _('Tomorrow')

    try:
        dgui_encoding = codecs.lookup(dgui_encoding).name
    except (TypeError, LookupError):
        dgui_encoding = codecs.lookup(locale.getpreferredencoding()).name

    time_zone = get_localtz()[0]

    default_freetimes = {'opening': 8 * 60, 'closing': 17 * 60, 'minimum': 30, 'buffer': 15}

    git_command, git_history, git_commit, git_init = getGit()
    hg_command, hg_history, hg_commit, hg_init = getMercurial()

    default_vcs = ''

    default_options = {
        'action_markups': {'default': 1.0, },
        'action_minutes': 6,
        'action_interval': 1,
        'action_keys': 'k',
        'action_timer': {'running': '', 'paused': ''},
        'action_rates': {'default': 100.0, },
        'action_template': '!hours!h $!value!) !label! (!count!)',

        'agenda_colors': 2,
        'agenda_days': 2,
        'agenda_indent': 3,
        'agenda_width1': 32,
        'agenda_width2': 18,
        'agenda_omit': ['ac', 'fn', 'ns'],

        'alert_default': ['m'],
        'alert_displaycmd': '',
        'alert_soundcmd': '',
        'alert_template': '!time_span!\n!l!\n\n!d!',
        'alert_voicecmd': '',
        'alert_wakecmd': '',

        'ampm': True,
        'completions_width': 36,

        'calendars': [],

        'cfg_files': {'completions': [], 'reports': [], 'users': []},

        'countdown_command': '',
        'countdown_minutes': 10,

        'current_textfile': '',
        'current_htmlfile': '',
        'current_icsfolder': '',
        'current_indent': 3,
        'current_opts': '',
        'current_width1': 48,
        'current_width2': 18,

        'datadir': default_datadir,
        'dayfirst': dayfirst,

        'details_rows': 4,

        'display_idletime': True,

        'early_hour': 6,

        'edit_cmd': '',
        'email_template': "!time_span!\n!l!\n\n!d!",
        'etmdir': etmdir,
        'exportdir': etmdir,
        'encoding': {'file': dfile_encoding, 'gui': dgui_encoding,
                     'term': dterm_encoding},
        'filechange_alert': '',
        'fontsize_fixed': 0,
        'fontsize_tree': 0,
        'freetimes': default_freetimes,
        'icscal_file': os.path.normpath(os.path.join(etmdir, 'etmcal.ics')),
        'icsitem_file': os.path.normpath(os.path.join(etmdir, 'etmitem.ics')),
        'icssync_folder': '',
        'ics_subscriptions': [],

        'local_timezone': time_zone,

        'message_last': 0,
        'message_next': 0,

        # 'monthly': os.path.join('personal', 'monthly'),
        'monthly': os.path.join('personal', 'monthly'),
        'outline_depth': 0,
        'prefix': "\n  ",
        'prefix_uses': 'dfjlmrtz+-',
        'report_begin': '1',
        'report_end': '+1/1',
        'report_colors': 2,
        'report_indent': 3,
        'report_width1': 43,
        'report_width2': 17,

        'show_finished': 1,

        'snooze_command': '',
        'snooze_minutes': 7,

        'smtp_from': '',
        'smtp_id': '',
        'smtp_pw': '',
        'smtp_server': '',

        'sms_from': '',
        'sms_message': '!summary!',
        'sms_phone': '',
        'sms_pw': '',
        'sms_server': '',
        'sms_subject': '!time_span!',

        'style': default_style,

        'sundayfirst': False,
        'update_minutes': 15,
        'vcs_system': default_vcs,
        'vcs_settings': {'command': '', 'commit': '', 'dir': '', 'file': '', 'history': '', 'init': '', 'limit': ''},
        'weeks_after': 52,
        'yearfirst': yearfirst}

    if not os.path.isdir(etmdir):
        # first etm use, no etmdir
        os.makedirs(etmdir)
    logfile = os.path.normpath(os.path.abspath(os.path.join(etmdir, "etmtk_log.txt")))
    if not os.path.isfile(logfile):
        fo = codecs.open(logfile, 'w', dfile_encoding)
        fo.write("")
        fo.close()

    if os.path.isfile(newconfig):
        try:
            logger.info('user options: {0}'.format(newconfig))
            fo = codecs.open(newconfig, 'r', dfile_encoding)
            user_options = yaml.safe_load(fo)
            fo.close()
        except yaml.parser.ParserError:
            logger.exception(
                'Exception loading {0}. Using default options.'.format(newconfig))
            user_options = {}
    elif os.path.isfile(oldconfig):
        try:
            using_oldcfg = True
            logger.info('user options: {0}'.format(oldconfig))
            fo = codecs.open(oldconfig, 'r', dfile_encoding)
            user_options = yaml.safe_load(fo)
            fo.close()
        except yaml.parser.ParserError:
            logger.exception(
                'Exception loading {0}. Using default options.'.format(oldconfig))
            user_options = {}
    else:
        logger.info('using default options')
        user_options = {'datadir': default_datadir}
        fo = codecs.open(newconfig, 'w', dfile_encoding)
        yaml.safe_dump(user_options, fo)
        fo.close()

    options = deepcopy(default_options)
    changed = False
    if user_options:
        if 'agenda_omit' in user_options:
            tmp = [x for x in user_options['agenda_omit'] if x in ['ac', 'by', 'fn', 'ns', 'oc']]
            if tmp != user_options['agenda_omit']:
                user_options['agenda_omit'] = tmp
                changed = True
        if ('actions_timercmd' in user_options and
                user_options['actions_timercmd']):
            user_options['action_timer']['running'] = \
                user_options['actions_timercmd']
            del user_options['actions_timercmd']
            changed = True
        options.update(user_options)
    else:
        user_options = {}
    # logger.debug("user_options: {0}".format(user_options))

    for key in default_options:
        if key in ['action_keys', 'show_finished', 'fontsize_busy', 'fontsize_fixed', 'fontsize_tree', 'outline_depth', 'prefix', 'prefix_uses', 'icssyc_folder', 'ics_subscriptions', 'agenda_days', 'message_next', 'message_last', 'agenda_omit']:
            if key not in user_options:
                # we want to allow 0 as an entry
                options[key] = default_options[key]
                changed = True
        elif key in ['ampm', 'dayfirst', 'yearfirst', 'retain_ids', 'display_idletime']:
            if key not in user_options:
                # we want to allow False as an entry
                options[key] = default_options[key]
                changed = True

        elif default_options[key] and (key not in user_options or not user_options[key]):
            options[key] = default_options[key]
            changed = True

    if type(options['update_minutes']) is not int or options['update_minutes'] <= 0 or options['update_minutes'] > 59:
        options['update_minutes'] = default_options['update_minutes']

    remove_keys = []
    for key in options:
        if key not in default_options:
            remove_keys.append(key)
            changed = True
    for key in remove_keys:
        del options[key]

    action_keys = [x for x in options['action_keys']]
    if action_keys:
        for at_key in action_keys:
            if at_key not in key2type or "~" not in key2type[at_key]:
                action_keys.remove(at_key)
                changed = True
        if changed:
            options['action_keys'] = "".join(action_keys)

    # check freetimes
    for key in default_freetimes:
        if key not in options['freetimes']:
            options['freetimes'][key] = default_freetimes[key]
            logger.warn('A value was not provided for freetimes[{0}] - using the default value.'.format(key))
            changed = True
        else:
            if type(options['freetimes'][key]) is not int:
                changed = True
                try:
                    options['freetimes'][key] = int(eval(options['freetimes'][key]))
                except:
                    logger.warn('The value provided for freetimes[{0}], "{1}", could not be converted to an integer - using the default value instead.'.format(key, options['freetimes'][key]))
                    options['freetimes'][key] = default_freetimes[key]

    free_keys = [x for x in options['freetimes'].keys()]
    for key in free_keys:
        if key not in default_freetimes:
            del options['freetimes'][key]
            logger.warn('A value was provided for freetimes[{0}], but this is an invalid option and has been deleted.'.format(key))
            changed = True

    if not os.path.isdir(options['datadir']):
        """
        <datadir>
            personal/
                monthly/
            sample/
                completions.cfg
                reports.cfg
                sample.txt
                users.cfg
            shared/
                holidays.txt

        etmtk.cfg
            calendars:
            - - personal
              - true
              - personal
            - - sample
              - true
              - sample
            - - shared
              - true
              - shared
        """
        changed = True
        term_print('creating datadir: {0}'.format(options['datadir']))
        # first use of this datadir - first use of new etm?
        os.makedirs(options['datadir'])
        # create one task for new users to join the etm discussion group
        currfile = ensureMonthly(options)
        with open(currfile, 'w') as fo:
            fo.write(JOIN)
        sample = os.path.normpath(os.path.join(options['datadir'], 'sample'))
        os.makedirs(sample)
        with codecs.open(os.path.join(sample, 'sample.txt'), 'w', dfile_encoding) as fo:
            fo.write(SAMPLE)
        holidays = os.path.normpath(os.path.join(options['datadir'], 'shared'))
        os.makedirs(holidays)
        with codecs.open(os.path.join(holidays, 'holidays.txt'), 'w', dfile_encoding) as fo:
            fo.write(HOLIDAYS)
        with codecs.open(os.path.join(options['datadir'], 'sample', 'completions.cfg'), 'w', dfile_encoding) as fo:
            fo.write(COMPETIONS)
        with codecs.open(os.path.join(options['datadir'], 'sample', 'reports.cfg'), 'w', dfile_encoding) as fo:
            fo.write(REPORTS)
        with codecs.open(os.path.join(options['datadir'], 'sample', 'users.cfg'), 'w', dfile_encoding) as fo:
            fo.write(USERS)
        if not options['calendars']:
            options['calendars'] = [['personal', True, 'personal'], ['sample', True, 'sample'], ['shared', True, 'shared']]
    logger.info('using datadir: {0}'.format(options['datadir']))
    logger.debug('changed: {0}; user: {1}; options: {2}'.format(changed, (user_options != default_options), (options != default_options)))
    if changed or using_oldcfg:
        # save options to newconfig even if user options came from oldconfig
        logger.debug('Writing etmtk.cfg changes to {0}'.format(newconfig))
        fo = codecs.open(newconfig, 'w', options['encoding']['file'])
        yaml.safe_dump(options, fo, default_flow_style=False)
        fo.close()

    # add derived options
    if options['vcs_system'] == 'git':
        if git_command:
            options['vcs'] = {'command': git_command, 'history': git_history, 'commit': git_commit, 'init': git_init, 'dir': '.git', 'limit': '-n', 'file': ""}
            repo = os.path.normpath(os.path.join(options['datadir'], options['vcs']['dir']))
            work = options['datadir']
            # logger.debug('{0} options: {1}'.format(options['vcs_system'], options['vcs']))
        else:
            logger.warn('could not setup "git" vcs')
            options['vcs'] = {}
            options['vcs_system'] = ''
    elif options['vcs_system'] == 'mercurial':
        if hg_command:
            options['vcs'] = {'command': hg_command, 'history': hg_history, 'commit': hg_commit, 'init': hg_init, 'dir': '.hg', 'limit': '-l', 'file': ''}
            repo = os.path.normpath(os.path.join(options['datadir'], options['vcs']['dir']))
            work = options['datadir']
            # logger.debug('{0} options: {1}'.format(options['vcs_system'], options['vcs']))
        else:
            logger.warn('could not setup "mercurial" vcs')
            options['vcs'] = {}
            options['vcs_system'] = ''
    else:
        options['vcs_system'] = ''
        options['vcs'] = {}

    # overrule the defaults if any custom settings are given
    if options['vcs_system']:
        if options['vcs_settings']:
            # update any settings with custom modifications
            for key in options['vcs_settings']:
                if options['vcs_settings'][key]:
                    options['vcs'][key] = options['vcs_settings'][key]
        # add the derived options
        options['vcs']['repo'] = repo
        options['vcs']['work'] = work

    if options['vcs']:
        vcs_lst = []
        keys = [x for x in options['vcs'].keys()]
        keys.sort()
        for key in keys:
            vcs_lst.append("{0}: {1}".format(key, options['vcs'][key]))
        vcs_str = "\n      ".join(vcs_lst)
    else:
        vcs_str = ""
    logger.info('using vcs {0}; options:\n      {1}'.format(options['vcs_system'], vcs_str))

    (options['daybegin_fmt'], options['dayend_fmt'], options['reprtimefmt'], options['longreprtimefmt'], options['reprdatetimefmt'], options['etmdatetimefmt'],
     options['rfmt'], options['efmt']) = get_fmts(options)
    options['config'] = newconfig
    options['scratchpad'] = os.path.normpath(os.path.join(options['etmdir'], _("scratchpad")))
    options['colors'] = os.path.normpath(os.path.join(options['etmdir'], "colors.cfg"))

    if options['action_minutes'] not in [1, 6, 12, 15, 30, 60]:
        term_print(
            "Invalid action_minutes setting: %s. Reset to 1." %
            options['action_minutes'])
        options['action_minutes'] = 1

    setConfig(options)

    z = gettz(options['local_timezone'])
    if z is None:
        term_print(
            "Error: bad entry for local_timezone in etmtk.cfg: '%s'" %
            options['local_timezone'])
        options['local_timezone'] = ''

    if 'vcs_system' in options and options['vcs_system']:
        logger.debug('vcs_system: {0}'.format(options['vcs_system']))
        f = ''
        if options['vcs_system'] == 'mercurial':
            f = os.path.normpath(os.path.join(options['datadir'], '.hgignore'))
        elif options['vcs_system'] == 'git':
            f = os.path.normpath(os.path.join(options['datadir'], '.gitignore'))
        if f and not os.path.isfile(f):
            fo = open(f, 'w')
            fo.write(IGNORE)
            fo.close()
            logger.info('created: {0}'.format(f))
        logger.debug('checking for {0}'.format(options['vcs']['repo']))
        if not os.path.isdir(options['vcs']['repo']):
            init = options['vcs']['init']
            # work = (options['vcs']['work'])
            command = init.format(work=options['vcs']['work'], repo=options['vcs']['repo'], mesg="initial commit")
            logger.debug('initializing vcs: {0}'.format(command))
            # run_cmd(command)
            subprocess.call(command, shell=True)

    if options['current_icsfolder']:
        if not os.path.isdir(options['current_icsfolder']):
            os.makedirs(options['current_icsfolder'])

    options['lcl'] = lcl
    logger.info('using lcl: {0}'.format(lcl))

    options['hide_finished'] = False
    # define parse using dayfirst and yearfirst
    setup_parse(options['dayfirst'], options['yearfirst'])
    term_encoding = options['encoding']['term']
    file_encoding = options['encoding']['file']
    gui_encoding = options['encoding']['gui']
    local_timezone = options['local_timezone']
    options['background_color'] = BGCOLOR
    options['highlight_color'] = HLCOLOR
    options['foreground_color'] = FGCOLOR
    options['calendar_colors'] = CALENDAR_COLORS

    # set 'bef' here and update on newday using a naive datetime
    now = datetime.now()
    year, wn, dn = now.isocalendar()
    weeks_after = options['weeks_after']
    if dn > 1:
        days = dn - 1
    else:
        days = 0
    week_beg = now - days * ONEDAY
    bef = (week_beg + (7 * (weeks_after + 1)) * ONEDAY)
    options['bef'] = bef

    logger.debug("ending get_options")
    return user_options, options, use_locale


def get_fmts(options):
    global rfmt, efmt
    df = "%x"
    ef = "%a %b %d"
    if 'ampm' in options and options['ampm']:
        reprtimefmt = "%I:%M%p"
        longreprtimefmt = "%I:%M:%S%p"
        daybegin_fmt = "12am"
        dayend_fmt = "11:59pm"
        rfmt = "{0} %I:%M%p %z".format(df)
        efmt = "%I:%M%p {0}".format(ef)

    else:
        reprtimefmt = "%H:%M"
        longreprtimefmt = "%H:%M:%S"
        daybegin_fmt = "0:00"
        dayend_fmt = "23:59"
        rfmt = "{0} %H:%M%z".format(df)
        efmt = "%H:%M {0}".format(ef)

    reprdatetimefmt = "%s %s %%Z" % (reprdatefmt, reprtimefmt)
    etmdatetimefmt = "%s %s" % (etmdatefmt, reprtimefmt)
    return (daybegin_fmt, dayend_fmt, reprtimefmt, longreprtimefmt, reprdatetimefmt, etmdatetimefmt, rfmt, efmt)


def checkForNewerVersion():
    global python_version2
    import socket

    timeout = 10
    socket.setdefaulttimeout(timeout)
    if platform.python_version() >= '3':
        python_version2 = False
        from urllib.request import urlopen
        from urllib.error import URLError
        # from urllib.parse import urlencode
    else:
        python_version2 = True
        from urllib2 import urlopen, URLError

    url = "http://people.duke.edu/~dgraham/etmtk/version.txt"
    try:
        response = urlopen(url)
    except URLError as e:
        if hasattr(e, 'reason'):
            msg = """\
The latest version could not be determined.
Reason: %s.""" % e.reason
        elif hasattr(e, 'code'):
            msg = """\
The server couldn\'t fulfill the request.
Error code: %s.""" % e.code
        return 0, msg
    else:
        # everything is fine
        if python_version2:
            res = response.read()
            vstr = rsplit('\s+', res)[0]
        else:
            res = response.read().decode(term_encoding)
            vstr = rsplit('\s+', res)[0]

        if version < vstr:
            return (1, """\
A newer version of etm, %s, is available at \
people.duke.edu/~dgraham/etmtk.""" % vstr)
        else:
            return 1, 'You are using the latest version.'


type_keys = [x for x in '=^*-+%~$?!#']

type2Str = {
    '$': "ib",
    '^': "oc",
    '*': "ev",
    '~': "ac",
    '!': "nu",  # undated only appear in folders
    '-': "un",  # for next view
    '+': "un",  # for next view
    '%': "du",
    '?': "so",
    '#': "dl"}

id2Type = {
    #   TStr  TNum Forground Color   Icon         view
    "ac": '~',
    "av": '-',
    "by": '>',
    "cs": '+',  # job
    "cu": '+',  # job with unfinished prereqs
    "dl": '#',
    "ds": '%',
    "du": '%',
    "ev": '*',
    "fn": u"\u2713",
    "ib": '$',
    "ns": '!',
    "nu": '!',
    "oc": '^',
    "pc": '+',  # job pastdue
    "pu": '+',  # job pastdue with unfinished prereqs
    "pd": '%',
    "pt": '-',
    "rm": '*',
    "so": '?',
    "un": '-',
}

# the named colors are listed in colors.py.

# the contents of colors_light.cfg:
colors_light = """\
base:
  foreground: 'black'           # default font color
  highlight: '#B2B2AF'          # default highlight color
  background: '#FEFEFC'         # default background color

item:                           # font colors for items in tree views
  ac: 'darkorchid'              # action
  av: 'RoyalBlue3'              # scheduled, available task
  by: 'DarkGoldenRod3'          # begin by
  cs: 'RoyalBlue3'              # scheduled job
  cu: 'gray65'                  # scheduled job with unfinished prereqs
  dl: 'gray70'                  # hidden (folder view)
  ds: 'darkslategray'           # scheduled, delegated task
  du: 'darkslategray'           # unscheduled, delegated task
  ev: 'springgreen4'            # event
  fn: 'gray70'                  # finished task
  ib: 'coral2'                  # inbox
  ns: 'saddlebrown'             # note
  nu: 'saddlebrown'             # unscheduled noted
  oc: 'peachpuff4'              # occasion
  pc: 'firebrick1'              # pastdue job
  pu: 'firebrick1'              # pastdue job with unfinished prereqs
  pd: 'firebrick1'              # pastdue, delegated task
  pt: 'firebrick1'              # pastdue task
  rm: 'seagreen'                # reminder
  so: 'SteelBlue3'              # someday
  un: 'RoyalBlue3'              # unscheduled task (next)

calendar:
  date: 'RoyalBlue3'            # week/month calendar dates
  grid: 'gray85'                # week/month calendar grid lines
  busybar: 'RoyalBlue3'         # week/month busy bars
  current: '#DCEAFC'            # current date calendar background
  active: '#FCFCD9'             # active/selected date background
  occasion: 'gray92'            # occasion background
  conflict: '#FF3300'           # conflict flag
  year_past: 'springgreen4'     # calendar, past years font color
  year_current: 'black'         # calendar, current year font color
  year_future: 'RoyalBlue3'     # calendar, future years font color
"""
# The contents of colors_light should duplicate the default
# colors below.

# default colors
BASE_COLORS = {
    'foreground': "black",
    'highlight': "#B2B2AF",
    'background': "#FEFEFC"
}

ITEM_COLORS = {
    "ac": "darkorchid",
    "av": "RoyalBlue3",
    "by": "DarkGoldenRod3",
    "cs": "RoyalBlue3",
    "cu": "gray65",
    "dl": "gray70",
    "ds": "darkslategray",
    "du": "darkslategray",
    "ev": "springgreen4",
    "fn": "gray70",
    "ib": "coral2",
    "ns": "saddlebrown",
    "nu": "saddlebrown",
    "oc": "peachpuff4",
    "pc": "firebrick1",
    "pu": "firebrick1",
    "pd": "firebrick1",
    "pt": "firebrick1",
    "rm": "seagreen",
    "so": "SteelBlue3",
    "un": "RoyalBlue3",
}

CALENDAR_COLORS = {
    "date": "RoyalBlue3",
    "grid": "gray85",
    "busybar": "RoyalBlue3",
    "current": "#DCEAFC",
    "active": "#FCFCD9",
    "occasion": "gray92",
    "conflict": "#FF3300",
    "year_past": "springgreen4",
    "year_current": 'black',
    "year_future": 'RoyalBlue3',
}

# type string to Sort Color Icon. The color will be added in
# get_options either from colors.cfg or from the above defaults
tstr2SCI = {
    #   TStr  TNum Forground Color   Icon         view
    "ac": [23, "", "action", "day"],
    "av": [16, "", "task", "day"],
    "by": [19, "", "beginby", "now"],
    "cs": [18, "", "child", "day"],
    "cu": [22, "", "child", "day"],
    "dl": [28, "", "delete", "folder"],
    "ds": [17, "", "delegated", "day"],
    "du": [21, "", "delegated", "day"],
    "ev": [12, "", "event", "day"],
    "fn": [27, "", "finished", "day"],
    "ib": [10, "", "inbox", "now"],
    "ns": [24, "", "note", "day"],
    "nu": [25, "", "note", "day"],
    "oc": [11, "", "occasion", "day"],
    "pc": [15, "", "child", "now"],
    "pu": [15, "", "child", "now"],
    "pd": [14, "", "delegated", "now"],
    "pt": [13, "", "task", "now"],
    "rm": [12, "", "reminder", "day"],
    "so": [26, "", "someday", "now"],
    "un": [20, "", "task", "next"],
}

def fmt_period(td, parent=None, short=False):
    if type(td) is not timedelta:
        return td
    if td < ONEMINUTE * 0:
        return '0m'
    if td == ONEMINUTE * 0:
        return '0m'
    until = []
    td_days = td.days
    td_hours = td.seconds // (60 * 60)
    td_minutes = (td.seconds % (60 * 60)) // 60

    if short:
        if td_days > 1:
            if td_minutes > 30:
                td_hours += 1
            td_minutes = 0
        if td_days > 7:
            if td_hours > 12:
                td_days += 1
            td_hours = 0

    if td_days:
        until.append("%dd" % td_days)
    if td_hours:
        until.append("%dh" % td_hours)
    if td_minutes:
        until.append("%dm" % td_minutes)
    if not until:
        until = "0m"
    return "".join(until)


def fmt_time(dt, omitMidnight=False, seconds=False, options=None):
    # fmt time, omit leading zeros and, if ampm, convert to lowercase
    # and omit trailing m's
    if not options:
        options = {}
    if omitMidnight and dt.hour == 0 and dt.minute == 0:
        return u''
    # logger.debug('dt before fmt: {0}'.format(dt))
    if seconds:
        dt_fmt = dt.strftime(options['longreprtimefmt'])
    else:
        dt_fmt = dt.strftime(options['reprtimefmt'])
    # logger.debug('dt dt_fmt: {0}'.format(dt_fmt))
    if dt_fmt[0] == "0":
        dt_fmt = dt_fmt[1:]
    # The 3rd test is for Poland where am, pm = ''
    if 'ampm' in options and options['ampm'] and not dt_fmt[-1].isdigit():
        # dt_fmt = dt_fmt.lower()[:-1]
        dt_fmt = dt_fmt.lower()
        dt_fmt = leadingzero.sub('', dt_fmt)
        dt_fmt = trailingzeros.sub('', dt_fmt)
    return s2or3(dt_fmt)


def fmt_date(dt, short=False):
    if type(dt) in [str, unicode]:
        return unicode(dt)
    if short:
        tdy = datetime.today()
        if type(dt) == datetime:
            dt = dt.date()
        if dt == tdy.date():
            if python_version2:
                dt_fmt = u"{0} ({1})".format(unicode(dt.strftime(shortyearlessfmt), gui_encoding, 'ignore'), TODAY)
            else:
                dt_fmt = "{0} ({1})".format(dt.strftime(shortyearlessfmt), TODAY)
        elif dt == tdy.date() - ONEDAY:
            if python_version2:
                dt_fmt = u"{0} ({1})".format(unicode(dt.strftime(shortyearlessfmt), gui_encoding, 'ignore'), YESTERDAY)
            else:
                dt_fmt = "{0} ({1})".format(dt.strftime(shortyearlessfmt), YESTERDAY)
        elif dt == tdy.date() + ONEDAY:
            if python_version2:
                dt_fmt = u"{0} ({1})".format(unicode(dt.strftime(shortyearlessfmt), gui_encoding, 'ignore'), TOMORROW)
            else:
                dt_fmt = "{0} ({1})".format(dt.strftime(shortyearlessfmt), TOMORROW)
        elif dt.year == tdy.year:
            dt_fmt = dt.strftime(shortyearlessfmt)
        else:
            dt_fmt = dt.strftime(shortdatefmt)
    else:
        if python_version2:
            dt_fmt = unicode(dt.strftime(reprdatefmt), term_encoding)
        else:
            dt_fmt = dt.strftime(reprdatefmt)
    dt_fmt = leadingzero.sub('', s2or3(dt_fmt))
    return dt_fmt


def fmt_shortdatetime(dt, options=None):
    if not options:
        options = {}
    if type(dt) in [str, unicode]:
        return unicode(dt)
    tdy = datetime.today()
    if dt.date() == tdy.date():
        dt_fmt = "%s %s" % (fmt_time(dt, options=options), TODAY)
    elif dt.date() == tdy.date() - ONEDAY:
        dt_fmt = "%s %s" % (fmt_time(dt, options=options), YESTERDAY)
    elif dt.date() == tdy.date() + ONEDAY:
        dt_fmt = "%s %s" % (fmt_time(dt, options=options), TOMORROW)
    elif dt.year == tdy.year:
        try:
            x1 = unicode(fmt_time(dt, options=options))
            x2 = unicode(dt.strftime(shortyearlessfmt))
            dt_fmt = "%s %s" % (x1, x2)
        except:
            dt_fmt = dt.strftime("%X %x")
    else:
        try:
            dt_fmt = dt.strftime(shortdatefmt)
            dt_fmt = leadingzero.sub('', dt_fmt)
        except:
            dt_fmt = dt.strftime("%X %x")
    return s2or3(dt_fmt)


def fmt_datetime(dt, options=None):
    if not options:
        options = {}
    t_fmt = fmt_time(dt, options=options)
    dt_fmt = "%s %s" % (dt.strftime(etmdatefmt), t_fmt)
    return s2or3(dt_fmt)


def fmt_weekday(dt):
    return fmt_dt(dt, weekdayfmt)


def fmt_dt(dt, f):
    dt_fmt = dt.strftime(f)
    return s2or3(dt_fmt)


rrule_hsh = {
    'f': 'FREQUENCY',  # unicode
    'i': 'INTERVAL',  # positive integer
    't': 'COUNT',  # total count positive integer
    's': 'BYSETPOS',  # integer
    'u': 'UNTIL',  # unicode
    'M': 'BYMONTH',  # integer 1...12
    'm': 'BYMONTHDAY',  # positive integer
    'W': 'BYWEEKNO',  # positive integer
    'w': 'BYWEEKDAY',  # integer 0 (SU) ... 6 (SA)
    'h': 'BYHOUR',  # positive integer
    'n': 'BYMINUTE',  # positive integer
    'E': 'BYEASTER',  # non-negative integer number of days after easter
}

# for icalendar export we need BYDAY instead of BYWEEKDAY
ical_hsh = deepcopy(rrule_hsh)
ical_hsh['w'] = 'BYDAY'
ical_hsh['f'] = 'FREQ'

ical_rrule_hsh = {
    'FREQ': 'r',  # unicode
    'INTERVAL': 'i',  # positive integer
    'COUNT': 't',  # total count positive integer
    'BYSETPOS': 's',  # integer
    'UNTIL': 'u',  # unicode
    'BYMONTH': 'M',  # integer 1...12
    'BYMONTHDAY': 'm',  # positive integer
    'BYWEEKNO': 'W',  # positive integer
    'BYDAY': 'w',  # integer 0 (SU) ... 6 (SA)
    # 'BYWEEKDAY': 'w',  # integer 0 (SU) ... 6 (SA)
    'BYHOUR': 'h',  # positive integer
    'BYMINUTE': 'n',  # positive integer
    'BYEASTER': 'E',  # non negative integer number of days after easter
}

# don't add f and u - they require special processing in get_rrulestr
rrule_keys = ['i', 'm', 'M', 'w', 'W', 'h', 'n', 't', 's', 'E']
ical_rrule_keys = ['f', 'i', 'm', 'M', 'w', 'W', 'h', 'n', 't', 's', 'u']

# ^ Presidential election day @s 2004-11-01 12am
#   @r y &i 4 &m 2, 3, 4, 5, 6, 7, 8 &M 11 &w TU

# don't add l (list) - handeled separately
freq_hsh = {
    'y': 'YEARLY',
    'm': 'MONTHLY',
    'w': 'WEEKLY',
    'd': 'DAILY',
    'h': 'HOURLY',
    'n': 'MINUTELY',
    'E': 'EASTERLY',
}

ical_freq_hsh = {
    'YEARLY': 'y',
    'MONTHLY': 'm',
    'WEEKLY': 'w',
    'DAILY': 'd',
    'HOURLY': 'h',
    'MINUTELY': 'n',
    # 'EASTERLY': 'e'
}

amp_hsh = {
    'r': 'f',    # the starting value for an @r entry is frequency
    'a': 't'     # the starting value for an @a entry is *triggers*
}

at_keys = [
    's',  # start datetime
    'e',  # extent time spent
    'x',  # expense money spent
    'a',  # alert
    'b',  # begin
    'c',  # context
    'k',  # keyword
    't',  # tags
    'l',  # location
    'n',  # noshow, tasks only. list of views in a, d, k, t.
    'u',  # user
    'f',  # finish date
    'h',  # history (task group)
    'i',  # invitees
    'g',  # goto
    'j',  # job
    'p',  # priority
    'q',  # queue
    'r',  # repetition rule
    '+',  # include
    '-',  # exclude
    'o',  # overdue
    'd',  # description
    'm',  # memo
    'z',  # time zone
    'I',  # id',
    'v',  # action rate key
    'w',  # expense markup key
]

all_keys = at_keys + ['entry', 'fileinfo', 'itemtype', 'rrule', '_summary', '_group_summary', '_a', '_j', '_p', '_r', 'prereqs']

all_types = [u'=', u'^', u'*', u'-', u'+', u'%', u'~', u'$',  u'?', u'!',  u'#']
# job_types = [u'-', u'+', u'%', u'$', u'?', u'#']
job_types = [u'-', u'+', u'%']
any_types = [u'=', u'$', u'?', u'#']

# @key to item types - used to check for valid key usage
key2type = {
    u'+': all_types,
    u'-': all_types,
    u'a': all_types,
    u'b': all_types,
    u'c': all_types,
    u'd': all_types,
    u'e': all_types,
    u'f': job_types + any_types,
    u'g': all_types + any_types,
    u'h': [u'+'] + any_types,
    u'i': [u'*', u'^'] + any_types,
    u'I': all_types,
    u'j': [u'+'] + any_types,
    u'k': all_types,
    u'l': all_types,
    u'm': all_types,
    u'o': job_types + any_types,
    u'n': [u'-', u'%', u'*'] + any_types,
    # u'n': [u'-', u'%'] + any_types,
    u'p': job_types + any_types,
    u'q': all_types,
    u'r': all_types,
    u's': all_types,
    u't': all_types,
    u'u': all_types,
    u'v': [u'~'] + any_types,
    u'w': [u'~'] + any_types,
    u'x': [u'~'] + any_types,
    u'z': all_types,
}

label_keys = [
    # 'f',  # finish date
    '_a',  # alert
    'b',  # begin
    'c',  # context
    'd',  # description
    'g',  # goto
    'i',  # invitees
    'k',  # keyword
    'l',  # location
    'm',  # memo
    'p',  # priority
    '_r',  # repetition rule
    't',  # tags
    'u',  # user
]

amp_keys = {
    'r': [
        u'f',   # r frequency
        u'i',   # r interval
        u'm',   # r monthday
        u'M',   # r month
        u'w',   # r weekday
        u'W',   # r week
        u'h',   # r hour
        u'n',   # r minute
        u'E',   # r easter
        u't',   # r total (dateutil COUNT) (c is context in j)
        u'u',   # r until
        u's'],  # r set position
    'j': [
        u'j',   # j job summary
        u'b',   # j beginby
        u'c',   # j context
        u'd',   # j description
        u'e',   # e extent
        u'f',   # j finish
        u'h',   # h history (task group jobs)
        u'p',   # j priority
        u'u',   # user
        u'q'],  # j queue position
}


@memoize
def makeTree(tree_rows, view=None, calendars=None, sort=True, fltr=None, hide_finished=False):
    """
    e.g. row:
    [('now', (1, 13), datetime.datetime(2015, 8, 20, 0, 0), 10, 'Call Saul', 'personal/dag/monthly/2015/08.txt'),
      'Now',
      'Available',
      ('e2d85baae43140d5966f63ccabe455dcetm', 'pt', 'Call Saul', '-38d', datetime.datetime(2015, 8, 20, 0, 0))]
    """
    tree = {}
    lofl = []
    root = '_'
    empty = True
    cal_regex = None
    if calendars:
        cal_pattern = r'^%s' % '|'.join([x[2] for x in calendars if x[1]])
        cal_regex = re.compile(cal_pattern)
    if fltr is not None:
        mtch = True
        if fltr[0] == '!':
            mtch = False
            fltr = fltr[1:]
        filter_regex = re.compile(r'{0}'.format(fltr), re.IGNORECASE)
        logger.debug('filter: {0} ({1})'.format(fltr, mtch))
    else:
        filter_regex = None
    root_key = tuple(["", root])
    tree.setdefault(root_key, [])
    for pc in tree_rows:
        if hide_finished and pc[-1][1] == 'fn':
            continue
        if cal_regex and not cal_regex.match(pc[0][-1]):
            continue
        if view and pc[0][0] != view:
            continue
        if filter_regex is not None:
            s = "{0} {1}".format(pc[-1][2], " ".join(pc[1:-1]))
            # logger.debug('looking in "{0}"'.format(s))
            m = filter_regex.search(s)
            if not ((mtch and m) or (not mtch and not m)):
                continue
        if sort:
            pc.pop(0)
        empty = False
        key = tuple([root, pc[0]])
        if key not in tree[root_key]:
            tree[root_key].append(key)
        # logger.debug('key: {0}'.format(key))
        lofl.append(pc)
        for i in range(len(pc) - 1):
            if pc[:i]:
                parent_key = tuple([":".join(pc[:i]), pc[i]])
            else:
                parent_key = tuple([root, pc[i]])
            child_key = tuple([":".join(pc[:i + 1]), pc[i + 1]])
            # logger.debug('parent: {0}; child: {1}'.format(parent_key, child_key))
            if pc[:i + 1] not in lofl:
                lofl.append(pc[:i + 1])
            tree.setdefault(parent_key, [])
            if child_key not in tree[parent_key]:
                tree[parent_key].append(child_key)
    if empty:
        return {}
    return tree


def truncate(s, l):
    if l > 0 and len(s) > l:
        if re.search(' ~ ', s):
            s = s.split(' ~ ')[0]
        s = "%s.." % s[:l - 2]
    return s


def tree2Html(tree, indent=2, width1=54, width2=20, colors=2):
    global html_lst
    html_lst = []
    if colors:
        e_c = "</font>"
    else:
        e_c = ""
    tab = " " * indent

    def t2H(tree_hsh, node=('', '_'), level=0):
        if type(node) == tuple:
            if type(node[1]) == tuple:
                t = id2Type[node[1][1]]
                col2 = "{0:^{width}}".format(
                    truncate(node[1][3], width2), width=width2)
                if colors == 2:
                    s_c = '<font color="%s">' % tstr2SCI[node[1][1]][1]
                elif colors == 1:
                    if node[1][1][0] == 'p':
                        # past due
                        s_c = '<font color="%s">' % tstr2SCI[node[1][1]][1]
                    else:
                        s_c = '<font color="black">'
                else:
                    s_c = ''
                if width1 > 0:
                    rmlft = width1 - indent * level
                else:
                    rmlft = 0
                s = "%s%s%s %-*s %s%s" % (tab * level, s_c, unicode(t),
                                          rmlft, unicode(truncate(node[1][2], rmlft)),
                                          col2, e_c)
                html_lst.append(s)
            else:
                html_lst.append("%s%s" % (tab * level, node[1]))
        else:
            html_lst.append("%s%s" % (tab * level, node))
        if node not in tree_hsh:
            return ()
        level += 1
        nodes = tree_hsh[node]
        for n in nodes:
            t2H(tree_hsh, n, level)
    t2H(tree)
    return [x[indent:] for x in html_lst]


def tree2Rst(tree, indent=2, width1=54, width2=14, colors=0,
             number=False, count=0, count2id=None):
    global text_lst
    args = [count, count2id]
    text_lst = []
    if colors:
        e_c = ""
    else:
        e_c = ""
    tab = "   " * indent

    def t2H(tree_hsh, node=('', '_'), level=0):
        if args[1] is None:
            args[1] = {}
        if type(node) == tuple:
            if type(node[1]) == tuple:
                args[0] += 1
                # join the uuid and the datetime of the instance
                args[1][args[0]] = "{0}::{1}".format(node[-1][0], node[-1][-1])
                t = id2Type[node[1][1]]
                s_c = ''
                col2 = "{0:^{width}}".format(
                    truncate(node[1][3], width2), width=width2)
                if number:
                    rmlft = width1 - indent * level - 2 - len(str(args[0]))
                    s = "%s\%s%s [%s] %-*s %s%s" % (
                        tab * (level - 1), s_c, unicode(t),
                        args[0], rmlft,
                        unicode(truncate(node[1][2], rmlft)),
                        col2, e_c)
                else:
                    rmlft = width1 - indent * level
                    s = "%s\%s%s %-*s %s%s" % (tab * (level - 1), s_c, unicode(t),
                                               rmlft,
                                               unicode(truncate(node[1][2], rmlft)),
                                               col2, e_c)
                text_lst.append(s)
            else:
                if node[1].strip() != '_':
                    text_lst.append("%s[b]%s[/b]" % (tab * (level - 1), node[1]))
        else:
            text_lst.append("%s%s" % (tab * (level - 1), node))
        if node not in tree_hsh:
            return ()
        level += 1
        nodes = tree_hsh[node]
        for n in nodes:
            t2H(tree_hsh, n, level)

    t2H(tree)
    return [x for x in text_lst], args[0], args[1]


def tree2Text(tree, indent=4, width1=43, width2=20, colors=0,
              number=False, count=0, count2id=None, depth=0):
    global text_lst
    logger.debug("data.tree2Text: width1={0}, width2={1}, colors={2}".format(width1, width2, colors))
    args = [count, count2id]
    text_lst = []
    if colors:
        e_c = ""
    else:
        e_c = ""
    tab = " " * indent

    def t2H(tree_hsh, node=('', '_'), level=0):
        if depth and level > depth:
            return
        if args[1] is None:
            args[1] = {}
        if type(node) == tuple:
            if type(node[1]) == tuple:
                args[0] += 1
                # join the uuid and the datetime of the instance
                args[1][args[0]] = "{0}::{1}".format(node[-1][0], node[-1][-1])
                t = id2Type[node[1][1]]
                s_c = ''
                # logger.debug("node13: {0}; width2: {1}".format(node[1][3],  width2))
                if node[1][3]:
                    col2 = "{0:^{width}}".format(
                        truncate(node[1][3], width2), width=width2)
                else:
                    col2 = ""
                if number:
                    if width1 > 0:
                        rmlft = width1 - indent * level - 2 - len(str(args[0]))
                    else:
                        rmlft = 0
                    s = u"{0:s}{1:s}{2:s} [{3:s}] {4:<*s} {5:s}{6:s}".format(
                        tab * level,
                        s_c,
                        unicode(t),
                        args[0],
                        rmlft,
                        unicode(truncate(node[1][2], rmlft)),
                        col2, e_c)
                else:
                    if width1 > 0:
                        rmlft = width1 - indent * level
                    else:
                        rmlft = 0
                    s = "%s%s%s %-*s %s%s" % (tab * level, s_c, unicode(t), rmlft, unicode(truncate(node[1][2], rmlft)), col2, e_c)
                text_lst.append(s)
            else:
                aug = "%s%s" % (tab * level, node[1])
                text_lst.append(aug.split('!!')[0])
        else:
            text_lst.append("%s%s" % (tab * level, node))
        if node not in tree_hsh:
            return ()
        level += 1
        nodes = tree_hsh[node]
        for n in nodes:
            t2H(tree_hsh, n, level)

    t2H(tree)
    return [x[indent:] for x in text_lst], args[0], args[1]


lst = None
rows = None
row = None


def tallyByGroup(list_of_tuples, max_level=0, indnt=3, options=None, export=False):
    """
list_of_tuples should already be sorted and the last component
in each tuple should be a tuple (minutes, value, expense, charge)
to be tallied.

     ('Scotland', 'Glasgow', 'North', 'summary sgn', (306, 10, 20.00, 30.00)),
     ('Scotland', 'Glasgow', 'South', 'summary sgs', (960, 10, 45.00, 60.00)),
     ('Wales', 'Cardiff', 'summary wc', (396, 10, 22.50, 30.00)),
     ('Wales', 'Bangor', 'summary wb', (126, 10, 37.00, 37.00)),

Recursively process groups and accumulate the totals.
    """
    if not options:
        options = {}
    if not max_level:
        max_level = len(list_of_tuples[0]) - 1
    level = -1
    global lst
    global head
    global auglst
    head = []
    auglst = []
    lst = []
    if 'action_template' in options:
        action_template = options['action_template']
    else:
        action_template = "!hours! $!value!) !label! (!count!)"

    action_template = "!indent!%s" % action_template

    if 'action_minutes' in options and options['action_minutes'] in [6, 12, 15, 30, 60]:
        # floating point hours
        m = options['action_minutes']

    tab = " " * indnt

    global rows, row
    rows = []
    row = ['' for i in range(max_level + 1)]

    def doLeaf(tup, lvl):
        global row, rows, head, auglst
        if len(tup) < 2:
            rows.append(deepcopy(row))
            return ()
        k = tup[0]
        g = tup[1:]
        t = tup[-1]
        lvl += 1
        row[lvl] = k
        row[-1] = t
        hsh = {}
        if max_level and lvl > max_level - 1:
            rows.append(deepcopy(row))
            return ()
        indent = " " * indnt
        hsh['indent'] = indent * lvl
        hsh['count'] = 1
        hsh['minutes'] = t[0]
        hsh['value'] = "%.2f" % t[1]  # only 2 digits after the decimal point
        hsh['expense'] = t[2]
        hsh['charge'] = t[3]
        hsh['total'] = t[1] + t[3]
        if options['action_minutes'] in [6, 12, 15, 30, 60]:
            # floating point hours
            hsh['hours'] = "{0:n}".format(
                ((t[0] // m + (t[0] % m > 0)) * m) / 60.0)
        else:
            # hours and minutes
            hsh['hours'] = "%d:%02d" % (t[0] // 60, t[0] % 60)
        hsh['label'] = k
        lst.append(expand_template(action_template, hsh, complain=True))
        head.append(lst[-1].lstrip())
        auglst.append(head)

        if len(g) >= 1:
            doLeaf(g, lvl)

    def doGroups(tuple_list, lvl):
        global row, rows, head, auglst
        hsh = {}
        lvl += 1
        if max_level and lvl > max_level - 1:
            rows.append(deepcopy(row))
            return
        hsh['indent'] = tab * lvl
        for k, g, t in group_sort(tuple_list):
            head = head[:lvl]
            row[lvl] = k[-1]
            row[-1] = t
            hsh['count'] = len(g)
            hsh['minutes'] = t[0]  # only 2 digits after the decimal point
            hsh['value'] = "%.2f" % t[1]
            hsh['expense'] = t[2]
            hsh['charge'] = t[3]
            hsh['total'] = t[1] + t[3]
            if options['action_minutes'] in [6, 12, 15, 30, 60]:
                # hours and tenths
                hsh['hours'] = "{0:n}".format(
                    ((t[0] // m + (t[0] % m > 0)) * m) / 60.0)
            else:
                # hours and minutes
                hsh['hours'] = "%d:%02d" % (t[0] // 60, t[0] % 60)

            hsh['label'] = k[-1]
            lst.append(expand_template(action_template, hsh, complain=True))
            head.append(lst[-1].lstrip())
            if len(head) == max_level:
                auglst.append(head)
            if len(g) > 1:
                doGroups(g, lvl)
            else:
                doLeaf(g[0], lvl)

    doGroups(list_of_tuples, level)

    for i in range(len(auglst)):
        if type(auglst[i][-1]) in [str, unicode]:
            res = auglst[i][-1].split('!!')
            if len(res) > 1:
                summary = res[0]
                uid = res[1]
                auglst[i][-1] = tuple((uid, 'ac', summary, ''))
    res = makeTree(auglst, sort=False)

    if export:
        for i in range(len(rows)):
            # remove the uuid from the summary
            summary = rows[i][-2].split('!!')[0]
            rows[i][-2] = summary
        return rows
    else:
        return res


def group_sort(row_lst):
    # last element of each list component is a (minutes, value,
    # expense, charge) tuple.
    # next to last element is a summary string.
    key = lambda cols: [cols[0]]
    for k, group in groupby(row_lst, key):
        t = []
        g = []
        for x in group:
            t.append(x[-1])
            g.append(x[1:])
        s = tupleSum(t)
        yield k, g, s


def uniqueId():
    # return unicode(thistime.strftime("%Y%m%dT%H%M%S@etmtk"))
    return unicode("{0}etm".format(uuid.uuid4().hex))


def nowAsUTC():
    return datetime.now(tzlocal()).astimezone(tzutc()).replace(tzinfo=None)


def datetime2minutes(dt):
    if type(dt) != datetime:
        return ()
    t = dt.time()
    return t.hour * 60 + t.minute


def parse_str(dt, timezone=None, fmt=None):
    """
    E.g., ('2/5/12', 'US/Pacific', rfmt) => "20120205T0000-0800"
    Return datetime object if fmt is None
    Return
    """
    if type(dt) in [str, unicode]:
        if dt == 'now':
            if timezone is None:
                dt = datetime.now()
            else:
                dt = datetime.now().replace(
                    tzinfo=tzlocal()).astimezone(
                    gettz(timezone)).replace(tzinfo=None)
        elif period_string_regex.match(dt):
            dt = datetime.now() + parse_period(dt, minutes=False)
        else:
            now = datetime.now()

            estr = estr_regex.search(dt)
            rel_mnth = rel_month_regex.search(dt)
            rel_date = rel_date_regex.search(dt)

            if estr:
                y = estr.group(1)
                e = easter(int(y))
                E = e.strftime("%Y-%m-%d")
                dt = estr_regex.sub(E, dt)

            if rel_mnth:
                new_y = now.year
                now_m = now.month
                mnth, day = map(int, rel_mnth.groups())
                new_m = now_m + mnth
                new_d = day
                if new_m <= 0:
                    new_y -= 1
                    new_m += 12
                elif new_m > 12:
                    new_y += 1
                    new_m -= 12
                new_date = "%s-%02d-%02d" % (new_y, new_m, new_d)
                dt = rel_month_regex.sub(new_date, dt)
            elif rel_date:
                days = int(rel_date.group(0))
                new_date = (now + days * ONEDAY).strftime("%Y-%m-%d")
                dt = rel_date_regex.sub(new_date, dt)

            dt = parse(dt)
            if type(dt) is not datetime:
                # we have a problem, return the error message
                return dt
    else:
        # dt is a datetime
        if dt.utcoffset() is None:
            dt = dt.replace(tzinfo=tzlocal())

    if timezone is None:
        dtz = dt.replace(tzinfo=tzlocal())
    else:
        dtz = dt.replace(tzinfo=gettz(timezone))

    if windoz and dtz.year < 1970:
        y = dtz.year
        m = dtz.month
        d = dtz.day
        H = dtz.hour
        M = dtz.minute
        dtz = datetime(y, m, d, H, M, 0, 0)
        epoch = datetime(1970, 1, 1, 0, 0, 0, 0)

        # dtz.replace(tzinfo=None)
        td = epoch - dtz
        seconds = td.days * 24 * 60 * 60 + td.seconds
        dtz = epoch - timedelta(seconds=seconds)

    if fmt is None:
        return dtz
    else:
        return dtz.strftime(fmt)


def parse_date_period(s):
    """
    fuzzy_date [ (+|-) period string]
    e.g. mon + 7d: the 2nd Monday on or after today
    used in reports to handle begin and end options
    """
    parts = [x.strip() for x in rsplit(' [+-] ', s)]
    try:
        dt = parse_str(parts[0])
    except Exception:
        return 'error: could not parse date "{0}"'.format(parts[0])
    if len(parts) > 1:
        try:
            pr = parse_period(parts[1])
        except Exception:
            return 'error: could not parse period "{0}"'.format(parts[1])
        if ' + ' in s:
            return dt + pr
        else:
            return dt - pr
    else:
        return dt


def parse_period(s, minutes=True):
    """\
    Take a case-insensitive period string and return a corresponding timedelta.
    Examples:
        parse_period('-2W3D4H5M')= -timedelta(weeks=2,days=3,hours=4,minutes=5)
        parse_period('1h30m') = timedelta(hours=1, minutes=30)
        parse_period('-10') = timedelta(minutes= 10)
    where:
        W or w: weeks
        D or d: days
        H or h: hours
        M or m: minutes
    If an integer is passed or a string that can be converted to an
    integer, then return a timedelta corresponding to this number of
    minutes if 'minutes = True', and this number of days otherwise.
    Minutes will be True for alerts and False for beginbys.
    """
    td = timedelta(seconds=0)
    if minutes:
        unitperiod = ONEMINUTE
    else:
        unitperiod = ONEDAY
    try:
        m = int(s)
        return m * unitperiod
    except Exception:
        m = int_regex.match(s)
        if m:
            return td + int(m.group(1)) * unitperiod, ""
            # if we get here we should have a period string
    m = period_string_regex.match(s)
    if not m:
        logger.error("Invalid period string: '{0}'".format(s))
        return "Invalid period string: '{0}'".format(s)
    m = week_regex.search(s)
    if m:
        td += int(m.group(1)) * ONEWEEK
    m = day_regex.search(s)
    if m:
        td += int(m.group(1)) * ONEDAY
    m = hour_regex.search(s)
    if m:
        td += int(m.group(1)) * ONEHOUR
    m = minute_regex.search(s)
    if m:
        td += int(m.group(1)) * ONEMINUTE
    if type(td) is not timedelta:
        return "Could not parse {0}".format(s)
    m = sign_regex.match(s)
    if m and m.group(1) == '-':
        return -1 * td
    else:
        return td


def year2string(startyear, endyear):
    """compute difference and append suffix"""
    diff = int(endyear) - int(startyear)
    suffix = 'th'
    if diff < 4 or diff > 20:
        if diff % 10 == 1:
            suffix = 'st'
        elif diff % 10 == 2:
            suffix = 'nd'
        elif diff % 10 == 3:
            suffix = 'rd'
    return "%d%s" % (diff, suffix)


def lst2str(l):
    if type(l) != list:
        return l
    tmp = []
    for item in l:
        if type(item) in [datetime]:
            tmp.append(parse_str(item, fmt=zfmt))
        elif type(item) in [timedelta]:
            tmp.append(timedelta2Str(item))
        elif isinstance(item, unicode):
            tmp.append(item)
        else:  # type(i) in [str,]:
            tmp.append(str(item))
    return ", ".join(tmp)


def hsh2str(hsh, options=None, include_uid=False):
    """
For editing one or more, but not all, instances of an item. Needed:
1. Add @+ datetime to orig and make copy sans all repeating info and
   with @s datetime.
2. Add &r datetime - ONEMINUTE to each _r in orig and make copy with
   @s datetime
3. Add &f datetime to selected job.
    """
    if not options:
        options = {}
    msg = []
    if '_summary' not in hsh:
        hsh['_summary'] = ''
    if '_group_summary' in hsh:
        sl = ["%s %s" % (hsh['itemtype'], hsh['_group_summary'])]
        if 'I' in hsh:
            # fix the item index
            hsh['I'] = hsh['I'].split(':')[0]
    else:
        sl = ["%s %s" % (hsh['itemtype'], hsh['_summary'])]
    if 'I' not in hsh or not hsh['I']:
        hsh['I'] = uniqueId()
    bad_keys = [x for x in hsh.keys() if x not in all_keys]
    if bad_keys:
        omitted = []
        for key in bad_keys:
            omitted.append('@{0} {1}'.format(key, hsh[key]))
        msg.append("unrecognized entries: {0}".format(", ".join(omitted)))
    for key in at_keys:
        amp_key = None
        if hsh['itemtype'] == "=":
            prefix = ""
        elif 'prefix_uses' in options and key in options['prefix_uses']:
            prefix = options['prefix']
        else:
            prefix = ""
        if key == 'a' and '_a' in hsh:
            alerts = []
            for alert in hsh["_a"]:
                triggers, acts, arguments = alert
                _ = "@a %s" % ", ".join([fmt_period(x) for x in triggers])
                if acts:
                    _ += ": %s" % ", ".join(acts)
                    if arguments:
                        arg_strings = []
                        for arg in arguments:
                            arg_strings.append(", ".join(arg))
                        _ += "; %s" % "; ".join(arg_strings)
                alerts.append(_)
            sl.extend(alerts)
        elif key in ['r', 'j']:
            at_key = key
            keys = amp_keys[key]
            key = "_%s" % key
        elif key in ['+', '-']:
            keys = []
        elif key in ['t', 'l', 'd']:
            keys = []
        else:
            keys = []

        if key in hsh and hsh[key] is not None:
            # since r and j can repeat, value will be a list
            value = hsh[key]
            if keys:
                # @r or @j --- value will be a list of hashes or
                # possibly, in the  case of @a, a list of lists. f
                # will be the first key for @r and t will be the
                # first for @a
                omitted = []
                for v in value:
                    for k in v.keys():
                        if k not in keys:
                            omitted.append('&{0} {1}'.format(k, v[k]))
                if omitted:
                    msg.append("unrecognized entries: {0}".format(", ".join(omitted)))

                tmp = []
                for h in value:
                    if unicode(keys[0]) not in h:
                        logger.warning("{0} not in {1}".format(keys[0], h))
                        continue
                    tmp.append('%s@%s %s' % (prefix, at_key,
                                             lst2str(h[unicode(keys[0])])))
                    for amp_key in keys[1:]:
                        if amp_key in h:
                            if at_key == 'j' and amp_key == 'f':
                                pairs = []
                                for pair in h['f']:
                                    pairs.append(";".join([
                                        x.strftime(zfmt) for x in pair if x]))
                                v = (', '.join(pairs))
                            elif at_key == 'j' and amp_key == 'h':
                                pairs = []
                                for pair in h['h']:
                                    pairs.append(";".join([
                                        x.strftime(zfmt) for x in pair if x]))
                                v = (', '.join(pairs))
                            elif amp_key == 'e':
                                try:
                                    v = fmt_period(h['e'])
                                except Exception:
                                    v = h['e']
                                    logger.error(
                                        "error: could not parse h['e']: '{0}'".format(
                                            h['e']))
                            else:
                                v = lst2str(h[amp_key])
                            tmp.append('&%s %s' % (amp_key, v))
                if tmp:
                    sl.append(" ".join(tmp))
            elif key == 's':
                try:
                    sl.append("%s@%s %s" % (prefix, key, fmt_datetime(value, options=options)))
                except:
                    msg.append("problem with @{0}: {1}".format(key, value))
            elif key == 'q':
                # Added this for abused women to record place in a queue - value should be the datetime the person entered the queue. Entering "now" would record the current datetime.
                if type(value) is datetime:
                    sl.append("%s@%s %s" % (
                        prefix, key,
                        value.strftime(zfmt),
                    ))
                else:
                    sl.append("%s@%s %s" % (prefix, key, value))
            elif key == 'e':
                try:
                    sl.append("%s@%s %s" % (prefix, key, fmt_period(value)))
                except:
                    msg.append("problem with @{0}: {1}".format(key, value))
            elif key == 'f':
                tmp = []
                for pair in hsh['f']:
                    tmp.append(";".join([x.strftime(zfmt) for x in pair if x]))
                sl.append("%s@f %s" % (prefix, ", {0}".format(prefix).join(tmp)))
            elif key == 'I':
                if include_uid and hsh['itemtype'] != "=":
                    sl.append("prefix@i {0}".format(prefix, value))
            elif key == 'h':
                tmp = []
                for pair in hsh['h']:
                    tmp.append(";".join([x.strftime(zfmt) for x in pair if x]))
                sl.append("%s@h %s" % (prefix, ", {0}".format(prefix).join(tmp)))
            else:
                sl.append("%s@%s %s" % (prefix, key, lst2str(value)))
    return " ".join(sl), msg


def process_all_datafiles(options):
    prefix, filelist = getFiles(options['datadir'])
    return process_data_file_list(filelist, options=options)


def process_data_file_list(filelist, options=None):
    if not options:
        options = {}
    messages = []
    file2lastmodified = {}
    bad_datafiles = {}
    file2uuids = {}
    uuid2hashes = {}
    uuid2labels = {}
    for f, r in filelist:
        file2lastmodified[(f, r)] = os.path.getmtime(f)
        msg, hashes, u2l = process_one_file(f, r, options)
        uuid2labels.update(u2l)
        if msg:
            messages.append("errors loading %s:" % r)
            messages.extend(msg)
        try:
            for hsh in hashes:
                if hsh['itemtype'] == '=':
                    continue
                uid = hsh['I']
                uuid2hashes[uid] = hsh
                file2uuids.setdefault(r, []).append(uid)
        except Exception:
            fio = StringIO()
            msg = fio.getvalue()
            bad_datafiles[r] = msg
            logger.error('Error processing: {0}\n{1}'.format(r, msg))
    return uuid2hashes, uuid2labels, file2uuids, file2lastmodified, bad_datafiles, messages


def process_one_file(full_filename, rel_filename, options=None):
    if not options:
        options = {}
    file_items = getFileItems(full_filename, rel_filename)
    return items2Hashes(file_items, options)


def getFiles(root, include=r'*.txt', exclude=r'.*', other=[]):
    """
    Return the common prefix and a list of full paths from root
    :param root: directory
    :return: common prefix of files and a list of full file paths
    """
    # includes = r'*.txt'
    # excludes = r'.*'
    paths = [root]
    filelist = []
    other.sort()
    for path in other:
        paths.append(path)
    common_prefix = os.path.commonprefix(paths)
    for path in other:
        rel_path = relpath(path, common_prefix)
        filelist.append((path, rel_path))
    for path, dirs, files in os.walk(root):
        # exclude dirs
        dirs[:] = [os.path.join(path, d) for d in dirs
                   if not fnmatch.fnmatch(d, exclude)]

        # exclude/include files
        files = [os.path.join(path, f) for f in files
                 if not fnmatch.fnmatch(f, exclude)]
        files = [os.path.normpath(f) for f in files if fnmatch.fnmatch(f, include)]

        for fname in files:
            rel_path = relpath(fname, common_prefix)
            filelist.append((fname, rel_path))
    return common_prefix, filelist


def getAllFiles(root, include=r'*', exclude=r'.*', other=[]):
    """
    Return the common prefix and a list of full paths from root
    :param root: directory
    :return: common prefix of files and a list of full file paths
    """
    paths = [root]
    filelist = []
    for path in other:
        paths.append(path)
    other.sort()
    common_prefix = os.path.commonprefix(paths)
    for path in other:
        rel_path = relpath(path, common_prefix)
        filelist.append((path, rel_path))
    for path, dirs, files in os.walk(root):
        # exclude dirs
        dirs[:] = [os.path.join(path, d) for d in dirs
                   if not fnmatch.fnmatch(d, exclude)]
        # exclude/include files
        files = [os.path.join(path, f) for f in files
                 if not fnmatch.fnmatch(f, exclude)]
        files = [os.path.normpath(f) for f in files if fnmatch.fnmatch(f, include)]
        for fname in files:
            rel_path = relpath(fname, common_prefix)
            filelist.append((fname, rel_path))
        if not (dirs or files):
            # empty
            rel_path = relpath(path, common_prefix)
            filelist.append((path, rel_path))
    return common_prefix, filelist


def getFileTuples(root, include=r'*.txt', exclude=r'.*', all=False, other=[]):
    """
    Used in view to get config files
    """
    if all:
        common_prefix, filelist = getAllFiles(root, include, exclude, other=other)
    else:
        common_prefix, filelist = getFiles(root, include, exclude, other=other)
    lst = []
    prior = []
    for fp, rp in filelist:
        drive, tup = os_path_splitall(rp)
        for i in range(0, len(tup)):
            if len(prior) > i and tup[i] == prior[i]:
                continue
            prior = tup[:i]
            disable = (i < len(tup) - 1) or os.path.isdir(fp)
            lst.append(("{0}{1}".format(" " * 6 * i, tup[i]), rp, disable))
    return common_prefix, lst


def os_path_splitall(path, debug=False):
    parts = []
    drive, path = os.path.splitdrive(path)
    while True:
        newpath, tail = os.path.split(path)
        if newpath == path:
            assert not tail
            if path:
                parts.append(path)
            break
        parts.append(tail)
        path = newpath
    parts.reverse()
    return drive, parts


def getFileItems(full_name, rel_name, append_newline=True):
    """
        Group the lines in file f into logical items and return them.
    :param full_name: including datadir
    :param rel_name: from datadir
    :param append_newline: bool, default True
    """
    fo = codecs.open(full_name, 'r', file_encoding)
    lines = fo.readlines()
    fo.close()
    # make sure we have a trailing new-line. Yes, we really need this.
    if append_newline:
        lines.append('\n')
    linenum = 0
    linenums = []
    logical_line = []
    for line in lines:
        linenums.append(linenum)
        linenum += 1
        # preserve new lines and leading whitespace within logical lines
        stripped = line.rstrip()
        m = item_regex.match(stripped)
        if m is not None or stripped == '=':
            if logical_line:
                yield (''.join(logical_line), rel_name, linenums)
            logical_line = []
            linenums = []
            logical_line.append("%s\n" % line.rstrip())
        elif stripped:
            # a line which does not continue, end of logical line
            logical_line.append("%s\n" % line.rstrip())
        elif logical_line:
            # preserve interior empty lines
            logical_line.append("\n")
    if logical_line:
        # end of sequence implies end of last logical line
        yield (''.join(logical_line), rel_name, linenums)


def items2Hashes(list_of_items, options=None):
    """
        Return a list of messages and a list of hashes corresponding to items in
        list_of_items.
    """
    if not options:
        options = {}
    messages = []
    hashes = []
    uuid2labels = {}
    defaults = {}
    # in_task_group = False
    for item, rel_name, linenums in list_of_items:
        hsh, msg = str2hsh(item, options=options)
        logger.debug("items2Hashes:\n  item='{0}'  hsh={1}\n  msg={2}".format(item, hsh, msg))

        if item.strip() == "=":
            # reset defaults
            defaults = {}

        tmp_hsh = {}
        tmp_hsh.update(defaults)
        tmp_hsh.update(hsh)
        hsh = tmp_hsh
        try:
            hsh['fileinfo'] = (rel_name, linenums[0], linenums[-1])
        except:
            raise ValueError("exception in fileinfo:",
                             rel_name, linenums, "\n", hsh)
        if msg:
            lines = []
            item = item.strip()
            if len(item) > 56:
                lines.extend(wrap(item, 56))
            else:
                lines.append(item)
            for line in lines:
                messages.append("{0}".format(line))
            for m in msg:
                messages.append('{0}'.format(m))
            msg.append('    {0}'.format(hsh['fileinfo']))
            # put the bad item in the inbox for repairs
            hsh['_summary'] = "{0} {1}".format(hsh['itemtype'], hsh['_summary'])
            hsh['itemtype'] = "$"
            hsh['I'] = uniqueId()
            hsh['errors'] = "\n    ".join(msg)
            logger.warn("{0}".format(hsh['errors']))
            # no more processing
            # ('hsh:', hsh)
            hashes.append(hsh)
            continue

        itemtype = hsh['itemtype']
        if itemtype == '$':
            # inbasket item
            hashes.append(hsh)
        elif itemtype == '#':
            # deleted item
            # yield this so that hidden entries are in file2uuids
            hashes.append(hsh)
        elif itemtype == '=':
            # set group defaults
            # hashes.append(this so that default entries are in file2uuids
            logger.debug("items2Hashes defaults: {0}".format(hsh))
            defaults = hsh
            hashes.append(hsh)
        elif itemtype == '+':
            # needed for task group:
            #   the original hsh with the summary adjusted to show
            #       the number of tasks and type changed to '-' and the
            #       date updated to refect the due (keep) due date
            #   a non-repeating hash with type '+' for each job
            #       with current due date for unfinished jobs and
            #       otherwise the finished date. These will appear
            #       in days but not folders
            #   '+' items will be not be added to folders
            # Finishing a group task should be handled separately
            # when the last job is finished and 'f' is updated.
            # Here we assume that one or more jobs are unfinished.
            queue_hsh = {}
            tmp_hsh = {}
            for at_key in defaults:
                if at_key in key2type and itemtype in key2type[at_key]:
                    tmp_hsh[at_key] = defaults[at_key]

            # tmp_hsh.update(defaults)
            tmp_hsh.update(hsh)
            group_defaults = tmp_hsh
            group_task = deepcopy(group_defaults)
            done, due, following = getDoneAndTwo(group_task)
            if 'f' in group_defaults and due:
                del group_defaults['f']
                group_defaults['s'] = due
            if 'rrule' in group_defaults:
                del group_defaults['rrule']
            prereqs = []
            last_level = 1
            uid = hsh['I']
            summary = hsh['_summary']
            if 'j' not in hsh:
                continue
            job_num = 0
            jobs = [x for x in hsh['j']]
            completed = []
            num_jobs = len(jobs)
            del group_defaults['j']
            if following:
                del group_task['j']
                # group_task['s'] = following
                group_task['s'] = following
                group_task['_summary'] = "%s [%s jobs]" % (
                    summary, len(jobs))
                hashes.append(group_task)
            for job in jobs:
                tmp_hsh = {}
                tmp_hsh.update(group_defaults)
                tmp_hsh.update(job)
                job = tmp_hsh
                job['itemtype'] = '+'
                job_num += 1
                current_id = "%s:%02d" % (uid, job_num)
                if 'f' in job:
                    # this will be a done:due pair with the due
                    # of the current group task
                        completed.append(current_id)
                job["_summary"] = "%s %d/%d: %s" % (
                    summary, job_num, num_jobs, job['j'])
                del job['j']
                if 'q' not in job:
                    logger.warn('error: q missing from job')
                    continue
                try:
                    current_level = int(job['q'])
                except:
                    logger.warn('error: bad value for q', job['q'])
                    continue
                job['I'] = current_id

                queue_hsh.setdefault(current_level, set([])).add(current_id)

                if current_level < last_level:
                    prereqs = []
                    for k in queue_hsh:
                        if k > current_level:
                            queue_hsh[k] = set([])
                for k in queue_hsh:
                    if k < current_level:
                        prereqs.extend(list(queue_hsh[k]))
                job['prereqs'] = [x for x in prereqs if x not in completed]

                last_level = current_level
                try:
                    job['fileinfo'] = (rel_name, linenums[0], linenums[-1])
                except:
                    logger.exception("fileinfo: {0}.{1}".format(rel_name, linenums))
                logger.debug('appending job: {0}'.format(job))
                hashes.append(job)
        else:
            tmp_hsh = {}
            for at_key in defaults:
                if at_key in key2type and itemtype in key2type[at_key]:
                    tmp_hsh[at_key] = defaults[at_key]

            # tmp_hsh.update(defaults)
            tmp_hsh.update(hsh)
            hsh = tmp_hsh
            try:
                hsh['fileinfo'] = (rel_name, linenums[0], linenums[-1])
            except:
                raise ValueError("exception in fileinfo:",
                                 rel_name, linenums, "\n", hsh)
            hashes.append(hsh)
        if itemtype not in ['=', '$']:
            tmp = [' ']
            for key in label_keys:
                if key in hsh and hsh[key]:
                    # dump the '_'
                    key = key[-1]
                    tmp.append(key)
                # else:
                #     tmp.append(' ')
            uuid2labels[hsh['I']] = "".join(tmp)
    return messages, hashes, uuid2labels


def get_reps(bef, hsh):
    if hsh['itemtype'] in ['+', '-', '%']:
        done, due, following = getDoneAndTwo(hsh)
        if hsh['itemtype'] == '+':
            if done and following:
                start = following
            elif due:
                start = due
        elif due:
            start = due
        else:
            start = done
    else:
        start = hsh['s'].replace(tzinfo=None)
    tmp = []
    if not start:
        return False, []
    for hsh_r in hsh['_r']:
        tests = [
            u'f' in hsh_r and hsh_r['f'] == 'l',
            u't' in hsh_r,
            u'u' in hsh_r
        ]
        for test in tests:
            passed = False
            if test:
                passed = True
                break
        if not passed:
            break

    if passed:
        # finite, get instances after start
        try:
            tmp.extend([x for x in hsh['rrule'] if x >= start])
        except:
            logger.exception('done: {0}; due: {1}; following: {2}; start: {3}; rrule: {4}'.format(done, due, following, start, hsh['rrule']))
    else:
        tmp.extend(list(hsh['rrule'].between(start, bef, inc=True)))
        tmp.append(hsh['rrule'].after(bef, inc=False))

    if windoz:
        ret = []
        epoch = datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=None)
        for i in tmp:
            if not i:
                continue
            # i.replace(tzinfo=gettz(hsh['z']))
            if i.year < 1970:
                # i.replace(tzinfo=gettz(hsh['z']))
                td = epoch - i
                i = epoch - td
            else:
                i.replace(tzinfo=gettz(hsh['z'])).astimezone(tzlocal()).replace(tzinfo=None)
            ret.append(i)
        return passed, ret

    return passed, [j.replace(tzinfo=gettz(hsh['z'])).astimezone(tzlocal()).replace(tzinfo=None) for j in tmp if j]


def get_rrulestr(hsh, key_hsh=rrule_hsh):
    """
        Parse the rrule relevant information in hsh and return a
        corresponding RRULE string.

        First pass - replace hsh['r'] with an equivalent rrulestr.
    """
    if 'r' not in hsh:
        return ()
    try:
        lofh = hsh['r']
    except:
        raise ValueError("Could not load rrule:", hsh['r'])
    ret = []
    l = []
    if type(lofh) == dict:
        lofh = [lofh]
    for h in lofh:
        if 'f' in h and h['f'] == 'l':
            # list only
            l = []
        else:
            try:
                l = ["RRULE:FREQ=%s" % freq_hsh[h['f']]]
            except:
                logger.exception("bad rrule: {0}, {1}, {2}\n{3}".format(rrule, "\nh:", h, hsh))

        for k in rrule_keys:
            if k in h and h[k]:
                v = h[k]
                if type(v) == list:
                    v = ",".join(map(str, v))
                if k == 'w':
                    # make weekdays upper case
                    v = v.upper()
                    m = threeday_regex.search(v)
                    while m:
                        v = threeday_regex.sub("%s" % m.group(1)[:2],
                                               v, count=1)
                        m = threeday_regex.search(v)
                l.append("%s=%s" % (rrule_hsh[k], v))
        if 'u' in h:
            dt = parse_str(h['u'], hsh['z']).replace(tzinfo=None)
            l.append("UNTIL=%s" % dt.strftime(sfmt))
        ret.append(";".join(l))
    return "\n".join(ret)


def get_rrule(hsh):
    """
        Used to process the rulestr entry. Dates and times in *rstr*
        will be datetimes with offsets. Parameters *aft* and *bef* are
        UTC datetimes. Datetimes from *rule* will be returned as local
        times.

        Second pass - use the hsh['r'] rrulestr entry
    """
    rlst = []
    warn = []
    if 'z' not in hsh:
        hsh['z'] = local_timezone
    if 'o' in hsh and hsh['o'] == 'r' and 'f' in hsh:
        dtstart = hsh['f'][-1][0].replace(tzinfo=gettz(hsh['z']))
    elif 's' in hsh:
        dtstart = parse_str(hsh['s'], hsh['z']).replace(tzinfo=None)
    else:
        dtstart = datetime.now()
    if 'r' in hsh:
        if hsh['r']:
            rlst.append(hsh['r'])
        if dtstart:
            rlst.insert(0, "DTSTART:%s" % dtstart.strftime(sfmt))
    if '+' in hsh:
        parts = hsh['+']
        if type(parts) != list:
            parts = [parts]
        if parts:
            start = parse_str(dtstart, fmt=sfmt)
            for part in map(str, parts):
                # rlst.append("RDATE:%s" % parse(part).strftime(sfmt))
                plus = parse_str(part, fmt=sfmt)
                if plus >= start:
                    rlst.append("RDATE:%s" % plus)
    if '-' in hsh:
        tmprule = dtR.rrulestr("\n".join(rlst))
        parts = hsh['-']
        if type(parts) != list:
            parts = [parts]
        if parts:
            for part in map(str, parts):
                thisdatetime = parse_str(part, hsh['z']).replace(tzinfo=None)
                beforedatetime = tmprule.before(thisdatetime, inc=True)
                if beforedatetime != thisdatetime:
                    warn.append(_(
                        "{0} is listed in @- but doesn't match any datetimes generated by @r.").format(
                        thisdatetime.strftime(rfmt)))
                rlst.append("EXDATE:%s" % parse_str(part, fmt=sfmt))
    rulestr = "\n".join(rlst)
    try:
        rule = dtR.rrulestr(rulestr)
    except ValueError as e:
        rule = None
        warn.append("{0}".format(e))
        # raise ValueError("could not create rule from", rulestr)
    return rulestr, rule, warn


def checkhsh(hsh):
    messages = []
    if hsh['itemtype'] in ['*', '~', '^'] and 's' not in hsh:
        messages.append(
            "An entry for @s is required for events, actions and occasions.")
    elif hsh['itemtype'] in ['~'] and 'e' not in hsh and 'x' not in hsh:
        messages.append("An entry for either @e or @x is required for actions.")
    if ('a' in hsh or 'r' in hsh) and 's' not in hsh:
        messages.append(
            "An entry for @s is required for items with either @a or @r entries.")
    if ('+' in hsh or '-' in hsh) and 'r' not in hsh:
        messages.extend(
            ["An entry for @r is required for items with",
             "either @+ or @- entries."])
    if ('n' in hsh and hsh['n']):
        n_views = ['d', 't', 'k']
        bad = []
        for v in hsh['n']:
            if v not in n_views:
                bad.append(v)
        if bad:
            messages.extend(
                ["Not allowed in @n: {0}. Only values from".format(', '.join(bad)),
                "{0} are allowed.".format(", ".join(n_views)),
                 ])
    return messages


def str2opts(s, options=None, cli=True):
    if not options:
        options = {}
    filters = {}
    if 'calendars' in options:
        cal_pattern = r'^%s' % '|'.join(
            [x[2] for x in options['calendars'] if x[1]])
        filters['cal_regex'] = re.compile(cal_pattern)
    s = s2or3(s)
    op_str = s.split('#')[0]
    parts = minus_regex.split(op_str)
    head = parts.pop(0)
    report = head[0]
    groupbystr = head[1:].strip()
    if not report or report not in ['c', 'a'] or not groupbystr:
        return {}
    grpby = {'report': report}
    filters['dates'] = False
    dated = {'grpby': False}
    filters['report'] = unicode(report)
    filters['omit'] = [True, []]
    filters['neg_fields'] = []
    filters['pos_fields'] = []
    groupbylst = [unicode(x.strip()) for x in groupbystr.split(';')]
    grpby['lst'] = groupbylst
    for part in groupbylst:
        if groupdate_regex.search(part):
            dated['grpby'] = True
            filters['dates'] = True
        elif part not in ['c', 'u', 'l'] and part[0] not in ['k', 'f', 't']:
            term_print(
                str(_('Ignoring invalid grpby part: "{0}"'.format(part))))
            groupbylst.remove(part)
    if not groupbylst:
        return '', '', ''
        # we'll split cols on :: after applying fmts to the string
    grpby['cols'] = "::".join(["{%d}" % i for i in range(len(groupbylst))])
    grpby['fmts'] = []
    grpby['tuples'] = []
    filters['grpby'] = ['_summary']
    filters['missing'] = False
    # include = {'y', 'm', 'w', 'd'}
    include = {'y', 'm', 'd'}
    for group in groupbylst:
        d_lst = []
        if groupdate_regex.search(group):
            if 'w' in group:
                # groupby week or some other date spec,  not both
                group = "w"
                d_lst.append('w')
                include.discard('w')
                if 'y' in group:
                    include.discard('y')
                if 'M' in group:
                    include.discard('m')
                if 'd' in group:
                    include.discard('d')
            else:
                if 'y' in group:
                    d_lst.append('yyyy')
                    include.discard('y')
                if 'M' in group:
                    d_lst.append('MM')
                    include.discard('m')
                if 'd' in group:
                    d_lst.append('dd')
                    include.discard('d')
            grpby['tuples'].append(" ".join(d_lst))
            grpby['fmts'].append(
                "d_to_str(tup[-3], '%s')" % group)

        elif '[' in group:
            if group[0] == 'f':
                if ':' in group:
                    grpby['fmts'].append(
                        "'/'.join(rsplit('/', hsh['fileinfo'][0])%s)" %
                        (group[1:]))
                    grpby['tuples'].append(
                        "'/'.join(rsplit('/', hsh['fileinfo'][0])%s)" %
                        (group[1:]))
                else:
                    grpby['fmts'].append(
                        "rsplit('/', hsh['fileinfo'][0])%s" % (group[1:]))
                    grpby['tuples'].append(
                        "rsplit('/', hsh['fileinfo'][0])%s" % (group[1:]))
            elif group[0] == 'k':
                if ':' in group:
                    grpby['fmts'].append(
                        "':'.join(rsplit(':', hsh['%s'])%s)" %
                        (group[0], group[1:]))
                    grpby['tuples'].append(
                        "':'.join(rsplit(':', hsh['%s'])%s)" %
                        (group[0], group[1:]))
                else:
                    grpby['fmts'].append(
                        "rsplit(':', hsh['%s'])%s" % (group[0], group[1:]))
                    grpby['tuples'].append(
                        "rsplit(':', hsh['%s'])%s" % (group[0], group[1:]))
            filters['grpby'].append(group[0])
        else:
            if 'f' in group:
                grpby['fmts'].append("hsh['fileinfo'][0]")
                grpby['tuples'].append("hsh['fileinfo'][0]")
            else:
                grpby['fmts'].append("hsh['%s']" % group.strip())
                grpby['tuples'].append("hsh['%s']" % group.strip())
            filters['grpby'].append(group[0])
        if include:
            if include == {'y', 'm', 'd'}:
                grpby['include'] = "yyyy-MM-dd"
            elif include == {'m', 'd'}:
                grpby['include'] = "MMM d"
            elif include == {'y', 'd'}:
                grpby['include'] = "yyyy-MM-dd"
            elif include == set(['y', 'w']):
                groupby['include'] = "w"
            elif include == {'d'}:
                grpby['include'] = "MMM dd"
            elif include == set(['w']):
                grpby['include'] = "w"
            else:
                grpby['include'] = ""
        else:
            grpby['include'] = ""
        logger.debug('grpby final: {0}'.format(grpby))

    for part in parts:
        key = unicode(part[0])
        if key in ['b', 'e']:
            dt = parse_date_period(part[1:])
            dated[key] = dt.replace(tzinfo=None)

        elif key == 'm':
            value = unicode(part[1:].strip())
            if value == '1':
                filters['missing'] = True

        elif key == 'f':
            value = unicode(part[1:].strip())
            if value[0] == '!':
                filters['folder'] = (False, re.compile(r'%s' % value[1:],
                                                       re.IGNORECASE))
            else:
                filters['folder'] = (True, re.compile(r'%s' % value,
                                                      re.IGNORECASE))
        elif key == 's':
            value = unicode(part[1:].strip())
            if value[0] == '!':
                filters['search'] = (False, re.compile(r'%s' % value[1:],
                                                       re.IGNORECASE))
            else:
                filters['search'] = (True, re.compile(r'%s' % value,
                                                      re.IGNORECASE))
        elif key == 'S':
            value = unicode(part[1:].strip())
            if value[0] == '!':
                filters['search-all'] = (False, re.compile(r'%s' % value[1:], re.IGNORECASE | re.DOTALL))
            else:
                filters['search-all'] = (True, re.compile(r'%s' % value, re.IGNORECASE | re.DOTALL))
        elif key == 'd':
            if cli:
                if grpby['report'] == 'a':
                    d = int(part[1:])
                    if d:
                        d += 1
                    grpby['depth'] = d
            else:
                pass

        elif key == 't':
            value = [x.strip() for x in part[1:].split(',')]
            for t in value:
                if t[0] == '!':
                    filters['neg_fields'].append((
                        't', re.compile(r'%s' % t[1:], re.IGNORECASE)))
                else:
                    filters['pos_fields'].append((
                        't', re.compile(r'%s' % t, re.IGNORECASE)))
        elif key == 'o':
            value = unicode(part[1:].strip())
            if value[0] == '!':
                filters['omit'][0] = False
                filters['omit'][1] = [x for x in value[1:]]
            else:
                filters['omit'][0] = True
                filters['omit'][1] = [x for x in value]
        elif key == 'h':
            grpby['colors'] = int(part[1:])
        elif key == 'w':
            grpby['width1'] = int(part[1:])
        elif key == 'W':
            grpby['width2'] = int(part[1:])
        else:
            value = unicode(part[1:].strip())
            if value[0] == '!':
                filters['neg_fields'].append((
                    key, re.compile(r'%s' % value[1:], re.IGNORECASE)))
            else:
                filters['pos_fields'].append((
                    key, re.compile(r'%s' % value, re.IGNORECASE)))
    if 'b' not in dated:
        dated['b'] = parse_str(options['report_begin']).replace(tzinfo=None)
    if 'e' not in dated:
        dated['e'] = parse_str(options['report_end']).replace(tzinfo=None)
    if 'colors' not in grpby or grpby['colors'] not in [0, 1, 2]:
        grpby['colors'] = options['report_colors']
    if 'width1' not in grpby:
        grpby['width1'] = options['report_width1']
    if 'width2' not in grpby:
        grpby['width2'] = options['report_width2']
    grpby['lst'].append(u'summary')
    logger.debug('grpby: {0}; dated: {1}; filters: {2}'.format(grpby, dated, filters))
    return grpby, dated, filters


def applyFilters(file2uuids, uuid2hash, filters):
    """
        Apply all filters except begin and end and return a list of
        the uid's of the passing hashes.

        TODO: memoize?
    """

    typeHsh = {
        'a': '~',
        'd': '%',
        'e': '*',
        'g': '+',
        'o': '^',
        'n': '!',
        't': '-',
        's': '?',
    }
    uuids = []

    omit = None
    if 'omit' in filters:
        omit, omit_types = filters['omit']
        omit_chars = [typeHsh[x] for x in omit_types]

    for f in file2uuids:
        if 'cal_regex' in filters and not filters['cal_regex'].match(f):
            continue
        if 'folder' in filters:
            tf, folder_regex = filters['folder']
            if tf and not folder_regex.search(f):
                continue
            if not tf and folder_regex.search(f):
                continue
        for uid in file2uuids[f]:
            hsh = uuid2hash[uid]
            skip = False
            type_char = hsh['itemtype']
            if type_char in ['=', '#', '$']:
                # omit defaults, hidden, inbox and someday
                continue
            if filters['dates'] and 's' not in hsh:
                # groupby includes a date specification and this item is undated
                continue
            if filters['report'] == 'a' and type_char != '~':
                continue
            if filters['report'] == 'c' and omit is not None:
                if omit and type_char in omit_chars:
                    # we're omitting this type
                    continue
                if not omit and type_char not in omit_chars:
                    # we're not showing this type
                    continue
            if 'search' in filters:
                tf, rx = filters['search']
                l = []
                for g in filters['grpby']:
                    # search over the leaf summary and the branch
                    for t in ['_summary', u'c', u'k', u'f', u'u']:
                        if t not in g:
                            continue
                        if t == 'f':
                            v = hsh['fileinfo'][0]
                        elif t in hsh:
                            v = hsh[t]
                        else:
                            continue
                            # add v to l
                        l.append(v)
                s = ' '.join(l)
                res = rx.search(s)
                if tf and not res:
                    skip = True
                if not tf and res:
                    skip = True
            if 'search-all' in filters:
                tf, rx = filters['search-all']
                # search over the entire entry and the file path
                l = [hsh['entry'], hsh['fileinfo'][0]]
                s = ' '.join(l)
                res = rx.search(s)
                if tf and not res:
                    skip = True
                if not tf and res:
                    skip = True
            for t in ['c', 'k', 'u', 'l']:
                if t in filters['grpby']:
                    if filters['missing']:
                        if t not in hsh:
                            hsh[t] = NONE
                    else:
                        if t in hsh and hsh[t] == NONE:
                            # we added this on an earlier report
                            del hsh[t]
                        if t not in hsh:
                            skip = True
                            break
            if skip:
                # try the next uid
                continue
            for flt, rgx in filters['pos_fields']:
                if flt == 't':
                    if 't' not in hsh or not rgx.search(" ".join(hsh['t'])):
                        skip = True
                        break
                elif flt not in hsh or not rgx.search(hsh[flt]):
                    skip = True
                    break
            if skip:
                # try the next uid
                continue
            for flt, rgx in filters['neg_fields']:
                if flt == 't':
                    if 't' in hsh and rgx.search(" ".join(hsh['t'])):
                        skip = True
                        break
                elif flt in hsh and rgx.search(hsh[flt]):
                    skip = True
                    break
            if skip:
                # try the next uid
                continue
                # passed all tests
            uuids.append(uid)
    return uuids


def reportDT(dt, include, options=None):
    # include will be something like "MMM d yyyy"
    if not options:
        options = {}
    res = ''
    if dt.hour == 0 and dt.minute == 0:
        if not include:
            return ''
        return d_to_str(dt, "yyyy-MM-dd")
    else:
        if options['ampm']:
            if include:
                res = dt_to_str(dt, "%s h:mma" % include)
            else:
                res = dt_to_str(dt, "h:mma")
        else:
            if include:
                res = dt_to_str(dt, "%s hh:mm" % include)
            else:
                res = dt_to_str(dt, "hh:mm")
        return leadingzero.sub('', res.lower())


# noinspection PyChainedComparisons
def makeReportTuples(uuids, uuid2hash, grpby, dated, options=None):
    """
        Using filtered uuids, and dates: grpby, b and e, return a sorted
        list of tuples
            (sort1, sort2, ... typenum, dt or '', uid)
        using dt takes care of time when needed or date and time when
        grpby has no date specification
    """
    if not options:
        options = {}
    today_datetime = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0)
    today_date = datetime.now().date()
    tups = []
    for uid in uuids:
        try:
            hsh = {}
            for k, v in uuid2hash[uid].items():
                hsh[k] = v
                # we'll make anniversary subs to a copy later
            hsh['summary'] = hsh['_summary']
            tchr = hsh['itemtype']
            tstr = type2Str[tchr]
            if 't' not in hsh:
                hsh['t'] = []
            if dated['grpby']:
                dates = []
                if 'f' in hsh and hsh['f']:
                    next = getDoneAndTwo(hsh)[1]
                    if next:
                        start = next
                else:
                    start = parse_str(hsh['s'], hsh['z']).astimezone(tzlocal()).replace(tzinfo=None)
                if 'rrule' in hsh:
                    if dated['b'] > start:
                        start = dated['b']
                    for date in hsh['rrule'].between(dated['b'], dated['e'], inc=True):
                        # to local time
                        date = date.replace(tzinfo=gettz(hsh['z'])).astimezone(tzlocal()).replace(tzinfo=None)
                        if date < dated['e']:
                            bisect.insort(dates, date)
                elif 's' in hsh and hsh['s'] and 'f' not in hsh:
                    if dated['b'] <= hsh['s'] < dated['e']:
                        bisect.insort(dates, start)
                        # datesSL.insert(start)
                if 'f' in hsh and hsh['f']:
                    dt = parse_str(
                        hsh['f'][-1][0], hsh['z']).astimezone(
                        tzlocal()).replace(tzinfo=None)
                    if dated['b'] <= dt <= dated['e']:
                        bisect.insort(dates, dt)
                for dt in dates:
                    if not (dated['b'] <= dt <= dated['e']):
                        continue
                    item = []
                    # ('dt', type(dt), dt)
                    for g in grpby['tuples']:
                        if groupdate_regex.search(g):
                            item.append(d_to_str(dt, g))
                        elif g in ['c', 'u']:
                            item.append(hsh[g])
                        else:  # should be f or k
                            item.append(eval(g))
                    item.extend([
                        tstr2SCI[tstr][0],
                        tstr,
                        dt,
                        reportDT(dt, grpby['include'], options),
                        uid])
                    bisect.insort(tups, tuple(item))

            else:  # no date spec in grpby
                item = []
                dt = ''
                if hsh['itemtype'] in [u'+', u'-', u'%']:
                    # task type
                    done, due, following = getDoneAndTwo(hsh)
                    if due:
                        # add a due entry
                        if due.date() < today_date:
                            if tchr == '+':
                                tstr = 'pc'
                            elif tchr == '-':
                                tstr = 'pt'
                            elif tchr == '%':
                                tstr = 'pd'
                        dt = due
                    elif done:
                        dt = done
                else:
                    # not a task type
                    if 's' in hsh:
                        if 'rrule' in hsh:
                            if tchr in ['^', '*', '~']:
                                dt = (hsh['rrule'].after(today_datetime, inc=True) or hsh['rrule'].before(today_datetime, inc=True))
                                if dt is None:
                                    logger.warning('No valid datetimes for {0}, {1}'.format(hsh['_summary'], hsh['fileinfo']))
                                    continue
                            else:
                                dt = hsh['rrule'].after(hsh['s'], inc=True)
                        else:
                            dt = parse_str(hsh['s'], hsh['z']).replace(tzinfo=None)
                    else:
                        # undated
                        dt = ''
                for g in grpby['tuples']:
                    if groupdate_regex.search(g):
                        item.append(dt_to_str(dt, g))
                    else:
                        try:
                            res = eval(g)
                            item.append(res)
                        except:
                            pass
                if type(dt) == datetime:
                    if dated['b'] <= dt <= dated['e']:
                        dtstr = reportDT(dt, grpby['include'], options)
                        dt = dt.strftime(etmdatefmt)
                    else:
                        dt = None
                else:
                    dtstr = dt
                if dt is not None:
                    item.extend([
                        tstr2SCI[tstr][0],
                        tstr,
                        dt,
                        dtstr,
                        uid])
                    bisect.insort(tups, tuple(item))
        except:
            logger.exception('Error processing: {0}, {1}'.format(hsh['_summary'], hsh['fileinfo']))
    return tups


def getAgenda(allrows, colors=2, days=4, indent=2, width1=54,
              width2=14, calendars=None, omit=[], mode='html', fltr=None):
    if not calendars:
        calendars = []
    items = deepcopy(allrows)
    day = []
    inbasket = []
    now = []
    next = []
    someday = []
    if colors and mode == 'html':
        bb = "<b>"
        eb = "</b>"
    else:
        bb = ""
        eb = ""
    # show day items starting with beg and ending with lst
    beg = datetime.today()
    tom = beg + ONEDAY
    lst = beg + (days - 1) * ONEDAY
    beg_fmt = beg.strftime(u"%Y%m%d")
    tom_fmt = tom.strftime(u"%Y%m%d")
    lst_fmt = lst.strftime(u"%Y%m%d")
    if not items:
        return {}
    for item in items:
        if item[0][0] == 'day':
            if item[0][1] >= beg_fmt and item[0][1] <= lst_fmt:
                # if item[2][1] in ['fn', 'ac', 'ns']:
                if omit and item[2][1] in omit:
                    # skip omitted items
                    continue
                if item[0][1] == beg_fmt:
                    item[1] = u"{0}".format(fmt_date(beg, short=True))
                elif item[0][1] == tom_fmt:
                    item[1] = u"{0}".format(fmt_date(tom, short=True))
                day.append(item)
        elif item[0][0] == 'inbasket':
            item.insert(1, u"{0}{1}{2}".format(bb, _("In Basket"), eb))
            inbasket.append(item)
        elif item[0][0] == 'now':
            item.insert(1, u"{0}{1}{2}".format(bb, _("Now"), eb))
            now.append(item)
        elif item[0][0] == 'next':
            item.insert(1, u"{0}{1}{2}".format(bb, _("Next"), eb))
            next.append(item)
        elif item[0][0] == 'someday':
            item.insert(1, u"{0}{1}{2}".format(bb, _("Someday"), eb))
            someday.append(item)
    tree = {}
    nv = 0
    for l in [day, inbasket, now, next, someday]:
        if l:
            nv += 1
            update = makeTree(l, calendars=calendars, fltr=fltr)
            for key in update.keys():
                tree.setdefault(key, []).extend(update[key])
    logger.debug("called makeTree for {0} views".format(nv))
    return tree


# @memoize
def getReportData(s, file2uuids, uuid2hash, options=None, export=False,
                  colors=None, cli=True):
    """
        getViewData returns items with the format:
            [(view, (sort)), node1, node2, ...,
                (uuid, typestr, summary, col_2, dt_sort_str) ]
        pop item[0] after sort leaving
            [node1, node2, ... (xxx) ]

        for actions (tallyByGroup) we need
            (node1, node2, ... (minutes, value, expense, charge))
    """
    if not options:
        options = {}
    try:
        grpby, dated, filters = str2opts(s, options, cli)
    except:
        e = "{0}: {1}".format(_("Could not process"), s)
        logger.exception(e)
        return e
    if not grpby:
        return ["{0}: grpby".format(_('invalid setting'))]
    uuids = applyFilters(file2uuids, uuid2hash, filters)
    tups = makeReportTuples(uuids, uuid2hash, grpby, dated, options)
    items = []
    cols = grpby['cols']
    fmts = grpby['fmts']
    for tup in tups:
        uuid = tup[-1]
        hsh = uuid2hash[tup[-1]]

        # for eval we need to be sure that t is in hsh
        if 't' not in hsh:
            hsh['t'] = []

        try:
            # for eval: {} is the global namespace
            # and {'tup' ... dt_to_str} is the local namespace
            eval_fmts = [
                eval(x, {},
                     {'tup': tup, 'hsh': hsh, 'rsplit': rsplit,
                      'd_to_str': d_to_str, 'dt_to_str': dt_to_str})
                for x in fmts]
        except Exception:
            logger.exception('fmts: {0}'.format(fmts))
            continue
        if filters['dates']:
            dt = reportDT(tup[-3], grpby['include'], options)
            if dt == '00:00':
                dt = ''
                dtl = None
            else:
                dtl = tup[-3]
        else:
            # the datetime (sort string) will be in tup[-3],
            # the display string in tup[-2]
            dt = tup[-2]
            dtl = tup[-3]
        if dtl:
            etmdt = parse_str(dtl, hsh['z'], fmt=rfmt)
            if etmdt is None:
                etmdt = ""
        else:
            etmdt = ''

        try:
            item = (cols.format(*eval_fmts)).split('::')
        except:
            logger.exception("eval_fmts: {0}".format(*eval_fmts))

        if grpby['report'] == 'c':
            if fmts.count(u"hsh['t']"):
                position = fmts.index(u"hsh['t']")
                for tag in hsh['t']:
                    rowcpy = deepcopy(item)
                    rowcpy[position] = tag
                    rowcpy.append(
                        (tup[-1], tup[-4],
                         setSummary(hsh, parse(dtl)), dt, etmdt))
                    items.append(rowcpy)
            else:
                item.append((tup[-1], tup[-4],
                             setSummary(hsh, parse(dtl)), dt, etmdt))
                items.append(item)
        else:  # action report
            summary = format(setSummary(hsh, parse(dt)))
            item.append("{0}!!{1}!!".format(summary, uuid))
            temp = []
            temp.extend(timeValue(hsh, options))
            temp.extend(expenseCharge(hsh, options))
            item.append(temp)
            items.append(item)
    if grpby['report'] == 'c' and not export:
        tree = makeTree(items, sort=False)
        return tree
    else:
        if grpby['report'] == 'a' and 'depth' in grpby and grpby['depth']:
            depth = min(grpby['depth']-1, len(grpby['lst']))
        else:
            depth = len(grpby['lst'])
        logger.debug('using depth: {0}'.format(depth))
        if export:
            data = []
            head = [x for x in grpby['lst'][:depth]]
            logger.debug('head: {0}\nlst: {1}\ndepth: {2}'.format(head, grpby['lst'], depth))
            if grpby['report'] == 'c':
                for row in items:
                    tup = ['"{0}"'.format(x) for x in row.pop(-1)[2:6]]
                    row.extend(tup)
                    data.append(row)
            else:
                head.extend(['minutes', 'value', 'expense', 'charge'])
                data.append(head)
                lst = tallyByGroup(
                    items, max_level=depth, options=options, export=True)
                for row in lst:
                    tup = [x for x in list(row.pop(-1))]
                    row.extend(tup)
                    data.append(row)
            return data
        else:
            res = tallyByGroup(items, max_level=depth, options=options)
            return res


def str2hsh(s, uid=None, options=None):
    if not options:
        options = {}
    msg = []
    try:
        hsh = {}
        alerts = []
        at_parts = at_regex.split(s)
        # logger.debug('at_parts: {0}'.format(at_parts))
        head = at_parts.pop(0).strip()
        if head and head[0] in type_keys:
            itemtype = unicode(head[0])
            summary = head[1:].strip()
        else:
            # in basket
            itemtype = u'$'
            summary = head
        hsh['itemtype'] = itemtype
        hsh['_summary'] = summary
        if uid:
            hsh['I'] = uid
        if itemtype == u'+':
            hsh['_group_summary'] = summary
        hsh['entry'] = s
        for at_part in at_parts:
            at_key = unicode(at_part[0])
            at_val = at_part[1:].strip()
            if itemtype not in key2type[at_key]:
                msg.append("An entry for @{0} is not allowed in items of type '{1}'.".format(at_key, itemtype))
                continue
            if at_key == 'a':
                actns = options['alert_default']
                arguments = []
                # alert_parts = at_val.split(':', maxsplit=1)
                alert_parts = re.split(':', at_val, maxsplit=1)
                t_lst = alert_parts.pop(0).split(',')
                periods = []
                for x in t_lst:
                    p = parse_period(x)
                    if type(p) is timedelta:
                        periods.append(p)
                    else:
                        msg.append(p)
                periods = tuple(periods)
                triggers = [x for x in periods]
                if alert_parts:
                    action_parts = [
                        x.strip() for x in alert_parts[0].split(';')]
                    actns = [
                        unicode(x.strip()) for x in
                        action_parts.pop(0).split(',')]
                    if action_parts:
                        arguments = []
                        for action_part in action_parts:
                            tmp = action_part.split(',')
                            arguments.append(tmp)
                alerts.append([triggers, actns, arguments])
            elif at_key in ['+', '-', 'i', 'n']:
                parts = comma_regex.split(at_val)
                tmp = []
                for part in parts:
                    tmp.append(part)
                hsh[at_key] = tmp
            elif at_key in ['r', 'j']:
                amp_parts = amp_regex.split(at_val)
                part_hsh = {}
                this_key = unicode(amp_hsh.get(at_key, at_key))
                amp_0 = amp_parts.pop(0)
                part_hsh[this_key] = amp_0
                for amp_part in amp_parts:
                    amp_key = unicode(amp_part[0])
                    amp_val = amp_part[1:].strip()
                    if amp_key in ['q', 'i', 't']:
                        try:
                            part_hsh[amp_key] = int(amp_val)
                        except ValueError:
                            msg.append('"&{0} {1}" is invalid - a positive integer is required.'.format(amp_key, amp_val))
                            logger.exception('Bad entry "{0}" given for "&{1}" in "{2}". An integer is required.'.format(amp_val, amp_key, hsh['entry']))
                        else:
                            if part_hsh[amp_key] < 1:
                                msg.append('"&{0} {1}" is invalid - a positive integer is required.'.format(amp_key, amp_val))

                    elif amp_key == 'e':
                        p = parse_period(amp_val)
                        if type(p) is timedelta:
                            part_hsh['e'] = p
                        else:
                            msg.append(p)
                    else:
                        m = range_regex.search(amp_val)
                        if m:
                            if m.group(3):
                                part_hsh[amp_key] = [
                                    x for x in range(
                                        int(m.group(1)),
                                        int(m.group(3)))]
                            else:
                                part_hsh[amp_key] = range(int(m.group(1)))
                        # value will be a scalar or list
                        elif comma_regex.search(amp_val):
                            part_hsh[amp_key] = comma_regex.split(amp_val)
                        else:
                            part_hsh[amp_key] = amp_val
                try:
                    hsh.setdefault("%s" % at_key, []).append(part_hsh)
                except:
                    msg.append("error appending '%s' to hsh[%s]" %
                               (part_hsh, at_key))
            else:
                # value will be a scalar or list
                if at_key in ['a', 't']:
                    if comma_regex.search(at_val):
                        hsh[at_key] = [
                            x for x in comma_regex.split(at_val) if x]
                    else:
                        hsh[at_key] = [at_val]
                elif at_key == 's':
                    # we'll parse this after we get the timezone
                    hsh['s'] = at_val
                elif at_key == 'k':
                    hsh['k'] = ":".join([x.strip() for x in at_val.split(':')])
                elif at_key == 'e':
                    p = parse_period(at_val)
                    if type(p) is timedelta:
                        hsh['e'] = p
                    else:
                        msg.append(p)

                elif at_key == 'p':
                    hsh['p'] = int(at_val)
                    if hsh['p'] <= 0 or hsh['p'] >= 10:
                        hsh['p'] = 10
                else:
                    hsh[at_key] = at_val
        if alerts:
            hsh['_a'] = alerts
        if 'z' not in hsh:
            if 's' in hsh or 'f' in hsh or 'q' in hsh:
                hsh['z'] = options['local_timezone']
        if 'z' in hsh:
            z = gettz(hsh['z'])
            if z is None:
                msg.append("error: bad timezone: '%s'" % hsh['z'])
                hsh['z'] = ''
        if 's' in hsh:
            dt = parse_str(hsh['s'], hsh['z'])
            if type(dt) is datetime:
                hsh['s'] = dt.replace(tzinfo=None)
            else:
                msg.append(dt)
        if 'q' in hsh:
            try:
                hsh['q'] = parse_str(hsh['q'], hsh['z']).replace(tzinfo=None)
            except:
                err = "error: could not parse '@q {0}'".format(hsh['q'])
                msg.append(err)
        if '+' in hsh:
            tmp = []
            for part in hsh['+']:
                r = parse_str(part, hsh['z']).replace(tzinfo=None)
                tmp.append(r)
            hsh['+'] = tmp
        if '-' in hsh:
            tmp = []
            for part in hsh['-']:
                r = parse_str(part, hsh['z']).replace(tzinfo=None)
                tmp.append(r)
            hsh['-'] = tmp
        if 'b' in hsh:
            try:
                hsh['b'] = int(hsh['b'])
            except:
                msg.append(
                    '"@b {0}" is invalid - a positive integer is required'.format(hsh['b']))
            else:
                if hsh['b'] < 1:
                    msg.append(
                        '"@b {0}" is invalid - a positive integer is required'.format(hsh['b']))

        if 'f' in hsh:
            # this will be a list of done:due pairs
            # 20120201T1325;20120202T1400, ...
            # logger.debug('hsh["f"]: {0}'.format(hsh['f']))
            pairs = [x.strip() for x in hsh['f'].split(',') if x.strip()]
            # logger.debug('pairs: {0}'.format(pairs))
            hsh['f'] = []
            for pair in pairs:
                pair = pair.split(';')
                done = parse_str(
                        pair[0], hsh['z']).replace(tzinfo=None)
                if len(pair) > 1:
                    due = parse_str(pair[1], hsh['z']).replace(tzinfo=None)
                else:
                    due = done
                    # logger.debug("appending {0} to {1}".format(done, hsh['entry']))
                hsh['f'].append((done, due))
        if 'h' in hsh:
            # this will be a list of done:due pairs
            # 20120201T1325;20120202T1400, ...
            # logger.debug('hsh["f"]: {0}'.format(hsh['f']))
            pairs = [x.strip() for x in hsh['h'].split(',') if x.strip()]
            # logger.debug('pairs: {0}'.format(pairs))
            hsh['h'] = []
            for pair in pairs:
                pair = pair.split(';')
                done = parse_str(
                        pair[0], hsh['z']).replace(tzinfo=None)
                if len(pair) > 1:
                    due = parse_str(
                            pair[1], hsh['z']).replace(tzinfo=None)
                else:
                    due = done
                    # logger.debug("appending {0} to {1}".format(done, hsh['entry']))
                hsh['h'].append((done, due))
        if 'j' in hsh:
            for i in range(len(hsh['j'])):
                job = hsh['j'][i]
                if 'q' not in job:
                    msg.append("@j: %s" % job['j'])
                    msg.append("an &q entry is required for jobs")
                if 'f' in job:
                    if 'z' not in hsh:
                        hsh['z'] = options['local_timezone']

                    pair = job['f'].split(';')
                    done = parse_str(
                            pair[0], hsh['z']).replace(tzinfo=None)
                    if len(pair) > 1:
                        due = parse_str(
                                pair[1], hsh['z']).replace(tzinfo=None)
                    else:
                        due = ''

                    job['f'] = [(done, due)]

                if 'h' in job:
                    # this will be a list of done:due pairs
                    # 20120201T1325;20120202T1400, ...
                    logger.debug("job['h']: {0}, {1}".format(job['h'], type(job['h'])))
                    if type(job['h']) is str:
                        pairs = job['h'].split(',')
                    else:
                        pairs = job['h']
                    logger.debug('starting pairs: {0}, {1}'.format(pairs, type(pairs)))
                    job['h'] = []
                    # if type(pairs) in [unicode, str]:
                    if type(pairs) not in [list]:
                        pairs = [pairs]
                    for pair in pairs:
                        logger.debug('splitting pair: {0}'.format(pair))
                        pair = pair.split(';')
                        logger.debug('processing done, due: {0}'.format(pair))
                        done = parse_str(
                                pair[0], hsh['z']).replace(tzinfo=None)
                        if len(pair) > 1:
                            logger.debug('parsing due: {0}, {1}'.format(pair[1], type(pair[1])))
                            due = parse_str(
                                    pair[1], hsh['z']).replace(tzinfo=None)
                        else:
                            due = done
                        logger.debug("appending ({0}, {1}) to {2} ".format(done, due, job['j']))
                        job['h'].append((done, due))
                        logger.debug("job['h']: {0}".format(job['h']))
                # put the modified job back in the hash
                    hsh['j'][i] = job
        for k, v in hsh.items():
            if type(v) in [datetime, timedelta]:
                pass
            elif k == 's':
                pass
            elif type(v) in [list, int, tuple]:
                hsh[k] = v
            else:
                hsh[k] = v.strip()
        if 'r' in hsh:
            if hsh['r'] == 'l':
                # list only with no '&' fields
                hsh['r'] = {'f': 'l'}
                # skip one time and handle with finished, begin and pastdue
        msg.extend(checkhsh(hsh))
        if msg:
            return hsh, msg
        if 'p' in hsh:
            hsh['_p'] = hsh['p']
        else:
            hsh['_p'] = 10
        if 'a' in hsh:
            hsh['_a'] = hsh['a']
        if 'j' in hsh:
            hsh['_j'] = hsh['j']
        if 'r' in hsh:
            hsh['_r'] = hsh['r']
            try:
                hsh['r'] = get_rrulestr(hsh)
            except:
                msg.append("exception processing rulestring: %s" % hsh['_r'])
            try:
                hsh['r'], hsh['rrule'], warn = get_rrule(hsh)
                if warn:
                    msg.extend(warn)
            except:
                logger.exception("exception processing rrule: {0}".format(hsh['_r']))
        if 'I' not in hsh:
            hsh['I'] = uniqueId()

    except:
        logger.exception('exception processing "{0}"'.format(s))
        msg.append('exception processing "{0}"'.format(s))
    return hsh, msg


def expand_template(template, hsh, lbls=None, complain=False):
    if not lbls:
        lbls = {}
    marker = '!'
    if hsh and "_summary" in hsh and "summary" not in hsh:
        hsh["summary"] = hsh["_summary"]

    def lookup(w):
        if w == '':
            return marker
        l1, l2 = lbls.get(w, ('', ''))
        v = hsh.get(w, None)
        if template.startswith("mailto"):
            v = quote(v)
        if v is None:
            if complain:
                return w
            else:
                return ''
        if type(v) in [str, unicode]:
            return "%s%s%s" % (l1, v, l2)
        if type(v) == datetime:
            return "%s%s%s" % (l1, v.strftime("%a %b %d, %Y %H:%M"), l2)
        return "%s%s%s" % (l1, repr(v), l2)

    parts = template.split(marker)
    parts[1::2] = map(lookup, parts[1::2])
    s = ''.join(parts).strip()
    return blank_lines_regex.sub('', s)



def getToday():
    return datetime.today().strftime(sortdatefmt)


def getCurrentDate():
    return datetime.today().strftime(reprdatefmt)


last_added = None


def add2list(l, item, expand=True):
    """Add item to l if not already present using bisect to maintain order."""
    global last_added
    if expand and len(item) == 3 and type(item[1]) is tuple:
        # this is a tree entry, so we need to expand the middle tuple
        # for makeTree
        try:
            entry = [item[0]]
            entry.extend(list(item[1]))
            entry.append(item[2])
            item = entry
        except:
            logger.exception('error expanding: {0}'.formt(item))
            return ()
    try:
        # i = bisect.bisect_left(name2list[l], item)
        name2SL[l].insert(item)
    except:
        logger.exception("error adding:\n{0}\n\n    last added:\n{1}".format(item, last_added))
        return ()

    return True


def removeFromlist(l, item, expand=True):
    """Add item to l if not already present using bisect to maintain order."""
    global last_added
    if expand and len(item) == 3 and type(item[1]) is tuple:
        # this is a tree entry, so we need to expand the middle tuple
        # for makeTree
        try:
            entry = [item[0]]
            entry.extend(list(item[1]))
            entry.append(item[2])
            item = entry
        except:
            logger.exception('error expanding: {0}'.formt(item))
            return ()
    try:
        name2SL[l].remove(item)
    except:
        logger.exception("error adding:\n{0}\n\n    last added:\n{1}".format(item, last_added))
        return ()
    return True


def getPrevNext(l, cal_regex):
    result = []
    seen = []
    # remove duplicates
    for xx in l:
        if cal_regex and not cal_regex.match(xx[1]):
            continue
        x = xx[0].date()
        i = bisect.bisect_left(seen, x)
        if i == len(seen) or seen[i] != x:
            seen.insert(i, x)
            result.append(x)
    l = result

    prevnext = {}
    if not l:
        return {}
    aft = l[0]
    bef = l[-1]
    d = aft
    prev = 0
    nxt = len(l) - 1
    last_prev = 0
    while d <= bef:
        i = bisect.bisect_left(l, d)
        j = bisect.bisect_right(l, d)
        if i != len(l) and l[i] == d:
            # d is in the list
            last_prev = i
            curr = i
            prev = max(0, i - 1)
            nxt = min(len(l) - 1, j)
        else:
            # d is not in the list
            curr = last_prev
            prev = last_prev
        prevnext[d] = [l[prev], l[curr], l[nxt]]
        d += ONEDAY
    return prevnext


def get_changes(options, file2lastmodified):
    new = []
    deleted = []
    modified = []
    prefix, filelist = getFiles(options['datadir'])
    for f, r in filelist:
        if (f, r) not in file2lastmodified:
            new.append((f, r))
        elif os.path.getmtime(f) != file2lastmodified[(f, r)]:
            logger.debug('mtime: {0}; lastmodified: {1}'.format(os.path.getmtime(f), file2lastmodified[(f, r)]))
            modified.append((f, r))
    for (f, r) in file2lastmodified:
        if (f, r) not in filelist:
            deleted.append((f, r))
    return new, modified, deleted


def get_data(options=None):
    if not options:
        options = {}
    bad_datafiles = []
    (uuid2hash, uuid2labels, file2uuids, file2lastmodified, bad_datafiles, messages) = process_all_datafiles(options)
    if bad_datafiles:
        logger.warn("bad data files: {0}".format(bad_datafiles))
    return uuid2hash, uuid2labels, file2uuids, file2lastmodified, bad_datafiles, messages


def expandPath(path):
    path, ext = os.path.splitext(path)
    folders = []
    while 1:
        path, folder = os.path.split(path)
        if folder != "":
            folders.append(folder)
        else:
            if path != "":
                folders.append(path)
            break
    folders.reverse()
    return folders


# noinspection PyArgumentList
def getDoneAndTwo(hsh, keep=False):
    if hsh['itemtype'] not in ['+', '-', '%']:
        return
    done = None
    nxt = None
    following = None
    if 'z' in hsh:
        today_datetime = datetime.now(gettz(hsh['z'])).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    else:
        today_datetime = get_current_time()
    if 'f' in hsh and hsh['f']:
        if type(hsh['f']) in [str, unicode]:
            parts = str(hsh['f']).split(';')
            done = parse_str(parts[0], hsh['z']).replace(tzinfo=None)
            if len(parts) < 2:
                due = done
            else:
                due = parse_str(parts[1], hsh['z']).replace(tzinfo=None)
        elif type(hsh['f'][-1]) in [list, tuple]:
            done, due = hsh['f'][-1]
        else:
            done = hsh['f'][-1]
            due = done
        k_aft = due
        k_inc = False
        r_aft = done
        r_inc = False
        if due and due < today_datetime:
            s_aft = today_datetime
            s_inc = True
        else:
            s_aft = due
            s_inc = False
    else:
        if 's' in hsh:
            k_aft = r_aft = hsh['s']
        else:
            k_aft = r_aft = today_datetime
        k_inc = r_inc = True
        s_aft = today_datetime
        s_inc = True

    if 'rrule' in hsh:
        nxt = None
        if keep or 'o' not in hsh or hsh['o'] == 'k':
            # keep
            if k_aft:
                nxt = hsh['rrule'].after(k_aft, k_inc)
        elif hsh['o'] == 'r':
            # restart
            if r_aft:
                nxt = hsh['rrule'].after(r_aft, r_inc)
        elif hsh['o'] == 's':
            # skip
            if s_aft:
                nxt = hsh['rrule'].after(s_aft, s_inc)
        if nxt:
            following = hsh['rrule'].after(nxt, False)
    elif 's' in hsh and hsh['s']:
        if 'f' in hsh:
            nxt = None
        else:
            nxt = parse_str(hsh['s'], hsh['z']).replace(tzinfo=None)
    return done, nxt, following


def timeValue(hsh, options):
    """
        Return rounded integer minutes and float value.
    """
    minutes = value = 0
    if 'e' not in hsh or hsh['e'] <= ONEMINUTE * 0:
        return 0, 0.0
    td_minutes = hsh['e'].seconds // 60 + (hsh['e'].seconds % 60 > 0)

    a_m = int(options['action_minutes'])
    if a_m not in [1, 6, 12, 15, 30, 60]:
        a_m = 1
    minutes = ((td_minutes // a_m + (td_minutes % a_m > 0)) * a_m)

    if 'action_rates' in options:
        if 'v' in hsh and hsh['v'] in options['action_rates']:
            rate = float(options['action_rates'][hsh['v']])
        elif 'default' in options['action_rates']:
            rate = float(options['action_rates']['default'])
        else:
            rate = 0.0
        value = rate * (minutes / 60.0)
    else:
        value = 0.0
    return minutes, value


def expenseCharge(hsh, options):
    expense = charge = 0.0
    rate = 1.0
    if 'x' in hsh:
        expense = charge = float(hsh['x'])
        if 'action_markups' in options:
            if 'w' in hsh and hsh['w'] in options['action_markups']:
                rate = float(options['action_markups'][hsh['w']])
            elif 'default' in options['action_markups']:
                rate = float(options['action_markups']['default'])
            else:
                rate = 1.0
            charge = rate * expense
    return expense, charge


def timedelta2Str(td, short=False):
    """
    """
    if td <= ONEMINUTE * 0:
        return 'none'
    until = []
    td_days = td.days
    td_hours = td.seconds // (60 * 60)
    td_minutes = (td.seconds % (60 * 60)) // 60
    if short:
        # drop the seconds part
        return "+%s" % str(td)[:-3]

    if td_days:
        if td_days == 1:
            days = _("day")
        else:
            days = _("days")
        until.append("%d %s" % (td_days, days))
    if td_hours:
        if td_hours == 1:
            hours = _("hour")
        else:
            hours = _("hours")
        until.append("%d %s" % (td_hours, hours))
    if td_minutes:
        if td_minutes == 1:
            minutes = _("minute")
        else:
            minutes = _("minutes")
        until.append("%d %s" % (td_minutes, minutes))
    return " ".join(until)


def timedelta2Sentence(td):
    string = timedelta2Str(td)
    if string == 'none':
        return _("now")
    else:
        return _("{0} from now").format(string)


def add_busytime(key, sm, em, evnt_summary, uid, rpth):
    """
    key = (year, weeknum, weekdaynum with Monday=1, Sunday=7)
    value = [minute_total, list of (uid, start_minute, end_minute)]
    """
    # key = tuple(sd.isocalendar())  # year, weeknum, weekdaynum
    entry = (sm, em, evnt_summary, uid, rpth)
    # logger.debug("adding busytime: {0}; {1}".format(key, evnt_summary))
    busytimesSL.setdefault(key, IndexableSkiplist(2000, "busytimes")).insert(entry)


def remove_busytime(key, bt):
    """
    key = (year, weeknum, weekdaynum with Monday=1, Sunday=7)
    value = [minute_total, list of (uid, start_minute, end_minute)]
    """
    busytimesSL[key].remove(bt)


def add_occasion(key, evnt_summary, uid, f):
    # key = tuple(sd.isocalendar())  # year, weeknum, weekdaynum
    # logger.debug("adding occasion: {0}; {1}".format(key, evnt_summary))
    occasionsSL.setdefault(key, IndexableSkiplist(1000, "occasions")).insert((evnt_summary, uid, f))


def remove_occasion(key, oc):  # sd, evnt_summary, uid, f):
    # logger.debug("removing occasion: {0}, {1}".format(key, oc))
    occasionsSL[key].remove(oc)


def setSummary(hsh, dt):
    if not dt:
        return hsh['_summary']
    # logger.debug("dt: {0}".format(dt))
    mtch = anniversary_regex.search(hsh['_summary'])
    retval = hsh['_summary']
    if mtch:
        startyear = mtch.group(1)
        numyrs = year2string(startyear, dt.year)
        retval = anniversary_regex.sub(numyrs, hsh['_summary'])
    return retval


def setItemPeriod(hsh, start, end, short=False, options=None):
    if not options:
        options = {}
    sy = start.year
    ey = end.year
    sm = start.month
    em = end.month
    sd = start.day
    ed = end.day
    if start == end:  # same time - zero extent
        if short:
            period = "%s" % fmt_time(start, options=options)
        else:
            period = "%s %s" % (
                fmt_time(start, options=options), fmt_date(start, True))
    elif (sy, sm, sd) == (ey, em, ed):  # same day
        if short:
            period = "%s - %s" % (
                fmt_time(start, options=options),
                fmt_time(end, options=options))
        else:
            period = "%s - %s %s" % (
                fmt_time(start, options=options),
                fmt_time(end, options=options),
                fmt_date(end, True))
    else:
        period = "%s %s - %s %s" % (
            fmt_time(start, options=options), fmt_date(start, True),
            fmt_time(end, options=options), fmt_date(end, True))
    return period


def getDataFromFile(f, file2data, bef, file2uuids=None, uuid2hash=None, options=None):
    if not options:
        options = {}
    if file2data is None:
        file2data = {}
    if not file2uuids:
        file2uuids = {}
    if not uuid2hash:
        uuid2hash = {}
    today_datetime = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0)
    today_date = datetime.now().date()
    yearnum, weeknum, daynum = today_date.isocalendar()
    items = []       # [(view, sort(3|4), fn), (branches), (leaf)]
    datetimes = []
    busytimes = []
    occasions = []
    alerts = []
    alert_minutes = {}
    folders = expandPath(f)
    pastduerepeating = []
    for uid in file2uuids[f]:
        # this will give the items in file order!
        if uuid2hash[uid]['itemtype'] in ['=']:
            continue
        sdt = ""
        hsh = {}
        for k, v in uuid2hash[uid].items():
            hsh[k] = v
            # we'll make anniversary subs to a copy later
        hsh['summary'] = hsh['_summary']
        typ = type2Str[hsh['itemtype']]
        # we need a context for due view and a keyword for keyword view

        if hsh['itemtype'] != '#':
            if 'c' not in hsh:
                if 's' not in hsh and hsh['itemtype'] in [u'+', u'-', u'%']:
                    # undated task
                    hsh['c'] = NONE
                else:
                    hsh['c'] = NONE

            if 'k' not in hsh:
                hsh['k'] = NONE

            if 't' not in hsh:
                hsh['t'] = [NONE]

        # make task entries for day, keyword and folder view
        if hsh['itemtype'] in [u'+', u'-', u'%']:
            done, due, following = getDoneAndTwo(hsh)
            hist_key = 'f'
            if hsh['itemtype'] == '+' and 'h' in hsh:
                hist_key = 'h'
            if done:
                # add the last show_finished completions to day and keywords
                # dts = done.strftime(sortdatefmt)
                # sdt = fmt_date(hsh['f'][-1][0], True)
                sdt = fmt_date(hsh['f'][-1][0], True)
                typ = 'fn'
                # add a finished entry to day view
                # only show the last 'show_finished' completions
                for d0, d1 in hsh[hist_key][-options['show_finished']:]:
                    if 'n' not in hsh or 'd' not in hsh['n']:
                        item = [
                            ('day', d0.strftime(sortdatefmt),
                             tstr2SCI[typ][0], hsh['_p'], '', f),
                            (fmt_date(d0, short=True), ),
                            (uid, typ, setSummary(hsh, d0), '', d0)]
                        items.append(item)
                        datetimes.append((d0, f))
                    if 'k' in hsh:
                        if 'n' not in hsh or 'k' not in hsh['n']:
                            keywords = [x.strip() for x in hsh['k'].split(':')]
                            item = [
                                ('keyword', (hsh['k'], tstr2SCI[typ][0]),
                                 d0, hsh['_summary'], f), tuple(keywords),
                                (uid, typ,
                                 setSummary(hsh, d0), fmt_date(d0, True), d0)]
                            items.append(item)

                if not due:
                    # add the last completion to folder view
                    item = [
                        ('folder', (f, tstr2SCI[typ][0]), done,
                         hsh['_summary'], f), tuple(folders),
                        (uid, typ, setSummary(hsh, done), sdt, done)]
                    items.append(item)

            if due:
                # add a due entry to folder view
                dtl = due
                # dts = due.strftime(sortdatefmt)
                sdt = fmt_date(due, True)
                time_diff = (due - today_datetime).days
                if time_diff >= 0:
                    time_str = sdt
                    pastdue = False
                else:
                    if time_diff > -99:
                        time_str = '%s: %dd' % (sdt, time_diff)
                    else:
                        time_str = sdt
                    pastdue = True
                time_str = leadingzero.sub('', time_str)

                if hsh['itemtype'] == '%':
                    if pastdue:
                        typ = 'pd'
                    else:
                        typ = 'ds'
                elif hsh['itemtype'] == '-':
                    if pastdue:
                        typ = 'pt'
                    else:
                        typ = 'av'
                else:
                    # group
                    if 'prereqs' in hsh and hsh['prereqs']:
                        if pastdue:
                            typ = 'pu'
                        else:
                            typ = 'cu'
                    else:
                        if pastdue:
                            typ = 'pc'
                        else:
                            typ = 'cs'
                item = [
                    ('folder', (f, tstr2SCI[typ][0]), due,
                     hsh['_summary'], f), tuple(folders),
                    (uid, typ, setSummary(hsh, due), time_str, dtl)]
                items.append(item)
                if 'k' in hsh and hsh['itemtype'] != '#':
                    if 'n' not in hsh or 'k' not in hsh['n']:
                        keywords = [x.strip() for x in hsh['k'].split(':')]
                        item = [
                            ('keyword', (hsh['k'], tstr2SCI[typ][0]),
                             due, hsh['_summary'], f), tuple(keywords),
                            (uid, typ,
                             setSummary(hsh, due), time_str, dtl)]
                        items.append(item)
                if 't' in hsh and hsh['itemtype'] != "#":
                    if 'n' not in hsh or 't' not in hsh['n']:
                        for tag in hsh['t']:
                            item = [
                                ('tag', (tag, tstr2SCI[typ][0]), due,
                                 hsh['_summary'], f), (tag,),
                                (uid, typ,
                                 setSummary(hsh, due), time_str, dtl)]
                            items.append(item)
            if not due and not done:  # undated
                # dts = "none"
                dtl = today_datetime
                extstr = ""
                exttd = ""
                if 'q' in hsh and type(hsh['q']) is datetime:
                    # extstr = exttd = fmt_datetime(hsh['q'], options=options)
                    dtl = hsh['q']
                    exttd = hsh['q'] - datetime.now()
                    extstr = fmt_period(abs(exttd), short=True)
                item = [
                    ('folder', (f, tstr2SCI[typ][0]), '',
                     hsh['_summary'], f),
                    tuple(folders),
                    (uid, typ, setSummary(hsh, ''), extstr)]
                items.append(item)

                if 'k' in hsh and hsh['itemtype'] != "#":
                    if 'n' not in hsh or 'k' not in hsh['n']:
                        keywords = [x.strip() for x in hsh['k'].split(':')]
                        item = [
                            ('keyword', (hsh['k'], tstr2SCI[typ][0]), dtl,
                             hsh['_summary'], f), tuple(keywords),
                            (uid, typ, setSummary(hsh, ''), extstr, dtl)]
                        items.append(item)
                if 't' in hsh and hsh['itemtype'] != "#":
                    if 'n' not in hsh or 't' not in hsh['n']:
                        for tag in hsh['t']:
                            item = [
                                ('tag', (tag, tstr2SCI[typ][0]), dtl,
                                 hsh['_summary'], f), (tag,),
                                (uid, typ, setSummary(hsh, ''), extstr, dtl)]
                            items.append(item)

        else:  # not a task type
            if 's' in hsh:
                if 'rrule' in hsh:
                    if hsh['itemtype'] in [u'^', u'*', u'~']:
                        dt = (
                            hsh['rrule'].after(today_datetime, inc=True)
                            or hsh['rrule'].before(
                                today_datetime, inc=True))
                    else:
                        dt = hsh['rrule'].after(hsh['s'], inc=True)
                else:
                    dt = parse_str(hsh['s'], hsh['z']).replace(tzinfo=None)
                    # dt = hsh['s'].replace(tzinfo=None)
            else:
                dt = None
                # dts = "none"
                sdt = ""

            if dt:
                if hsh['itemtype'] == '*':
                    sdt = fmt_shortdatetime(dt, options=options)
                elif hsh['itemtype'] == '~':
                    if 'e' in hsh:
                        sd = fmt_date(dt, True)
                        sd = leadingzero.sub('', sd)
                        sdt = "%s: %s" % (
                            sd,
                            fmt_period(hsh['e'])
                        )
                    else:
                        sdt = ""
                else:
                    # sdt = fmt_date(dt, True)
                    # sdt = leadingzero.sub('', fmt_date(dt, True)),
                    sdt = fmt_date(dt, True)
                    sdt = leadingzero.sub('', sdt)
            else:
                dt = today_datetime

            if hsh['itemtype'] == '*':
                if 'e' in hsh and hsh['e']:
                    typ = 'ev'
                else:
                    typ = 'rm'
            else:
                typ = type2Str[hsh['itemtype']]
            item = [
                ('folder', (f, tstr2SCI[typ][0]), dt,
                 hsh['_summary'], f), tuple(folders),
                (uid, typ, setSummary(hsh, dt), sdt, dt)]
            items.append(item)
            if 'k' in hsh and hsh['itemtype'] != "#":
                keywords = [x.strip() for x in hsh['k'].split(':')]
                item = [
                    ('keyword', (hsh['k'], tstr2SCI[typ][0]), dt,
                     hsh['_summary'], f), tuple(keywords),
                    (uid, typ, setSummary(hsh, dt), sdt, dt)]
                items.append(item)
            if 't' in hsh and hsh['itemtype'] != "#":
                for tag in hsh['t']:
                    item = [
                        ('tag', (tag, tstr2SCI[typ][0]), dt,
                         hsh['_summary'], f), (tag,),
                        (uid, typ, setSummary(hsh, dt), sdt, dt)]
                    items.append(item)
            if hsh['itemtype'] == '#':
                # don't include hidden items in any other views
                continue
        # could be anything
        # make in basket and someday entries #
        # sort numbers for now view --- we'll add the typ num to
        if hsh['itemtype'] == '$':
            item = [
                ('inbasket', (0, tstr2SCI['ib'][0]), dt,
                 hsh['_summary'], f),
                (uid, 'ib', setSummary(hsh, dt), sdt, dt)]
            items.append(item)
            continue
        if hsh['itemtype'] == '?':
            item = [
                ('someday', 2, (tstr2SCI['so'][0]), dt,
                 hsh['_summary'], f),
                (uid, 'so', setSummary(hsh, dt), sdt, dt)]
            items.append(item)
            continue
        if hsh['itemtype'] == '!':
            if not ('k' in hsh and hsh['k']):
                hsh['k'] = _("none")
            keywords = [x.strip() for x in hsh['k'].split(':')]
            item = [
                ('note', (hsh['k'], tstr2SCI[typ][0]), '',
                 hsh['_summary'], f), tuple(keywords),
                (uid, typ, setSummary(hsh, ''), '', dt)]
            items.append(item)
        # make entry for next view
        if 's' not in hsh and hsh['itemtype'] in [u'+', u'-', u'%']:
            if 'f' in hsh:
                continue
            if 'q' in hsh and type(hsh['q']) is datetime:
                # extstr = exttd = fmt_datetime(hsh['q'], options=options)
                exttd = hsh['q'] - datetime.now()
                extstr = fmt_period(abs(exttd), short=True)
                # extstr = exttd = hsh['q'].strftime(zfmt)
            elif 'e' in hsh and hsh['e'] is not None:
                extstr = fmt_period(hsh['e'])
                exttd = hsh['e']
            else:
                extstr = ''
                exttd = 0 * ONEDAY
            if hsh['itemtype'] == '+':
                if 'prereqs' in hsh and hsh['prereqs']:
                    typ = 'cu'
                else:
                    typ = 'cs'
            elif hsh['itemtype'] == '%':
                typ = 'du'
            else:
                typ = type2Str[hsh['itemtype']]
            if 'n' not in hsh or 'd' not in hsh['n']:
                item = [
                    ('next', (1, hsh['c'], hsh['_p'], exttd),
                     tstr2SCI[typ][0], hsh['_p'], hsh['_summary'], f),
                    (hsh['c'],), (uid, typ, hsh['_summary'], extstr)]
                items.append(item)
            continue
        # make entries for day view and friends
        dates = []
        if 'rrule' in hsh:
            gotall, dates = get_reps(bef, hsh)
            for date in dates:
                # add2list("datetimes", (date, f))
                datetimes.append((date, f))

        elif 's' in hsh and hsh['s'] and 'f' not in hsh:
            thisdate = parse_str(hsh['s'], hsh['z']).astimezone(
                tzlocal()).replace(tzinfo=None)
            dates.append(thisdate)
            # add2list("datetimes", (thisdate, f))
            datetimes.append((thisdate, f))
        for dt in dates:
            dtl = dt
            sd = dtl.date()
            st = dtl.time()
            if typ == 'oc':
                st_fmt = ''
            else:
                st_fmt = fmt_time(st, options=options)
            alertId = (hsh['_summary'], hsh['s'])
            summary = setSummary(hsh, dtl)
            tmpl_hsh = {'alertId': alertId, 'I': uid, 'summary': summary, 'start_date': fmt_date(dtl, True), 'start_time': fmt_time(dtl, True, options=options)}
            if 't' in hsh:
                tmpl_hsh['t'] = ', '.join(hsh['t'])
            else:
                tmpl_hsh['t'] = ''
            if 'e' in hsh:
                try:
                    tmpl_hsh['e'] = fmt_period(hsh['e'])
                    etl = (dtl + hsh['e'])
                except:
                    logger.exception("Could not fmt hsh['e']=%s" % hsh['e'])
            else:
                tmpl_hsh['e'] = ''
                etl = dtl
            tmpl_hsh['time_span'] = setItemPeriod(
                hsh, dtl, etl, options=options)
            tmpl_hsh['busy_span'] = setItemPeriod(
                hsh, dtl, etl, True, options=options)
            for k in ['c', 'd', 'i', 'k', 'l', 'm', 'uid', 'z']:
                if k in hsh:
                    tmpl_hsh[k] = hsh[k]
                else:
                    tmpl_hsh[k] = ''
            if '_a' in hsh and hsh['_a']:
                for alert in hsh['_a']:
                    time_deltas, acts, arguments = alert
                    if not acts:
                        acts = options['alert_default']
                    tmpl_hsh['alert_email'] = tmpl_hsh['alert_process'] = ''
                    tmpl_hsh["_alert_action"] = acts
                    tmpl_hsh["_alert_argument"] = arguments
                    num_deltas = len(time_deltas)
                    for i in range(num_deltas):
                        td = time_deltas[i]
                        adt = dtl - td
                        if adt.date() == today_date:
                            this_hsh = deepcopy(tmpl_hsh)
                            if i == num_deltas - 1:
                                this_hsh['next_alert'] = _("This is the last alert.")
                                this_hsh['next'] = None
                            else:
                                nxt = timedelta2Str(time_deltas[i+1])
                                strt = _("starting time")
                                if nxt == 'none':
                                    this_hsh['next'] = _("at the {0}".format(strt))
                                    this_hsh['next_alert'] = _("The next alert is at the {0}.".format(strt))
                                else:
                                    this_hsh['next'] = _("{0} before the {1}".format(nxt, strt))
                                    this_hsh['next_alert'] = _("The next alert is {0} before the {1}.".format(nxt, strt))

                            this_hsh['td'] = td
                            this_hsh['at'] = adt
                            this_hsh['alert_time'] = fmt_time(
                                adt, True, options=options)
                            this_hsh['time_left'] = timedelta2Str(td)
                            this_hsh['when'] = timedelta2Sentence(td)
                            if adt.date() != dtl.date():
                                this_hsh['_event_time'] = fmt_period(td)
                            else:
                                this_hsh['_event_time'] = fmt_time(
                                    dtl, True, options=options)
                            amn = adt.hour * 60 + adt.minute
                            # we don't want ties in amn else add2list will try to sort on the hash and fail
                            if amn in alert_minutes:
                                # add 6 seconds to avoid the tie
                                alert_minutes[amn] += .1
                            else:
                                alert_minutes[amn] = amn
                            alerts.append((alert_minutes[amn], this_hsh['I'], this_hsh, f))
            if (hsh['itemtype'] in ['+', '-', '%'] and dtl < today_datetime):
                time_diff = (dtl - today_datetime).days
                if time_diff == 0:
                    time_str = fmt_period(hsh['e'])
                    pastdue = False
                else:
                    time_str = '%dd' % time_diff
                    pastdue = True
                if hsh['itemtype'] == '%':
                    if pastdue:
                        typ = 'pd'
                    else:
                        typ = 'ds'
                    cat = _('Delegated')
                    sn = (2, tstr2SCI[typ][0])
                elif hsh['itemtype'] == '-':
                    if pastdue:
                        typ = 'pt'
                    else:
                        typ = 'av'
                    cat = _('Available')
                    sn = (1, tstr2SCI[typ][0])
                else:
                    # group
                    if 'prereqs' in hsh and hsh['prereqs']:
                        if pastdue:
                            typ = 'pu'
                        else:
                            typ = 'cu'
                        cat = _('Waiting')
                        sn = (2, tstr2SCI[typ][0])
                    else:
                        if pastdue:
                            typ = 'pc'
                        else:
                            typ = 'cs'
                        cat = _('Available')
                        sn = (1, tstr2SCI[typ][0])
                if 'f' in hsh and 'rrule' not in hsh:
                    continue
                else:
                    if 'n' not in hsh or 'd' not in hsh['n']:
                        if 'rrule' in hsh and 'o' in hsh and hsh['o'] == 'r':
                            # only nag about the oldest instance
                            if uid in pastduerepeating:
                                continue
                            pastduerepeating.append(uid)
                        item = [
                            ('now', sn, dtl, hsh['_p'], summary, f), (cat,),
                            (uid, typ, summary, time_str, dtl)]
                        items.append(item)

            if 'b' in hsh:
                time_diff = (dtl - today_datetime).days
                if time_diff > 0 and time_diff <= int(hsh['b']):
                    if 'n' not in hsh or 'd' not in hsh['n']:
                        extstr = '%dd' % time_diff
                        exttd = 0 * ONEDAY
                        item = [('day',
                                 today_datetime.strftime(sortdatefmt),
                                 tstr2SCI['by'][0],
                                 # tstr2SCI[typ][0],
                                 time_diff,
                                 hsh['_p'],
                                 f),
                                (fmt_date(today_datetime, short=True),),
                                (uid, 'by', summary, extstr, dtl)]
                        items.append(item)
                        datetimes.append((today_datetime, f))

            if hsh['itemtype'] == '!':
                typ = 'ns'
                item = [
                    ('day', sd.strftime(sortdatefmt), tstr2SCI[typ][0],
                     hsh['_p'], '', f),
                    (fmt_date(dt, short=True),),
                    (uid, typ, summary, '', dtl)]
                items.append(item)
                continue
            if hsh['itemtype'] == '^':
                typ = 'oc'
                item = [
                    ('day', sd.strftime(sortdatefmt),
                     tstr2SCI[typ][0], hsh['_p'], '', f),
                    (fmt_date(dt, short=True),),
                    (uid, typ, summary, '', dtl)]
                items.append(item)
                occasions.append([sd, summary, uid, f])
                continue
            if hsh['itemtype'] == '~':
                typ = 'ac'
                if 'e' in hsh:
                    sdt = fmt_period(hsh['e'])
                else:
                    sdt = ""
                item = [
                    ('day', sd.strftime(sortdatefmt),
                     tstr2SCI[typ][0], hsh['_p'], '', f),
                    (fmt_date(dt, short=True),),
                    (uid, 'ac', summary,
                     sdt, dtl)]
                items.append(item)
                continue
            if hsh['itemtype'] == '*':
                sm = st.hour * 60 + st.minute
                ed = etl.date()
                et = etl.time()
                em = et.hour * 60 + et.minute
                evnt_summary = "%s: %s" % (tmpl_hsh['summary'], tmpl_hsh['busy_span'])
                if et != st:
                    et_fmt = " ~ %s" % fmt_time(et, options=options)
                else:
                    et_fmt = ''
                if ed > sd:
                    # this event overlaps more than one day
                    # first_min = 24*60 - sm
                    # last_min = em
                    # the first day tuple
                    item = [
                        ('day', sd.strftime(sortdatefmt),
                         tstr2SCI[typ][0], hsh['_p'],
                         st.strftime(sorttimefmt), f),
                        (fmt_date(sd, short=True),),
                        (uid, typ, summary, '%s ~ %s' %
                                            (st_fmt,
                                             options['dayend_fmt']), dtl)]
                    items.append(item)
                    busytimes.append([sd, sm, day_end_minutes, evnt_summary, uid, f])
                    sd += ONEDAY
                    i = 0
                    item_copy = []
                    while sd < ed:
                        item_copy.append([x for x in item])
                        item_copy[i][0] = list(item_copy[i][0])
                        item_copy[i][1] = list(item_copy[i][1])
                        item_copy[i][2] = list(item_copy[i][2])
                        item_copy[i][0][1] = sd.strftime(sortdatefmt)
                        item_copy[i][1][0] = fmt_date(sd, short=True)
                        item_copy[i][2][3] = '%s ~ %s' % (
                            options['daybegin_fmt'],
                            options['dayend_fmt'])
                        item_copy[i][0] = tuple(item_copy[i][0])
                        item_copy[i][1] = tuple(item_copy[i][1])
                        item_copy[i][2] = tuple(item_copy[i][2])
                        # add2list("items", item_copy[i])
                        items.append(item_copy[i])
                        busytimes.append([sd, 0, day_end_minutes, evnt_summary, uid, f])
                        sd += ONEDAY
                        i += 1
                        # the last day tuple
                    if em:
                        item_copy.append([x for x in item])
                        item_copy[i][0] = list(item_copy[i][0])
                        item_copy[i][1] = list(item_copy[i][1])
                        item_copy[i][2] = list(item_copy[i][2])
                        item_copy[i][0][1] = sd.strftime(sortdatefmt)
                        item_copy[i][1][0] = fmt_date(sd, short=True)
                        item_copy[i][2][3] = '%s%s' % (
                            options['daybegin_fmt'], et_fmt)
                        item_copy[i][0] = tuple(item_copy[i][0])
                        item_copy[i][1] = tuple(item_copy[i][1])
                        item_copy[i][2] = tuple(item_copy[i][2])
                        # add2list("items", item_copy[i])
                        items.append(item_copy[i])
                        busytimes.append([sd, 0, em, evnt_summary, uid, f])
                else:
                    # single day event or reminder
                    item = [
                        ('day', sd.strftime(sortdatefmt),
                         tstr2SCI[typ][0], hsh['_p'],
                         st.strftime(sorttimefmt), f),
                        (fmt_date(sd, short=True),),
                        (uid, typ, summary, '%s%s' % (
                            st_fmt,
                            et_fmt), dtl)]
                    items.append(item)
                    busytimes.append([sd, sm, em, evnt_summary, uid, f])
                    continue
                    # other dated items
            if (hsh['itemtype'] in ['-', '%'] and ('n' not in hsh or 'd' not in hsh['n'])) or hsh['itemtype'] in ['+']:
                if 'f' in hsh and hsh['f'] and hsh['f'][-1][1] == dtl:
                    typ = 'fn'
                else:
                    if hsh['itemtype'] == '%':
                        typ = 'ds'
                    elif hsh['itemtype'] == '+':
                        if 'prereqs' in hsh and hsh['prereqs']:
                            typ = 'cu'
                        else:
                            typ = 'cs'
                    else:
                        typ = 'av'
                sm = st.hour * 60 + st.minute
                if sm != 0:
                    ed = etl.date()
                    et = etl.time()
                    em = et.hour * 60 + et.minute

                    # make tasks with set starting times highest priority
                    hsh['_p'] = 0

                    evnt_summary = "%s: %s" % (tmpl_hsh['summary'], tmpl_hsh['busy_span'])
                    if et != st:
                        et_fmt = " ~ %s" % fmt_time(et, options=options)
                    else:
                        et_fmt = ''
                    if ed > sd:
                        # this task overlaps more than one day
                        # first_min = 24*60 - sm
                        # last_min = em
                        # the first day tuple
                        item = [
                            ('day', sd.strftime(sortdatefmt),
                             tstr2SCI[typ][0], hsh['_p'],
                             st.strftime(sorttimefmt), f),
                            (fmt_date(sd, short=True),),
                            (uid, typ, summary, '%s ~ %s' %
                                                (st_fmt,
                                                 options['dayend_fmt']), dtl)]
                        items.append(item)
                        busytimes.append([sd, sm, day_end_minutes, evnt_summary, uid, f])
                        sd += ONEDAY
                        i = 0
                        item_copy = []
                        while sd < ed:
                            item_copy.append([x for x in item])
                            item_copy[i][0] = list(item_copy[i][0])
                            item_copy[i][1] = list(item_copy[i][1])
                            item_copy[i][2] = list(item_copy[i][2])
                            item_copy[i][0][1] = sd.strftime(sortdatefmt)
                            item_copy[i][1][0] = fmt_date(sd)
                            item_copy[i][2][3] = '%s ~ %s' % (
                                options['daybegin_fmt'],
                                options['dayend_fmt'])
                            item_copy[i][0] = tuple(item_copy[i][0])
                            item_copy[i][1] = tuple(item_copy[i][1])
                            item_copy[i][2] = tuple(item_copy[i][2])
                            # add2list("items", item_copy[i])
                            items.append(item_copy[i])
                            busytimes.append([sd, 0, day_end_minutes, evnt_summary, uid, f])
                            sd += ONEDAY
                            i += 1
                            # the last day tuple
                        if em:
                            item_copy.append([x for x in item])
                            item_copy[i][0] = list(item_copy[i][0])
                            item_copy[i][1] = list(item_copy[i][1])
                            item_copy[i][2] = list(item_copy[i][2])
                            item_copy[i][0][1] = sd.strftime(sortdatefmt)
                            item_copy[i][1][0] = fmt_date(sd)
                            item_copy[i][2][3] = '%s%s' % (
                                options['daybegin_fmt'], et_fmt)
                            item_copy[i][0] = tuple(item_copy[i][0])
                            item_copy[i][1] = tuple(item_copy[i][1])
                            item_copy[i][2] = tuple(item_copy[i][2])
                            # add2list("items", item_copy[i])
                            items.append(item_copy[i])
                            busytimes.append([sd, 0, em, evnt_summary, uid, f])
                    else:
                        # single day task
                        item = [
                            ('day', sd.strftime(sortdatefmt),
                             tstr2SCI[typ][0], hsh['_p'],
                             st.strftime(sorttimefmt), f),
                            (fmt_date(sd, short=True),),
                            (uid, typ, summary, '%s%s' % (
                                st_fmt,
                                et_fmt), dtl)]
                        items.append(item)
                        busytimes.append([sd, sm, em, evnt_summary, uid, f])
                        continue
                else: # sm == 0
                    # midnight task - show extent only
                    # use 11:59pm as the sorting datetime
                    dtm = dtl + 1439 * ONEMINUTE
                    item = [
                        ('day', dtm.strftime(sortdatefmt), tstr2SCI[typ][0],
                         hsh['_p'], '', f),
                        (fmt_date(dt, short=True),),
                        (uid, typ, summary, tmpl_hsh['e'], dtl)]
                    items.append(item)
                    continue
    file2data[f] = [items, alerts, busytimes, datetimes, occasions]


# noinspection PyChainedComparisons
def getViewData(bef, file2uuids=None, uuid2hash=None, options=None, file2data=None):
    """
        Collect data on all items, apply filters later
    """
    tt = TimeIt(loglevel=2, label="getViewData")
    if not file2uuids:
        file2uuids = {}
    if not uuid2hash:
        uuid2hash = {}
    if not options:
        options = {}
    file2data = {}
    clear_all_data()
    logger.debug('calling getDataFromFile for {0} files'.format(len(file2uuids.keys())))
    for f in file2uuids:
        getDataFromFile(f, file2data, bef, file2uuids, uuid2hash, options)
    logger.debug('calling updateViewFromFile for {0} files'.format(len(file2uuids.keys())))
    for f in file2data:
        updateViewFromFile(f, file2data)
    numfiles = len(file2uuids.keys())
    numitems = len(uuid2hash.keys())
    logger.info("files: {0}\n    file items: {1}\n    view items: {2}\n    datetimes: {3}\n    alerts: {4}\n    busytimes: {5}\n    occasions: {6}".format(numfiles, numitems, len(list(itemsSL)), len(list(datetimesSL)), len(list(alertsSL)), len(busytimesSL.keys()), len(occasionsSL.keys())))
    tt.stop()
    return file2data


def updateViewFromFile(f, file2data):
    if not file2data:
        file2data = {}
    if f not in file2data:
        file2data[f] = [[], [], [], [], []]
    _items, _alerts, _busytimes, _datetimes, _occasions = file2data[f]
    # logger.debug('file: {0}'.format(f))
    for item in _items:
        # logger.debug('adding item: {0}'.format(item))
        add2list("items", item)
    for alert in _alerts:
        # logger.debug('adding alert: {0}'.format(alert))
        add2list("alerts", alert)
    for dt in _datetimes:
        # logger.debug('adding datetime: {0}'.format(dt))
        add2list("datetimes", dt)
    for bt in _busytimes:
        # logger.debug('adding busytime: {0}'.format(bt))
        sd, sm, em, evnt_summary, uid, rpth = bt
        key = sd.isocalendar()
        add_busytime(key, sm, em, evnt_summary, uid, rpth)
    for oc in _occasions:
        # logger.debug('adding occasion: {0}'.format(oc))
        sd, evnt_summary, uid, f = oc
        key = sd.isocalendar()
        add_occasion(key, evnt_summary, uid, f)


def updateViewData(f, bef, file2uuids=None, uuid2hash=None, options=None, file2data=None):
    tt = TimeIt(loglevel=2, label="updateViewData")
    if not file2uuids:
        file2uuids = {}
    if not uuid2hash:
        uuid2hash = {}
    if not options:
        options = {}
    if file2data is None:
        file2data = {}
    # clear data for this file
    _items = _alerts = _busytimes = _datetimes = _occasions = []
    if file2data is not None and f in file2data:
        _items, _alerts, _busytimes, _datetimes, _occasions = file2data[f]
        if _items:
            for item in _items:
                # logger.debug('removing item: {0}'.format(item))
                removeFromlist("items", item)
                # itemsSL.remove(item)
            for alert in _alerts:
                # logger.debug('removing alert: {0}'.format(alert))
                removeFromlist("alerts", alert)
                # alertsSL.remove(alert)
            for dt in _datetimes:
                # logger.debug('removing datetime: {0}'.format(datetime))
                removeFromlist("datetimes", dt)
                # datetimesSL.remove(datetime)
            for bt in _busytimes:
                bt = list(bt)
                sd = bt.pop(0)
                bt = tuple(bt)
                key = sd.isocalendar()
                # logger.debug('removing busytime: {0}: {1}'.format(key, bt))
                remove_busytime(key, bt)
            for oc in _occasions:
                oc = list(oc)
                sd = oc.pop(0)
                oc = tuple(oc)
                key = sd.isocalendar()
                # logger.debug('removing occasion: {0}: {1}'.format(key, oc))
                remove_occasion(key, oc)

        # remove the old entry for f in file2data
        del file2data[f]

    # update file2data
    getDataFromFile(f, file2data, bef, file2uuids, uuid2hash, options)
    # update itemsSL, ...
    updateViewFromFile(f, file2data)

    rows = list(itemsSL)
    alerts = list(alertsSL)
    datetimes = list(datetimesSL)
    busytimes = {}
    for key in busytimesSL:
        busytimes[key] = list(busytimesSL[key])
    occasions = {}
    for key in occasionsSL:
        occasions[key] = list(occasionsSL[key])

    numitems = len(file2uuids[f])
    logger.info("file: {0}\n    file items: {1}\n    view items: {2}\n    datetimes: {3}\n    alerts: {4}\n    busytimes: {5}\n    occasions: {5}".format(f, numitems, len(_items), len(_datetimes), len(_alerts), len(_busytimes), len(_occasions)))
    tt.stop()
    return rows, alerts, busytimes, datetimes, occasions, file2data


def updateCurrentFiles(allrows, file2uuids, uuid2hash, options):
    logger.debug("updateCurrent")
    # logger.debug(('options: {0}'.format(options)))
    res = True
    if options['current_textfile']:
        if 'current_opts' in options and options['current_opts']:
            txt, count2id = getReportData(
                options['current_opts'],
                file2uuids,
                uuid2hash,
                options,
                colors=0)
        else:
            tree = getAgenda(
                allrows,
                colors=options['agenda_colors'],
                days=options['agenda_days'],
                indent=options['current_indent'],
                width1=options['current_width1'],
                width2=options['current_width2'],
                calendars=options['calendars'],
                omit=options['agenda_omit'],
                mode='text'
            )
        # logger.debug('text colors: {0}'.format(options['agenda_colors']))
        txt, args0, args1 = tree2Text(tree, colors=options['agenda_colors'], indent=options['current_indent'], width1=options['current_width1'], width2=options['current_width2'])
        # logger.debug('text: {0}'.format(txt))
        if txt and not txt[0].strip():
            txt.pop(0)
        fo = codecs.open(options['current_textfile'], 'w', file_encoding)
        fo.writelines("\n".join(txt))
        fo.close()
    if options['current_htmlfile']:
        if 'current_opts' in options and options['current_opts']:
            html, count2id = getReportData(
                options['current_opts'],
                file2uuids,
                uuid2hash,
                options)
        else:
            tree = getAgenda(
                allrows,
                colors=options['agenda_colors'],
                days=options['agenda_days'],
                indent=options['current_indent'],
                width1=options['current_width1'],
                width2=options['current_width2'],
                calendars=options['calendars'],
                omit=options['agenda_omit'],
                mode='html')
        txt = tree2Html(tree, colors=options['agenda_colors'], indent=options['current_indent'], width1=options['current_width1'], width2=options['current_width2'])
        if not txt[0].strip():
            txt.pop(0)
        fo = codecs.open(options['current_htmlfile'], 'w', file_encoding)
        fo.writelines('<!DOCTYPE html> <html> <head> <meta charset="utf-8">\
            </head><body><pre>%s</pre></body>' % "\n".join(txt))
        fo.close()
    if has_icalendar and options['current_icsfolder']:
        res = export_ical(file2uuids, uuid2hash, options['current_icsfolder'], options['calendars'])
    return res


def availableDates(s):
    """
    start; end; busy
    Return dates between start and end that are not in busy where
    busy is a comma separated list of dates and date intervals, e.g.
    'jul 3, jul 7 - jul 15, jul 8, jul 6 - jul 10, jul 23 - aug 8'.
    """
    start_date, end_date, busy_dates = s.split(';')

    set = dtR.rruleset()
    set.rrule(rrule(DAILY, dtstart=parse(start_date), until=parse(end_date)))
    parts = busy_dates.split(',')
    for part in parts:
        interval = part.split('-')
        if len(interval) == 1:
            set.exdate(parse(interval[0]))
        if len(interval) == 2:
            set.exrule(rrule(DAILY, dtstart=parse(interval[0]), until=parse(interval[1])))

    res = "\n  ".join(x.strftime("%a %b %d") for x in list(set))
    prompt = "between {0} and {1}\nbut not in {2}:\n\n  {3}".format(start_date.strip(), end_date.strip(), busy_dates.strip(), res)
    return prompt


def tupleSum(list_of_tuples):
    # get the common length of the tuples
    l = len(list_of_tuples[0])
    res = []
    for i in range(l):
        res.append(sum([x[i] for x in list_of_tuples]))
    return res


def hsh2ical(hsh):
    """
        Convert hsh to ical object and return tuple (Success, object)
    """
    summary = hsh['_summary']
    if hsh['itemtype'] in ['*', '^']:
        element = Event()
    elif hsh['itemtype'] in ['-', '%', '+']:
        element = Todo()
    elif hsh['itemtype'] in ['!', '~']:
        element = Journal()
    else:
        return False, 'Cannot export item type "%s"' % hsh['itemtype']

    element.add('uid', hsh[u'I'])
    if 'z' in hsh:
        # pytz is required to get the proper tzid into datetimes
        tz = pytz.timezone(hsh['z'])
    else:
        tz = None
    if 's' in hsh:
        dt = hsh[u's']
        dz = dt.replace(tzinfo=tz)
        tzinfo = dz.tzinfo
        dt = dz
        dd = dz.date()
    else:
        dt = None
        tzinfo = None
        # tzname = None

    if u'_r' in hsh:
        # repeating
        rlst = hsh[u'_r']
        for r in rlst:
            if 'f' in r and r['f'] == 'l':
                if '+' not in hsh:
                    logger.warn("An entry for '@+' is required but missing.")
                    continue
                    # list only kludge: make it repeat daily for a count of 1
                # using the first element from @+ as the starting datetime
                dz = parse_str(hsh['+'].pop(0), hsh['z']).replace(tzinfo=tzinfo)
                dt = dz
                dd = dz.date()

                r['r'] = 'd'
                r['t'] = 1

            rhsh = {}
            for k in ical_rrule_keys:
                if k in r:
                    if k == 'f':
                        rhsh[ical_hsh[k]] = freq_hsh[r[k]]
                    elif k == 'w':
                        if type(r[k]) == list:
                            rhsh[ical_hsh[k]] = [x.upper() for x in r[k]]
                        else:
                            rhsh[ical_hsh[k]] = r[k].upper()
                    elif k == 'u':
                        uz = parse_str(r[k], hsh['z']).replace(tzinfo=tzinfo)
                        rhsh[ical_hsh[k]] = uz
                    else:
                        rhsh[ical_hsh[k]] = r[k]
            chsh = CaselessDict(rhsh)
            element.add('rrule', chsh)
        if '+' in hsh:
            for pd in hsh['+']:
                element.add('rdate', pd)
        if '-' in hsh:
            for md in hsh['-']:
                element.add('exdate', md)

    element.add('summary', summary)

    if 'q' in hsh:
        element.add('priority', hsh['_p'])
    if 'l' in hsh:
        element.add('location', hsh['l'])
    if 't' in hsh:
        element.add('categories', hsh['t'])
    if 'd' in hsh:
        element.add('description', hsh['d'])
    if 'm' in hsh:
        element.add('comment', hsh['m'])
    if 'u' in hsh:
        element.add('organizer', hsh['u'])
    if 'i' in hsh:
        for x in hsh['i']:
            element.add('attendee', "MAILTO:{0}".format(x))


    if hsh['itemtype'] in ['-', '+', '%']:
        done, due, following = getDoneAndTwo(hsh)
        if 's' in hsh:
            element.add('dtstart', dt)
        if done:
            finz = done.replace(tzinfo=tzinfo)
            fint = vDatetime(finz)
            element.add('completed', fint)
        if due:
            duez = due.replace(tzinfo=tzinfo)
            dued = vDate(duez)
            element.add('due', dued)
    elif hsh['itemtype'] == '^':
        element.add('dtstart', dd)
    elif dt:
        try:
            element.add('dtstart', dt)
        except:
            logger.exception('exception adding dtstart: {0}'.format(dt))

    if hsh['itemtype'] == '*':
        if 'e' in hsh and hsh['e']:
            ez = dz + hsh['e']
        else:
            ez = dz
        try:
            element.add('dtend', ez)
        except:
            logger.exception('exception adding dtend: {0}, {1}'.format(ez, tz))
    elif hsh['itemtype'] == '~':
        if 'e' in hsh and hsh['e']:
            element.add('comment', timedelta2Str(hsh['e']))
    return True, element


def export_ical_item(hsh, vcal_file):
    """
        Export a single item in iCalendar format
    """
    if not has_icalendar:
        logger.error("Could not import icalendar")
        return False

    cal = Calendar()
    cal.add('prodid', '-//etm_tk %s//dgraham.us//' % version)
    cal.add('version', '2.0')

    ok, element = hsh2ical(hsh)
    if not ok:
        return False
    cal.add_component(element)
    (name, ext) = os.path.splitext(vcal_file)
    pname = "%s.ics" % name
    try:
        cal_str = cal.to_ical()
    except Exception:
        logger.exception("could not serialize the calendar")
        return False
    try:
        fo = open(pname, 'wb')
    except:
        logger.exception("Could not open {0}".format(pname))
        return False
    try:
        fo.write(cal_str)
    except Exception:
        logger.exception("Could not write to {0}".format(pname))
    finally:
        fo.close()
    return True


def export_ical_active(file2uuids, uuid2hash, vcal_file, calendars=None):
    """
    Export items from active calendars to an ics file with the same name in vcal_folder.
    """
    if not has_icalendar:
        logger.error('Could not import icalendar')
        return False
    logger.debug("vcal_file: {0}; calendars: {1}".format(vcal_file, calendars))

    calendar = Calendar()
    calendar.add('prodid', '-//etm_tk {0}//dgraham.us//'.format(version))
    calendar.add('version', '2.0')

    cal_tuples = []
    if calendars:
        for cal in calendars:
            logger.debug('processing cal: {0}'.format(cal))
            if not cal[1]:
                continue
            name = cal[0]
            regex = re.compile(r'^{0}'.format(cal[2]))
            cal_tuples.append((name, regex))
    else:
        logger.debug('processing cal: all')
        regex = re.compile(r'^.*')
        cal_tuples.append(('all', regex))

    if not cal_tuples:
        return

    logger.debug('using cal_tuples: {0}'.format(cal_tuples))
    for rp in file2uuids:
        match = False
        for name, regex in cal_tuples:
            if regex.match(rp):
                for uid in file2uuids[rp]:
                    this_hsh = uuid2hash[uid]
                    ok, element = hsh2ical(this_hsh)
                    if ok:
                        calendar.add_component(element)
                break
        if not match:
            logger.debug('skipping {0} - no match in calendars'.format(rp))

    try:
        cal_str = calendar.to_ical()
    except Exception:
        logger.exception("Could not serialize the calendar: {0}".format(calendar))
        return False
    try:
        fo = open(vcal_file, 'wb')
    except:
        logger.exception("Could not open {0}".format(vcal_file))
        return False
    try:
        fo.write(cal_str)
    except Exception:
        logger.exception("Could not write to {0}" .format(vcal_file))
        return False
    finally:
        fo.close()
    return True


def export_json(file2uuids, uuid2hash, options={}):
    """
    Export items from each calendar to a json file with @c entries corresponding to the calendar name.
    New ids will be generated each time this is run.
    """
    # TODO: export relevant config info as well
    json_folder = options.get('datadir', None)
    calendars = options.get('calendars', None)
    logger.debug("json_folder: {0}; calendars: {1}".format(json_folder, calendars))

    cal_tuples = []
    calfiles = []
    if calendars:
        for cal in calendars:
            logger.debug('processing cal: {0}'.format(cal))
            name = cal[0]
            regex = re.compile(r'^{0}'.format(cal[2]))
            cal_tuples.append((name, regex))
    else:
        logger.debug('processing cal: all')
        regex = re.compile(r'^.*')
        cal_tuples.append(('all', regex))

    if not cal_tuples:
        return

    hsh  = {}
    hsh['items'] = {}
    logger.debug('using cal_tuples: {0}'.format(cal_tuples))
    json_file = os.path.join(json_folder, "etm-db.json")

    prefix, filelist = getFiles(options['datadir'])
    filetimes = {}

    for fp, rp in filelist:
        atime = os.path.getatime(fp)
        mtime = os.path.getmtime(fp)
        filetimes[rp] = (mtime, max(atime - mtime, 86400))

    # uuids for jobs will have etm:NN appended - we only want one copy
    # e.g., b63c362940f147a1ae8404d8265fa4bdetm:01
    for rp in file2uuids:
        this_calendar = None
        # this_lst = []  # for error logging
        for name, regex in cal_tuples:
            if regex.match(rp):
                this_calendar = name
                intervals = len(file2uuids[rp])
                stime, diff = filetimes[rp]
                delta = diff / intervals
                last_uid = ""
                for uid in file2uuids[rp]:
                    if uid[:32] == last_uid[:32]:
                        # only use the first instance of job ids
                        continue
                    last_uid = uid
                    secs = int(uniform(stime, stime + delta))
                    id = int(datetime.fromtimestamp(secs).strftime("%Y%m%d%H%M%S%f"))
                    stime += delta
                    old_hsh = uuid2hash[uid]
                    new_hsh = deepcopy(old_hsh)
                    itemtype = old_hsh['itemtype']
                    if itemtype in ['=', '#']:
                        continue

                    for key in new_hsh:
                        if type(new_hsh[key]) is datetime:
                            new_hsh[key] = new_hsh[key].strftime("%Y%m%dT%H%M")
                        elif type(new_hsh[key]) is timedelta:
                            new_hsh[key] = fmt_period(new_hsh[key])

                    for key in  ['I', 'fileinfo']:
                        if key in new_hsh:
                            del new_hsh[key]
                    if '_a' in new_hsh:
                        alerts = []
                        for a_tup in new_hsh['_a']:
                            if len(a_tup) <= 1:
                                alert = a_tup[0]
                            else:
                                alert = a_tup

                            args = []
                            if len(alert) >= 3:
                                for r in alert[2]:
                                    args.extend(r)
                            args = [x.strip() for x in args]
                            tds = []
                            for td in alert[0]:
                                tds.append(fmt_period(td))
                            for cmd in alert[1]:
                                if args:
                                    alerts.append((tds, cmd, args))
                                else:
                                    alerts.append((tds, cmd))
                        new_hsh['a'] = alerts
                        del new_hsh['_a']
                    if 'h' in new_hsh:
                        tmp = []
                        for pair in new_hsh['h']:
                            tmp.append(pair[0].strftime("%Y%m%dT%H%M"))
                            # tmp.append([x.strftime("%Y%m%dT%H%M") for x in pair if x])
                        new_hsh['h'] = tmp
                    if 'f' in new_hsh:
                        d, n, f = getDoneAndTwo(old_hsh)
                        o = old_hsh.get('o', 'k')
                        hd = []
                        if n:
                            new_hsh['s'] = n.strftime("%Y%m%dT%H%M")
                            # if o == 'r':
                            #     # reset start to the finish time
                            #     new_hsh['s'] = old_hsh['f'][0][0].strftime("%Y%m%dT%H%M")
                            # else:
                            #     # reset start to the next due date
                            #     new_hsh['s'] = n.strftime("%Y%m%dT%H:%M")
                            hd = [x[0].strftime("%Y%m%dT%H%M") for x in new_hsh['f'][-3:]]
                            del new_hsh['f']
                        else:
                            hd = [x[0].strftime("%Y%m%dT%H%M") for x in new_hsh['f'][-3:-1]]
                            new_hsh['f'] = new_hsh['f'][-1][0].strftime("%Y%m%dT%H%M")
                        if hd:
                            new_hsh.setdefault('h', []).extend(hd)

                    if '+' in new_hsh and 's' in new_hsh:
                        new_hsh['+'] = [x for x in new_hsh['+'] if x.strftime("%Y%m%dT%H%M") >= new_hsh['s']]

                    if 'rrule' in new_hsh:
                        del new_hsh['rrule']
                    if 'r' in new_hsh and 's' in new_hsh:
                        new_hsh['rrulestr'] = "{}".format(new_hsh['r'][22:])
                        del new_hsh['r']

                    if '_j' in new_hsh:
                        count = 0
                        jobs = {}
                        # make sure jobs are in q order
                        finished = True
                        for job in new_hsh['_j']:
                            q = job['q']
                            jobs.setdefault(q, []).append(job)
                            del job['q']

                            if 'h' in job:
                                tmp = []
                                for pair in job['h']:
                                    tmp.append(pair[0].strftime("%Y%m%dT%H%M"))
                                job['h'] = tmp
                            else:
                                finished = False

                            if 'f' in job:
                                job['f'] = job['f'][0][0].strftime("%Y%m%dT%H%M")
                            else:
                                finished = False

                        if 'f' in new_hsh and not finished:
                            del new_hsh['f']

                        q_keys = [x for x in jobs]
                        q_keys.sort()
                        q_count = 0
                        prereqs = []
                        for q_key in q_keys:
                            tmp = []
                            for job in jobs[q_key]:
                                count += 1
                                job['i'] = str(count)
                                job['p'] = prereqs
                                # job['j'] = "{} {}: {}".format(
                                #     new_hsh['_group_summary'], job['i'], job['j'])
                                tmp.append(job['i'])
                            prereqs = tmp
                        new_hsh['j'] = []
                        for q in q_keys:
                            new_hsh['j'].extend(jobs[q])
                        del new_hsh['_j']
                    for key in ['+', '-']:
                        if key in new_hsh:
                            tmp = []
                            for dt in new_hsh[key]:
                                tmp.append(dt.strftime("%Y%m%dT%H%M"))
                            new_hsh[key] = tmp

                    if '_p' in new_hsh:
                        if 0 < new_hsh['_p'] < 10:
                            new_hsh['p'] = new_hsh['_p']
                        del new_hsh['_p']

                    for key in ['_entry', '_id', '_rrulestr', '_summary', '_r']:
                        if key in new_hsh:
                            del new_hsh[key]
                            nkey = key[1:]
                            new_hsh[nkey] = old_hsh[key]
                    if 'r' in new_hsh:
                        tmp_r = []
                        for tmp_hsh in new_hsh['r']:
                            if 't' in tmp_hsh:
                                tmp_hsh['c'] = tmp_hsh['t']
                                del tmp_hsh['t']
                            if 'f' in tmp_hsh:
                                tmp_hsh['r'] = tmp_hsh['f']
                                del tmp_hsh['f']
                            if 'u' in tmp_hsh:
                                tmp_hsh['u'] = parse(tmp_hsh['u']).strftime("%Y%m%dT%H%M")
                            tmp_r.append(tmp_hsh)
                        new_hsh['r'] = tmp_r
                    this_c = new_hsh.get('c', None)
                    this_l = new_hsh.get('l', None)
                    temp_l = "; ".join([x for x in [this_l, this_c] if x is not None])
                    if temp_l:
                        new_hsh['l'] = temp_l
                    new_hsh['c'] = this_calendar
                    k = old_hsh.get('k', None)
                    if k is not None:
                        new_hsh['i'] = k
                        del new_hsh['k']
                    if itemtype in ['+', '-', '%']:
                        itemtype = '-'
                        s = old_hsh.get('s', None)
                        if s is None:
                            # undated
                            if 'z' in new_hsh:
                                del new_hsh['z']
                        elif s.hour == s.minute == 0:
                            # date-only
                            if 'z' in new_hsh:
                                del new_hsh['z']
                    if '_group_summary' in new_hsh:
                        new_hsh['summary'] = new_hsh['_group_summary']
                        del new_hsh['_group_summary']

                    if itemtype == "^":
                        itemtype = "*"
                        if 'z' in new_hsh:
                            del new_hsh['z']
                    elif itemtype == "!":
                        itemtype = "%"
                    elif itemtype == "$":
                        itemtype = "!"
                    elif itemtype == "~":
                        itemtype = "%"
                        if 'e' in new_hsh:
                            tmp_s = parse_str(new_hsh['s'], new_hsh.get('z', None))
                            tmp_e = parse_period(new_hsh['e'])
                            new_hsh['f'] = (tmp_s + tmp_e).strftime("%Y%m%dT%H%M")


                    new_hsh['itemtype'] = itemtype
                    # new_hsh['entry'] = hsh2entry(new_hsh)
                    # if 'r' in new_hsh:
                    #     del new_hsh['r']
                    # if 'z' in new_hsh:
                    #     del new_hsh['z']
                    try:
                        json.dumps(new_hsh)
                        hsh['items'][id] = new_hsh
                    except:
                        print('bad hsh')
                        print(new_hsh)


        if not this_calendar:
            logger.debug('skipping {0} - no match in calendars'.format(rp))
            print('skipping {0} - no match in calendars'.format(rp))

    with open(json_file, 'w') as jo:
        json.dump(hsh, jo, indent=1, sort_keys=True)

    return True

def etm2dsp(s):
    """
    >>> etm2dsp("20160710T1730")
    (True, '2016-07-10 05:30PM')
    >>> etm2dsp("2016710T1730")
    (False, 'Invalid datetime: 2016710T1730')
    >>> etm2dsp("20160710")
    (True, '2016-07-10')
    >>> etm2dsp("20160710T0000")
    (True, '2016-07-10')
    """

    dt_regex = re.compile(r'\d{8}T\d{4}')
    d_regex = re.compile(r'\d{8}')
    m_regex = re.compile(r'\d{8}T0000')
    if m_regex.fullmatch(s):
        dt = datetime.strptime(s, "%Y%m%dT%H%M")
        return True, dt.strftime("%Y-%m-%d") 
    elif d_regex.fullmatch(s):
        dt = datetime.strptime(s, "%Y%m%d")
        return True, dt.strftime("%Y-%m-%d") 
    elif dt_regex.fullmatch(s):
        dt = datetime.strptime(s, "%Y%m%dT%H%M")
        return True, dt.strftime("%Y-%m-%d %I:%M%p") 
    else:
        return False, "Invalid datetime: {}".format(s)

def hsh2entry(h):
    """
    """
    # all_keys = [x for x in "seabr+-cdfghijklmnopqtuvz"]
    all_keys = [x for x in "seabr+-cdfghijlmnoptx"]
    rrule_keys = [x for x in "iMmWwhmEcus"]
    job_keys = [x for x in "jsabcdefhlnipq"]

    res = []
    hsh = deepcopy(h)
    zstr = ""
    if 'z' in hsh and hsh['z']:
        if hsh['z'] != local_timezone:
            zstr = ", {}".format(hsh['z'])
        del hsh['z']
    res.append("{} {}".format(hsh['itemtype'], hsh['summary']))
    for k in all_keys:
        if k not in hsh:
            continue
        v = hsh[k]
        if k == 's':
            res.append("@s {}{}".format(etm2dsp(v)[1], zstr))
        elif k in ['+', '-', 'h']:
            # res.append("@{} {}".format(k, ", ".join([etm2dsp(x)[1] for x in v])))
            res.append("@{} {}".format(k, ", ".join(v)))
        elif k == 'r':
            for r in v:
                frq = r['r']
                del r['r']
                tmp = []
                for amp_key in rrule_keys:
                    if amp_key not in r:
                        continue
                    v = r[amp_key]
                    if type(v) is list:
                        v = ", ".join([str(x) for x in v])
                    tmp.append("&{} {}".format(amp_key, v))
                res.append("@r {} {}".format(frq, " ".join(tmp)))
        elif k == 'j':
            for j in v:
                jnm = j['j']
                del j['j']
                tmp = []
                for amp_key in job_keys:
                    if amp_key not in j:
                        continue
                    if amp_key == 'a':
                        for a in j['a']:
                            tmp.append("&a {}: {}".format(a[0], " ".join(a[1:])))
                    elif amp_key == 'p':
                        if j['p']:
                            tmp.append("&p {}".format(", ".join(j['p'])))
                        # else:
                        #     tmp.append("&p None")
                    # elif amp_key == 'f':
                    #     tmp.append("&f {}".format("; ".join(j['f'])))
                    else:
                        v = j[amp_key]
                        if type(v) is list:
                            v = ", ".join([str(x) for x in v])
                        tmp.append("&{} {}".format(amp_key, v))
                res.append("@j {} {}".format(jnm, " ".join(tmp)))
        elif k == 'a':
            for a in v:
                res.append("@a {}: {}".format(a[0], ", ".join(a[1:])))
        # elif k == 'f':
        #     res.append(("@f {}".format("; ".join(v))))
        else:
            res.append("@{} {}".format(k, v))
    return " ".join(res)



def export_ical(file2uuids, uuid2hash, vcal_folder, calendars=None):
    """
    Export items from each calendar to an ics file with the same name in vcal_folder.
    """
    if not has_icalendar:
        logger.error('Could not import icalendar')
        return False
    logger.debug("vcal_folder: {0}; calendars: {1}".format(vcal_folder, calendars))

    cal_tuples = []
    calfiles = []
    if calendars:
        for cal in calendars:
            logger.debug('processing cal: {0}'.format(cal))
            name = cal[0]
            regex = re.compile(r'^{0}'.format(cal[2]))
            calendar = Calendar()
            calendar.add('prodid', '-//etm_tk {0}//dgraham.us//'.format(version))
            calendar.add('version', '2.0')
            cal_tuples.append((name, regex, calendar))
    else:
        logger.debug('processing cal: all')
        all = Calendar()
        all.add('prodid', '-//etm_tk {0}//dgraham.us//'.format(version))
        all.add('version', '2.0')
        regex = re.compile(r'^.*')
        cal_tuples.append(('all', regex, all))

    if not cal_tuples:
        return

    logger.debug('using cal_tuples: {0}'.format(cal_tuples))
    for rp in file2uuids:
        this_calendar = None
        this_file = None
        this_lst = []  # for error logging
        for name, regex, calendar in cal_tuples:
            if regex.match(rp):
                this_calendar = calendar
                this_file = os.path.join(vcal_folder, "{0}.ics".format(name))
                for uid in file2uuids[rp]:
                    this_hsh = uuid2hash[uid]
                    ok, element = hsh2ical(this_hsh)
                    if ok:
                        this_lst.append(element)
                        this_calendar.add_component(element)
                calfiles.append([this_calendar, this_file, this_hsh, this_lst])
                break
        if not this_calendar:
            logger.debug('skipping {0} - no match in calendars'.format(rp))

    for this_calendar, this_file, this_hsh, this_lst in calfiles:
        try:
            cal_str = this_calendar.to_ical()
        except Exception:
            logger.exception("Could not serialize the calendar: {0}; {1}\n  {2}\n  {3}".format(this_calendar, this_file, this_lst, this_hsh))
            return False
        try:
            fo = open(this_file, 'wb')
        except:
            logger.exception("Could not open {0}".format(this_file))
            return False
        try:
            fo.write(cal_str)
        except Exception:
            logger.exception("Could not write to {0}" .format(this_file))
            return False
        finally:
            fo.close()
    return True


def txt2ical(file2uuids, uuid2hash, datadir, txt_rp, ics_rp):
    """
    Export items from txtfile to icsfile.
    """
    if not has_icalendar:
        logger.error('Could not import icalendar')
        return False

    if txt_rp not in file2uuids:
        return

    cal = Calendar()
    cal.add('prodid', '-//etm_tk {0}//dgraham.us//'.format(version))
    cal.add('version', '2.0')

    for uid in file2uuids[txt_rp]:
        hsh = uuid2hash[uid]
        ok, element = hsh2ical(hsh)
        if ok:
            cal.add_component(element)

    try:
        cal_str = cal.to_ical()
    except Exception:
        logger.exception("Could not serialize the calendar")
        return False
    ics = os.path.join(datadir, ics_rp)
    try:
        fo = open(ics, 'wb')
    except:
        logger.exception("Could not open {0}".format(ics))
        return False
    try:
        fo.write(cal_str)
    except Exception:
        logger.exception("Could not write to {0}" .format(ics))
        return False
    finally:
        fo.close()
    return True


def update_subscription(url, txt):
    if python_version2:
        import urllib2 as request
    else:
        from urllib import request

    res = False
    u = request.urlopen(url)
    vcal = u.read()
    if vcal:
        res = import_ical(vcal=vcal.decode('utf-8'), txt=txt.decode('utf-8'))
    return res


def import_ical(ics="", txt="", vcal=""):
    if not has_icalendar:
        logger.error("Could not import icalendar")
        return False
    logger.debug("ics: {0}, txt: {1}, vcal:{2}".format(ics, txt, vcal))
    if vcal:
        cal = Calendar.from_ical(vcal)
    else:
        g = open(ics, 'rb')
        cal = Calendar.from_ical(g.read())
        g.close()
    ilst = []
    for comp in cal.walk():
        clst = []
        # dated = False
        start = None
        t = ''  # item type
        s = ''  # @s
        e = ''  # @e
        f = ''  # @f
        tzid = comp.get('tzid')
        if comp.name == "VEVENT":
            t = '*'
            start = comp.get('dtstart')
            if start:
                s = start.to_ical().decode()[:16]
                # dated = True
                end = comp.get('dtend')
                if end:
                    e = end.to_ical().decode()[:16]
                    logger.debug('start: {0}, s: {1}, end: {2}, e: {3}'.format(start, s, end, e))
                    extent = parse(e) - parse(s)
                    e = fmt_period(extent)
                else:
                    t = '^'

        elif comp.name == "VTODO":
            t = '-'
            tmp = comp.get('completed')
            if tmp:
                f = tmp.to_ical().decode()[:16]
            due = comp.get('due')
            start = comp.get('dtstart')
            if due:
                s = due.to_ical().decode()
            elif start:
                s = start.to_ical().decode()

        elif comp.name == "VJOURNAL":
            t = u'!'
            tmp = comp.get('dtstart')
            if tmp:
                s = tmp.to_ical().decode()[:16]
        else:
            continue
        summary = comp.get('summary')
        clst = [t, summary]
        if start:
            if 'TZID' in start.params:
                logger.debug("TZID: {0}".format(start.params['TZID']))
                clst.append('@z %s' % start.params['TZID'])

        if s:
            clst.append("@s %s" % s)
        if e:
            clst.append("@e %s" % e)
        if f:
            clst.append("@f %s" % f)
        tzid = comp.get('tzid')
        if tzid:
            clst.append("@z %s" % tzid.to_ical().decode())
            logger.debug("Using tzid: {0}".format(tzid.to_ical().decode()))
        else:
            logger.debug("Using tzid: {0}".format(local_timezone))
            clst.append("@z {0}".format(local_timezone))

        tmp = comp.get('description')
        if tmp:
            clst.append("@d %s" % tmp.to_ical().decode('utf-8'))
        rule = comp.get('rrule')
        if rule:
            rlst = []
            keys = rule.sorted_keys()
            for key in keys:
                if key == 'FREQ':
                    rlst.append(ical_freq_hsh[rule.get('FREQ')[0].to_ical().decode()])
                elif key in ical_rrule_hsh:
                    rlst.append("&%s %s" % (
                        ical_rrule_hsh[key],
                        ", ".join(map(str, rule.get(key)))))
            clst.append("@r %s" % " ".join(rlst))

        tags = comp.get('categories')
        if tags:
            if type(tags) is list:
                tags = [x.to_ical().decode() for x in tags]
                clst.append("@t %s" % u', '.join(tags))
            else:
                clst.append("@t %s" % tags)

        invitees = comp.get('attendee')
        if invitees:
            if type(invitees) is list:
                invitees = [x.to_ical().decode() for x in invitees]
                ilst = []
                for x in invitees:
                    if x.startswith("MAILTO:"):
                        x = x[7:]
                    ilst.append(x)
                clst.append("@i %s" % u', '.join(ilst))
            else:
                clst.append("@i %s" % invitee)

        tmp = comp.get('organizer')
        if tmp:
            clst.append("@u %s" % tmp.to_ical().decode())

        item = u' '.join(clst)
        ilst.append(item)
    if ilst:
        if txt:
            if os.path.isfile(txt):
                tmpfile = "{0}.tmp".format(os.path.splitext(txt)[0])
                shutil.copy2(txt, tmpfile)
            fo = codecs.open(txt, 'w', file_encoding)
            fo.write("\n".join(ilst))
            fo.close()
        elif vcal:
            return "\n".join(ilst)
        return True


def syncTxt(file2uuids, uuid2hash, datadir, relpath):
    root = os.path.splitext(relpath)[0]
    ics_rp = "{0}.ics".format(root)
    txt_rp = "{0}.txt".format(root)
    logger.debug('txt_rp: {0}, ics_rp: {1}'.format(txt_rp, ics_rp))
    sync_ics = os.path.join(datadir, ics_rp)
    sync_txt = os.path.join(datadir, txt_rp)
    logger.debug('sync_txt: {0}, sync_ics: {1}'.format(sync_txt, sync_ics))
    mode = 0  # do nothing
    if os.path.isfile(sync_txt) and not os.path.isfile(sync_ics):
        mode = 1  # to ics
    elif os.path.isfile(sync_ics) and not os.path.isfile(sync_txt):
        mode = 2  # to txt
    elif os.path.isfile(sync_ics) and os.path.isfile(sync_txt):
        mod_ics = os.path.getmtime(sync_ics)
        mod_txt = os.path.getmtime(sync_txt)
        if mod_ics < mod_txt:
            logger.debug('mode 1, to ics: {0} < {1}'.format(mod_ics, mod_txt))
            mode = 1  # to ics
        elif mod_txt < mod_ics:
            logger.debug('mode 2, to txt: {0} > {1}'.format(mod_ics, mod_txt))
            mode = 2  # to txt
        else:
            logger.debug('sync_txt and sync_ics have the same mtime: {0}'.format(mod_txt))
    if not mode:
        return

    if mode == 1:  # to ics
        logger.debug('calling txt2ical: {0}, {1}, {2}'.format(datadir, txt_rp, ics_rp))
        res = txt2ical(file2uuids, uuid2hash, datadir, txt_rp, ics_rp)
        if not res:
            return
        seconds = os.path.getmtime(sync_txt)

    elif mode == 2:  # to txt
        res = import_ical(ics=sync_ics, txt=sync_txt)
        if not res:
            return
        seconds = os.path.getmtime(sync_ics)

    # update times
    logger.debug('updating mtimes using seconds: {0}'.format(seconds))
    os.utime(sync_ics, times=(seconds, seconds))
    os.utime(sync_txt, times=(seconds, seconds))


def ensureMonthly(options, date=None):
    """
    """
    retval = None
    if ('monthly' in options and
            options['monthly']):
        monthly = os.path.normpath(os.path.join(
            options['datadir'],
            options['monthly']))
        if not os.path.isdir(monthly):
            os.makedirs(monthly)
            sleep(0.5)
        if date is None:
            date = datetime.now().date()
        yr = date.year
        mn = date.month
        curryear = os.path.normpath(os.path.join(monthly, "%s" % yr))
        if not os.path.isdir(curryear):
            os.makedirs(curryear)
            sleep(0.5)
        currfile = os.path.normpath(os.path.join(curryear, "%02d.txt" % mn))
        if not os.path.isfile(currfile):
            fo = codecs.open(currfile, 'w', options['encoding']['file'])
            fo.write("")
            fo.close()
        if os.path.isfile(currfile):
            retval = currfile
    return retval


class ETMCmd():
    """
        Data handling commands
    """

    def __init__(self, options=None, parent=None):
        if not options:
            options = {}
        self.options = options
        self.calendars = deepcopy(options['calendars'])

        self.cal_regex = None
        self.messages = []
        self.cmdDict = {
            '?': self.do_help,
            'a': self.do_a,
            'd': self.do_d,
            'n': self.do_n,
            'k': self.do_k,
            'm': self.do_m,
            'N': self.do_N,
            'p': self.do_p,
            'c': self.do_c,
            't': self.do_t,
            'v': self.do_v,
        }

        self.helpDict = {
            'help': self.help_help,
            'a': self.help_a,
            'd': self.help_d,
            'n': self.help_n,
            'k': self.help_k,
            'm': self.help_m,
            'N': self.help_N,
            'p': self.help_p,
            'c': self.help_c,
            't': self.help_t,
            'v': self.help_v,
        }
        self.do_update = False
        self.ruler = '-'
        # self.rows = []
        self.file2uuids = {}
        self.file2lastmodified = {}
        self.uuid2hash = {}
        self.loop = False
        self.number = True
        self.count2id = {}
        self.uuid2labels = {}
        self.last_rep = ""
        self.item_hsh = {}
        self.output = 'text'
        self.tkversion = ''
        self.tkstyle = ''
        self.rows = None
        self.busytimes = None
        self.busydays = None
        self.alerts = None
        self.occasions = None
        self.file2data = None
        self.prevnext = None
        self.line_length = self.options['agenda_indent'] + self.options['agenda_width1'] + self.options['agenda_width2']
        self.currfile = ''  # ensureMonthly(options)
        if 'edit_cmd' in self.options and self.options['edit_cmd']:
            self.editcmd = self.options['edit_cmd']
        else:
            self.editcmd = ''
        self.tmpfile = os.path.normpath(os.path.join(self.options['etmdir'], '.temp.txt'))

    def do_command(self, s):
        logger.debug('processing command: {0}'.format(s))
        args = s.split(' ')
        cmd = args.pop(0)
        if args:
            arg_str = " ".join(args)
        else:
            arg_str = ''
        if cmd not in self.cmdDict:
            return _('"{0}" is an unrecognized command.').format(cmd)
        logger.debug('do_command: {0}, {1}'.format(cmd, arg_str))
        res = self.cmdDict[cmd](arg_str)
        return res

    def do_help(self, cmd):
        if cmd:
            return self.helpDict[cmd]()
        else:
            return self.help_help()

    def mk_rep(self, arg_str):
        logger.debug("arg_str: {0}".format(arg_str))
        # we need to return the output string rather than print it
        self.last_rep = arg_str
        cmd = arg_str[0]
        ret = []
        views = {
            # everything but agenda, week and month
            'd': 'day',
            'p': 'folder',
            't': 'tag',
            'n': 'note',
            'k': 'keyword'
        }
        try:
            if cmd == 'a':
                if len(arg_str) > 2:
                    f = arg_str[1:].strip()
                else:
                    f = None
                    return (getAgenda(
                        self.rows,
                        colors=self.options['agenda_colors'],
                        days=self.options['agenda_days'],
                        indent=self.options['agenda_indent'],
                        width1=self.options['agenda_width1'],
                        width2=self.options['agenda_width2'],
                        omit=self.options['agenda_omit'],
                        calendars=self.calendars,
                        mode=self.output,
                        fltr=f))
                logger.debug('calling getAgenda')
            elif cmd in views:
                view = views[cmd]
                if len(arg_str) > 2:
                    f = arg_str[1:].strip()
                else:
                    f = None
                if not self.rows:
                    return {}
                rows = deepcopy(self.rows)
                return (makeTree(rows, view=view, calendars=self.calendars, fltr=f, hide_finished=self.options['hide_finished']))
            else:
                res = getReportData(
                    arg_str,
                    self.file2uuids,
                    self.uuid2hash,
                    self.options)
                return res

        except:
            logger.exception("could not process '{0}'".format(arg_str))
            s = str(_('Could not process "{0}".')).format(arg_str)
            # p = str(_('Enter ? r or ? t for help.'))
            ret.append(s)
        return '\n'.join(ret)

    def loadData(self, e=None):
        self.count2id = {}
        now = datetime.now()
        bef = self.options['bef']
        self.file2data = {}
        logger.debug('calling get_data')
        uuid2hash, uuid2labels, file2uuids, self.file2lastmodified, bad_datafiles, messages = get_data(options=self.options)
        self.file2uuids = file2uuids
        self.uuid2hash = uuid2hash
        self.uuid2labels = uuid2labels
        logger.debug('calling getViewData')
        self.file2data = getViewData(bef, file2uuids, uuid2hash, self.options)
        self.rows = tuple(itemsSL)
        self.alerts = list(alertsSL)
        self.datetimes = list(datetimesSL)
        self.busytimes = {}
        for key in busytimesSL:
            self.busytimes[key] = list(busytimesSL[key])

        self.occasions = {}
        for key in occasionsSL:
            self.occasions[key] = list(occasionsSL[key])

        self.do_update = True
        self.currfile = ensureMonthly(self.options, now)
        if self.last_rep:
            logger.debug('calling mk_rep with {0}'.format(self.last_rep))
            return self.mk_rep(self.last_rep)

    def updateDataFromFile(self, fp, rp):
        """
        Called from safe_save. Calls process_one_file to produce hashes
        for the items in the file
        """
        logger.debug('starting updateDataFromFile: {0}; {1}'.format(fp, rp))
        self.count2id = {}
        now = datetime.now()
        bef = self.options['bef']
        if rp in self.file2uuids:
            ids = self.file2uuids[rp]
        else:
            ids = []
        logger.debug('rp: {0}; ids: {1}'.format(rp, ids))
        # remove the old
        logger.debug('removing the relevant entries in uuid2hash')
        for id in ids:
            if id in self.uuid2hash:
                del self.uuid2hash[id]
            if id in self.uuid2labels:
                logger.debug('removing uuid2label[{0}] = {1}'.format(id, self.uuid2labels[id]))
                del self.uuid2labels[id]
        logger.debug('removing the relevant entry in file2uuids')
        self.file2uuids[rp] = []
        msg, hashes, u2l = process_one_file(fp, rp, self.options)
        logger.debug('update labels: {0}'.format(u2l))
        self.uuid2labels.update(u2l)
        loh = [x for x in hashes if x]
        for hsh in loh:
            if hsh['itemtype'] == '=':
                continue
            logger.debug('adding: {0}, {1}'.format(hsh['I'], hsh['_summary']))
            id = hsh['I']
            self.uuid2hash[id] = hsh
            self.file2uuids.setdefault(rp, []).append(id)
        mtime = os.path.getmtime(fp)
        self.file2lastmodified[(fp, rp)] = mtime
        (self.rows, self.alerts, self.busytimes, self.datetimes, self.occasions, self.file2data) = updateViewData(rp, bef, self.file2uuids, self.uuid2hash, self.options, self.file2data)

        logger.debug('ended updateDataFromFile')

    def edit_tmp(self):
        if not self.editcmd:
            term_print("""\
Either ITEM must be provided or edit_cmd must be specified in etmtk.cfg.
""")
            return [], {}
        hsh = {'file': self.tmpfile, 'line': 1}
        cmd = expand_template(self.editcmd, hsh)
        msg = True
        while msg:
            subprocess.call(cmd, shell=True)
            # check the item
            fo = codecs.open(self.tmpfile, 'r', file_encoding)
            lines = [unicode(u'%s') % x.rstrip() for x in fo.readlines()]
            fo.close()
            if len(lines) >= 1:
                while len(lines) >= 1 and not lines[-1]:
                    lines.pop(-1)
            if not lines:
                term_print(_('canceled'))
                return False
            item = "\n".join(lines)
            new_hsh, msg = str2hsh(item, options=self.options)
            if msg:
                term_print('Error messages:')
                term_print("\n".join(msg))
                rep = raw_input('Correct item? [Yn] ')
                if rep.lower() == 'n':
                    term_print(_('canceled'))
                    return [], {}
        item = unicode(u"{0}".format(hsh2str(new_hsh, self.options)[0]))
        lines = item.split('\n')
        return lines, new_hsh

    def commit(self, file, mode=""):
        if self.options['vcs_system']:
            mesg = u"{0}".format(mode)
            if python_version == 2 and type(mesg) == unicode:
                # hack to avoid unicode in .format() for python 2
                cmd = self.options['vcs']['commit'].format(
                    repo=self.options['vcs']['repo'],
                    work=self.options['vcs']['work'],
                    mesg="XXX")
                cmd = cmd.replace("XXX", mesg)
            else:
                cmd = self.options['vcs']['commit'].format(
                    repo=self.options['vcs']['repo'],
                    work=self.options['vcs']['work'],
                    mesg=mesg)
            subprocess.call(cmd, shell=True)
            logger.debug("executed vcs commit command:\n    {0}".format(cmd))
        return True

    def safe_save(self, file, s, mode="", cli=False):
        """
            Try writing the s to tmpfile and then, if it succeeds,
            copy tmpfile to file.
        """
        if not mode:
            mode = "Edited file"
        logger.debug('starting safe_save. file: {0}, mode: {1}, cli: {2},\n     file_encoding: {3}, type(s): {4}, term_encoding: {5}'.format(file, mode, cli, file_encoding, type(s), term_encoding))
        try:
            fo = codecs.open(self.tmpfile, 'w', file_encoding)
            # add a trailing newline to make diff happy
            fo.write("{0}\n".format(s.rstrip()))
            fo.close()
        except:
            return 'error writing to file - aborted'
        shutil.copy2(self.tmpfile, file)
        logger.debug("modified file: '{0}'".format(file))
        pathname, ext = os.path.splitext(file)
        if not cli and ext == ".txt":
            # this is a data file
            fp = file
            rp = relpath(fp, self.options['datadir'])
            # this will update self.uuid2hash, ...
            self.updateDataFromFile(fp, rp)
        return self.commit(file, mode)

    def get_itemhash(self, arg_str):
        try:
            count = int(arg_str)
        except:
            return _('an integer argument is required')
        if count not in self.count2id:
            return _('Item number {0} not found').format(count)
        uid, dtstr = self.count2id[count].split('::')
        hsh = self.uuid2hash[uid]
        if dtstr:
            hsh['_dt'] = parse_str(dtstr, hsh['z'])
        return hsh

    def do_a(self, arg_str):
        return self.mk_rep('a {0}'.format(arg_str))

    def help_a(self):
        return ("""\
Usage:

    etm a

Generate an agenda including dated items for the next {0} days (agenda_days from etmtk.cfg) together with any now and next items.\
""".format(self.options['agenda_days']))

    def cmd_do_delete(self, choice):
        if not choice:
            return False
        try:
            choice = int(choice)
        except:
            return False

        if choice in [1, 2, 4]:
            hsh = self.item_hsh
            dt = parse(
                hsh['_dt']).replace(
                tzinfo=tzlocal()).astimezone(
                gettz(hsh['z']))
            dtn = dt.replace(tzinfo=None)
            hsh_rev = deepcopy(hsh)

            if choice == 1:
                # delete this instance only by removing it from @+
                # or adding it to @-

                if 'f' in hsh_rev:
                    for i in range(len(hsh_rev['f'])):
                        d = hsh_rev['f'][i][0]
                        if d == dtn:
                            hsh_rev['f'].pop(i)
                            break

                if '+' in hsh_rev and dtn in hsh_rev['+']:
                    hsh_rev['+'].remove(dtn)
                    if not hsh_rev['+'] and hsh_rev['r'] == 'l':
                        del hsh_rev['r']
                        del hsh_rev['_r']
                else:
                    hsh_rev.setdefault('-', []).append(dt)
                # newstr = hsh2str(hsh_rev, self.options)
                self.replace_item(hsh_rev)

            elif choice == 2:
                # delete this and all subsequent instances by adding
                # this instance - one minute to &u for each @r

                if 'f' in hsh_rev:
                    for i in range(len(hsh_rev['f'])):
                        d = hsh_rev['f'][i][0]
                        if d >= dtn:
                            hsh_rev['f'].pop(i)

                tmp = []
                for h in hsh_rev['_r']:
                    if 'f' in h and h['f'] != u'l':
                        h['u'] = (dtn - ONEMINUTE).strftime(sfmt)
                    tmp.append(h)
                hsh_rev['_r'] = tmp

                if u'+' in hsh:
                    tmp_rev = []
                    for d in hsh_rev['+']:
                        if d < dtn:
                            tmp_rev.append(d)
                    if tmp_rev:
                        hsh_rev['+'] = tmp_rev
                    else:
                        del hsh_rev['+']

                if u'-' in hsh:
                    tmp_rev = []
                    for d in hsh_rev['-']:
                        if d < dtn:
                            tmp_rev.append(d)
                    if tmp_rev:
                        hsh_rev['-'] = tmp_rev
                    else:
                        del hsh_rev['-']
                self.replace_item(hsh_rev)

            elif choice == 4:
                # delete all previous instances

                if 'f' in hsh_rev:
                    for i in range(len(hsh_rev['f']), 0, -1):
                        d = hsh_rev['f'][i-1][1]
                        if d < dtn:
                            hsh_rev['f'].pop(i-1)
                    if not hsh_rev['f']:
                        del hsh_rev['f']

                if u'+' in hsh:
                    logger.debug('starting @+: {0}'.format(hsh['+']))
                    tmp_rev = []
                    for d in hsh_rev['+']:
                        if d >= dtn:
                            tmp_rev.append(d)
                    if tmp_rev:
                        hsh_rev['+'] = tmp_rev
                        logger.debug('ending @+: {0}'.format(hsh['+']))
                    else:
                        del hsh_rev['+']
                        logger.debug('removed @+')

                if u'-' in hsh:
                    logger.debug('starting @-: {0}'.format(hsh['-']))
                    tmp_rev = []
                    for d in hsh_rev['-']:
                        if d >= dtn:
                            tmp_rev.append(d)
                    if tmp_rev:
                        hsh_rev['-'] = tmp_rev
                        logger.debug('ending @-: {0}'.format(hsh['-']))
                    else:
                        del hsh_rev['-']
                        logger.debug('removed @-')
                hsh_rev['s'] = dtn
                self.replace_item(hsh_rev)
        else:
            self.delete_item()

    def cmd_do_reschedule(self, new_dtn):
        # new_dtn = new_dt.astimezone(gettz(self.item_hsh['z'])).replace(tzinfo=None)
        hsh_rev = deepcopy(self.item_hsh)
        if self.old_dt:
            # old_dtn = self.old_dt.astimezone(gettz(self.item_hsh['z'])).replace(tzinfo=None)
            old_dtn = self.old_dt
            if 'r' in hsh_rev:
                if '+' in hsh_rev and old_dtn in hsh_rev['+']:
                    hsh_rev['+'].remove(old_dtn)
                    if not hsh_rev['+'] and hsh_rev['r'] == 'l':
                        del hsh_rev['r']
                        del hsh_rev['_r']
                else:
                    hsh_rev.setdefault('-', []).append(old_dtn)
                hsh_rev.setdefault('+', []).append(new_dtn)
                # check starting time
                if new_dtn < hsh_rev['s']:
                    d = (hsh_rev['s'] - new_dtn).days
                    hsh_rev['s'] -= (d + 1) * ONEDAY
            else:  # dated but not repeating
                hsh_rev['s'] = new_dtn
        else:  # either undated or not repeating
            hsh_rev['s'] = new_dtn
        logger.debug(('replacement: {0}'.format(hsh_rev)))
        self.replace_item(hsh_rev)

    def cmd_do_schedulenew(self, new_dtn):
        # new_dtn = new_dt.astimezone(gettz(self.item_hsh['z'])).replace(tzinfo=None)
        hsh_rev = deepcopy(self.item_hsh)
        if self.old_dt:
            # old_dtn = self.old_dt.astimezone(gettz(self.item_hsh['z'])).replace(tzinfo=None)
            if 'r' in hsh_rev:
                if '+' in hsh_rev and new_dtn in hsh_rev['+']:
                    return
                if '-' in hsh_rev and new_dtn in hsh_rev['-']:
                    hsh_rev['-'].remove(new_dtn)
                else:
                    hsh_rev.setdefault('+', []).append(new_dtn)
                # check starting time
                if new_dtn < hsh_rev['s']:
                    d = (hsh_rev['s'] - new_dtn).days
                    hsh_rev['s'] -= (d + 1) * ONEDAY
            else:  # dated but not repeating
                if hsh_rev['s'] == new_dtn:
                    return
                hsh_rev['r'] = 'l'
                hsh_rev.setdefault('+', []).append(new_dtn)
        else:  # either undated or not repeating
            hsh_rev['s'] = new_dtn
        logger.debug(('replacement: {0}'.format(hsh_rev)))
        self.replace_item(hsh_rev)

    def delete_item(self):
        f, begline, endline = self.item_hsh['fileinfo']
        fp = os.path.normpath(os.path.join(self.options['datadir'], f))
        fo = codecs.open(fp, 'r', file_encoding)
        lines = fo.readlines()
        fo.close()
        self.replace_lines(fp, lines, begline, endline, [])
        return True

    def replace_item(self, new_hsh):
        new_item, msg = hsh2str(new_hsh, self.options)
        logger.debug(new_item)
        newlines = new_item.split('\n')
        f, begline, endline = new_hsh['fileinfo']
        fp = os.path.normpath(os.path.join(self.options['datadir'], f))
        fo = codecs.open(fp, 'r', file_encoding)
        lines = fo.readlines()
        fo.close()
        self.replace_lines(fp, lines, begline, endline, newlines)
        # self.loadData()
        return True

    def append_item(self, new_hsh, file, cli=False):
        """
        """
        # new_item, msg = hsh2str(new_hsh, self.options, include_uid=True)
        new_item, msg = hsh2str(new_hsh, self.options)
        old_items = getFileItems(file, self.options['datadir'], False)
        items = [u'%s' % x[0].rstrip() for x in old_items if x[0].strip()]
        items.append(new_item)
        itemstr = "\n".join(items)
        mode = _("added item")
        logger.debug('saving {0} to {1}, mode: {2}'.format(itemstr, file, mode))
        self.safe_save(file, itemstr, mode=mode, cli=cli)
        # self.loadData()
        return "break"

    def cmd_do_finish(self, dt, options={}):
        """
        Called by do_f to process the finish datetime and add it to the file.
        """
        hsh = self.item_hsh
        done, due, following = getDoneAndTwo(hsh)
        if 'z' not in hsh:
            hsh['z'] = options['local_timezone']
        if due:
            # undated tasks won't have a due date
            ddn = due.replace(
                tzinfo=tzlocal()).astimezone(
                gettz(hsh['z'])).replace(tzinfo=None)
        else:
            ddn = ''
        if 's' in hsh and 'o' in hsh and hsh['o'] == 'r':
            hours = hsh['s'].hour
            minutes = hsh['s'].minute
            dt = dt.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        if hsh['itemtype'] == u'+':
            m = group_regex.match(hsh['_summary'])
            if m:
                group, num, tot, job = m.groups()
                hsh['_j'][int(num) - 1]['f'] = [
                    (dt.replace(tzinfo=None), ddn)]
                finished = True
                # check to see if all jobs are finished
                for job in hsh['_j']:
                    if 'f' not in job:
                        finished = False
                        break
                if finished:
                    # move the finish dates from the jobs to the history
                    for j in range(len(hsh['_j'])):
                        job = hsh['_j'][j]
                        job.setdefault('h', []).append(job['f'][0])
                        del job['f']
                        hsh['_j'][j] = job

                    # and add the last finish date (this one) to the group
                    completion = (dt.replace(tzinfo=None), ddn)
                    hsh['f'] = [completion]
        else:
            dtz = dt.replace(tzinfo=tzlocal()).astimezone(gettz(hsh['z'])).replace(tzinfo=None)
            if not ddn:
                ddn = dtz
            hsh.setdefault('f', []).append((dtz, ddn))
        logger.debug('finish hsh: {0}'.format(hsh))
        self.replace_item(hsh)

    def do_k(self, arg_str):
        # self.prevnext = getPrevNext(self.dates)
        return self.mk_rep('k {0}'.format(arg_str))

    @staticmethod
    def help_k():
        return ("""\
Usage:

    etm k [FILTER]

Show items grouped and sorted by keyword optionally limited to those containing a case insenstive match for the regex FILTER.\
""")

    def do_m(self, arg_str):
        lines = self.options['reports']
        try:
            n = int(arg_str)
            if n < 1 or n > len(lines):
                return _('report {0} does not exist'.format(n))
        except:
            return self.help_m()
        rep_spec = "{0}".format(lines[n - 1].strip().split('#')[0])
        logger.debug(('rep_spec: {0}'.format(rep_spec)))
        tree = getReportData(
            rep_spec,
            self.file2uuids,
            self.uuid2hash,
            self.options)
        return(tree)

    def help_m(self):
        res = []
        lines = self.options['reports']
        if lines:
            res.append(_("""\
Usage:

    etm m N

where N is the number of a report specification:\n """))
            for i in range(len(lines)):
                res.append("{0:>2}. {1}".format(i + 1, lines[i].strip()))
        return "\n".join(res)
        # return(res)

    def do_n(self, arg_str):
        return self.mk_rep('n {0}'.format(arg_str))

    @staticmethod
    def help_n():
        return ("""\
Usage:

    etm N [FILTER]

Show notes grouped and sorted by keyword optionally limited to those containing a case insenstive match for the regex FILTER.\
""")

    def do_N(self, arg_str='', itemstr=""):
        logger.debug('arg_str: {0}, type(arg_str): {1}'.format(arg_str, type(arg_str)))
        if arg_str:
            new_item = s2or3(arg_str)
            new_hsh, msg = str2hsh(new_item, options=self.options)
            logger.debug('new_hsh: {0}'.format(new_hsh))
            if msg:
                return "\n".join(msg)
            if 's' not in new_hsh:
                new_hsh['s'] = None
            res = self.append_item(new_hsh, self.currfile, cli=True)
            if res:
                return _("item saved")

    @staticmethod
    def help_N():
        return _("""\
Usage:

    etm n ITEM

Create a new item from ITEM. E.g.,

    etm n '* meeting @s +0 4p @e 1h30m'

The item will be appended to the monthly file for the current month.\
""")

    @staticmethod
    def do_q(line):
        sys.exit()

    @staticmethod
    def help_q():
        return '{0}\n'.format(_("quit"))

    def do_c(self, arg):
        logger.debug('custom spec: {0}, {1}'.format(arg, type(arg)))
        """report (non actions) specification"""
        if not arg:
            return self.help_c()
        res = getReportData(
            arg,
            self.file2uuids,
            self.uuid2hash,
            self.options)
        return res

    @staticmethod
    def help_c():
        return _("""\
Usage:

    etm c <type> <groupby> [options]

Generate a custom view where type is either 'a' (action) or 'c' (composite).
Groupby can include *semicolon* separated date specifications and
elements from:
    c context
    f file path
    k keyword
    t tag
    u user

A *date specification* is either
    w:   week number
or a combination of one or more of the following:
    yy:   2-digit year
    yyyy:   4-digit year
    MM:   month: 01 - 12
    MMM:   locale specific abbreviated month name: Jan - Dec
    MMMM:   locale specific month name: January - December
    dd:   month day: 01 - 31
    ddd:   locale specific abbreviated week day: Mon - Sun
    dddd:   locale specific week day: Monday - Sunday

Options include:
    -b begin date
    -c context regex
    -d depth (CLI a reports only)
    -e end date
    -f file regex
    -k keyword regex
    -l location regex
    -o omit (r reports only)
    -s summary regex
    -S search regex
    -t tags regex
    -u user regex
    -w column 1 width
    -W column 2 width

Example:

    etm c 'c ddd, MMM dd yyyy -b 1 -e +1/1'
""")

    def do_d(self, arg_str):
        if self.calendars:
            cal_pattern = r'^%s' % '|'.join(
                [x[2] for x in self.calendars if x[1]])
            self.cal_regex = re.compile(cal_pattern)
            logger.debug("cal_pattern: {0}".format(cal_pattern))
        self.prevnext = getPrevNext(self.datetimes, self.cal_regex)
        return self.mk_rep('d {0}'.format(arg_str))

    @staticmethod
    def help_d():
        return ("""\
Usage:

    etm d [FILTER]

Show the day view with dated items grouped and sorted by date and type, optionally limited to those containing a case insensitive match for the regex FILTER.\
""")

    def do_p(self, arg_str):
        return self.mk_rep('p {0}'.format(arg_str))

    @staticmethod
    def help_p():
        return ("""\
Usage:

    etm p [FILTER]

Show items grouped and sorted by file path, optionally limited to those containing a case insensitive match for the regex FILTER.\
""")

    def do_t(self, arg_str):
        return self.mk_rep('t {0}'.format(arg_str))

    @staticmethod
    def help_t():
        return ("""\
Usage:

    etm t [FILTER]

Show items grouped and sorted by tag, optionally limited to those containing a case insensitive match for the regex FILTER.\
""")

    def do_v(self, arg_str):
        d = {
            'copyright': '2009-%s' % datetime.today().strftime("%Y"),
            'home': 'www.duke.edu/~dgraham/etmtk',
            'dev': 'daniel.graham@duke.edu',
            'group': "groups.google.com/group/eventandtaskmanager",
            'gpl': 'www.gnu.org/licenses/gpl.html',
            'etmversion': fullversion,
            'platform': platform.platform(terse=1),
            'python': platform.python_version(),
            'dateutil': dateutil_version,
            'pyyaml': yaml.__version__,
            'tkversion': self.tkversion,
            'tkstyle': self.tkstyle,
            'file_encoding': file_encoding,
            'gui_encoding': gui_encoding,
            'term_encoding': term_encoding,
            'github': 'https://github.com/dagraham/etm-tk',
        }
        if not d['tkversion']:  # command line
            d['tkversion'] = 'NA'
        if not d['tkstyle']:  # command line
            d['tkstyle'] = 'NA'
        return _("""\
Event and Task Manager
etmtk {0[etmversion]}

This application provides a format for using plain text files to store events, tasks and other items and a Tk based GUI for creating and modifying items as well as viewing them.

System Information:
  Platform:   {0[platform]}
  Python:     {0[python]}
  Dateutil:   {0[dateutil]}
  PyYaml:     {0[pyyaml]}
  Tk/Tcl
     Version: {0[tkversion]}
     Style:   {0[tkstyle]}
  Encodings
     File:    {0[file_encoding]}
     GUI:     {0[gui_encoding]}
     Term:    {0[term_encoding]}

ETM Information:
  Homepage:
    {0[home]}
  Discussion:
    {0[group]}
  GitHub:
    {0[github]}
  Developer:
    {0[dev]}
  GPL License:
    {0[gpl]}

Copyright {0[copyright]} {0[dev]}. All rights reserved. This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\
""".format(d))

    @staticmethod
    def help_v():
        return _("""\
Display information about etm and the operating system.""")

    @staticmethod
    def help_help():
        return (USAGE)

    def replace_lines(self, fp, oldlines, begline, endline, newlines):
        lines = oldlines
        del lines[begline - 1:endline]
        newlines.reverse()
        for x in newlines:
            lines.insert(begline - 1, x)
        itemstr = "\n".join([unicode(u'%s') % x.rstrip() for x in lines
                             if x.strip()])
        if newlines:
            mode = _("replaced item")
        else:
            mode = _("removed item")
        self.safe_save(fp, itemstr, mode=mode)
        return "break"


def main(etmdir='', argv=[]):
    global lang, trans
    lang = trans = None
    logger.debug("data.main etmdir: {0}, argv: {1}".format(etmdir, argv))
    use_locale = ()
    (user_options, options, use_locale) = get_options(etmdir)
    ARGS = ['a', 'k', 'm', 'n', 'N', 'p', 'c', 'd', 't', 'v']
    QUESTION = s2or3("?")
    if len(argv) > 1:
        for i in range(len(argv)-1):
            j = i+1
            argv[j] = s2or3(argv[j])
        c = ETMCmd(options)
        c.loop = False
        c.number = False
        args = []
        if len(argv) == 2 and argv[1] == QUESTION:
            term_print(USAGE)
        elif len(argv) == 2 and argv[1] == 'v':
            term_print(c.do_v(""))
        elif len(argv) == 3 and QUESTION in argv:
            if argv[1] == QUESTION:
                args = [QUESTION, argv[2]]
            else:
                args = [QUESTION, argv[1]]
            if args[1] not in ARGS:
                term_print(USAGE)
            else:
                argstr = ' '.join(args)
                res = c.do_command(argstr)
                term_print(res)
        elif argv[1] in ARGS:
            for x in argv[1:]:
                x = s2or3(x)
                args.append(x)
            argstr = ' '.join(args)
            opts = {}
            if len(args) > 1:
                try:
                    tmp = str2opts(" ".join(args[1:]), options)
                except:
                    logger.exception('Could not process" {0}'.format(args[1:]))
                    return
                if len(tmp) == 3:
                    opts = str2opts(" ".join(args[1:]), options)[0]
            tt = TimeIt(loglevel=2, label="cmd '{0}'".format(argstr))
            c.loadData()
            res = c.do_command(argstr)
            width1 = 43
            if opts and 'width1' in opts:
                width1 = opts['width1']
            elif options:
                if 'report_width1' in options:
                    width1 = options['report_width1']
                elif 'agenda_width1' in options:
                    width1 = options['agenda_width1']

            width2 = 20
            if opts and 'width2' in opts:
                width2 = opts['width2']
            elif options:
                if 'report_width2' in options:
                    width2 = options['report_width2']
                elif 'agenda_width2' in options:
                    width2 = options['agenda_width2']

            indent = 4
            if options:
                if 'report_indent' in options:
                    indent = options['report_indent']
                elif 'agenda_indent' in options:
                    indent = options['agenda_indent']

            colors = 0
            if options:
                if 'report_colors' in options:
                    colors = options['report_colors']
                elif 'agenda_colors' in options:
                    colors = options['agenda_colors']

            if type(res) is dict:
                logger.debug("data.main res is dict; calling tree2Text width1={0}, width2={1}".format(width1, width2))
                lines = tree2Text(res, indent=indent, width1=width1, width2=width2, colors=colors)[0]
                if lines and not lines[0]:
                    lines.pop(0)
                res = "\n".join(lines)
            tt.stop()

            term_print(res)
        else:
            logger.warn("argv: {0}".format(argv))

if __name__ == "__main__":
    etmdir = ''
    if len(sys.argv) > 1:
        if sys.argv[1] not in ['a', 'c']:
            etmdir = sys.argv.pop(1)
    import doctest
    doctest.testmod()

    main(etmdir, sys.argv)
