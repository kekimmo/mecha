#!/bin/bash

# Crond might not set this
export LC_CTYPE=fi_FI.UTF-8

MECHA_DIR=$(dirname $(readlink -f $0))
PID_FILE=$MECHA_DIR/mecha.pid
PIPE_FILE=$MECHA_DIR/mecha.fifo
#INPUT_LOG=$MECHA_DIR/wiki.log
MECHA_LOG=$MECHA_DIR/mecha.log
MECHA_ERR=$MECHA_DIR/mecha.err.log
MECHA_CMD=./mecha.py
INPUT_CMD=./desuwiki.py


is_running () {
  if [ -f $PID_FILE ]
  then
    read PID < $PID_FILE
    if kill -0 $PID
    then
      # Running
      return 0
    else
      # Not running, stale PID file
      return 1
    fi
  else
    # Not running, no PID file
    return 1
  fi
}


if ! is_running
then
  # Remove possible stale PID file
  rm -f $PID_FILE
  # Remove possible old pipe
  rm -f $PIPE_FILE
  # Start mecha in the background
  cd $MECHA_DIR
  $MECHA_CMD >> $MECHA_LOG 2>> $MECHA_ERR &
fi

# Pipe new input to mecha
cd $MECHA_DIR
$INPUT_CMD >> $PIPE_FILE

