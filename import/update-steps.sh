#!/bin/bash

. update.conf

export PYTHONPATH=$toolkit_path:$data_root/../lib

log="$log_dir/import.log"
err="$log_dir/import.err"
audit="$log_dir/audit.txt"
status="$log_dir/status.txt"

update () {
    script="update-$1.sh"
    if test -z "$2"; then
	proj=$1
    else
	proj=$2
    fi
    echo $proj >> $status
    echo
    echo "===== UPDATING $proj ====" >> $log
    $script $data_root $2 $3 >> $log 2>> $err
}


import_by_fr_po () {
    proj_letter=$1
    proj_dir=$data_root/$2
    for fname in `find "$proj_dir" -name 'fr.po'`; do
	echo $fname >> $log
	pattern=`echo $fname | sed 's/\/fr\.po/\/%LANG%.po/'`
	import_compact.py $proj_letter $data_root "$pattern" >> $log 2>> $err
    done
}


import_by_fr_dir () {
    proj_letter=$1
    proj_dir=$data_root/$2
    for fname in `find "$proj_dir/fr" -name '*.po'`; do
	echo $fname >> $log
	pattern=`echo $fname | sed 's/\/fr\//\/%LANG%\//'`
	import_compact.py $proj_letter $data_root "$pattern" >> $log 2>> $err
    done
}


import_by_fr_mix () {
    proj_letter=$1
    proj_dir=$data_root/$2
    for fname in `find "$proj_dir" -name '*.fr.po'`; do
	echo $fname >> $log
	pattern=`echo $fname | sed 's/\/fr\//\/%LANG%\//' | sed 's/\.fr\.po/.%LANG%.po/'`
	import_compact.py $proj_letter $data_root "$pattern" >> $log 2>> $err
    done
}


rm -f $log $err $audit
date > $log
echo -n "removing broken repos..." >> $log
rm -rf $data_root/suse-i18n
rm -rf $data_root/inkscape
echo "done" >> $log

echo "importing" > $status

update svn debian-installer svn://svn.d-i.alioth.debian.org/svn/d-i/trunk/packages/po
update fedora
update gnome
update svn inkscape-i18n https://inkscape.svn.sourceforge.net/svnroot/inkscape/inkscape/trunk/po
update kde
update mandriva
update svn opensuse-i18n svn://svn.berlios.de/opensuse-i18n/trunk
update xfce

if [ ! -d $data_root/../data ]; then
    mkdir $data_root/../data
fi

rm -rf $data_root/../data/ten*.db*
sqlite3 $data_root/../data/ten.db < $data_root/../import/step1.sql
import_db_init.py $data_root/../data/ten.db >> $log 2>> $err

echo "processing" >> $status

date >> $log

import_by_fr_po D debian-installer
import_by_fr_po R fedora
import_by_fr_po G gnome-po
import_by_fr_po I inkscape-i18n
import_by_fr_dir K l10n-kde4
import_by_fr_po A mandriva
import_by_fr_mix S opensuse-i18n
import_by_fr_po X xfce

date >> $log
rm $status
