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
from traceback import print_exc

datadir = sys.argv[1]

iconn = sqlite.connect(datadir + '/ten.db')
icur = iconn.cursor()

word_id = 0

sf = open(datadir + '/../import/step2.sql')
schema = sf.read()
sf.close()


project_names = {}


def define_schema(oconn, ocur):
    ocur.executescript(schema)
    oconn.commit()


def move_projects():
    global project_names
    icur.execute("""
SELECT id, name
FROM projects
ORDER BY id
""")
    for (pid, name) in icur.fetchall():
        project_names[pid] = name


def store_words(oconn, ocur, phraseid, words):
    global word_id
    cnt = 1
    last = words[0]
    for word in words[1:]:
        word_id += 1
        if word == last:
            cnt += 1
            continue
        ocur.execute(u"insert into twords(id, word, phraseid, count) values (?, ?, ?, ?)", \
                         (word_id, last, phraseid, cnt))
        last = word
        cnt = 1
    word_id += 1
    ocur.execute(u"insert into twords(id, word, phraseid, count) values (?, ?, ?, ?)", \
                     (word_id, last, phraseid, cnt))


def move_phrases(oconn, ocur, lang):
    global project_names
    cnt = 0
    lid = 0
    phrase = ""

    icur.execute("""
SELECT DISTINCT phrase, projectid, locationid, flags
FROM phrases_%s
ORDER BY phrase
""" % lang)

    for (nphrase, projectid, nlid, flags) in icur.fetchall():
        if cnt % 5000 == 0:
            print ".",
            sys.stdout.flush()
        cnt += 1
        if phrase != nphrase:
            p = Phrase(nphrase, lang[:2], stem=True)
            length = p.length()
            if length < 1:
                continue
            lid = nlid
            ocur.execute("""
INSERT INTO phrases (id, phrase, length)
VALUES (?, ?, ?)""", (nlid, nphrase, length))
            store_words(oconn, ocur, nlid, p.canonical_list())
            phrase = nphrase
        if lang == "en":
            proj = project_names[projectid]
        else:
            proj = ""
        ocur.execute("""
INSERT INTO locations (locationid, phraseid, project, flags)
VALUES (?, ?, ?, ?)""", (nlid, lid, project_names[projectid], flags))
    oconn.commit()


move_projects()

if len(sys.argv) > 2 and sys.argv[2] == 'local':
    langs = ['de', 'en', 'pl']
else:
    langs = sorted(LANGUAGES)

for lang in langs:
    oconn = sqlite.connect(datadir + '/ten-' + lang + '.db')
    ocur = oconn.cursor()
    print "Moving %s phrases..." % lang,
    sys.stdout.flush()
    try:
        define_schema(oconn, ocur)
        move_phrases(oconn, ocur, lang)
        print "done."
    except Exception, e:
        sys.stderr.write(str(e))
        print_exc()
        print "failed."
    sys.stdout.flush()
    ocur.close()
    oconn.close()

icur.close()
iconn.close()

