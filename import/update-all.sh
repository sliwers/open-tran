#!/bin/bash

. /home/leonardof/ot.leonardof.org/import/update.conf

export LC_ALL=C
export PATH=$PATH:$data_root/../import

svn up $data_root/../lib > /dev/null 2>&1
svn up $data_root/../import > /dev/null 2>&1

update-steps.sh
