#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-

import gettext2, string, sys, dircache
from pysqlite2 import dbapi2 as sqlite
from phrase import Phrase, Handlers

conn = sqlite.connect("first.db")


class Project:
    def __init__(self, name):
        self._name = name
        self._trans = {}
        self._cursor = conn.cursor()

    def read(self):
        try:
            self._trans = gettext2.GNUTranslations(open('/usr/share/locale/pl/LC_MESSAGES/' + self._name + '.mo', 'rb')).catalog
        except:
            pass

    def _store_word(self, word, phraseid, count):
        self._cursor.execute(u"insert into words (word, phraseid, count) values (?, ?, ?)", (word, phraseid, count))

    def _store_words(self, phraseid, phrase):
        last_word = phrase.canonical_list()[0]
        count = 1
        for word in phrase.canonical_list()[1:]:
            if word != last_word:
                self._store_word(last_word, phraseid, count)
                last_word = word
                count = 1
            else:
                count += 1
        self._store_word(last_word, phraseid, count)

    def _store(self, en, pl):
        phrase = Phrase(en, Handlers().resolve("en"))
        length = phrase.length()
        if length == 0:
            return
        self._cursor.execute(u"insert into phrases (en, pl, length) values (?, ?, ?)", (en, pl, length))
        self._store_words(self._cursor.lastrowid, phrase)

    def store(self):
        for k, v in self._trans.iteritems():
            if type(k) is type(u''):
                msg = k
            else:
                msg, n = k
                if n > 0:
                    continue
            self._store(msg, v)
            


for file_name in dircache.listdir('/usr/share/locale/pl/LC_MESSAGES'):
    if file_name == "sharutils.mo":
        continue
    proj_name = file_name[:-3]
    print "Processing project: ", proj_name
    sys.stdout.flush()
    proj = Project(proj_name)
    print "  reading...",
    sys.stdout.flush()
    proj.read()
    print "done."
    print "  storing...",
    sys.stdout.flush()
    proj.store()
    print "done."
    sys.stdout.flush()

# proj = Project("GConf2")
# proj.read()
# proj.store()

#p = Phrase('der konnte nicht typname verarbeitet warnung werden', DEHandler())
#print p.canonical()


#trans = gettext2.GNUTranslations(open('/usr/share/locale/pl/LC_MESSAGES/eog.mo', 'rb'))
#for k, v in trans.catalog.iteritems():
#phrase = "rock'n'roll'em"
#cursor.execute(u"insert into phrases (locationid, canonicalid, phrase) values (%s, %s, %s)", (3, 133, "rock'n'roll'em"))
#conn.commit()

conn.commit()
conn.close()
