#!/usr/bin/env python

import math
import os
import sys

from setuptools import setup


this_dir = os.path.dirname(__file__)

APPNAME = "Spyrit"  # TODO: get from spyrit itself
VERSION = "0.5dev"  # TODO: get from spyrit itself

RM = "rm"
BUILDDIR = os.path.join(this_dir, "build")
DISTDIR = os.path.join(this_dir, "dist")
IMGGLOB = "%s-*.*.dmg %s-*.*.sparseimage" % (APPNAME, APPNAME)

APP = [os.path.join("..", "..", "%s.py" % APPNAME)]
ICON_FILE = os.path.join("..", "..", "resources", "spyrit-logo.icns")
INCLUDES = ["PyQt5._qt", "sip"]
OPTIONS = {"argv_emulation": True, "iconfile": ICON_FILE, "includes": INCLUDES}

PRUNE = [
    ("Frameworks", "phonon.framework"),
    ("Frameworks", "QtAssistant.framework"),
    ("Frameworks", "QtDBus.framework"),
    ("Frameworks", "QtDesigner.framework"),
    ("Frameworks", "QtHelp.framework"),
    ("Frameworks", "QtOpenGL.framework"),
    ("Frameworks", "QtScript.framework"),
    ("Frameworks", "QtSql.framework"),
    ("Frameworks", "QtSvg.framework"),
    ("Frameworks", "QtTest.framework"),
    ("Frameworks", "QtWebKit.framework"),
    ("Frameworks", "QtXml.framework"),
    ("Frameworks", "QtXmlPatterns.framework"),
    ("Frameworks", "QtGui.framework", "Versions", "5", "QtGui_debug"),
    ("Frameworks", "QtCore.framework", "Versions", "5", "QtCore_debug"),
    ("Frameworks", "QtNetwork.framework", "Versions", "5", "QtNetwork_debug"),
]

HDIUTIL = "hdiutil"
MKDIR = "mkdir"
CP = "cp"
MOUNTROOT = os.path.join(this_dir, "mnt")
CONVERT2SP = "convert %s-template.dmg -format UDSP -o %s-%s" % (
    APPNAME,
    APPNAME,
    VERSION,
)
CONVERT2DMG = "convert %s-%s.sparseimage -format UDBZ -o %s-%s.dmg" % (
    APPNAME,
    VERSION,
    APPNAME,
    VERSION,
)
RESIZE = "resize -size %%sm %s-%s.sparseimage" % (APPNAME, VERSION)
MOUNT = "mount %s-%s.sparseimage -mountroot %s" % (APPNAME, VERSION, MOUNTROOT)
EJECT = "eject %s" % os.path.join(MOUNTROOT, APPNAME)
DUSAGE = "du"
OVERHEAD = 9.1  # Size already taken in empty DMG
APPDIR = os.path.join(this_dir, "dist", "%s.app" % APPNAME, "Contents")
PACKDIR = os.path.join(MOUNTROOT, "%s" % APPNAME, "%s.app" % APPNAME)


def cleanup():

    ## Removes build and dist folders as well as old images before running setup.

    os.system(" ".join([RM, "-rf", BUILDDIR]))
    os.system(" ".join([RM, "-rf", DISTDIR]))
    os.system(" ".join([RM, "-f", IMGGLOB]))


def build():

    ## Uses py2app to create Mac application from source.

    sys.argv.append("py2app")

    setup(
        app=APP, data_files=[], options={"py2app": OPTIONS}, setup_requires=["py2app"]
    )


def prune():

    ## Manually remove Frameworks or libraries we know will NOT be used. This
    ## is a dangerous solution at best but can lead up to a final image 50 to 60%
    ## smaller than the full set.

    for path in PRUNE:

        fullPath = os.path.join(APPDIR, *path)
        os.system(" ".join([RM, "-rf", fullPath]))


def package():

    ## Packages the built .app into a shiny DMG template we'll resize
    ## on the spot to fit the genrated application's size as closely as
    ## possible (to within a couple MB).

    ## We first need to compute the necessary size for our final DMG.
    ## Then we'll resize our template DMG, mount it and copy the app. Then
    ## we unmount it, convert it to a compressed DMG and we're done.

    appSize = os.popen(" ".join([DUSAGE, "-sm", APPDIR])).read().split()[0]
    appSize = float(appSize)
    fullSize = int(math.ceil(appSize + OVERHEAD))

    os.system(" ".join([HDIUTIL, CONVERT2SP]))
    os.system(" ".join([HDIUTIL, RESIZE % fullSize]))

    ## Custom mountpoint must exist

    os.system(" ".join([MKDIR, MOUNTROOT]))

    os.system(" ".join([HDIUTIL, MOUNT]))
    os.system(" ".join([CP, "-R", APPDIR, PACKDIR]))
    os.system(" ".join([HDIUTIL, EJECT]))
    os.system(" ".join([HDIUTIL, CONVERT2DMG]))


if __name__ == "__main__":

    cleanup()
    build()
    prune()
    package()
