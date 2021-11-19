from distutils.core import setup

import py2exe, sys, os

includes = [

    "encodings",

    "encodings.utf_8",

]

options = {

    "bundle_files": 1,  # create singlefile exe

    "compressed": 1,  # compress the library archive

    "optimize": 2,  # do optimize

    "dll_excludes": ["WSOCK32.dll", "USER32.dll", "ADVAPI32.dll", "SHELL32.dll", "KERNEL32.dll"],

    "includes": includes,

}

setup(

    options={"py2exe": options},

    console=[{'script': "tui.py"}],

    zipfile=None,

)