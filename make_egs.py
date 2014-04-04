#!/usr/bin/env python
from __future__ import print_function  # unicode_literals
from __future__ import absolute_import, division

# Look for files with the suffix '.eg' in the current working directory and its subdirectories and, using the file as a template, create a corresponding etm data file with the suffix '.txt', overwriting any existing file if necessary. In creating these .txt files, a string of the form '!i!' where i is an integer will be replaced by a date either i days after the current date or i days before the current date depending upon whether i is positive or negative.

import sys, datetime, os, os.path, fnmatch, shutil, commands, codecs, copy, re, uuid
from dateutil.rrule import *
from dateutil.parser import parse
from dateutil.relativedelta import *

# limit dates to at most 2 digits to leave anniversary subs untouched
date_regex = re.compile(r'\!(\-?\d{1,2})\!')
start_regex = re.compile(r'\!s\!')
weekday_regex = re.compile(r'\!([a-z]{3})\!')
nextday_regex = re.compile(r'\!([mtwhfau])\!')
lastday_regex = re.compile(r'\!([MTWHFAU])\!')
etmdir_regex = re.compile(r'etmdir\s*=')
etmdata_regex = re.compile(r'etmdata\s*=')
etmActions_regex = re.compile(r'etmActions\s*=')
etmEvents_regex = re.compile(r'etmEvents\s*=')
etmNotes_regex = re.compile(r'etmNotes\s*=')
etmTasks_regex = re.compile(r'etmTasks\s*=')
export_regex = re.compile(r'export\s*=')
anniversary_regex = re.compile(r'\!(\d{4})\!')

oneday = datetime.timedelta(days=1)
today = datetime.date.today()
now = datetime.datetime.now()
hr, min, sec = (now.strftime("%H,%M,%S")).split(",")
timestamp = now.strftime("### %Y-%m-%d %H:%M ###\n")

# added to current time, this will produce an even quarter hour at least
# 15 minutes from now. Used to test alerts.
min = 15-int(min)%15 + 15
sec = int(sec)

type_keys = [x for x in '=^*~!-+%$?#']

starttime = (now + relativedelta(minutes=+min,seconds=-sec)).strftime("%I:%M%p")

monday = parse('mon') # the date of the next monday on or after today
nextday = {}
nextday['m'] = monday               # match !m!
nextday['t'] = monday + oneday      # match !t!
nextday['w'] = monday + 2*oneday    # match !w!
nextday['h'] = monday + 3*oneday    # match !h!
nextday['f'] = monday + 4*oneday    # match !f!
nextday['a'] = monday + 5*oneday    # match !a!
nextday['u'] = monday + 6*oneday    # match !u!

MONDAY = monday - 7*oneday # the last monday before today
lastday = {}
lastday['M'] = MONDAY               # match !M!
lastday['T'] = MONDAY + oneday      # match !T!
lastday['W'] = MONDAY + 2*oneday    # match !W!
lastday['H'] = MONDAY + 3*oneday    # match !H!
lastday['F'] = MONDAY + 4*oneday    # match !F!
lastday['A'] = MONDAY + 5*oneday    # match !A!
lastday['U'] = MONDAY + 6*oneday    # match !U!

def uniqueId():
    return(str(uuid.uuid4()))

# idnum = 0
# def uniqueId():
#     global idnum
#     idnum += 1
#     return("%04d" % idnum)

# def make_rc(d, keep=True):
#     newrc = os.path.join(d, "rc")
#     if keep and os.path.exists(newrc):
#         print("found existing rc, skipping")
#         return()
#     print("making rc file")
#     homedir = os.path.expanduser("~")
#     etmdir = os.path.join(homedir, ".etm")
#     rc = os.path.join(homedir, ".etm", "rc")
#     fo = open(rc, 'r')
#     lines = fo.readlines()
#     lines.append('')
#     fo.close()
#     ok = False
#     for i in range(len(lines)):
#         if etmdir_regex.match(lines[i]):
#             lines[i] = "etmdir = '''%s'''\n" % d
#             ok = True
#         elif etmdata_regex.match(lines[i]):
#             lines[i] = "etmdata = '''%s'''\n" % d
#             ok = True
#         elif export_regex.match(lines[i]):
#             lines[i] = "export = '''%s'''\n" % os.path.join(d, 'export')
#             ok = True
#         elif etmActions_regex.match(lines[i]):
#             lines[i] = "etmActions = '''%s'''\n" % os.path.join(d, 'actns')
#             ok = True
#         elif etmEvents_regex.match(lines[i]):
#             lines[i] = "etmEvents = '''%s'''\n" % os.path.join(d, 'evnts')
#             ok = True
#         elif etmNotes_regex.match(lines[i]):
#             lines[i] = "etmNotes = '''%s'''\n" % os.path.join(d, 'notes')
#             ok = True
#         elif etmTasks_regex.match(lines[i]):
#             lines[i] = "etmTasks = '''%s'''\n" % os.path.join(d, 'tasks')
#             ok = True

