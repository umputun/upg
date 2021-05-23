
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

from common import *
from xml import sax
from pdb import set_trace as trace
import os, stat, calendar

class UpgConfig:
    def __init__(self, conf_xml="upg.xml"):
        self.__conf_xml = conf_xml
        self.__podcasts = {}
        self.__lastmtime = 0

    def parse(self):
        parser = sax.make_parser()
        handler = UpgContentHandler()
        items, settings, groups = {}, {}, {}
        handler.initResult(items, settings, groups)
        parser.setContentHandler(handler)
        self.__lastmtime = os.stat(self.__conf_xml)[stat.ST_MTIME]

        parser.parse(open(self.__conf_xml, "rb"))
        for name, value in items.items():

            items[name]['Days']  = \
                [ int( \
                        (d in "0123456" and d) or \
                        (d in _dayHeaders and str(_dayHeaders.index(d))) \
                      ) \
                for d in value['Days'].split(',') ]

            #items[name]['Days']  = [int(d) for d in value['Days'].split(',')]
            items[name]['Times'] = [int(d) for d in value['Times'].replace(':', '').split(',')]
            items[name]['Duration'] = int(value['Duration'])*60

        self.__podcasts = items
        self.__settings = settings
        self.__groups = groups
        

    def getChannels(self):
        return self.__podcasts

    def getGroups(self):
        return self.__groups

    def getSettings(self):
        return self.__settings

    def wasUpdated(self):
        curmtime =  os.stat(self.__conf_xml)[stat.ST_MTIME]
        return  (self.__lastmtime != curmtime)

class UpgContentHandler(sax.ContentHandler):

    def initResult(self, items, settings, groups):
        self.__items = items
        self.__settings = settings
        self.__groups = groups

    def startElement(self, name, attributes):
        if name == 'UPG':
            self.__in_item = False
            self.__is_name = False
            self.__in_item_param = False

        if name == 'Settings':
            for k,v in attributes.items():
                self.__settings[str(k)] = str(v)

        if name == 'Group':
            gr_name = str(attributes['name'])
            gr_info = {}
            for k,v in attributes.items():
                gr_info[str(k)] = v
            self.__groups[gr_name] = gr_info 


        if name == 'Item':
            self.__in_item = True
            self.__item_name = attributes['name'] 
            self.__item_param_name = None
            self.__item_param_data = {}
            if attributes.has_key('group'):
                self.__item_param_data['group'] =  attributes['group'].encode("utf-8") 
            else:
                self.__item_param_data['group'] =  '' 

            return

        if self.__in_item:
            self.__item_param_name = name
            self.__in_item_param = True


    
    def endElement(self, name):
        if name == 'Item': 
            self.__in_item = False
            self.__items[self.__item_name] = self.__item_param_data

        if self.__in_item:
            self.__in_item_param = False

    def characters(self, text):
        if self.__in_item and self.__in_item_param and self.__item_param_name:
            self.__item_param_data[str(self.__item_param_name)] = text.encode('utf-8')



if __name__ == "__main__":
    cnf = UpgConfig()
    cnf.parse()
    print cnf.getGroups()
