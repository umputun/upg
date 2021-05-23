
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

import sys, time, os, os.path, threading, Queue, socket, urlparse
from common import *

TIMEOUT, MAX_TIMEOUTS, MAX_RECONNECTS = 5, 10, 10

class Ripper(threading.Thread):
    def __init__(self, name, params, settings, updated_q, ev_terminate):
        self.__name = name
        self.__params = params
        self.__settings = settings
        self.__updated_q = updated_q
        self.__sock = None
        self.__ev_terminate = ev_terminate

        self.__timeout = TIMEOUT
        if self.__settings.has_key('timeout'):
            self.__timeout = int(self.__settings['timeout'])

        self.__maxtimeouts = MAX_TIMEOUTS
        if self.__settings.has_key('maxtimeouts'):
            self.__maxtimeouts = int(self.__settings['maxtimeouts'])

        self.__maxreconnects = MAX_RECONNECTS
        if self.__settings.has_key('maxreconnects'):
            self.__maxreconnects = int(self.__settings['maxreconnects'])

        self.__maxdays = 0
        if self.__settings.has_key('maxdays'):
            self.__maxdays = int(self.__settings['maxdays'])

        threading.Thread.__init__(self)
        LOG.msg("RIP: created ripper. timeout=%d, max.timeouts=%d, max.reconn=%d" % (self.__timeout,self.__maxtimeouts,self.__maxreconnects), 1)
            

    def run(self):

        if not self.__params[URL]: 
            return

        timestamp = time.time()
        elems = urlparse.urlparse(self.__params[URL])
        ip, port = elems[1].split(':')[0], int(elems[1].split(':')[1])
        request = "GET %s HTTP/1.1\nUser-agent:UPG\n\n" % elems[2]
        self.__connect(ip, port)

        LOG.msg("RIP: send reques %s" % request, 0)
        self.__sock.send(request)

        fname = "%s/%s/%s_%d.upg" % (self.__settings['root'], self.__params[DIR], self.__params[DIR], timestamp)
        duration = self.__params[LEN]
        LOG.msg("RIP: ripping started to %s for url=%s. duration=%d min." % (fname, self.__params[URL], int(duration/60) ), 2)

        fout = None
        timouts, reconnects = 0, 0

        while ( (time.time() - timestamp) < duration and (not self.__ev_terminate.isSet()) ):

            try:
                data = self.__sock.recv(4096)
                #print len(data)
                timouts = 0
            except:
                LOG.msg("RIP: timeout during loading url=%s [%s] )" % (self.__params[URL], fname), 0)

                if timouts > self.__maxtimeouts:
                    LOG.msg("RIP: too many timeouts. reconnecting activated", 2)
                    if reconnects > self.__maxreconnects:
                        LOG.msg("RIP: too many reconnects. ripping of %s termnated" % fname, 3)
                        break
                    self.__close()
                    self.__connect(ip, port)
                    self.__sock.send(request)
                    reconnects += 1
                    timouts = 0
                else:
                    timouts += 1
                continue


            if len(data):
                if not fout:
                    fout = open(fname, "wb")
                fout.write(data)
            else:
                time.sleep(0.1)

        if fout:
            fout.close()
            LOG.msg("RIP: done url=%s [%s]" % (self.__params[URL], fname),  1)
            self.__updated_q.put(fname)
        else:
            LOG.msg("RIP: failed url=%s [%s]" % (self.__params[URL], fname),  1)

        mp3_channel_dir = "%s/%s" % (self.__settings['root'], self.__params[DIR])
        self.__removeObsoleteFiles(mp3_channel_dir)
        self.__close()



    def __connect(self, ip, port):
        LOG.msg("RIP: connect to %s:%d" % (ip, port), 0)
        try:
            self.__sock = None
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.connect( (ip, port))
            self.__sock.settimeout(self.__timeout)
            return self.__sock
        except:
            LOG.msg("RIP: connect to %s:%d failed" % (ip, port), 3)
            return None


    def __close(self):
        try: self.__sock.close()
        except: pass

    def __removeObsoleteFiles(self, mp3dir):
        if self.__maxdays == 0: return
        items = os.listdir(mp3dir)
        for file_dir in items:
            full_file = "%s/%s" % (mp3dir, file_dir)
            if os.path.isdir(full_file): continue
            mtime_file = os.path.getmtime(full_file)

            if (time.time() - mtime_file) > self.__maxdays*3600*24:
                try:
                    os.remove(full_file)
                    LOG.msg("RIP: obsolete file %s deleted" % full_file, 1)
                except:
                    LOG.msg("RIP: can't deleted obsolete file %s " % full_file, 3)


