#!/bin/bash

## Setup directories:

_THIS_DIR=$(dirname $0)
_OLD_DIR=$(pwd)


## Build resources if needed.

_BUILD_RESOURCES=0

if [[ ! -e $_THIS_DIR/src/resources.py ]] ; then
  _BUILD_RESOURCES=1
fi

if [[ $_THIS_DIR/src/resources/ -nt $_THIS_DIR/src/resources.py ]] ; then
  _BUILD_RESOURCES=1
fi

if [[ $_BUILD_RESOURCES == "1" ]] ; then
  cd $_THIS_DIR/src/resources/
  python mkresources.py
  cd $_OLD_DIR
fi


## Launch Spyrit, but only check dependencies:

cd $_THIS_DIR/src
errmsg=$(python spyrit.py --check-dependencies-only)
errstate=$?
cd $_OLD_DIR


## Try to find a dialog tool on the computer:

_DIALOG=''

[[ -z $_DIALOG && ! -z $(which zenity) ]]  && _DIALOG="zenity --error --text="
[[ -z $_DIALOG && ! -z $(which kdialog) ]] && _DIALOG="kdialog --error="


## Display the error.

if [[ $errstate != 0 ]] ; then
  echo $errmsg
  [[ ! -z $_DIALOG ]] && $_DIALOG"$errmsg"
  exit $errstate
fi


## Launch Spyrit for real.

cd $_THIS_DIR/src
python spyrit.py $@
errstate=$?
cd $_OLD_DIR

exit $errstate
