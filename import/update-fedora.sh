#!/bin/bash

data_root="$1"
fedora_root="$data_root/fedora"

# This is a dummy run that should make wget avoid a refresh
wget -o /dev/null -O /dev/null http://git.fedorahosted.org/git/?a=project_index

modules=`wget -o /dev/null -O- http://git.fedorahosted.org/git/?a=project_index | sed 's/ .*//'`

if [ ! -d $fedora_root ]; then
    mkdir $fedora_root
fi

for m in $modules; do
    cd $fedora_root
    if test -d $m; then
	cd $m
	
	echo -n "pull $m..."
	git pull > /dev/null || true
	echo "done."
    else
	echo -n "clone $m..."
	git clone git://git.fedorahosted.org/$m $m > /dev/null || true
	echo "done."
    fi
done
