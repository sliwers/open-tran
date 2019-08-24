#!/usr/bin/env python
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

import sys
import signal
import os
from TranServer import TranServer

print "loading...",
sys.stdout.flush()

server = TranServer(("", 8080))

f = open(os.path.join(os.path.dirname(sys.argv[0]), 'server.pid'), 'w')
f.write(str(os.getpid()))
f.close()

print "done."
sys.stdout.flush()

server.serve_forever()
