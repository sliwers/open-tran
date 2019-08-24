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

from PremiumHTTPServer import PremiumServer, PremiumRequestHandler, \
    PremiumActionRedirect, PremiumActionCustom, PremiumActionServeFile, \
    PremiumActionJSON
from datetime import datetime
from suggest import TranDB
from tempfile import NamedTemporaryFile
from phrase import Phrase
from urlparse import urlparse
from Cookie import SimpleCookie
from common import LANGUAGES

import email
import xmlrpclib
import urllib
import posixpath
import os
import sys
import logging


SUGGESTIONS_TXT = {
    'ar': u'﻿ترجمات مُقتَرَحة',
    'be_latin' : u'Prapanavanyja pierakłady',
    'ca' : u'Possibles traduccions',
    'csb': u'Sugerowóny dolmaczënczi',
    'da' : u'Oversćttelsesforslag',
    'de' : u'Übersetzungsvorschläge',
    'el' : u'Προτεινόμενες μεταφράσεις',
    'en' : u'Translation suggestions',
    'es' : u'Sugerencias de traducción',
    'fi' : u'Käännösehdotukset',
    'fr' : u'Traductions suggérées',
    'fy' : u'Oersetsuggestjes',
    'gl' : u'Suxesti&oacute;ns de traduci&oacute;n',
    'he' : u'הצעות לתרגום',
    'hu' : u'Fordítási javaslatok',
    'it' : u'Suggerimenti traduzione',
    'ka' : u'თარგმნის შემოთავაზებები',
    'ko' : u'번역어 제안',
    'pl' : u'Sugestie tłumaczeń',
    'pt_br': u'Sugestões de tradução',
    'sk' : u'Navrhované preklady',
    'sl' : u'Predlogi prevoda',
    'sq' : u'Këshillime përkthimi',
    'sr' : u'Предлози превода',
    'sr_latn' : u'Predlozi prevoda',
    'sv' : u'Översättningsförslag',
    'uk' : u'Запропоновані переклади'
    }


RTL_LANGUAGES = ['ar', 'fa', 'ha', 'he']


logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(levelname)-8s %(message)s',
                    datefmt = '%y-%m-%d|%H:%M',
                    filename = '/var/log/open-tran.log',
                    filemode = 'a')


def _replace_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


class renderer(object):
    def __init__(self):
        self.projects = []
        self.langs = { 'be_latin' : 'be@latin',
                       'en_gb' : 'en_GB',
                       'pt_br' : 'pt_BR',
                       'sr_latn' : 'sr@Latn',
                       'zh_cn' : 'zh_CN',
                       'zh_hk' : 'zh_HK',
                       'zh_tw' : 'zh_TW' }
    
    def clear(self):
        self.projects = []

    def feed(self, project):
        if project["path"][0] == self.name[0]:
            self.projects.append(project)

    def render_icon(self):
        return '<img src="%s" alt="%s"/>' % (self.icon_path, self.name)

    def render_count(self, needplus):
        cnt = reduce(lambda x,y: x + y["count"], self.projects, 0)
        if cnt == 0:
            return None
        if needplus:
            result = " + "
        else:
            result = ""
        if cnt > 1:
            result += "%d&times;" % cnt
        return result

    def render_icon_cnt(self, needplus):
        cnt = self.render_count(needplus)
        if cnt == None:
            return ""
        return  cnt + self.render_icon()
    
    def render_links(self, lang):
        result = []
        for project in self.projects:
            if project["count"] > 1:
                result.append("%d&times;" % project["count"])
            path = self.name + " " + project["path"][2:]
            if project["flags"] == 1:
                result.append('<span class="fuzzy">')
            result.append("%s: %s<br/>\n" % (self.render_link(path), _replace_html(project["orig_phrase"])))
            if project["flags"] == 1:
                result.append('</span>')
        return ''.join(result)

    def render_project_link(self):
        icon = self.render_icon()
        return self.render_link(icon + " " + self.name)


