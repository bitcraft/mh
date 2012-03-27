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
