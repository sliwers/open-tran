#!/usr/bin/python
# -*- coding: utf-8 -*-
#  Copyright (C) 2008 Jacek Śliwerski (rzyjontko)
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 2.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.  

import sys
from phrase import Phrase
from sqlite3 import dbapi2 as sqlite
from common import LANGUAGES

datadir = sys.argv[1]

def move_words(conn, cur, lang):
    cnt = 0
    nwordid = -1
    word = ""

    cur.execute("""
SELECT id, word, phraseid, count
FROM twords
ORDER BY word
""")

    for (wordid, nword, phraseid, count) in cur.fetchall():
        if cnt % 5000 == 0:
            print ".",
            sys.stdout.flush()
        cnt += 1
        if word != nword:
            word = nword
            nwordid = wordid
            cur.execute("INSERT INTO words (id, word) VALUES (?, ?)", (nwordid, nword))
        cur.execute("INSERT INTO wp (wordid, phraseid, count) VALUES (?, ?, ?)", (nwordid, phraseid, count))
    conn.commit()



if len(sys.argv) > 2 and sys.argv[2] == 'local':
    langs = ['de', 'en', 'pl']
else:
    langs = sorted(LANGUAGES)

for lang in langs:
    conn = sqlite.connect(datadir + '/ten-' + lang + '.db')
    cur = conn.cursor()
    print "Moving %s words..." % lang,
    sys.stdout.flush()
    try:
        move_words(conn, cur, lang)
        print "IW",
        sys.stdout.flush()
        cur.execute("CREATE INDEX idx ON words(word)")
        print "IWP1",
        sys.stdout.flush()
        cur.execute("CREATE INDEX wpw ON wp(wordid)")
        print "IWP2",
        sys.stdout.flush()
        cur.execute("CREATE INDEX wpp ON wp(phraseid)")
        print "IL1",
        sys.stdout.flush()
        cur.execute("CREATE INDEX lp ON locations(phraseid)")
        print "IL2",
        sys.stdout.flush()
        cur.execute("CREATE INDEX ll ON locations(locationid)")
        print "D",
        sys.stdout.flush()
        cur.execute("DROP TABLE twords")
        print "V",
        sys.stdout.flush()
        cur.execute("VACUUM")
        print "done."
    except:
        print "failed."
    sys.stdout.flush()
    cur.close()
    conn.close()
