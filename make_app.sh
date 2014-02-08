#!/bin/sh
#pyinstaller --clean --noupx -y --log-level=WARN etmtk.py
cxfreeze3 -OO etmTk/etmtk.py --target-dir ~/etm-tk/dist
