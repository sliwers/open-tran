#!/usr/bin/python
# -*- coding: utf-8 -*-
#  Copyright (C) 2010 Jacek Śliwerski (rzyjontko)
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
from datetime import date
from os import stat

datadir = sys.argv[1]


class Project:
    def __init__(self, name, url, icon, branch, lic, expected):
        self.name = name
        self.url = url
        self.icon = icon
        self.branch = branch
        self.lic = lic
        self.expected = expected
        self.min = -1
        self.max = -1
        self.langs = 0
        self.total = 0
        self.eng = 0


languages = {}
projects = {
    'K': Project("KDE",
                 "http://www.kde.org",
                 "/images/kde-logo.png",
                 "trunk",
                 '<a href="http://www.gnu.org/copyleft/gpl.html">GPL</a>(<a href="http://en.wikipedia.org/wiki/KDE#Licensing_issues" rel="nofollow">issues</a>)',
                 170000),

    'M': Project("Mozilla",
                 "http://www.mozilla.org",
                 "/images/mozilla-logo.png",
                 "trunk",
                 '<a href="http://www.mozilla.org/MPL/">MPL</a>/<a href="http://www.gnu.org/copyleft/gpl.html">GPL</a>/<a href="http://www.gnu.org/licenses/lgpl.html">LGPL</a> (<a href="http://en.wikipedia.org/wiki/Mozilla_Firefox#Licensing" rel="nofollow">issues</a>)',
                 15000),

    'G': Project("GNOME",
                 "http://www.gnome.org",
                 "/images/gnome-logo.png",
                 "trunk",
                 '<a href="http://www.gnu.org/copyleft/gpl.html">GPL</a>/<a href="http://www.gnu.org/licenses/lgpl.html">LGPL</a>',
                 500000),

    'D': Project("Debian Installer",
                 "http://www.debian.org/devel/debian-installer/",
                 "/images/debian-logo.png",
                 "level1",
                 '<a href="http://www.gnu.org/copyleft/gpl.html">GPL</a>',
                 1000),

    'F': Project("Cor Jousma",
                 "http://members.chello.nl/~s.hiemstra/kompjtr.htm",
                 "/images/pompelyts.png",
                 "",
                 '<a href="http://www.gnu.org/copyleft">Copyleft</a>',
                 0),

    'S': Project("openSUSE",
                 "http://www.opensuse.org",
                 "/images/suse-logo.png",
                 "trunk",
                 '<a href="http://www.gnu.org/copyleft/gpl.html">GPL</a>',
                 35000),

    'X': Project("XFCE",
                 "http://www.xfce.org",
                 "/images/xfce-logo.png",
                 "master",
                 '<a href="http://www.gnu.org/copyleft/gpl.html">GPL</a>/<a href="http://www.gnu.org/copyleft/lgpl.html">LGPL</a>',
                 9000),

    'I': Project("Inkscape",
                 "http://www.inkscape.org",
                 "/images/inkscape-logo.png",
                 "trunk",
                 '<a href="http://www.gnu.org/copyleft/gpl.html">GPL</a>',
                 4500),

    'O': Project("OpenOffice.org",
                 "http://www.openoffice.org",
                 "/images/oo-logo.png",
                 "",
                 '<a href="http://www.gnu.org/licenses/lgpl.html">LGPL</a>',
                 38000),

    'R': Project("Fedora",
                 "http://fedoraproject.org",
                 "/images/fedora-logo.png",
                 "master",
                 '<a href="http://www.gnu.org/copyleft/gpl.html">GPL</a>',
                 10000),

    'A': Project("Mandriva",
                 "http://www.mandriva.com",
                 "/images/mandriva-logo.png",
                 "trunk",
                 '<a href="http://www.gnu.org/copyleft/gpl.html">GPL</a>',
                 16000)
    }



conn = sqlite.connect(datadir + '/ten.db')
cur = conn.cursor()


for lang in LANGUAGES:
    conn = sqlite.connect(datadir + '/ten-' + lang + '.db')
    cur = conn.cursor()
    cur.execute("""
SELECT substr(project, 1, 1) proj, count(0) cnt
FROM locations
GROUP BY substr(project, 1, 1)""")
    languages[lang] = 0
    for (proj, cnt) in cur.fetchall():
        projects[proj].total += cnt
        projects[proj].langs += 1
        if lang == 'en':
            projects[proj].eng = cnt
        languages[lang] += cnt
    cur.close()
    conn.close()


fprojs = open('/tmp/projects.html', 'w')
fprojs.write('''
<div class="ltr">
<h1>Projects</h1>
<p>
  Latest import was created from the sources updated on %s.
</p>
<table border="1">
  <tr>
    <th>Project</th>
    <th>Branch</th>
    <th>English Phrases</th>
    <th>Total Phrases</th>
    <th>Languages</th>
    <th>License</th>
  </tr>
''' % date.fromtimestamp(stat(datadir + '/ten-en.db').st_ctime).strftime('%B %d, %Y'))

projs = sorted(projects.values(), key = lambda p: p.total, reverse = True)
for project in projs:
    if not project.total:
        continue
    fprojs.write('<tr>\n')
    fprojs.write('\t<td><a href="%s"><img src="%s" alt=""/> %s</a></td>\n' \
        % (project.url, project.icon, project.name))
    fprojs.write('\t<td>%s</td>\n' % project.branch)
    fprojs.write('\t<td align="right">%s</td>\n' % pretty_int(project.eng))
    fprojs.write('\t<td align="right">%s</td>\n' % pretty_int(project.total))
    fprojs.write('\t<td align="right">%d</td>\n' % project.langs)
    fprojs.write('\t<td>%s</td>\n' % project.lic)
    fprojs.write('</tr>\n')

fprojs.write('''
</table>
<p>
  Notice that some of the logos might be copyrighted and their use
  might be restricted.  Open-Tran hosts them in order to make sure
  that they are always available from the same location and in order
  to avoid so-called hot-linking.
</p>
</div>
''')
fprojs.close()

flangs = open('/tmp/languages.html', 'w')
flangs.write('''
<div class="ltr">
<h1>Languages</h1>

<table>
<tr><th>Code</th><th>Language</th><th class="right">Count</th></tr>
''')

for lang in sorted(LANGUAGES):
    flangs.write((u'<tr><td>%s</td><td><a href="http://%s.open-tran.eu">%s</a></td><td align="right">%s</td></tr>\n' % (lang, lang, LANGUAGES[lang], pretty_int(languages[lang]))).encode('utf-8'))

flangs.write('''
</table>
</div>
''')


fails = [proj for proj in projs if proj.eng < proj.expected]
if fails:
    f = open(datadir + '/failed.txt', 'w')
    for fail in fails:
        f.write('%s: %d\n' % (fail.name, fail.eng))
    f.close()
    sys.exit(1)

