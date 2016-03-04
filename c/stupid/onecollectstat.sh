#!/bin/bash
FLAT_FILE=$1
BINARY_DIR=$2
LOG_DIR=$3
OUT_DIR=$4
QUERY_QTY=5000
# The value of this shouldn't affect statistics
PARTITION_QTY=32

if [ "$FLAT_FILE" = "" ] ; then
  echo "Specify FLAT_FILE (1st arg)"
  exit 1
fi

if [ ! -f "$FLAT_FILE" ] ; then
  echo "FLAT_FILE (1st arg) is not a file"
  exit 1
fi

if [ "$BINARY_DIR" = "" ] ; then
  echo "Specify BINARY_DIR (2d arg)"
  exit 1
fi

if [ ! -d "$BINARY_DIR" ] ; then
  echo "BINARY_DIR (2d arg) is not a directory"
  exit 1
fi


if [ "$LOG_DIR" = "" ] ; then
  echo "Specify LOG_DIR (3d arg)"
  exit 1
fi

if [ ! -d "$LOG_DIR" ] ; then
  echo "LOG_DIR (3d arg) is not a directory"
  exit 1
fi


if [ "$OUT_DIR" = "" ] ; then
  echo "Specify OUT_DIR (4th arg)"
  exit 1
fi

if [ ! -d "$OUT_DIR" ] ; then
  echo "OUT_DIR (4th arg) is not a directory"
  exit 1
fi

for log_type in aol 1mq ; do
  $BINARY_DIR/budgetedtest  $FLAT_FILE  $LOG_DIR/${log_type}.txt   -i simd   -p $PARTITION_QTY -b 16 -s s4-bp128-4  -l $QUERY_QTY -B 32 -d 2>&1|tee $OUT_DIR/${log_type}.out
  if [ "$?" != "0" ] ; then
    echo "fail!"
    exit 1
  fi
done

