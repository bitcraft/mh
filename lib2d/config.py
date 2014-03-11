"""
Copyright 2010, 2011  Leif Theden


This file is part of lib2d.

lib2d is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

lib2d is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with lib2d.  If not, see <http://www.gnu.org/licenses/>.
"""


from configobj import ConfigObj

config_file = "lib2d.config"

g_parsed = False
g_config = {}

def read_config():
    global g_parsed
    config = ConfigObj(config_file)
    g_parsed = True
    return config

def get_config():
    global g_config
    if g_parsed == False: g_config = read_config()
    return config    