#     if ok:
#         fo = open(newrc, 'w')
#         fo.writelines(lines)
#         fo.close()
#     return(ok)

def make_new(d):
    data = os.path.join(d, 'data')
    for path, subdirs, names in os.walk(data):
        for name in names:
            if fnmatch.fnmatch(name, '*.eg'):
                file = os.path.join(path,name)
                process_file(file)
    print("\nmakeing the initial repository commit:")
    cmd = "hg com -A -I 'glob:**.txt' -m 'initial commit'"
    os.system(cmd)

def remove_old(d):
    data = os.path.join(d, 'data')
    hg = os.path.join(data, '.hg')
    if os.path.exists(hg):
        print("    removing", hg)
        shutil.rmtree(hg)
    # init hg repository
    print("    creating hg repository:", data)
    cmd = 'hg init %s' % data
    os.system(cmd)

    for path, subdirs, names in os.walk(data):
        for name in names:
            # print("looking in", path, subdirs, name)
            for pat in ['.*.txt', '*.txt', '*.text', '.*.log', '*.log',
             '.*_actns', '.*_evnts', '.*_tasks', '.*_rmdrs', '.*_notes',
              '.*.bak', '*.pkl',
             ]:
                if fnmatch.fnmatch(name, pat): # and os.path.exists(name):
                    try:
                        # print("    removing", os.path.join(path,name))
                        os.remove(os.path.join(path, name))
                    except:
                        pass

def process_file(eg_file):
    pathname, ext = os.path.splitext(eg_file)
    dir, name = os.path.split(pathname)
    txtfile = os.path.join(dir, "%s.txt" % name)
    # logfile = os.path.join(dir, "%s.log" % name)
    fo = open(eg_file, 'r')
    lines = fo.readlines()
    fo.close()
    # lines.append(' ')
    # mo = open(logfile, 'w')
    fo = open(txtfile, 'w')
    p_line = lines[0]
    grouptask = False
    setId = False
    in_item = False
    for i in range(len(lines)):
        s = lines[i]
        # print("\nline", i, s.rstrip())
        # print["typechar", typechar]
        if s[0] in type_keys:
            typechar = s[0]
        s = start_regex.sub(starttime, s)
        m = date_regex.search(s)
        r = date_regex.finditer(s)
        t = list(s)
        for m in r:
            d = m.expand('today + \\1 * oneday')
            d = eval(d)
            d = d.strftime("%Y-%m-%d")
            ms = m.start()
            me = m.end()
            t[ms] = d
            for j in range(ms+1, me):
                t[j] = ''
            lines[i] = ''.join(t)
        # w = weekday_regex.search(s)
        x = weekday_regex.finditer(s)
        for w in x:
            d = w.expand('parse("\\1")')
            d = eval(d)
            d = d.strftime("%Y-%m-%d")
            ws = w.start()
            we = w.end()
            t[ws] = d
            for j in range(ws+1, we):
                t[j] = ''
            lines[i] = ''.join(t)
        y = nextday_regex.finditer(s)
        for w in y:
            k = w.expand("\\1")
            d = nextday[k]
            d = d.strftime("%Y-%m-%d")
            ws = w.start()
            we = w.end()
            t[ws] = d
            for j in range(ws+1, we):
                t[j] = ''
            lines[i] = ''.join(t)
        z = lastday_regex.finditer(s)
        for w in z:
            k = w.expand("\\1")
            d = lastday[k]
            d = d.strftime("%Y-%m-%d")
            ws = w.start()
            we = w.end()
            t[ws] = d
            for j in range(ws+1, we):
                t[j] = ''
            lines[i] = ''.join(t)
    lines.append('\n')
    fo.writelines(lines)
    fo.close()

if __name__ == "__main__":
    cwd = os.getcwd()
    head, tail = os.path.split(cwd)
    ok_dirs = ['etm-sample', 'etm-prob', 'etm-test', 'etm-empty', 'etmdata-test']
    if sys.argv[-1] == '-h':
        print("""\
usage: python make_egs.py [option]
Options:
    -h:     show this message and exit.
    -r:     remove files matching '*.txt', '*.log', '*_done', '*_evnts',
            '*_jrnl' or '*_tasks' and exit.
Run without an option, remove old files as with '-r' and walk current working
directory (which must be named 'eg') producing new files.
#########     This program must be run from the 'eg' directory     #########""")
    elif tail not in ok_dirs:
        print("""
    The current working directory must have one of the following names
    for this progam to run:
        %s
    This is a safety measure to prevent the accidental removal of files
    not related to the examples.
    """ % "\n        ".join(ok_dirs))
    else:
        if sys.argv[-1] != '-r':
            remove_old(cwd)
            # make_rc(cwd)
            make_new(cwd)
        else:
            remove_old(cwd, rem_rc = True)
