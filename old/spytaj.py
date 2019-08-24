#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-

import sys, socket
from pysqlite2 import dbapi2 as sqlite
from phrase import Phrase, Handlers

dbconn = sqlite.connect("first.db")
dbcur = dbconn.cursor()

print "Initializing...",
sys.stdout.flush()
conn = sqlite.connect(":memory:")
cur = conn.cursor()

cur.execute("""
        create table phrases (
            id integer primary key,
            en text not null,
            pl text not null
        )""")

cur.execute("""
        create table words (
            word text not null,
            phraseid  integer not null,
            count integer not null
        )""")

dbcur.execute("select id, en, pl from phrases")
for (id, en, pl) in dbcur:
    cur.execute(u"insert into phrases (id, en, pl) values (?, ?, ?)", (id, en, pl))

dbcur.execute("select word, phraseid, count from words")
for (word, phraseid, count) in dbcur:
    cur.execute(u"insert into words (word, phraseid, count) values (?, ?, ?)", (word, phraseid, count))

cur.execute("create index word_index on words(word)")

conn.commit()
dbconn.close()
print "done."
sys.stdout.flush()

class Candidate:
    def __init__(self, phrase, translation):
        self.phrase = phrase
        self.translation = translation
        self.query_hits = 0
        self.this_hits = 0

    def value(self):
        return self.phrase.length() - self.query_hits - self.this_hits
    
    def comparer(c1, c2):
        c1v = c1.value()
        c2v = c2.value()
        if c1v < c2v:
            return -1
        if c1v > c2v:
            return 1
        return 0

class Query:
    def __init__(self, sentence):
        self._phrase = Phrase(sentence, Handlers().resolve("en"))
        self._candidates = {}

    def _add_candidate(self, row, query_hits):
        phraseid = row[0]
        if phraseid not in self._candidates:
            cursor = conn.cursor()
            cursor.execute(u"select en, pl from phrases where id = ?", (phraseid,))
            nrow = cursor.fetchone()
            en_phrase = Phrase(nrow[0], Handlers().resolve("en"))
            cand = Candidate(en_phrase, nrow[1])
            self._candidates[phraseid] = cand
        else:
            cand = self._candidates[phraseid]
        cand.query_hits += query_hits
        cand.this_hits += row[1]

    def _process_word(self, word, hits):
        cur.execute(u"select phraseid, count from words where word = ?", (word,))
        for row in cur:
            self._add_candidate(row, hits)

    def _get(self):
        length = self._phrase.length()
        if length == 0:
            return
        last_word = self._phrase.canonical_list()[0]
        count = 1
        for word in self._phrase.canonical_list()[1:]:
            if word != last_word:
                self._process_word(last_word, count)
                last_word = word
                count = 1
            else:
                count += 1
        self._process_word(last_word, count)

    def execute(self):
        self._get()
        return sorted(self._candidates.values(), Candidate.comparer)



SELF_PORT = 10003

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', SELF_PORT))
s.setblocking(1)

while 1:
    (data, client) = s.recvfrom(2000)
    print data
    query = Query(data)
    cnt = 0
    response = u""
    for cand in query.execute():
        if cnt == 10:
            break
        else:
            cnt += 1
        response += repr(cand.translation)
    s.sendto(response, client)

conn.close()
