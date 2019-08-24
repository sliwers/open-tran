#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-

import sys
from pysqlite2 import dbapi2 as sqlite
from phrase import Phrase, Handlers

dbconn = sqlite.connect("first.db")
mmconn = sqlite.connect(":memory:")

mmcur = mmconn.cursor()
mmcur.execute("""
        create table words (
            word text not null,
            phraseid integer not null,
            count integer not null
        )""")

print "Reading phrases...",
dbcur = dbconn.cursor()
dbcur.execute("select word, phraseid, count from words")
print "done."

print "Storing words...",
sys.stdout.flush()
for (word, phraseid, count) in dbcur:
    mmcur.execute(u"insert into words (word, phraseid, count) values (?, ?, ?)", (word, phraseid, count))

mmconn.commit()
print "done."
