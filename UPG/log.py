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

import time

class Log:
    '''send messages to log and stdout. Supports differnet verbose levels'''
    def __init__(self, is_show = True, log_name='log.log', level=0):
        self.log_name_ = log_name
        self.is_show_ = is_show
        self.level_ = level
        self.levels_ = ('L', 'M', 'H', 'C')
        open(self.log_name_, 'a+').write("\n")

    def msg(self, msg_str, level=0) :
        if level < self.level_:
            return

        msg_str = "[" + self.levels_[level] +"] " + time.strftime('%m/%d/%y %H:%M:%S') +" " + msg_str
        if self.is_show_:
            print msg_str.encode("utf-8")
        open(self.log_name_, 'a+').write((msg_str + "\n").encode("utf-8"))

    def name(self):
        return self.log_name_

    def setShow(self, is_show):
        self.is_show_ = is_show

    def setLevel(self, level):
        self.level_ = level





