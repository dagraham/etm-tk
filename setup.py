# from distutils.core import setup
from setuptools import setup
from v import version
import glob

import sys
if sys.version_info >= (3, 2):
    REQUIRES = ["python-dateutil>=1.5", "PyYaml>=3.10"]
    EXTRAS = ["icalendar>=3.6", "pytz"]
else:
    REQUIRES = ["python>=2.7,<3.0", "python-dateutil>=1.5", "PyYaml>=3.10", "icalendar>=3.5"]
    EXTRAS = ["icalendar>=3.5", "pytz"]

setup(
    name='etmtk',
    version=version,
    zip_safe=False,
    url='http://people.duke.edu/~dgraham/etmqt',
    description='event and task manager',
    long_description='manage events and tasks using simple text files',
    platforms='Any',
    license='License :: OSI Approved :: GNU General Public License (GPL)',
    author='Daniel A Graham',
    author_email='daniel.graham@duke.edu',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows XP',
        'Operating System :: Microsoft :: Windows :: Windows Vista',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: News/Diary',
        'Topic :: Office/Business :: Scheduling'],
    packages=['etmTk'],
    scripts=['etm'],
    install_requires=REQUIRES,
    extras_require={"icalendar": EXTRAS},
    package_data={'etmTk': ['version.txt', 'CHANGES']},
    data_files=[
        ('share/doc/etmtk', ['etmTk/version.txt', 'etmTk/CHANGES']),
        ('share/man/man1', ['etmTk/etmtk.1']),
        ('share/pixmaps', ['etmTk/etmtk.xpm']),
        ('share/applications', ['etmTk/applications/etmtk.desktop']),
        ('share/doc/etmtk/help', glob.glob('etmTk/help/*.html')),
        ('share/doc/etmtk/help/images', glob.glob('etmTk/help/images/*.png')),
    ]
)

# import sys
# from cx_Freeze import setup, Executable
#
# executables = [
#         Executable("advanced_1.py"),
#         Executable("advanced_2.py")
# ]
#
# buildOptions = dict(
#         compressed = True,
#         includes = ["testfreeze_1", "testfreeze_2"],
#         path = sys.path + ["modules"])
#
# setup(
#         name = "advanced_cx_Freeze_sample",
#         version = "0.1",
#         description = "Advanced sample cx_Freeze script",
#         options = dict(build_exe = buildOptions),
#         executables = executables, requires=['icalendar', 'pytz'])
