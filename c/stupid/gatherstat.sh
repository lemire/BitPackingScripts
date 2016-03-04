#!/bin/bash

function MAIL {
  stat=$1
  error=$2
  echo "gatherstat.sh completed, status $1, error $2" | mail -s "gatherstat.sh completion report" leo@boytsov.info
  exit $stat
}

function DO {
  FLAT_FILE=$1
  BINARY_DIR=$2
  LOG_DIR=$3
  OUT_DIR=$4

  ./onecollectstat.sh  $FLAT_FILE $BINARY_DIR $LOG_DIR $OUT_DIR
  stat=$?
  if [ "$stat" != "0" ] ; then
    MAIL $stat  "onecollectstat.sh failed for $FLAT_FILE $BINARY_DIR $LOG_DIR $OUT_DIR"
  fi 
}

BINARY_DIR=$HOME/GIT/SIMDCompressionAndIntersection
DO $HOME/ClueWeb09Flat/clueweb09.unsorted $BINARY_DIR $HOME/ClueWeb09Flat $HOME/OutStat/ClueWeb09 
DO $HOME/Gov2Flat/gov2.unsorted $BINARY_DIR $HOME/Gov2Flat $HOME/OutStat/Gov2 

MAIL 0 ""

