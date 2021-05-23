#!/usr/bin/python

#***************************************************************************
#   Copyright (C) 2005 by Umputun                                     *
#   umputun@gmail.com                                                      *
#                                                                          *
#    This program is free software; you can redistribute it and/or modify  *
#    it under the terms of the GNU General Public License as published by  *
#    the Free Software Foundation; either version 2 of the License, or     *
#    (at your option) any later version.                                   *
#                                                                          *
#    This program is distributed in the hope that it will be useful,       *
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#    GNU General Public License for more details.                          *
#                                                                          *
#***************************************************************************

import BaseHTTPServer, SocketServer, threading, Queue, time, httplib, urllib
from rss_builder import RssBuilder
from html_processor import HtmlProcessor
from common import *

class UpgHttpConnection(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_QUIT (self):
        """send 200 OK response, and set server.stop to True"""
        self.send_response(200)
        self.end_headers()
        self.server.stop = True


    def do_GET(self):
        LOG.msg("SRV: GET request. src=%s params=%s" % (self.client_address,  self.path), 0)

        try:
            if self.path == "/":
                self.send_response(200, "")
                self.end_headers()
                self.wfile.write(self.server.getHomePage())
                return True
    
            req_elems = self.path[1:].split('?')
            html_name = req_elems[0]
            if len(req_elems) >1:
                req_params = self.__parseParams(req_elems[1])
            else:
                req_params = None
    
            if self.path.find(".xml") != -1:
                elems = self.path.split(".")
                name = elems[0][1:]
                self.send_response(200, "")
                self.send_header("Content-Type", "text/xml")
                self.end_headers()
                if self.path.find("group_") != -1:
                    group = self.path[7:-4]
                    LOG.msg("SRV: request for group %s" % group, 1)
                    self.wfile.write(self.server.getGroupRss(group).encode('utf-8'))
                else:
                    self.wfile.write(self.server.getRss(name).encode('utf-8'))
                return True
    
            if self.path.find(".mp3") != -1:
                mp3_file = self.path[1:]
                self.send_response(200, "")
                self.send_header("Content-Type", "audio/mpeg")
                self.end_headers()
                ifile = open(mp3_file, 'rb')
                try:
                    self.wfile.write(ifile.read())
                except:
                    LOG.msg("SRV: connection failed during sending %s" % mp3_file, 1)
                return True
    
            data = self.server.getHtmlFile(html_name, req_params)
    
            if data:
                self.send_response(200, "")
                if html_name.find(".html") != -1:
                    self.send_header("Content-Type", "text/html")
                else:
                    self.send_header("Content-Type", "image/jpeg")
    
                self.end_headers()
                self.wfile.write(data)
                return True
            else:
                LOG.msg("SRV: unknownw GET request. src=%s params=%s" % (self.client_address,  self.path), 2)
                self.send_response(404)
                self.end_headers()
        except:
            LOG.msg("SRV: connection failed or terminated", 1)
            #raise

        return False

    def do_POST(self):
        clen = self.headers.getheader('content-length')
        data = self.rfile.read(int(clen))
    
        decoded_data = self.decodeData(data)
        open("upg.xml", "wb").write(decoded_data['Setup'])

        self.server.activateRssBuilder()

        self.send_response(302, "/")
        self.send_header("location", "/")
        self.end_headers()
        return True


    def decodeData(self, data):
        result = {}
        elem_pairs = data.split("&")
        for pair in elem_pairs:
            key, value = pair.split("=")
            decoded = ""
            lines = value.split("%0D%0A")
            for l in lines:
                r = urllib.unquote_plus(l)
                #r = r.replace("'", '`')
                decoded += (r + '\n')
            result[key] = decoded
        return result



    def version_string(self):
        return "UPG Server 0.3.2"

    def log_message(self, msg1, msg2, msg3, msg4):
        #print "LOG", msg1, msg2, msg3, msg4
        pass
        
    def __parseParams(self, req_params):
        result = {}
        prms = req_params.split('&')
        for p in prms:
            spl_p = p.split('=')
            if len(spl_p) == 2:
                result[spl_p[0]] = spl_p[1]
            else:
                result[spl_p[0]] = True
        return result


class UpgHttpServer(BaseHTTPServer.HTTPServer, threading.Thread):

    def __init__(self, port, rss_builder, groups):
        self.__handler_class = UpgHttpConnection
        self.__addr = ('', port) 
        LOG.msg("SRV: listening on port %d" % port, 1)
        self.__rss_builder = rss_builder
        self.__port = port
        self.__ev_terminate = threading.Event()
        self.__html_proc = HtmlProcessor(self.__rss_builder, groups)
        BaseHTTPServer.HTTPServer.__init__(self, self.__addr, self.__handler_class)
        threading.Thread.__init__(self)

    def activateRssBuilder(self):
        self.__rss_builder.activate()

    def reloadRssBuilder(self, rss_builder):
        self.__rss_builder = rss_builder

    def getHomePage(self):
        return self.__html_proc.proc("index.html")

    def getHtmlFile(self, fname, params):
        return self.__html_proc.proc(fname, params)

    def getRss(self, name):
        return self.__rss_builder.getRss(name)

    def getGroupRss(self, group):
        return self.__rss_builder.getGroupRss(group)


    def terminate(self):
        LOG.msg("SRV: received termination request", 0)
        self.__ev_terminate.set()
        conn = httplib.HTTPConnection("localhost:%d" % self.__port)
        conn.request("QUIT", "/")
        conn.getresponse()

    def run(self):
        self.stop = False
        while (not self.__ev_terminate.isSet() ):
            if self.stop:
                break
            self.handle_request()
            time.sleep(0.05)
        LOG.msg("SRV: terminated", 1)


