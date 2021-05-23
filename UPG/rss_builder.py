

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

import os, time, stat, shutil
from common import *
from pdb import set_trace as trace

class RssBuilder:
    def __init__(self, settings, podcasts_conf, groups):
        self.__root = settings['root']
        self.__podcasts_conf = podcasts_conf
        self.__groups = groups
        self.__ip, self.__port = settings['ip'], int(settings['port'])
        self.__rss = {} #dict of all rss's. key is dirname, value - xml
        self.__rss_data = {} #dict of rss dictionaries
        self.__rss_combined = []
        try:
            os.mkdir(self.__root)
            LOG.msg("RSS: created mp3 root direcory [%s]" % (self.__root), 1)
        except:
            pass

    def getConf(self):
        return self.__podcasts_conf

    def setConf(self, podcasts_conf):
        self.__podcasts_conf = podcasts_conf

    def getRss(self, name):
        if name == 'combine':
            return self.getCombinedRss()
        if self.__rss.has_key(name):
            return self.__rss[name]
        return "<empty/>"

    def getRssData(self, name):
        if self.__rss_data.has_key(name):
            return self.__rss_data[name]
        return None

    def getAllRssData(self):
        return self.__rss_data

    def getCombinedRss(self):
        subs = self.getSubset(self.__rss_combined, combine=True)
        return self.dataToRss(subs, 'Combined')

    def getGroupRss(self, group):
        subs = self.getSubset(self.__rss_combined, group=group)
        return self.dataToRss(subs, self.__groups[group]['title'])




    def activate(self):
        '''build __rss (xml string) for each feed and __rss_data (dict of all important values) for each feed'''

        self.__rss = {}
        self.__rss_data = {}
        self.__rss_combined = []

        for name, params in self.__podcasts_conf.items():

            rss_data_item = []

            xml_last_build_time = ""
            xml_items = ""

            #get list of all files in root (usually mp3) directory
            try:
                files = os.listdir(self.__root+ "/" + params[DIR])
            except OSError:
                LOG.msg("RSS: directory %s created" % params[DIR], 1)
                os.mkdir(self.__root+ "/" + params[DIR])
                shutil.copy("upg.mp3", self.__root+ "/" + params[DIR])
                files = os.listdir(self.__root+ "/" + params[DIR])

                
            #sort files and keep .mp3 only, exclude temporary upg_* files
            sorted_file_list = []
            for mp3_file in files:
                if (mp3_file.find(".mp3") == -1) or (mp3_file.find("upg_") != -1): 
                    continue
                sorted_file_list.insert(0, mp3_file)

        
            #process all mp3 files for current channel (podcast)
            for  mp3_file in sorted_file_list:
                full_name = self.__root+ "/" + params[DIR] + "/" + mp3_file
                fsize = os.stat(full_name)[stat.ST_SIZE]
                ftime = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(os.stat(full_name)[stat.ST_MTIME]))
                fticks = os.stat(full_name)[stat.ST_MTIME]

                #created data entry
                rss_data =  { 
                      "file": full_name, "size" : fsize, "time" : ftime, "ticks" : fticks,
                      "title" : name, "url" : "http://%s:%d/%s" % (self.__ip, self.__port, full_name),                          
                      "dir" : params[DIR], "type" : "file", "id" : params[DIR], "group" : params[GROUP]
                }
                rss_data_item.append(rss_data) 
                self.__rss_combined.append(rss_data) #rss combined has all files from all channels
        
            self.__rss[params[DIR]] = self.dataToRss(rss_data_item, name)
            rss_data_item.sort(self.__cmp_item)
            self.__rss_data[params[DIR]] = rss_data_item            

        self.__rss_combined.sort(self.__cmp_item) #sort combined data by time (DESC)




    def __rssHeaderFooter(self, name):
        header  = '<rss version="2.0">\n<channel>\n<title>UPG - %s</title>\n' % name
        header += '<link>http://%s:%d</link>\n' % (self.__ip, self.__port)
        header += '<description>generated by UPG</description>\n'
        header += '<language>en-En</language><geneartor>UPG</geneartor>\n'''
        footer  = '</channel></rss>\n'
        return (header, footer)


    def dataToRss(self, rss_data, name):
        '''convert rss_data (list of item's dict) to valid rss xml'''

        LOG.msg("RSS: convert data to RSS for %s" % name, 0)
        #trace()
        xml_last_build_time = ""
        xml_items = ""
        rss_result = ""

        for ch_data in rss_data:
            if xml_last_build_time == "":
                xml_last_build_time = '<lastBuildDate>%s</lastBuildDate>\n' % ch_data['time']

            xml_items += '<item><title>%s</title><pubDate>%s</pubDate>\n' % (ch_data['title'], ch_data['time'])
            xml_items += '<description>generated by UPG</description>\n'
            xml_items += '<guid>%s.uid</guid>\n' % ch_data['file'].decode("utf-8")
            xml_items += '<link>/%s</link>\n' % ch_data['file'].decode("utf-8")
            xml_items += '<enclosure url="http://%s:%d/%s" length="%d" type="audio/mpeg"/>\n</item>\n' % (self.__ip, self.__port, ch_data['file'].decode("utf-8"), ch_data['size'])

        xml_header, xml_footer = self.__rssHeaderFooter(name)
        rss_result = xml_header + xml_last_build_time + xml_items + xml_footer
        return rss_result


    def getSubset(self, rss_data=None, channel=None, group=None, combine=False):
        '''get subset of rss_data for given channel (id). If defined group, combine all channels 
           for that group, if defined combine - combine all channels'''

        if not rss_data:
            rss_data = self.__rss_combined

        if combine and (not channel): 
            name = 'Combined'
        if channel: 
            name = channel

        data_result = []
        
        for ch_data in rss_data:

            #if defined the channel and not combine mode skip other channels
            if channel and (not combine):
                if ch_data['id'] != channel:
                    continue
            #for group request ignore other groups
            if group and (ch_data['group'] != group):
                    continue

            data_result.append(ch_data)

        return data_result
        

    def __cmp_item(self, x, y):
        return int(y['ticks'] - x['ticks'])

