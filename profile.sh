#!/bin/sh
# python -m cProfile -s time -o etm_qt.profile etm_qt $1
python -m cProfile -s cumtime etm $1 > etm.profile

