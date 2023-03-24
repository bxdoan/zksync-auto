#!/bin/sh
mkdir -p tmp/
pf="zksync_auto/app.py"
shift
file_name=${pf##*/}
today=$(date '+%Y-%m-%d_%H:%M:%S')
file_name="tmp/${file_name%.*}_${today}.log"
pipenv=/Users/`whoami`/.local/bin/pipenv
echo "Running $pf"
PYTHONPATH=`pwd` $pipenv run python $pf >> $file_name 2>&1
cat $file_name
echo "check file $file_name"