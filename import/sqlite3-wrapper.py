#!/usr/bin/python

from pysqlite2 import dbapi2 as sqlite
import sys

conn = sqlite.connect(sys.argv[1])
cursor = conn.cursor()
script = sys.stdin.read()
cursor.executescript(script)
conn.commit()