class gnome_renderer(renderer):
    def __init__(self):
        renderer.__init__(self)
        self.name = "GNOME"
        self.icon_path = "/images/gnome-logo.png"
    
    def render_link(self, project):
        return '<a href="http://www.gnome.org/i18n/">%s</a>' % project
    

class kde_renderer(renderer):
    def __init__(self):
        renderer.__init__(self)
        self.name = "KDE"
        self.icon_path = "/images/kde-logo.png"

    def render_link(self, project):
        return '<a href="http://l10n.kde.org/">%s</a>' % project


class mozilla_renderer(renderer):
    def __init__(self):
        renderer.__init__(self)
        self.name = "Mozilla"
        self.icon_path = "/images/mozilla-logo.png"

    def render_link(self, project):
        return '<a href="http://www.mozilla.org/projects/l10n/">%s</a>' % project


class fy_renderer(renderer):
    def __init__(self):
        renderer.__init__(self)
        self.name = "FY"
        self.icon_path = "/images/pompelyts.png"

    def render_link(self, project):
        return '<a href="http://members.chello.nl/~s.hiemstra/kompjtr.htm">%s</a>' % project.replace('FY', 'Cor Jousma')


class di_renderer(renderer):
    def __init__(self):
        renderer.__init__(self)
        self.name = "Debian Installer"
        self.icon_path = "/images/debian-logo.png"

    def render_link(self, project):
        return '<a href="http://d-i.alioth.debian.org/">%s</a>' % project


class suse_renderer(renderer):
    def __init__(self):
        renderer.__init__(self)
        self.name = "SUSE"
        self.icon_path = "/images/suse-logo.png"

    def render_link(self, project):
        return '<a href="http://i18n.opensuse.org/">%s</a>' % project


class xfce_renderer(renderer):
    def __init__(self):
        renderer.__init__(self)
        self.name = "XFCE"
        self.icon_path = "/images/xfce-logo.png"

    def render_link(self, project):
        return '<a href="http://i18n.xfce.org/">%s</a>' % project


class inkscape_renderer(renderer):
    def __init__(self):
        renderer.__init__(self)
        self.name = "Inkscape"
        self.icon_path = "/images/inkscape-logo.png"

    def render_link(self, project):
        return '<a href="http://www.inkscape.org">%s</a>' % project


class openoffice_renderer(renderer):
    def __init__(self):
        renderer.__init__(self)
        self.name = "OpenOffice.org"
        self.icon_path = "/images/oo-logo.png"

    def render_link(self, project):
        return '<a href="http://l10n.openoffice.org">%s</a>' % project


class fedora_renderer(renderer):
    def __init__(self):
        renderer.__init__(self)
        self.name = "Fedora"
        self.icon_path = "/images/fedora-logo.png"

    def render_link(self, project):
        return '<a href="https://translate.fedoraproject.org/">%s</a>' % project

    def feed(self, project):
        if project["path"][0] == 'R':
            self.projects.append(project)


class mandriva_renderer(renderer):
    def __init__(self):
        renderer.__init__(self)
        self.name = "Mandriva"
        self.icon_path = "/images/mandriva-logo.png"

    def render_link(self, project):
        return '<a href="http://wiki.mandriva.com/en/Development/Tasks/Translating">%s</a>' % project

    def feed(self, project):
        if project["path"][0] == 'A':
            self.projects.append(project)


class Suggestion:
    def __init__(self, source, target):
        self.source = source
        self.target = target


RENDERERS = [
    di_renderer(),
    fedora_renderer(),
    fy_renderer(),
    gnome_renderer(),
    inkscape_renderer(),
    kde_renderer(),
    mandriva_renderer(),
    mozilla_renderer(),
    openoffice_renderer(),
    suse_renderer(),
    xfce_renderer()
    ]



