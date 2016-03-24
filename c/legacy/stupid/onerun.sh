#!/bin/bash

BINARY_DIR=$1
FLAT_FILE=$2
QUERY_FILE=$3
OPTS=$4

echo "# $BINARY_DIR/budgetedtest  $FLAT_FILE  $QUERY_FILE -b 12 $OPTS -q "

if [ "$FLAT_FILE" = "" ] ; then
  echo "Specify FLAT_FILE (2d arg)"
  exit 1
fi

if [ ! -f "$FLAT_FILE" ] ; then
  echo "FLAT_FILE (2d arg) is not a file"
  exit 1
fi

if [ "$BINARY_DIR" = "" ] ; then
  echo "Specify BINARY_DIR (1st arg)"
  exit 1
fi

if [ ! -d "$BINARY_DIR" ] ; then
  echo "BINARY_DIR (1st arg) is not a directory"
  exit 1
fi


if [ "$QUERY_FILE" = "" ] ; then
  echo "Specify QUERY_FILE (3d arg)"
  exit 1
fi

if [ ! -f "$QUERY_FILE" ] ; then
  echo "QUERY_FILE (3d arg) is not a file"
  exit 1
fi

# -q is a quite mode
$BINARY_DIR/budgetedtest  $FLAT_FILE  $QUERY_FILE -b 12 $OPTS -q  2>&1

if [ "$?" != "0" ] ; then
  echo "fail!"
  exit 1
fi

exit 0
