#!/bin/sh

MECHA_DIR=$HOME/mecha

cd $MECHA_DIR
./desuwiki.py > pipe 2> wiki-error.log

