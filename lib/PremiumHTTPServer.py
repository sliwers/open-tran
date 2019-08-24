#!/usr/bin/env python
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

from DocXMLRPCServer import DocXMLRPCRequestHandler, DocXMLRPCServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ForkingMixIn
from StringIO import StringIO
from signal import signal, alarm, SIGPIPE, SIGALRM, SIG_IGN
from traceback import print_exc
from urlparse import urlparse
from multiprocessing import Lock, Array

import re
import os
import stat
import urllib

__version__ = "250"


def _replace_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def rw_handler(signum, frame):
    raise IOError, 'Read/Write Timeout'


def to_json(obj):
    if obj is None:
        return "null"
    if type(obj) is str or type(obj) is unicode:
        return '"' + obj.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').encode('utf-8') + '"'
    if type(obj) in (int, float, long, bool):
        return str(obj).lower()
    try:
        return "[" + ",".join([to_json(e) for e in obj]) + "]"
    except TypeError:
        return "{" + ",".join(['"' + a + '":' + to_json(getattr(obj, a))
                                for a in dir(obj)
                                if a[0] != '_'
                                and not callable(getattr(obj, a))]) + "}"


class FileWrapper:
    def __init__(self, socket):
        self.socket = socket
        signal(SIGALRM, rw_handler)
        for n in dir(self.socket):
            if not n[0:2] == '__' and n not in ['read', 'readline', 'write']:
                setattr(self, n, getattr(self.socket, n))

    def read(self, size = -1):
        alarm(45)
        result = self.socket.read(size)
        alarm(0)
        return result

    def readline(self, size = -1):
        alarm(45)
        result = self.socket.readline(size)
        alarm(0)
        return result

    def write(self, str):
        alarm(90)
        result = self.socket.write(str)
        alarm(0)
        return result



class ActionError(Exception):
    pass


class PremiumAction(object):
    def __init__(self):
        self.regex = ''

    def execute(self, request, match):
        raise ActionError, 'Empty action'


class PremiumActionServeFile(PremiumAction):
    def __init__(self, regex):
        self.regex = re.compile(regex)

    def execute(self, request, match):
        path = request.translate_path(request.path)
        if os.path.isdir(path):
            index = os.path.join(path, "index.shtml")
            if os.path.exists(index):
                path = index
            else:
                request.send_error(404, "File not found")
                return None
        try:
            f = open(path, 'rb')
            if path.endswith('.html'):
                return request.embed_in_template(f)
	    elif path.endswith('.shtml'):
                return request.process(f)
        except IOError:
            request.send_error(404, "File not found")
            return None
        fs = os.fstat(f.fileno())
        ctype = request.guess_type(path)
        if 'if-none-match' in request.headers and request.headers['if-none-match'] == str(fs[stat.ST_INO]):
            request.send_plain_headers(304, ctype, 0, 0)
            return None
        else:
            request.send_plain_headers(200, ctype, fs[stat.ST_SIZE], fs[stat.ST_INO])
        return f


class PremiumActionJSON(PremiumAction):
    def __init__(self, regex, method):
        self.regex = re.compile(regex)
        self.method = method


    def execute(self, request, match):
        try:
            f = StringIO()
            result = self.method(request)
            f.write(to_json(result))
            f.seek(0)
            request.send_plain_headers(200, "application/json", 0, 0)
            return f
        except Exception, inst:
            request.send_error(500, str(inst))
            print_exc()
            return None


class PremiumActionCustom(PremiumAction):
    def __init__(self, regex, method):
        self.regex = re.compile(regex)
        self.method = method

    def execute(self, request, match):
        try:
            return self.method(request, match)
        except Exception, inst:
            request.send_error(500, str(inst))
            print_exc()
            return None


class PremiumActionRedirect(PremiumAction):
    def __init__(self, mapping):
        self.mapping = mapping
        regex = ''
        for (old, new) in mapping:
            if len(regex) > 0:
                regex += '|'
            regex += '(%s)' % old
        self.regex = re.compile(regex)

    def execute(self, request, match):
        for i in range(match.lastindex + 1):
            if match.groups()[i]:
                request.permanent_redirect(self.mapping[i][1])
                return None
        raise ActionError, 'None of the redirection mappings executed'


