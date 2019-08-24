#!/bin/bash

data_root="$1"
gnome_root="$data_root/gnome-po"

gmodules=`wget -o /dev/null -O- http://svn.gnome.org/viewvc/ | grep 'a href="/viewvc/[^"]' | sed 's/.*\/viewvc\/\([^\/]*\)\/.*/\1/'`

if [ ! -d $gnome_root ]; then
    mkdir $gnome_root
fi

for m in $gmodules; do
    cd $gnome_root
    if test -d $m; then
	cd $m
	
	echo -n "cleanup $m..."
	svn cleanup > /dev/null || true
	echo "done."

	echo -n "up $m..."
	svn up > /dev/null || true
	echo "done."
    else
	echo -n "co $m..."
	svn co http://svn.gnome.org/svn/$m/trunk/po $m > /dev/null || true
	echo "done."
    fi
done
