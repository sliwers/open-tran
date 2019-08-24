#!/bin/bash

data_root="$1"
xfce_root="$data_root/xfce"

if [ -d $xfce_root/xfwm4/.svn ]; then
    rm -rf $xfce_root
fi

if [ ! -d $xfce_root ]; then
    mkdir $xfce_root
fi

cd $xfce_root

xmodules=`wget -o /dev/null -O- http://git.xfce.org | grep 'sublevel-repo[^~]*$' | sed "s/^.*href='\([^']*\)'.*$/\1/"`
for m in $xmodules; do
    dir=`echo $m | sed 's/.*\/\(.*\)\/$/\1/'`
    if test -d $dir; then
	cd $dir

	echo -n "pull $m..."
	git pull > /dev/null || true
	echo "done."

	cd ..
    else
	echo -n "clone $m..."
	git clone "git://git.xfce.org$m" > /dev/null || true
	echo "done."
    fi
done
