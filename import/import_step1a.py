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

icur.execute("attach database '%s/mo.db' as 'mo'" % datadir)
icur.execute("insert into projects select * from mo.projects;")

for lang in sorted(LANGUAGES):
    print lang
    icur.execute("""
insert into phrases_%s
select *
from mo.phrases
where lang = '%s'""" % (lang, lang))

iconn.commit()

icur.close()
iconn.close()

