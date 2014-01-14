#!/bin/sh
# python -m cProfile -s time -o etm_qt.profile etm_qt $1
pep8 etm.py etmKv/data.py
pyflakes etm.py etmTk/data.py