class TranRequestHandler(PremiumRequestHandler):
    srclang = None
    dstlang = None
    ifacelang = None
    idx = 1

    PremiumRequestHandler.substitutes['ifacelang'] = lambda request, f: request.write_flag(f)
    PremiumRequestHandler.substitutes['sifacelang'] = lambda request, f: request.write_flag(f, True)
    PremiumRequestHandler.substitutes['ifaceselect'] = lambda request, f: request.write_iface_select(f)
    PremiumRequestHandler.substitutes['srclang'] = lambda request, f: \
        request.write_language_select(f, request.srclang, request.ifacelang)
    PremiumRequestHandler.substitutes['dstlang'] = lambda request, f: \
        request.write_language_select(f, request.dstlang, 'en')
    PremiumRequestHandler.substitutes['searchShortName'] = lambda request, f: \
        f.write('<ShortName>Open-Tran.eu (%s/%s)</ShortName>' \
                    % (request.srclang, request.dstlang))
    PremiumRequestHandler.substitutes['searchTemplateURL'] = lambda request, f:\
        request.write_search_template_url(f)
    PremiumRequestHandler.substitutes['openSearchLink'] = lambda request, f: \
        request.write_opensearch_link(f)
    PremiumRequestHandler.substitutes['phrase'] = lambda request, f: \
        f.write(_replace_html(request.query).replace('"', '&quot;').encode('utf-8'))

    PremiumRequestHandler.actions.append(PremiumActionRedirect([('^/index.html$', '/index.shtml'),
                                                                ('^/API$', '/RPC2')]))
    PremiumRequestHandler.actions.append(PremiumActionCustom('^/suggest', \
        lambda request, match: request.send_search_head()))
    PremiumRequestHandler.actions.append(PremiumActionCustom('^/compare', \
        lambda request, match: request.send_compare_head()))
    PremiumRequestHandler.actions.append(PremiumActionCustom('^/setlang', \
        lambda request, match: request.set_language()))
    PremiumRequestHandler.actions.append(PremiumActionCustom('^/search.xml', \
        lambda request, match: request.send_search_xml()))
    PremiumRequestHandler.actions.append(PremiumActionCustom('^/words.html', \
        lambda request, match: request.send_words()))
    PremiumRequestHandler.actions.append(PremiumActionJSON('^/json/suggest', \
        lambda request: request.json_suggest()))
    PremiumRequestHandler.actions.append(PremiumActionJSON('^/json/supported', \
        lambda request: request.json_supported()))
    PremiumRequestHandler.actions.append(PremiumActionServeFile('^/'))


    def do_logging(self, level, format, *args):
	host = ""
	try:
	    host = self.headers['Host']
	except:
	    pass
	
	logging.log(level, '%s [%s] {%s} %s' % (host, self.ifacelang, self.address_string(), format % args))
        

    def log_error(self, *args):
        self.do_logging(logging.ERROR, *args)

    
    def log_message(self, format, *args):
	self.do_logging(logging.INFO, format, *args)


    def send_error(self, code, message=None):
        try:
            short, explain = self.responses[code]
        except KeyError:
            short, explain = '???', '???'
        if message is None:
            message = short
        self.log_error("code %d, message %s", code, message)
        content = "<h1>%d %s</h1><p>%s</p>" % (code, short, explain)
        content = content.encode('utf-8')
        if self.command != 'HEAD' and code >= 200 and code not in (204, 304):
            f = self.embed_in_template(content, code)
            self.copyfile(f, self.wfile)


    def render_all(self):
        needplus = False
        result = []
        for r in RENDERERS:
            icon = r.render_icon_cnt(needplus)
            if icon != "":
                needplus = True
            result.append(icon)
        return ''.join(result)


    def render_div(self, idx, dstlang):
        result = ''.join([r.render_links(dstlang) for r in RENDERERS])
        return '<div id="sug%d" dir="ltr">%s</div>\n' % (idx, result)


    def render_suggestions(self, suggs, dstlang):
        result = ['<ol>\n']
        for s in suggs:
            fuzzy = reduce(lambda s, p: p["flags"] == 1 and s or '', s["projects"], 'class="fuzzy"')
            result.append('<li value="%d"><a href="javascript:;" %s onclick="return visibility_switch(\'sug%d\')">%s (' % (s["value"], fuzzy, self.idx, _replace_html(s["text"])))
            for r in RENDERERS:
                r.clear()
            for p in s["projects"]:
                for r in RENDERERS:
                    r.feed(p)
            result.append(self.render_all())
            result.append(')</a>')
            result.append(self.render_div(self.idx, dstlang))
            result.append('</li>\n')
            result.append('<script language="JavaScript">visibility_switch("sug%d");</script>' % self.idx)
            self.idx += 1
        result.append('</ol>\n')
        return u''.join(result)


    def render_suggestions_compare(self, suggs, srclang):
        cnt, total = reduce(lambda x, y: (x[0] + 1, x[1] + len(y["text"])), suggs, (0, 0))
        result = ['<ol style="width: %dem">\n' % (total / cnt * 2 / 3)]
        for s in suggs:
            fuzzy = reduce(lambda s, p: p["flags"] == 1 and s or '', s["projects"], 'class="fuzzy"')
            for r in RENDERERS:
                r.clear()
            for p in s["projects"]:
                for r in RENDERERS:
                    r.feed(p)
            cnt = ''
            for r in RENDERERS:
                cnt = r.render_count(False)
                if cnt != None:
                    break
            result.append('<li value="%d">%s<a href="javascript:;" %s onclick="return visibility_switch(\'sug%d\')">%s</a>' % (s["value"], cnt, fuzzy, self.idx, _replace_html(s["text"])))
            result.append(self.render_div(self.idx, srclang))
            result.append('</li>\n')
            result.append('<script language="JavaScript">visibility_switch("sug%d");</script>' % self.idx)
            self.idx += 1
        result.append('</ol>\n')
        return u''.join(result)


    def render_project_link(self, project):
        for r in RENDERERS:
            r.clear()
            if r.name == project:
                return r.render_project_link()


    def dump(self, responses, srclang, dstlang):
        rtl = ''
        if dstlang in RTL_LANGUAGES:
            rtl = ' dir="rtl" style="text-align: right"'
        body = [u'<h1>%s (%s &rarr; %s)</h1><dl%s>'
                % (SUGGESTIONS_TXT.get(self.ifacelang, u'Translation suggestions'),
                   srclang, dstlang, rtl)]
        for key, suggs in responses:
            body.append(u'<di><dt><strong>%s</strong></dt>\n<dd>%s</dd></di>'
                        % (_replace_html(key),
                           self.render_suggestions(suggs, dstlang)))
        body.append(u"</dl>")
        return u''.join(body)


    def dump_compare(self, responses, lang):
        dic = {}
        def cmp_ps(x, y):
            if x[0] not in dic:
                dic[x[0]] = sum([sum([p["count"] for p in e["projects"]])
                                 for e in x[1]])
            if y[0] not in dic:
                dic[y[0]] = sum([sum([p["count"] for p in e["projects"]])
                                 for e in y[1]])
            return cmp(dic[x[0]], dic[y[0]])
            
        rtl = ''
        if lang in RTL_LANGUAGES:
            rtl = ' dir="rtl" style="text-align: right"'
        head = []
        body = []
        for project, suggs in sorted(responses.iteritems(), cmp = cmp_ps,
                                     reverse = True):
            head.append(u'<th>%s</th>' % self.render_project_link(project))
            body.append(u'<td>%s</td>' % self.render_suggestions_compare(suggs, lang))
        return '<table%s>\n<tr>%s</tr>\n<tr>%s</tr>\n</table>' % (rtl, ''.join(head), ''.join(body))


    def suggest(self, text, srclang, dstlang):
        suggs = self.server.suggest2(text, srclang, dstlang)
        return (text, suggs)


    def shutdown(self, errcode):
        self.send_error(errcode)
        self.wfile.flush()
        self.connection.shutdown(1)
        return


    def get_src_dst_languages(self):
        langone = ""
        langtwo = ""
        try:
            langone = self.headers['Host'].split('.')[0].replace('-', '_')
            langtwo = self.headers['Host'].split('.')[1].replace('-', '_')
        except:
	    pass

	try:
	    query = urlparse(self.path)[4]
	    vars = [x.strip().split('=') for x in query.split('&')]
	    langone = filter(lambda x: x[0] == 'src', vars)[0][1]
	    langtwo = filter(lambda x: x[0] == 'dst', vars)[0][1]
	except:
	    pass

        if langone in LANGUAGES and langtwo in LANGUAGES:
            self.srclang = langone
            self.dstlang = langtwo
        elif langone in LANGUAGES:
            self.srclang = langone
            self.dstlang = 'en'

	
    def convert_iface_lang(self, lang):
        lang = lang.lower()
        if lang in SUGGESTIONS_TXT:
            return lang
        for l in sorted(SUGGESTIONS_TXT.keys(), reverse = True):
            i = l.find('_')
	    if i < 0:
		i = len(l)
	    if lang[:i] == l[:i]:
                return l
        return None


    def get_iface_language(self):
	try:
            c = SimpleCookie(self.headers['Cookie'])
            self.ifacelang = self.convert_iface_lang(c['lang'].value)
            if self.ifacelang:
                return
        except:
            pass
        try:
            langs = self.headers['Accept-Language'].split(',')
            for lang in langs:
                self.ifacelang = self.convert_iface_lang(lang)
                if self.ifacelang:
                    return
        except:
            pass
        self.ifacelang = self.convert_iface_lang(self.srclang)
        if self.ifacelang:
            return
	self.ifacelang = self.convert_iface_lang(self.dstlang)
        if self.ifacelang:
            return
        self.ifacelang = "en"
	

    def get_languages(self):
        self.srclang = "en"
	self.dstlang = "en"
	self.ifacelang = "en"
	self.get_src_dst_languages()
	self.get_iface_language()
        if self.srclang == "en" and self.dstlang == "en":
            self.dstlang = self.ifacelang
    
    
    def set_language(self):
        referer = '/'
        try:
            referer = self.headers['Referer'].lower()
            idx = referer.find('open-tran.eu')
            if idx < 0:
                referer = '/'
            else:
                referer = referer[idx + len('open-tran.eu'):]
        except:
            pass
        query = urlparse(self.path)[4]
        idx = query.find('lang=')
        if idx < 0:
            lang = 'en'
        else:
            lang = query[idx + 5:]
        self.send_response(303)
        self.send_header('Location', referer)
        self.send_header('Set-Cookie', 'lang=%s; domain=.open-tran.eu' % lang)
        self.end_headers()
        return None


    def translate_path(self, path):
        return PremiumRequestHandler.translate_path(self, '/' + self.ifacelang + '/' + path)


    def find_template(self):
        path = self.translate_path('/template.html')
        return open(path, 'rb')


    def write_flag(self, f, static = False):
        lang = self.ifacelang
        if lang not in SUGGESTIONS_TXT:
            lang = "en"
        prefix = ""
        if static:
            prefix = "sel-"
        f.write(("""
      <a href="javascript:;" class="jslink" onclick="return visibility_switch('lang_choice');">
        <img src="/images/%sflag-%s.png" alt=""/>&nbsp;%s</a>
""" % (prefix, lang, LANGUAGES[lang])).encode('utf-8'))


    def write_iface_select(self, f):
	for lang in sorted(SUGGESTIONS_TXT.keys()):
	    f.write(('''
<li><a href="/setlang?lang=%s" class="jslink"><img src="/images/flag-%s.png" alt=""/>&nbsp;%s</a></li>
''' % (lang, lang, LANGUAGES[lang])).encode('utf-8'))


    def write_language_select(self, f, chosen, default):
        if chosen == None:
            chose = default
        for code in sorted(LANGUAGES.keys()):
            f.write('<option value="%s"' % code)
            if code == chosen:
                f.write(' selected="selected"')
            f.write('>%s: %s</option>' % (code, LANGUAGES[code].encode('utf-8')))


    def write_search_template_url(self, f):
        if self.dstlang != "en":
            f.write('template="http://%s.%s.' % (self.srclang,
                                                       self.dstlang))
        elif self.srclang != "en":
            f.write('template="http://%s.' % self.srclang)
        else:
            f.write('template="http://%s.' % self.ifacelang)
        f.write('open-tran.eu/suggest/{searchTerms}"')


    def write_opensearch_link(self, f):
        if self.srclang != "en" or self.dstlang != "en" \
                or self.ifacelang != "en":
            f.write('''<link rel="search"
type="application/opensearchdescription+xml"
title="Open-Tran.eu (%s/%s)" href="/search.xml" />'''
                    % (self.srclang, self.dstlang))



    def get_query(self, prefix_len = 8):
        query = None
        plen = len(self.path)
        if plen > prefix_len and self.path[prefix_len] == '/':
            query = urllib.unquote(self.path[prefix_len + 1:])
        elif plen > prefix_len and self.path[prefix_len] == '?':
            try:
                urlquery = urlparse(self.path)[4]
                vars = [x.strip().split('=') for x in urlquery.split('&')]
                query = filter(lambda x: x[0] == 'q', vars)[0][1]
                query = urllib.unquote(query)
            except:
                pass
        if query == None or self.dstlang == None:
            return None
        return query.replace('+', ' ').decode('utf-8')


    def send_search_head(self):
        self.query = self.get_query()
        if self.query == None:
            return self.shutdown(404)
        response = self.dump([self.suggest(self.query, self.srclang, self.dstlang)], self.srclang, self.dstlang).encode('utf-8')
        response += self.dump([self.suggest(self.query, self.dstlang, self.srclang)], self.dstlang, self.srclang).encode('utf-8')
        return self.embed_in_template(response)


    def dump_word(self, num, word, cnt):
        if self.srclang != self.dstlang:
            return u'<li value="%d"><a href="/compare/%s">%s</a> %d</li>' \
                % (num, _replace_html(word), _replace_html(word), cnt)
        else:
            return u'<li value="%d">%s %d</li>' \
                % (num, _replace_html(word), cnt)
    
    
    def dump_words(self, offset, words):
        return u'<ol>' \
            + u''.join([self.dump_word(offset + num + 1, word, cnt)
                       for (num, (word, cnt)) in enumerate(words)]) \
            + u'</ol>' \
            + u'<p><a href="/words.html/%d">next page</a></p>' \
            % (offset / 50 + 2)
        
    
    def words_offset(self):
        try:
            return 50 * (int(self.path[12:]) - 1)
        except ValueError:
            return 0
    
    
    def send_words(self):
        offset = self.words_offset()
        words = self.server.words(self.srclang, offset)
        response = self.dump_words(offset, words)
        response = response.encode('utf-8')
        return self.embed_in_template(response)
    
    
    def send_compare_head(self):
        self.query = self.get_query()
        if self.query == None:
            return self.shutdown(404)
        suggs = self.server.compare(self.query, self.srclang, self.dstlang)
        response = self.dump_compare(suggs, self.srclang).encode('utf-8')
        return self.embed_in_template(response)


    def send_search_xml(self):
        template = PremiumRequestHandler.translate_path(self, '/search.xml')
        return self.embed_in_given_template('', template, 200, 'text/xml')
        

    def json_suggest(self):
        self.query = self.get_query(13)
        if self.query == None:
            return self.shutdown(404)
        return self.server.storage.suggest2(self.query, self.srclang, self.dstlang)


    def json_supported(self):
        return LANGUAGES


    def request_init(self):
        self.query = ""
        self.get_languages()



