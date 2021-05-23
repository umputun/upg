
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

from log import Log
URL, DIR, DAY, TIME, LEN, TITLE, GROUP, TIMESHIFT  = "Url", "Directory", "Days", "Times", "Duration", "Title", "group", "timeshift"

LOG = Log(log_name="upg.log", level=0)
VERSION='0.3.6'
open("VERSION", "wb").write(VERSION)

