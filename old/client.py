#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-

from suggest import TranDB

db = TranDB("C")
db.suggest("couldn't convert from %s to %s", "pl")
