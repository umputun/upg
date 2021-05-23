
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

import sys, time, os
from rss_builder import RssBuilder
from common import *

class HtmlProcessor:

    def __init__(self, rss_builder, groups, html_root="html"):
        self.__rss_builder = rss_builder
        self.__root = html_root
        self.__groups = groups

        self.__tags = [
            self.__channels, 
            self.__item, 
            self.__setup, 
            self.__log,
            self.__group,
        ]

    def proc(self, fname, params=None):
        header = open(self.__root+"/header.html", "rb").read()
        header = self.__version(header)

        footer = open(self.__root+"/footer.html", "rb").read()
        try:
            fh = open(self.__root+"/" + fname, "rb")
            data = fh.read()
            if fname.find('.html') == -1:
                return data
            return (header+self.__procTags(data,params)+footer).encode("utf-8")
        except:
            raise
            LOG.msg("PRC: processing failed for %s" % fname, 3)
            return header+self.__error()+footer


    def __procTags(self, data, params):
        result = data
        for proc in self.__tags:
            result = proc(result, params)
        return result


    def __channels(self, data, params):

        if data.find('{channels}') == -1:
            return data

        today_mode = (params and params.has_key('today') )
        group_mode = (params and params.has_key('group'))

        rdata = self.__rss_builder.getAllRssData()

        #for i in rdata: print "*", i, len(rdata)

        html = '<table style="width: 100%; text-align: left;" border="0" cellpadding="2" cellspacing="2">'

        sorted_keys = []
        for ch_name, ch_data in  rdata.items():
            if len(ch_data) == 0:
                continue
            sorted_keys.append( (ch_name, ch_data[0]['ticks']) )
        sorted_keys.sort(self.__cmp_item)

        now = time.localtime(time.time())


        for (ch_name, tmp) in sorted_keys:
            ch_data = rdata[ch_name]
            last_up_item = ch_data[0]
            #print last_up_item['title'], len(sorted_keys)
            if (today_mode):
                ch_time = time.localtime(last_up_item['ticks'])
                if ch_time[0] != now[0] or ch_time[1] != now[1] or ch_time[2] != now[2]:
                    continue

            if group_mode:
                if not last_up_item.has_key('group') or last_up_item['group'] != params['group']:
                    continue

            if last_up_item.has_key('group') and last_up_item['group']:
                gr_name = last_up_item['group']
                gr_title = self.__groups[last_up_item['group']]['title']
            else:
                gr_name,gr_title = "", ""

            ch_html = '''<tr>
                            <td>
                                <a href="%s"><img border="0" align="absmiddle" src="mp3icon.gif"></a>
                                <b><a href="item.html?name=%s">%s</a></b>
                            </td>
                            <td><font size="1"><a href="group.html?group=%s">%s</a></font></td>
                            <td><font size="1">%s</font></td>
                            <td><font size="1">%d</font></td>
                            <td>
                                <a href="%s.xml"><img border="0" align="absmiddle" src="blue-podcast.gif"></a>
                            </td>
                         </tr>''' % (last_up_item['file'], ch_name, last_up_item['title'], 
                                     gr_name, gr_title,
                                     last_up_item['time'], len(ch_data), ch_name)

            html += ch_html

        html += "</table>"
        data = data.replace('{channels}',html)
        return data

    def __cmp_item(self, x, y):
        return y[1] - x[1]

    def __error(self):
        return "<center><br/><h3>INTERNAL ERROR</h3></center>"



    def __item(self, data, params):
        if not params or not params.has_key('name'):
            return data

        if params['name'] == 'combine':
            item_data = self.__rss_builder.getSubset(combine=True)
            title = 'Combined'
        else:
            item_data = self.__rss_builder.getSubset(channel=params['name'])
            title = item_data[0]['title']


        if data.find('{name}') != -1:
            desc = '<a href="%s.xml">%s</a>' % (params['name'], title )
            data = data.replace('{name}', desc)    

        if data.find('{item}') != -1:
            html = '<table style="width: 100%; text-align: left;" border="0" cellpadding="2" cellspacing="2">'
            ch_name = params['name']
            for item in item_data:
                if params['name'] == 'combine':
                    item_title = '<a href="item.html?name=%s">%s</a>' % (item['dir'], item['title'])
                else:
                    item_title = ""

                item_html = '''<tr>
                                <td>
                                    <a href="%s"><img border="0" align="absmiddle" src="mp3icon.gif"></a>
                                </td>
                                <td>
                                    %s
                                </td>
                                <td>%s</td>                                
                                <td><font size="1">%d</font></td>
                             </tr>''' % (item['file'], item_title, item['time'], item['size'])

                html += item_html

            html += "</table>"
            data = data.replace('{item}',html)
        
        return data


    def __group(self, data, params):
        if data.find('{group}') == -1:
            return data
        data = data.replace('{group}',
                 '<a href="group_%s.xml">%s</a>' % (params['group'], self.__groups[params['group']]['title']) )
        return data

    def __setup(self, data, params):
        if data.find('{setup}') == -1:
            return data
        conf = open("upg.xml", "rb").read()
        data = data.replace('{setup}',conf)
        return data.decode('utf-8')

    def __log(self, data, params):
        if data.find('{log}') == -1:
            return data
        log = open("upg.log", "rb").read()
        data = data.replace('{log}',log)
        return data.decode('utf-8')

    def __version(self, data):
        if data.find('{version}') == -1:
            return data
        data = data.replace('{version}', VERSION)
        return data.decode('utf-8')


