#!/bin/bash

HOME_DIR=$1

if [ "$HOME_DIR" = "" ] ; then
  echo "Specify HOME_DIR (1st arg)"
  exit 1
fi

if [ ! -d "$HOME_DIR" ] ; then
  echo "HOME_DIR (1st arg) is not a directory"
  exit 1
fi

BINARY_DIR=$2

if [ "$BINARY_DIR" = "" ] ; then
  echo "Specify BINARY_DIR (2d arg)"
  exit 1
fi

if [ ! -d "$BINARY_DIR" ] ; then
  echo "BINARY_DIR (2d arg) is not a directory"
  exit 1
fi

OUTPUT_DIR=$3

if [ "$OUTPUT_DIR" = "" ] ; then
  echo "Specify OUTPUT_DIR (3d arg)"
  exit 1
fi

if [ ! -d "$OUTPUT_DIR" ] ; then
  echo "OUTPUT_DIR (3d arg) is not a directory"
  exit 1
fi

EMAIL=$4

if [ "$EMAIL" = "" ] ; then
  echo "Specify EMAIL (4th arg)"
  exit 1
fi

function MAIL {
  stat=$1
  error=$2
  echo "mainrun.sh completed, status $1, error $2" | mail -s "mainrun.sh completion report" $EMAIL 
  exit $stat
}

### TABLE 4 #####
echo "==============================================================================="
echo "Table 4"
echo "==============================================================================="

for flat_type in ClueWeb09Flat Gov2Flat ; do
  list="sorted unsorted"
  if [ "$flat_type" = "ClueWeb09Flat" ] ; then
    list="unsorted"
  fi 
  for sort_type in $list  ; do
    FLAT_DIR=$HOME_DIR/$flat_type
    FLAT_FILE=$FLAT_DIR/$sort_type
    #for QUERY_FILE in aol.txt 1mq.txt ; do
    for q in 1mq.txt ; do
      QUERY_FILE=$FLAT_DIR/$q
      LOG_FILE=$OUTPUT_DIR/Table4_${flat_type}_${q}_${sort_type}
      echo > $LOG_FILE
      stat=$?
      if [ "$stat" != "0" ] ; then
          MAIL $stat  "onecollectstat.sh cannot create log file $LOG_FILE"
      fi
      echo "*******************************************************************************"
      echo "#####"
      for inter in skipping simd galloping scalar ; do
        echo "## Intersection: $inter"
      
        if [ "$inter" = "skipping" ] ; then
          OPTS="-k 5"
        else
          OPTS="-i $inter"
        fi

        echo "#####################################################################################"
        ./onerun.sh "$BINARY_DIR" "$FLAT_FILE" "$QUERY_FILE" "$OPTS" 2>&1|tee|tee >> $LOG_FILE
        stat=$?
        if [ "$stat" != "0" ] ; then
          MAIL $stat  "onecollectstat.sh failed for  $BINARY_DIR $FLAT_FILE $QUERY_FILE $OPTS"
        fi
        echo "#####################################################################################"
      done
    done
  done
done


### TABLE 5 #####
echo "==============================================================================="
echo "Table 5"
echo "==============================================================================="

for flat_type in ClueWeb09Flat Gov2Flat ; do
  list="sorted unsorted"
  if [ "$flat_type" = "ClueWeb09Flat" ] ; then
    list="unsorted"
  fi 
  for sort_type in $list  ; do
    FLAT_DIR=$HOME_DIR/$flat_type
    FLAT_FILE=$FLAT_DIR/$sort_type
    #for QUERY_FILE in aol.txt 1mq.txt ; do
    for q in 1mq.txt ; do
      QUERY_FILE=$FLAT_DIR/$q
      for B in  "" 8 16 32 ; do
        LOG_FILE=$OUTPUT_DIR/Table5_${flat_type}_${q}_${sort_type}_${B}
        echo > $LOG_FILE
        stat=$?
        if [ "$stat" != "0" ] ; then
            MAIL $stat  "onecollectstat.sh cannot create log file $LOG_FILE"
        fi
        echo "#####"
        for inter in galloping simd ; do
          echo "## Intersection: $inter"
      
          if [ "$B" = "" ] ; then
          # In the case when no bitmaps are used, split the index.
            if [ "$flat_type" = "ClueWeb09Flat" ] ; then
              B_OPTS="-p 64"
            else
              B_OPTS="-p 32"
            fi
          else
            B_OPTS="-B $B"
          fi

          if [ "$inter" = "simd" ] ; then
            clist="s4-bp128-4 s4-bp128-m s4-bp128-2 s4-bp128-1 s4-fastpfor-1"
          else
            clist="fastpfor varint"
          fi
          for codec in $clist ; do
              echo "## Codec: $codec "
              OPTS="$B_OPTS -s $codec -i $inter "
              echo "#####################################################################################"
              ./onerun.sh "$BINARY_DIR" "$FLAT_FILE" "$QUERY_FILE" "$OPTS" 2>&1|tee|tee >> $LOG_FILE
              stat=$?
              if [ "$stat" != "0" ] ; then
                  MAIL $stat  "onecollectstat.sh failed for  $BINARY_DIR $FLAT_FILE $QUERY_FILE $OPTS"
              fi 
              echo "#####################################################################################"
          done
        done
      done
    done
  done
done

### TABLE 5 (split bitmaps) #####
echo "==============================================================================="
echo "Table 5(split bitmaps) "
echo "==============================================================================="

for flat_type in ClueWeb09Flat Gov2Flat ; do
  list="sorted unsorted"
  if [ "$flat_type" = "ClueWeb09Flat" ] ; then
    list="unsorted"
  fi 
  for sort_type in $list  ; do
    FLAT_DIR=$HOME_DIR/$flat_type
    FLAT_FILE=$FLAT_DIR/$sort_type
    #for QUERY_FILE in aol.txt 1mq.txt ; do
    for q in 1mq.txt ; do
      QUERY_FILE=$FLAT_DIR/$q
      for B in  8 16 32 ; do
        LOG_FILE=$OUTPUT_DIR/Table5_SplitBitmap_${flat_type}_${q}_${sort_type}_${B}
        echo > $LOG_FILE
        stat=$?
        if [ "$stat" != "0" ] ; then
            MAIL $stat  "onecollectstat.sh cannot create log file $LOG_FILE"
        fi
        echo "#####"
        for inter in galloping simd ; do
          echo "## Intersection: $inter"
      
          # In the case when no bitmaps are used, split the index.
          if [ "$flat_type" = "ClueWeb09Flat" ] ; then
            B_OPTS="-p 64"
          else
            B_OPTS="-p 32"
          fi

          if [ "$inter" = "simd" ] ; then
            clist="s4-bp128-4 s4-bp128-m s4-bp128-2 s4-bp128-1 s4-fastpfor-1"
          else
            clist="fastpfor varint"
          fi
          for codec in $clist ; do
              echo "## Codec: $codec "
              OPTS="$B_OPTS -s $codec -i $inter "
              echo "#####################################################################################"
              ./onerun.sh "$BINARY_DIR" "$FLAT_FILE" "$QUERY_FILE" "$OPTS" 2>&1|tee|tee >> $LOG_FILE
              stat=$?
              if [ "$stat" != "0" ] ; then
                  MAIL $stat  "onecollectstat.sh failed for  $BINARY_DIR $FLAT_FILE $QUERY_FILE $OPTS"
              fi 
              echo "#####################################################################################"
          done
        done
      done
    done
  done
done


MAIL 0 ""