class TranServer(PremiumServer):

    def __proxy(self, srclang, dstlang):
        for (pred, proxy) in self.shadows:
            if pred(srclang, dstlang):
                return proxy


    def supported(self, lang):
        """
Checks if the service is capable of suggesting translations from or to
'lang' and returns True if it is.
"""
        logging.log(logging.DEBUG, 'supported(%s)' % lang)
        return lang in LANGUAGES


    def suggest3(self, text, srclang, dstlang, maxcount):
        '''
Is equivalent to calling suggest2(text, srclang, dstlang) and limiting
the number of returned records to maxcount.
'''
        logging.log(logging.DEBUG, 'suggest(%s, %s, %s, %d)'\
                        % (text, srclang, dstlang, maxcount))
        proxy = self.__proxy(srclang, dstlang)
        return proxy.suggest3(text, srclang, dstlang, maxcount)


    def suggest2(self, text, srclang, dstlang):
        '''
Translates text from srclang to dstlang.  Each language code must be one
of those displayed in the drop-down list in the search form.

Server sends back a result in the following form:
 * count: integer
 * text: string
 * value: integer
 * projects: list
   * count: integer
   * name: string
   * path: string
   * orig_phrase: string
   * flags: integer

Identical translations are grouped together as one suggestion - the 'count'
tells, how many of them there are.  The value indicates, how good the result
is - the lower, the better.  And the list contains quadruples: name of the
project name, original phrase, count and flags.  The sum of counts in the list
of projects equals the count stored in the suggestion object.  The flags are
currently only used to indicate if the translation is fuzzy (1) or not (0).

As an example consider a call: suggest2("save as", "en", "pl").  The server would
send a list of elements containing the following one:
 * count: 20
 * text: Zapisz jako...
 * value: 1
 * projects[0]:
   * name: GNOME
   * path: G/drgeo
   * orig_phrase: Save As...
   * count: 13
   * flags: 0
 * projects[1]:
   * name: GNOME
   * path: G/gxsnmp
   * orig_phrase: Save as...
   * count: 4
   * flags: 0
 * projects[2]:
   * name: SUSE
   * path: S/kpowersave
   * orig_phrase: Save As ...
   * count: 1
   * flags: 0
 * projects[3]:
   * name: KDE
   * path: K/koffice
   * orig_phrase: Save Document As
   * count: 1
   * flags: 0
 * projects[4]:
   * name: GNOME
   * path: G/gedit
   * orig_phrase: Save As…
   * count: 1
   * flags: 0
'''
        return self.suggest3(text, srclang, dstlang, 100)

    def suggest(self, text, dstlang):
        '''
Is equivalent to calling suggest2(text, "en", dstlang)
'''
        return self.suggest3(text, "en", dstlang, 100)


    def compare2(self, text, src, dst):
        '''
Returns the same results as suggest2, but grouped by the projects.
'''
        logging.log(logging.DEBUG, 'compare(%s, %s, %s)' % (text, src, dst))
        proxy = self.__proxy(src, dst)
        return proxy.compare2(text, src, dst)


    def compare(self, text, lang):
        '''
Returns the same results as suggest, but grouped by the projects.
'''
        logging.log(logging.DEBUG, 'compare(%s, %s)' % (text, lang))
        proxy = self.__proxy(lang, 'en')
        return proxy.compare(text, lang)
    

    def words(self, lang, offset = 0, limit = 50):
        """
Returns the list of most popular words for the given language.
The server will skip offset records from start and return at
most limit records.  Every record in the result set is a pair:
(word, count) where count is the number of occurences of the
word in the database.
"""
        logging.log(logging.DEBUG, 'words(%s, %d, %d)' % (lang, offset, limit))
        proxy = self.__proxy(lang, 'en')
        return proxy.words(lang, offset, limit)

    def __init__(self, addr):
        PremiumServer.__init__(self, addr, TranRequestHandler)
        self.set_server_title('Open-Tran.eu')
        self.set_server_name('Open-Tran.eu XML-RPC API documentation')
        self.set_server_documentation('''
This server exports the following methods through the XML-RPC protocol.
''')
        self.storage = TranDB('../data/')
        #self.register_function(self.suggest3, 'suggest3')
        #self.register_function(self.suggest2, 'suggest2')
        #self.register_function(self.suggest, 'suggest')
        #self.register_function(self.compare, 'compare')
        #self.register_function(self.compare2, 'compare2')
        #self.register_function(self.words, 'words')
        #self.register_function(self.supported, 'supported')
        self.register_introspection_functions()
        self.shadows = [
            (lambda src, dst: True,
             self.storage),
            ]