class PremiumRequestHandler(SimpleHTTPRequestHandler, DocXMLRPCRequestHandler):
    sys_version = ""
    server_version = "PremiumHTTP/" + __version__
    premre = re.compile("(?P<pre>^.*)<premium:(?P<action>[a-zA-Z0-9_]*) */ *>(?P<post>.*$)")
    substitutes = {}
    actions = []


    def request_init(self):
        pass


    def setup(self):
        self.connection = self.request
        self.rfile = FileWrapper(self.connection.makefile('rb', self.rbufsize))
        self.wfile = FileWrapper(self.connection.makefile('wb', self.wbufsize))


    def shutdown(self, errcode):
        self.send_error(errcode)
        self.wfile.flush()
        self.connection.shutdown(1)


    def permanent_redirect(self, path):
        self.send_response(301)
        self.send_header('Location', path)
        self.end_headers()
        

    def redirect(self, path):
        self.send_response(303)
        self.send_header('Location', path)
        self.end_headers()
        

    def redirect_back(self):
        referer = self.headers['Referer']
        path = urlparse(referer)[2]
        if not path:
            path = '/'
        self.redirect(path)
        return None


    def send_plain_headers(self, code, ctype, length, inode):
        self.send_response(code)
        self.send_header("Content-type", ctype)
        if length != 0:
            self.send_header("Content-Length", str(length))
        if inode != 0:
            self.send_header("ETag", str(inode))
        self.end_headers()


    def process(self, stream, code=200, content="text/html"):
	f = StringIO()
	for line in stream:
            m = re.search(PremiumRequestHandler.premre, line)
            if m:
                subst = PremiumRequestHandler.substitutes.get(m.group('action'))
                f.write(m.group('pre'))
                if subst:
                    subst(self, f)
                f.write(m.group('post'))
            else:
                f.write(line)
        f.flush()
        length = f.tell()
        f.seek(0)
        self.send_plain_headers(code, content, length, 0)
	return f


    def embed_in_given_template(self, text, template, code=200,
                                content="text/html"):
        if not isinstance(template, file):
            template = open(template, 'rb')
        f = StringIO()
        for line in template:
            if line.find('<premium:content/>') != -1:
                if isinstance(text, file):
                    self.copyfile(text, f)
                else:
                    f.write(text)
            else:
                f.write(line)
        f.flush()
        f.seek(0)
	result = self.process(f, code, content)
	f.close()
        return result
        


    def embed_in_template(self, text, code=200):
        template = self.find_template()
        return self.embed_in_given_template(text, template, code)


    def send_head(self):
        for action in PremiumRequestHandler.actions:
            match = re.match(action.regex, self.path)
            if match:
                try:
                    return action.execute(self, match)
                except ActionError, e:
                    self.log_error('Action failed: %s' %e)
                    self.send_error(404, "File not found")
                    return None
        self.send_error(404, "File not found")
        return None

        
    def list_directory(self, path):
        self.send_error(404, "File not found")
        return None


    def do_POST(self):
        self.request_init()
        if self.path == '/RPC2':
            host = self.client_address[0]
            addr = [int(b) for b in host.split('.')]
            addr = (addr[0] << 24) | (addr[1] << 16) | (addr[2] << 8) | addr[3]
            if self.server.add_post_host(addr):
                print "error"
                return self.send_error(409, "Concurrent API alls not allowed")
            try:
                return DocXMLRPCRequestHandler.do_POST(self)
            finally:
                self.server.del_post_host(addr)
        try:
            fname = "post_" + self.path[1:].replace('-', '_')
            if hasattr(self, fname):
                fun = getattr(self, fname)
                data = self.rfile.read(int(self.headers["content-length"]))
                fields = dict([urllib.unquote_plus(x).split('=') for x in data.split('&')])
                f = fun(**fields)
                if f:
                    try:
                        self.copyfile(f, self.wfile)
                    finally:
                        f.close()
            else:
                return self.shutdown(404)
        except Exception, e:
            self.log_error("POST action %s failed: %s" % (self.path, e))
            self.send_error(500)


    def do_GET(self):
        self.request_init()
        if self.path == '/RPC2':
            return DocXMLRPCRequestHandler.do_GET(self)
        return SimpleHTTPRequestHandler.do_GET(self)
        


class PremiumServer(ForkingMixIn, DocXMLRPCServer):
    max_children = 30
    allow_reuse_address = True


    def add_post_host(self, host):
        idx = -1
        for (i, x) in enumerate(self.serving_posts):
            if x == host:
                return True
            if x == 0 and idx == -1:
                idx = i
        self.serving_posts[idx] = host
        return False
        

    def del_post_host(self, host):
        idx = -1
        for (i, x) in enumerate(self.serving_posts):
            if x == host:
                idx = i
                break
        self.serving_posts[idx] = 0

    def __init__(self, addr, handler):
        signal(SIGPIPE, SIG_IGN)
        DocXMLRPCServer.__init__(self, addr, handler)
        self.serving_posts = Array('i', 70)
        self.set_server_title('Premium HTTP Server')
