#!/bin/bash

set -e

data_root="$1"
proj_name="$2"
url="$3"
svn_root="$data_root/$proj_name"

if test -d "$svn_root/.svn"; then
    cd $svn_root

    echo -n "cleanup $proj_name..."
    svn cleanup > /dev/null
    echo "done."

    echo -n "up $proj_name..."
    svn up > /dev/null
    echo "done."
else
    rm -rf $svn_root
    echo -n "co $proj_name..."
    cd $data_root
    echo "p" | svn co $url $svn_root 2>&1
    echo "done."
fi
