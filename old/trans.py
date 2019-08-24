#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-

import gettext2, string, sys, dircache, phrase

from pyPgSQL import PgSQL


conn = PgSQL.connect(database = 'trans3', client_encoding = 'utf-8', unicode_results = 1)
cursor = conn.cursor()
cursor.execute("set client_encoding to unicode")



class Project:
    def __init__(self, name):
        self._name = name
        self._phrases = {}
    
    def culture(self, str):
        lang = str[0:2]
        loc = str[3:5]
        return (lang, loc)

    def _read_mo(self, lang):
        try:
            trans = gettext2.GNUTranslations(open('/usr/share/locale/' + lang + '/LC_MESSAGES/' + self._name + '.mo', 'rb'))
        except Exception:
            return
        culture = self.culture(lang)
        for k, v in trans.catalog.iteritems():
            if type(k) is type(u''):
                msg = k
            else:
                msg, n = k
                if n > 0:
                    continue
            ts = self._phrases.setdefault(msg, {})
            ts[culture] = v

    def read_selected(self, langs):
        for lang in langs:
            try:
                self._read_mo(lang)
            except IOError:
                pass

    def read_all(self):
        self.read_selected(dircache.listdir('/usr/share/locale'))

    def _store_location(self, num):
        cursor.execute(u"insert into locations (project, number) values (%s, %s)", (self._name, num))
        cursor.execute("select currval('locations_id_seq') as id")
        return cursor.fetchone().id

    def _store_canonical(self, sentence, handler):
        if len(sentence) > 500:
            return -1
        phrase = phrase.Phrase(sentence, handler)
        if (phrase.length() < 1):
            return -1
        sys.stdout.flush()
        cursor.execute(u"select add_canonical(%s) as id", phrase.canonical())
        sys.stdout.flush()
        return cursor.fetchone().id
    
    def _store_phrase(self, lid, cid, lang_info, sentence):
        try:
            cursor.execute(u"insert into phrases(locationid, canonicalid, language, culture, phrase) values (%s, %s, %s, %s, %s)", \
                           (lid, cid, lang_info[0], lang_info[1], sentence))
        except:
            print "Couldn't store the following phrase:"
            print repr(sentence)
            sys.exit(1)

    def store(self):
        resolve = Handlers().resolve
        i = 0
        for k, v in self._phrases.iteritems():
            i = i + 1
            loc_id = self._store_location(i)
            can_id = self._store_canonical(k, resolve("en"))
            if can_id == -1:
                continue
            self._store_phrase(loc_id, can_id, ('C', ''), k)
            for cinfo, sentence in v.iteritems():
                can_id = self._store_canonical(sentence, resolve(cinfo[0]))
                if can_id != -1:
                    self._store_phrase(loc_id, can_id, cinfo, sentence)
        conn.commit()
    
    def output_cultures(self):
        for v in self._phrases.itervalues():
            for t in v.iterkeys():
                print " ", t,
            print
            break

    def output_phrases(self, lang):
        handler = DEHandler()
        for v in self._phrases.itervalues():
#            print repr(v[lang])
            print repr(phrase.Phrase(v[lang], handler).canonical())



for file_name in dircache.listdir('/usr/share/locale/fr/LC_MESSAGES'):
    if file_name == "sharutils.mo":
        continue
    proj_name = file_name[:-3]
    print "Processing project: ", proj_name
    sys.stdout.flush()
    proj = Project(proj_name)
    print "  reading...",
    sys.stdout.flush()
    proj.read_all()
    print "done."
    print "  storing...",
    sys.stdout.flush()
    proj.store()
    print "done."
    sys.stdout.flush()

# proj = Project("GConf2")
# proj.read_selected(['de'])
# proj.output_phrases(('de',''))

#p = Phrase('der konnte nicht typname verarbeitet warnung werden', DEHandler())
#print p.canonical()


#trans = gettext2.GNUTranslations(open('/usr/share/locale/pl/LC_MESSAGES/eog.mo', 'rb'))
#for k, v in trans.catalog.iteritems():
#phrase = "rock'n'roll'em"
#cursor.execute(u"insert into phrases (locationid, canonicalid, phrase) values (%s, %s, %s)", (3, 133, "rock'n'roll'em"))
#conn.commit()


conn.close()
