#!/bin/bash
if [ -z "$1" ]; then
   echo "Usage: irods-du /path/to/collection/"
   echo "NOTE: always end it with '/'"
   exit 1
fi

IN=$1

#echo "SELECT sum(DATA_SIZE) WHERE COLL_NAME = '${IN}'"
bytes=$(iquest "%s" "SELECT sum(DATA_SIZE) WHERE COLL_NAME like '${IN}%'")
if [ -z "$bytes" ] || [ "$bytes" = "NULL" ]; then
    echo "No data found or access denied for: $IN"
    exit 1
fi
mb=$(echo "scale=2; $bytes/1024/1024" | bc)
gb=$(echo "scale=2; $mb/1024" | bc)
if (( $(echo "$gb > 1024" | bc -l) )); then
    tb=$(echo "scale=2; $gb/1024" | bc)
    echo "$IN, ${tb} TB"
elif (( $(echo "$mb > 1024" | bc -l) )); then
    echo "$IN, ${gb} GB"
else
    echo "$IN, ${mb} MB"
fi
