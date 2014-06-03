# from distutils.core import setup
from setuptools import setup, find_packages
from etmTk.v import version
import glob

import sys
if sys.version_info >= (3, 2):
    REQUIRES = ["python-dateutil>=1.5", "PyYaml>=3.10","icalendar>=3.6", "pytz"]
else:
    REQUIRES = ["python>=2.7,<3.0", "python-dateutil>=1.5", "PyYaml>=3.10", "icalendar>=3.5", "pytz"]

APP = ['etm']

# includefiles = ["etmTk/etmlogo.gif", "etmTk/etmlogo.icns", "etmTk/etmlogo.ico"]

OPTIONS = {'build': {'build_exe': 'releases/etmtk-{0}'.format(version)},
              'build_exe': {'icon': 'etmTk/etmlogo.gif', 'optimize': '2',
                            'compressed': 1},
              'build_mac': {'iconfile': 'etmTk/etmlogo.gif',
                            'bundle_name': 'etm'},
              'Executable': {'targetDir': 'releases/etmtk-{0}'.format(version)}
            }

setup(
    name='etmtk',
    version=version,
    include_package_data=True,
    zip_safe=False,
    url='http://people.duke.edu/~dgraham/etmtk',
    description='event and task manager',
    long_description='manage events and tasks using simple text files',
    platforms='Any',
    license='License :: OSI Approved :: GNU General Public License (GPL)',
    author='Daniel A Graham',
    author_email='daniel.graham@duke.edu',
    # options=OPTIONS,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
    # install_requires=REQUIRES,
    # extras_require={"icalendar": EXTRAS},
    # package_data={'etmTk': ['etmlogo.*', 'CHANGES', 'etmtk.desktop', 'etmtk.1', 'etmtk.xpm']},
    package_data={'etmTk': ['etmtk.desktop', 'etmtk.1', 'etmtk.xpm'],
                  'etmTk/help' : ['help/UserManual.html', 'help/UserManual.md']},
    # TODO: fix man, icon, desktop, docs
    data_files=[
        # ('share/doc/etmtk', ['CHANGES']),
        # ('share/icons/etmtk', glob.glob('etmTk/etmlogo.*')),
        ('share/man/man1', ['etmTk/etmtk.1']),
        ('share/pixmaps', ['etmTk/etmtk.xpm']),
        ('share/applications', ['etmTk/etmtk.desktop']),
        ('etmtk',['etmTk/help/UserManual.html']),
        # ('share/doc/etmtk/help/images', glob.glob('etmTk/help/images/*.png')),
    ]
)
