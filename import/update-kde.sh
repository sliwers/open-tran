#!/bin/bash

data_root="$1"
kde_root="$data_root/l10n-kde4"

if [ ! -d $kde_root ]; then
    mkdir $kde_root
fi

cd $kde_root

modules=`svn ls svn://anonsvn.kde.org/home/kde/trunk/l10n-kde4`
for m in $modules; do
    if [ $m == "README" -o $m == "documentation" -o $m == "scripts" ]; then
	continue
    fi
    if test -d $m; then
	cd $m

	echo -n "clean $m..."
	svn cleanup > /dev/null || true
	echo "done."

	echo -n "up $m..."
	svn up > /dev/null || true
	echo "done."

	cd ..
    else
	echo -n "co $m..."
	svn co svn://anonsvn.kde.org/home/kde/trunk/l10n-kde4/$m > /dev/null || true
	echo "done."
    fi
done
