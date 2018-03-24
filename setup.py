# from distutils.core import setup
from setuptools import setup, find_packages
from etmTk.v import version
import glob

import sys

INSTALL_REQUIRES = ["python-dateutil>=1.5", "PyYaml>=3.10"]
EXTRAS_REQUIRE = {"icalendar": ["icalendar>=3.8.4", "pytz>=2015.1"]}

APP = ['etm']


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
    url='https://github.com/dagraham/etm-tk',
    description='event and task manager',
    long_description='manage events and tasks using simple text files',
    platforms='Any',
    license='License :: OSI Approved :: GNU General Public License (GPL)',
    author='Daniel A Graham',
    author_email='dnlgrhm@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows Vista',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: News/Diary',
        'Topic :: Office/Business :: Scheduling'],
    packages=['etmTk'],
    scripts=['etm'],
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    # extras_require={"icalendar": ["icalendar>=3.8.4"]},
    package_data={
        'etmTk': ['icons/*', 'etm.desktop', 'etm.appdata.xml', 'CHANGES', 'etm.1'],
        'etmTk/help' : ['help/UserManual.html'],
        'etmTk/icons': ['icons/*']},
    data_files=[
        ('share/man/man1', ['etmTk/etm.1']),
        ('share/doc/etm', ['etmTk/CHANGES']),
        ('share/icons', glob.glob('etmTk/icons/*.gif')),
        ('share/applications', ['etmTk/etm.desktop']),
        ('share/metainfo', ['etmTk/etm.appdata.xml'])
    ]
)
