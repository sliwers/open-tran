#!/bin/bash

set -e

local_dir=/home/sliwers/open-tran
log_dir=/var/log

export PYTHONPATH=$local_dir/lib

logout="$log_dir/import.log"
errout="$log_dir/import.err"

echo -n "########## Starting import: " >> $logout
date >> $logout

if file "$local_dir/data" | grep "dataa"; then
    olddir="$local_dir/dataa"
    newdir="$local_dir/datab"
else
    olddir="$local_dir/datab"
    newdir="$local_dir/dataa"
fi

echo -n "########## Downloading the database: " >> $logout
date >> $logout

rm -f $newdir/ten*.db
wget -o /dev/null -O $newdir/ten.db http://ot.leonardof.org/data/ten.db

echo -n "########## Copying Mozilla and OO.o phrases: " >> $logout
date >> $logout
$local_dir/import/import_step1a.py $newdir >> $logout 2>> $errout
echo -n "########## Moving phrases: " >> $logout
date >> $logout
$local_dir/import/import_step2.py $newdir >> $logout 2>> $errout

rm $newdir/ten.db

echo -n "########## Moving words: " >> $logout
date >> $logout
$local_dir/import/import_step3.py $newdir >> $logout 2>> $errout

echo -n "########## Finished " >> $logout
date >> $logout

$local_dir/import/update-switch.sh $local_dir/import

