#!/bin/bash

echo "MEMORY SCANNER!"
THEN=$(date +%s)
RESULTS_FILE=$(pwd)/results/results.yaml
RESOURCE_TYPES_FILE=$(pwd)/k8s_resource_types.txt
SEPARATOR="---"

rm -rf $RESULTS_FILE 2>/dev/null
touch $RESULTS_FILE

echo $SEPARATOR >> $RESULTS_FILE
COMMAND="oc get customresourcedefinitions" 
echo "> $COMMAND" >> $RESULTS_FILE
$COMMAND >> $RESULTS_FILE

ALL_CRDS=$(oc get crd | tr -s " " | cut -d " " -f 1)

for CRD in $ALL_CRDS
do
    if [[ $CRD  == "NAME" ]]; then
        continue
    fi
    echo $SEPARATOR >> $RESULTS_FILE
    COMMAND="oc get $CRD --all-namespaces"
    echo "> $COMMAND" >> $RESULTS_FILE 
    $COMMAND >> $RESULTS_FILE
done

#https://kubernetes.io/docs/reference/kubectl/overview/#resource-types
# not capturing k8s events (that's just my choice, we can add it back to the k8s resource list)
ALL_RESOURCE_TYPES=$(cat $RESOURCE_TYPES_FILE)
for RT in $ALL_RESOURCE_TYPES
do
    echo $SEPARATOR >> $RESULTS_FILE
    COMMAND="oc get $RT --all-namespaces"
    echo "> $COMMAND" >> $RESULTS_FILE
    $COMMAND >> $RESULTS_FILE
done

# SHOULD REMOVE AGE COL FROM ALL CRDS

NOW=$(date +%s)
SECONDS=$(expr $NOW - $THEN)
echo "DONE! After $(expr $SECONDS / 60) minutes and $(expr $SECONDS % 60) seconds!"