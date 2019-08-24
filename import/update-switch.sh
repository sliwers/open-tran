#!/bin/bash

set -e

IMPORTDIR=$1
if [[ -z "$IMPORTDIR" ]]; then
    echo "IMPORTDIR is not defined.  It should point to the import directory."
    exit 1
fi

export PYTHONPATH="$IMPORTDIR/../lib"

if file "$IMPORTDIR/../data" | grep "dataa"; then
    olddir="dataa"
    newdir="datab"
else
    olddir="datab"
    newdir="dataa"
fi

echo "Old directory: $olddir"
echo "New directory: $newdir"

rm -f $IMPORTDIR/../$newdir/failed.txt
$IMPORTDIR/audit_compact.py $IMPORTDIR/../$newdir

cd "$IMPORTDIR/.."
mv /tmp/projects.html server
mv /tmp/languages.html server
rm data
ln -s "$newdir" data
