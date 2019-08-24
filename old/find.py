#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-

import sys

from pyPgSQL import PgSQL
from optparse import OptionParser
from phrase import Phrase, Handlers

conn = PgSQL.connect(database = 'trans3', client_encoding = 'utf-8', unicode_results = 1)
cursor = conn.cursor()
cursor.execute("set client_encoding to unicode")

parser = OptionParser()
parser.add_option("-s", "--source", dest="source", help="use LANG as source language", metavar="LANG", default="C")
parser.add_option("-d", "--destination", dest="destination", help="use LANG as destination language", metavar="LANG", default="pl")
parser.add_option("-l", "--limit", dest="limit", help="show top N results", metavar="N", default=10)

(options, args) = parser.parse_args()

sentence = ' '.join(args)
phrase = Phrase(sentence, Handlers().resolve(options.source))

query = u"""select dc.id as id, dc.phrase as phrase, min(sp.note) as note, count(*) as cnt
from
(
	select sp.locationid, sp.phrase,
		sc.wordcount - sw.occ - sw.cnt as note
	from
	(
		select canonicalid, count(*) as cnt, sum(occurences) as occ
		from words
		where word in %s
		group by canonicalid
	) as sw join canonicalphrases sc on sw.canonicalid = sc.id join phrases sp on sp.canonicalid = sc.id
	where sp.language = %s
) as sp join phrases dp on sp.locationid = dp.locationid
	join canonicalphrases dc on dc.id = dp.canonicalid
where dp.language = %s
group by dc.id, dc.phrase
order by note asc, cnt desc
limit %s
"""

cursor.execute(query, (phrase.canonical_list(), options.source, options.destination, options.limit))

for row in cursor.fetchall():
    print "  *", repr(row.phrase)
