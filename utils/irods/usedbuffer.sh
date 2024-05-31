#!/bin/sh

/usr/bin/df -h|grep -E "ltfs|Filesystem"|awk '{print $2"\t"$3"\t"$4"\t"$5}'
