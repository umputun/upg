
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

import sys, time, os, threading
from common import *
from ripper import Ripper

class Scheduler:

    def __init__(self, settings, podcasts_conf, updated_q):
        self.__settings = settings
        self.__last_check = time.localtime(time.time()-60)
        self.__updated_q = updated_q
        self.setConf(podcasts_conf)
        self.__ev_terminate = threading.Event()

    def terminate(self):
        LOG.msg("SHD: received termination request", 0)
        self.__ev_terminate.set()

    def setConf(self, podcasts_conf):
        self.__podcasts_conf = podcasts_conf.getChannels()
        self.__podcasts_gr   = podcasts_conf.getGroups()

        for name, params in self.__podcasts_conf.items():
            timeshift = self.__getTimeShift(params)
            LOG.msg("SHD: scheduling for %s, days=%s, time=%s, timeshift=%d" % (name, params[DAY], params[TIME], timeshift), 1)

    def check(self):
        now = time.localtime(time.time())
        #print now[4], self.__last_check[4]
        if now[4] != self.__last_check[4]: #if not the same minute   
            for name, params in self.__podcasts_conf.items():
                #print "DAY", now[6], params[DAY]
                timeshift = self.__getTimeShift(params)
                now_adjusted = time.localtime(time.time() + (timeshift*3600))
                if not ( (now_adjusted[6]) in params[DAY]): 
                    continue
                dec_time = now_adjusted[3]*100+now_adjusted[4]
                #print "TIME", dec_time, params[TIME]
                if not dec_time in params[TIME]: continue
                LOG.msg("SHD: Scheduling activated for %s %d" % (name, dec_time), 2)                    
                ripper = Ripper(name, params, self.__settings, self.__updated_q, self.__ev_terminate)
                ripper.start()

            self.__last_check = now
        
            

    def __getTimeShift(self, item_param):
        if item_param.has_key('timeshift'): return int(item_param['timeshift'])
        try:
            timeshift = int(self.__podcasts_gr[item_param[GROUP]]['timeshift'])
            return timeshift
        except:
            return 0

