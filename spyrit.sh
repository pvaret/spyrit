#!/bin/bash

## Setup directories:

_THIS_DIR=$(dirname $0)
_OLD_DIR=$(pwd)



## Try to find a dialog tool on the computer, to alert the user in case of
## errors:

_DIALOG=''

[[ -z $_DIALOG && ! -z $(which kdialog 2>/dev/null) ]] && _DIALOG="kdialog --title=Spyrit --error="
[[ -z $_DIALOG && ! -z $(which zenity 2>/dev/null) ]]  && _DIALOG="zenity --title=Spyrit --error --text="



## In some bleeding-edge distros like Arch, 'python' point to Python 3 by
## default. Make sure we'll try our best to use Python 2.

_PYTHON=''
_CANDIDATES="python2 python2.7 python2.6 python2.5 python"

for _ALIAS in $_CANDIDATES ; do
  _PYTHON=$(which $_ALIAS 2>/dev/null)
  if [[ ! -z $_PYTHON ]] ; then
    break
  fi
done



## Did we find a Python 2 install?

if [[ -z $_PYTHON \
      || ! $($_PYTHON -c "import sys ; print sys.version_info[0]") == "2" ]] ; then
  errmsg="Couldn't find a Python 2 interpreter!"
  echo $errmsg
  [[ ! -z $_DIALOG ]] && $_DIALOG"$errmsg"
  exit 1
fi



## Build resources if needed.

_BUILD_RESOURCES=0

if [[ ! -e $_THIS_DIR/src/resources.py ]] ; then
  _BUILD_RESOURCES=1
fi

if [[ $_THIS_DIR/src/resources/ -nt $_THIS_DIR/src/resources.py ]] ; then
  _BUILD_RESOURCES=1
fi

if [[ $_BUILD_RESOURCES == "1" ]] ; then
  cd $_THIS_DIR/src
  $_PYTHON resources/spyrcc.py resources/resources.qrc -o resources.py
  cd $_OLD_DIR
fi



## Launch Spyrit, but only check dependencies:

cd $_THIS_DIR/src
errmsg=$($_PYTHON spyrit.py --check-dependencies-only)
errstate=$?
cd $_OLD_DIR




## Display the error.

if [[ $errstate != 0 ]] ; then
  echo $errmsg
  [[ ! -z $_DIALOG ]] && $_DIALOG"$errmsg"
  exit $errstate
fi



## Launch Spyrit for real.

cd $_THIS_DIR/src
$_PYTHON spyrit.py $@
errstate=$?
cd $_OLD_DIR

exit $errstate
