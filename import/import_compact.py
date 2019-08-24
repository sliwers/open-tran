#!/usr/bin/python
# -*- coding: utf-8 -*-
#  Copyright (C) 2007-2010 Jacek Śliwerski (rzyjontko)
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

from translate.storage import factory
from common import LANGUAGES
from phrase import Phrase
from sqlite3 import dbapi2 as sqlite
from os.path import split, exists
from sys import argv

prefix = argv[1]
dbname = argv[2] + '/../data/ten.db'
pattern = argv[3]

conn = sqlite.connect(dbname)
cursor = conn.cursor()

cursor.execute("select id from last_id")
_id = cursor.fetchone()[0]

def next():
    global _id
    _id += 1
    return _id


class ImporterProject(object):

    discarded_phrases = frozenset([
        'Your names',
        'Your emails',
        ])
        
    
    def __init__(self, project_id):
        self.phrase_ids = {}
        self.project_id = project_id


    def store_phrase(self, pid, lid, sentence, flags, lang):
        phrase = Phrase(sentence, lang[:2])
        length = phrase.length()
        if length == 0 or len(sentence) < 2 or length > 10:
            return
        if flags:
            flags = 1
        else:
            flags = 0
        cursor.execute(u"""
insert into phrases_%s
    (projectid, locationid, lang, length, phrase, flags)
values
    (?, ?, ?, ?, ?, ?)
""" % lang, (pid, lid, lang, length, sentence.decode('utf-8'), flags))


    def load_file(self, fname, lang):
        used_keys = set()
        store = factory.getclass('a.po').parsefile(fname)
        for unit in store.units:
            src = unit.source.encode('utf-8')
            if not len(src):
                continue
            if src in ImporterProject.discarded_phrases:
                continue
            dst = unit.target.encode('utf-8')
            key = (src, '::'.join(unit.getlocations())
                   + '::::' + unit.getcontext())
            if key in used_keys:
                continue
            if key in self.phrase_ids:
                pid = self.phrase_ids[key]
            else:
                pid = next()
                self.store_phrase(self.project_id, pid, src, 0, "en")
                self.phrase_ids[key] = pid
            self.store_phrase(self.project_id, pid,
                              dst, unit.isfuzzy(), lang)
            used_keys.add(key)
        return len(store.units)


(dirname, fname) = split(pattern)
fname = fname.replace('%LANG%', '')
if fname == '.po':
    (dirname, fname) = split(dirname)
if fname == 'po':
    (dirname, fname) = split(dirname)
if fname.endswith("..po"):
    fname = fname[:-4]
if fname.endswith(".po"):
    fname = fname[:-3]
name = prefix + '/' + fname

cursor.execute("select max(id) from projects")
project_id = (cursor.fetchone()[0] or 0) + 1

cursor.execute("insert into projects (id, name) values (?, ?)",
               (project_id, name))

lang_dict = {
    'as' : 'as_in',
    'be' : 'be_by',
    'ca_val' : 'ca_valencia',
    'fy' : 'fy_nl',
    'ga' : 'ga_ie',
    'gl' : 'gl_es',
    'hi' : 'hi_in',
    'hy' : 'hy_am',
    'ml' : 'ml_in',
    'mr' : 'mr_in',
    'nb' : 'nb_no',
    'nds' : 'nds_de',
    'nn' : 'nn_no',
    'nso' : 'ns',
    'or' : 'or_in',
    'sr_latn' : 'sr_latin',
    'sv' : 'sv_se',
    'sw' : 'sw_tz',
    'te' : 'te_in',
    've' : 'ven'
    }


def fname_iter_basic(pattern, lang):
    print lang,
    yield pattern.replace('%LANG%', lang)
    try:
        (lang, ctry) = lang.split('_')
        print lang + '_' + ctry.upper(),
        yield pattern.replace('%LANG%', lang + '_' + ctry.upper())
        print lang + '-' + ctry,
        yield pattern.replace('%LANG%', lang + '-' + ctry)
        print lang + '-' + ctry.upper(),
        yield pattern.replace('%LANG%', lang + '-' + ctry.upper())
        if len(ctry) > 2:
            print lang + '@' + ctry,
            yield pattern.replace('%LANG%', lang + '@' + ctry)
            print lang + '@' + ctry[0].upper() + ctry[1:],
            yield pattern.replace('%LANG%',
                                  lang + '@' + ctry[0].upper() + ctry[1:])
    except ValueError:
        print lang + '_' + lang,
        yield pattern.replace('%LANG%', lang + '_' + lang)
        print lang + '-' + lang,
        yield pattern.replace('%LANG%', lang + '-' + lang)
        print lang + '_' + lang.upper(),
        yield pattern.replace('%LANG%', lang + '_' + lang.upper())
        print lang + '-' + lang.upper(),
        yield pattern.replace('%LANG%', lang + '-' + lang.upper())


def fname_iter(pattern, lang):
    for fname in fname_iter_basic(pattern, lang):
        yield fname
    if lang in lang_dict:
        for fname in fname_iter_basic(pattern, lang_dict[lang]):
            yield fname


ip = ImporterProject(project_id)
for lang in sorted(LANGUAGES):
    if lang == 'en':
        continue
    print lang, "...",
    for fname in fname_iter(pattern, lang):
        if exists(fname):
            try:
                ip.load_file(fname, lang)
                print "done",
            except:
                print "error",
            break
    print

cursor.execute("update last_id set id = ?", (_id,))
conn.commit()
