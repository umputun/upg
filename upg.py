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


import sys, time, os, stat, signal, Queue, shutil
from UPG.common import *
from UPG.rss_builder import RssBuilder
from UPG.scheduler import Scheduler
import UPG.upg_conf, UPG.http_server

HTTPSRV, SCHED = None, None
WAS_TERM = False

def sig_handler(signum, frame):
    LOG.msg("UPG: signal handler called with signal %d" % signum, 2)
    HTTPSRV.terminate()
    SCHED.terminate()
    time.sleep(1)
    sys.exit(0)


        

if __name__ == "__main__":
    LOG.msg("UPG: started", 2)
    signal.signal(signal.SIGINT, sig_handler)

    conf = UPG.upg_conf.UpgConfig()
    conf.parse()

    updated_q = Queue.Queue()
    settings = conf.getSettings()

    sched = Scheduler(settings, conf, updated_q)
    SCHED = sched

    rss_builder = RssBuilder(settings, conf.getChannels(), conf.getGroups())
    rss_builder.activate()

    u_server = UPG.http_server.UpgHttpServer(int(settings['port']), rss_builder, conf.getGroups())
    HTTPSRV = u_server
    u_server.start()


    while(not WAS_TERM):

        if conf.wasUpdated():
            LOG.msg("UPG: XML config updated", 1)
            conf.parse()
            sched.setConf(conf)
            rss_builder.setConf(conf.getChannels())
            u_server.reloadRssBuilder(rss_builder)
            rss_builder.activate()

        sched.check()

        if not updated_q.empty():
            fname = updated_q.get()
            shutil.move(fname, fname.replace('.upg', '.mp3') )
            LOG.msg("UPG: New file [%s] detected" % fname.replace('.upg', '.mp3'), 2)
            rss_builder.activate()

        time.sleep(10)

    
    
