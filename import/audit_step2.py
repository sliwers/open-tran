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
from sqlite3 import dbapi2 as sqlite
from common import LANGUAGES, pretty_int


datadir = sys.argv[1]


conn = sqlite.connect(datadir + '/ten.db')
cur = conn.cursor()

print '''
<div class="ltr">
<h1>Languages</h1>

<table>
<tr><th>Code</th><th>Language</th><th class="right">Count</th></tr>
'''

cur.execute("""
SELECT lang, count(*)
FROM phrases
GROUP BY lang
ORDER BY lang""")
for (lang, cnt) in cur.fetchall():
    if not lang in LANGUAGES:
        continue
    print (u'<tr><td>%s</td><td><a href="http://%s.open-tran.eu">%s</a></td><td align="right">%s</td></tr>' % (lang, lang, LANGUAGES[lang], pretty_int(cnt))).encode('utf-8')

cur.close()
conn.close()

print '''
</table>
</div>
'''
