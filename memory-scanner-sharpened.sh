#!/bin/bash

echo "MEMORY SCANNER!"
THEN=$(date +%s)
TAG=$1
RESULTS_FILE=$(pwd)/results/results-$TAG.txt

rm -rf $RESULTS_FILE 2>/dev/null
touch $RESULTS_FILE

ALL_RESOURCES=$(oc api-resources | tr -s " " | awk '{if (NF==5) {print $1"."$3} else if ($2 ~ /\./) {print $1"."$2} else {print $1}}')

for RESOURCE in $ALL_RESOURCES
do
    if [[ $RESOURCE  == "NAME.APIGROUP" ]]; then
        continue
    fi
    COMMAND="oc get $RESOURCE --all-namespaces -o json | jq '-c .items'"
    echo $RESOURCE >> $RESULTS_FILE 
    oc get $RESOURCE --all-namespaces -o json | jq -c .items >> $RESULTS_FILE
done

NOW=$(date +%s)
SECONDS=$(expr $NOW - $THEN)
echo "DONE! After $(expr $SECONDS / 60) minutes and $(expr $SECONDS % 60) seconds!"