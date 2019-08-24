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
                 224),

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
                 25000)
    }



conn = sqlite.connect(datadir + '/ten.db')
cur = conn.cursor()

sys.stderr.write('Creating index...')
cur.execute("CREATE INDEX IF NOT EXISTS idy ON phrases(projectid)")
conn.commit()
sys.stderr.write('done.\n')


sys.stderr.write('Computing project boundaries...')
cur.execute("""
SELECT substr(name, 1, 1), min(id), max(id)
FROM projects
GROUP BY substr(name, 1, 1)
""")
for (proj, mn, mx) in cur.fetchall():
    projects[proj].min = mn
    projects[proj].max = mx
sys.stderr.write('done.\n')

for proj in projects.values():
    sys.stderr.write(proj.name + '...')
    cur.execute("""
SELECT count(*), count(distinct lang)
FROM phrases
WHERE projectid BETWEEN %d AND %d""" % (proj.min, proj.max))
    (cnt, lcnt) = cur.fetchone()
    proj.total = cnt
    proj.langs = lcnt
    cur.execute("""
SELECT count(*)
FROM phrases
WHERE lang = 'en'
  AND projectid BETWEEN %d AND %d""" % (proj.min, proj.max))
    (cnt,) = cur.fetchone()
    proj.eng = cnt
    sys.stderr.write('done.\n')

cur.close()
conn.close()

print '''
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
''' % date.fromtimestamp(stat(datadir + '/ten.db').st_ctime).strftime('%B %d, %Y')

projs = sorted(projects.values(), key = lambda p: p.total, reverse = True)
for project in projs:
    if not project.total:
        continue
    print '<tr>'
    print '\t<td><a href="%s"><img src="%s" alt=""/> %s</a></td>' \
        % (project.url, project.icon, project.name)
    print '\t<td>%s</td>' % project.branch
    print '\t<td align="right">%s</td>' % pretty_int(project.eng)
    print '\t<td align="right">%s</td>' % pretty_int(project.total)
    print '\t<td align="right">%d</td>' % project.langs
    print '\t<td>%s</td>' % project.lic
    print '</tr>'

print '''
</table>
<p>
  Notice that some of the logos might be copyrighted and their use
  might be restricted.  Open-Tran hosts them in order to make sure
  that they are always available from the same location and in order
  to avoid so-called hot-linking.
</p>
</div>
'''

fails = [proj for proj in projs if proj.eng < proj.expected]
if fails:
    f = open(datadir + '/failed.txt', 'w')
    for fail in fails:
        f.write('%s: %d\n' % (fail.name, fail.eng))
    f.close()
    sys.exit(1)

