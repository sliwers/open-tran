#!/bin/bash

cd `dirname $0`
export PYTHONPATH=../lib

if [[ -f server.pid ]]; then
    RUNNING=`cat server.pid`
    if kill -0 $RUNNING 2> /dev/null; then
	exit 0
    fi
fi

nohup authbind python server.py > /tmp/ot.out 2> /tmp/ot.err &
