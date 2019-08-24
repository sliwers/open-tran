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

from common import LANGUAGES
from pysqlite2 import dbapi2 as sqlite
from sys import argv

dbname = argv[1]
conn = sqlite.connect(dbname)
cursor = conn.cursor()

for lang in sorted(LANGUAGES):
    print lang, "..."
    cursor.execute("create table phrases_%s as select * from phrases"
                   % lang)

conn.commit()
