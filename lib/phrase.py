#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-
#  Copyright (C) 2007 Jacek Śliwerski (rzyjontko)
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

import re
from stem import PorterStemmer, SnowballStemmer

stemmers = {
    'da' : SnowballStemmer('danish'),
    'de' : SnowballStemmer('german'),
    'en' : PorterStemmer(),
    'es' : SnowballStemmer('spanish'),
    'fi' : SnowballStemmer('finnish'),
    'fr' : SnowballStemmer('french'),
    'hu' : SnowballStemmer('hungarian'),
    'it' : SnowballStemmer('italian'),
    'nl' : SnowballStemmer('dutch'),
    'no' : SnowballStemmer('norwegian'),
    'pt' : SnowballStemmer('portuguese'),
    'ro' : SnowballStemmer('romanian'),
    'ru' : SnowballStemmer('russian'),
    'sv' : SnowballStemmer('swedish'),
    }


class GenericHandler:
    def __init__(self, connectors):
        self._connectors = sorted(connectors + ["'"])

    def discard(self, word):
        return word.startswith('%') \
            or word.startswith('<') \
            or word in self._connectors
        

class AFHandler(GenericHandler):
    def __init__(self):
        GenericHandler.__init__(self, ["'n", "die"])

class DAHandler(GenericHandler):
    def __init__(self):
        GenericHandler.__init__(self, ["de", "dem", "den", "det", "en", "et"])

class DEHandler(GenericHandler):
    def __init__(self):
        GenericHandler.__init__(self, ["das", "dem", "den", "der", "deren", "des", "dessen", "die", "ein", "eine", "einem", "einen"])

class ENHandler(GenericHandler):
    def __init__(self):
        GenericHandler.__init__(self, ["a", "an", "the"])
    
class ESHandler(GenericHandler):
    def __init__(self):
        GenericHandler.__init__(self, ["el", "la", "las", "los", "una", "uno", "unas", "unos"])

class FRHandler(GenericHandler):
    def __init__(self):
        GenericHandler.__init__(self, ["la", "le", "les", "un", "une"])

class ITHandler(GenericHandler):
    def __init__(self):
        GenericHandler.__init__(self, ["i", "il", "lo", "gli", "la", "le", "un", "uno", "una"])

class NLHandler(GenericHandler):
    def __init__(self):
        GenericHandler.__init__(self, ["de", "een", "het"])

class PLHandler(GenericHandler):
    def __init__(self):
        GenericHandler.__init__(self, ["by"])

class PTHandler(GenericHandler):
    def __init__(self):
        GenericHandler.__init__(self, ["o", "os", "a", "as", "um", "uns", "uma", "umas"])

class SVHandler(GenericHandler):
    def __init__(self):
        GenericHandler.__init__(self, ['de', 'den', 'det', 'en', 'ena', 'ett'])


class Phrase:
    wre = re.compile("([\w'%<]/?(?:[&'_]?\w)*>?)", re.UNICODE)
    dre = re.compile('^\d+$', re.UNICODE)
    xre = re.compile("<\?w*>", re.UNICODE)
    qre = re.compile('"[^"]*"', re.UNICODE)

    __handlers = { "C"  : ENHandler (),
                   "af" : AFHandler (),
                   "da" : DAHandler (),
                   "de" : DEHandler (),
                   "en" : ENHandler (),
                   "es" : ESHandler (),
                   "fr" : FRHandler (),
                   "it" : ITHandler (),
                   "nl" : NLHandler (),
                   "pl" : PLHandler (),
                   "pt" : PTHandler (),
                   "sv" : SVHandler ()}
    __def_handler = GenericHandler ([])

    def __resolve(self, lang):
        lang = lang[:2]
        if lang in self.__handlers:
            return self.__handlers[lang]
        else:
            return self.__def_handler

    def __filterfun(self, word, handler):
        return len(word) < 50 \
            and not re.match(self.dre, word) \
            and not re.match(self.xre, word) \
            and not handler.discard(word)

    def __init__(self, phrase, lang, sort=True, stem=False):
        handler = self.__resolve (lang)
        self._phrase = phrase
        self._wordlist = filter(lambda x: self.__filterfun(x, handler), \
                                map(lambda x: x.replace('_', '').lower(), \
                                    self.wre.findall(phrase)))[:10]
        if stem and lang[:2] in stemmers:
            stemmer = stemmers[lang[:2]]
            self._wordlist = [stemmer.stem(word) for word in self._wordlist]
        if sort:
            self._wordlist.sort()

    def length(self):
        return len(self._wordlist)
    
    def canonical(self):
        return reduce (lambda x, y: x + ' ' + y, self._wordlist, '').lstrip()

    def canonical_list(self):
        return self._wordlist

    def required(self):
        return [m[1:-1] for m in self.qre.findall(self._phrase)][:5]
