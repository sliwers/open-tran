#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-

from xmlrpclib import ServerProxy, MultiCall
import sys

class Fetch:
    def __init__(self, phrases, lang):
        self.__phrases = phrases
        self.__server = ServerProxy("http://localhost:8080")
        self.__lang = lang
        self.__suggs = {}
        self.__idx = 0

    def fetch(self):
        multicall = MultiCall(self.__server)
        for phrase in self.__phrases:
            multicall.suggest(phrase, self.__lang)
        print "suggesting...", len(self.__phrases),
        sys.stdout.flush()
        result = multicall()
        print "done"
        return False

    def suggest(self, phrase):
        return self.__suggs.get(phrase, [])
