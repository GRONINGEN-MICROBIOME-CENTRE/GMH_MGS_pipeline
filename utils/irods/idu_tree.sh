#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: $0 : /path/to/collection to analyze for sizes"
    exit 1
fi

IN=$1
# count slashes in base path to identify first-level subfolders
base_slashes=$(echo "$IN" | awk -F"/" '{print NF}')

# get all subcollections
subcols=$(iquest "%s" "SELECT COLL_NAME WHERE COLL_NAME like '${IN}/%'")

for sub in $subcols; do
    # count slashes in this subcollection
    sub_slashes=$(echo "$sub" | awk -F"/" '{print NF}')
    # only first-level subfolders
    if [ "$sub_slashes" -eq $((base_slashes + 1)) ]; then
        bytes=$(iquest "%s" "SELECT sum(DATA_SIZE) WHERE COLL_NAME like '${sub}%'")
        if [ -z "$bytes" ] || [ "$bytes" = "NULL" ]; then
            echo "$sub : No data or access denied"
            continue
        fi
        gb=$(echo "scale=2; $bytes/1024/1024/1024" | bc)
        echo "$sub : ${gb} GB"
    fi
done
