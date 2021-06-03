#!/bin/bash

if [ "$1" = 'scan' ]; then
    ./login.sh $2 $3 $4
    ./memory-scanner.sh $5
elif [ "$1" = 'diff' ]; then
    if [ -z "${5}"]; then
        python3 ./spot-the-difference.py -f $2 -s $3 -o $4
    else
        python3 ./spot-the-difference.py -f $2 -s $3 -o $4 -c $5
    fi
else
    echo "please use either scan or diff"
fi