#!/bin/bash

echo "MEMORY SCANNER!"
THEN=$(date +%s)
TAG=$1
RESULTS_FILE=$(pwd)/results/scan-$TAG.jsonl

rm -rf $RESULTS_FILE 2>/dev/null
touch $RESULTS_FILE

AWK_COMMAND='
{
    if (oc_client_version ~ /4.6/ ){
        if (NF==5) {            # if all 5 columns have values...
            print $1"."$3       # skip short name, concat name and api group
        } 
        else if ($2 ~ /\./) {   # if shortname missing (only apigroup has period(s))
            print $1"."$2       # concat name and api group
        } 
        else {
            print $1            # api group missing, just print name 
        }
    }
    else { 

        # 4.7 or newer 
        # In 4.7, column APIGROUP replaced with APIVERSION
        # APIVERSION appears to be APIGROUP/VERSION (or just VERSION if APIGROUP undef)
        # APIVERSION also appears to be always defined
        # Must remove VERSION from APIGROUP for script to work

        if (NF==5) {                # if all 5 columns have values...
            if ($3 ~ /\//){         # and if APIVERSION contains APIGROUP
                split($3, a, "/")   # remove version
                print $1"."a[1]     # and concat name and api group
            }
            else{                   # but if APIVERSION only contains VERSION
                print $1            # just print name
            }
        } 
        else if ($2 ~ /\./) {       # if shortname missing (only apigroup has period(s))
            if ($2 ~ /\//){         # and if APIVERSION contains APIGROUP
                split($2, a, "/")   # remove version
                print $1"."a[1]     # and concat name and api group
            }
            else{                   # but if APIVERSION only contains VERSION
                print $1            # just print name
            }
        } 
        else {
            print $1                # not really necessary since APIVERSION always set
        }
    }
}
'

OC_CLIENT_VERSION=$(oc version --client | tr -s " " | awk '{split($3, a, "-"); print a[1]}')

ALL_RESOURCES=$(oc api-resources --verbs=list | tr -s " " | awk -v oc_client_version=$OC_CLIENT_VERSION "$AWK_COMMAND" )

for RESOURCE in $ALL_RESOURCES
do
    echo $RESOURCE
    RESOURCE_START=$(date +%s)
    if [[ $RESOURCE  == "NAME.APIGROUP" ]]; then
        continue
    fi

    if [[ $RESOURCE  == "NAME" ]]; then
        continue
    fi

    # echo $RESOURCE >> $RESULTS_FILE 
    OC_GET_JSON=$(oc get $RESOURCE --all-namespaces -o json | jq -c .items )

    if [ -z "${OC_GET_JSON}" ]; then
        OC_GET_JSON="[]"
    fi

    echo "{ \"$RESOURCE\" : $OC_GET_JSON }" | jq -rc '.' >> $RESULTS_FILE
    NOW=$(date +%s)
    SECONDS=$(expr $NOW - $RESOURCE_START)
    echo "$SECONDS seconds"

done

NOW=$(date +%s)
SECONDS=$(expr $NOW - $THEN)
echo "DONE! After $(expr $SECONDS / 60) minutes and $(expr $SECONDS % 60) seconds!"