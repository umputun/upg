
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
import common
app_name = "UPG"
version = common.VERSION

URL = 'http://upg.umputun.com/'

import sys
assert sys.version_info >= (2, 2, 1), "Python 2.2.1 or newer required"
import os
import re

#app_root = os.path.split(os.path.abspath(sys.argv[0]))[0]
#html_root = os.path.join(app_root, 'html')
#doc_root = app_root

upg_root= '/opt/upg'
var_root =  upg_root +'/mp3'
conf_root = upg_root
html_root = upg_root + '/html'
doc_root =  upg_root + '/docs'

