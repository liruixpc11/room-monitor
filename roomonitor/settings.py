import ConfigParser
import os

WEIXIN_SECRET = ""
WEIXIN_CORP_ID = ''

WEIXIN_AGENT_ID = 1

SECRET = ''

MODE = 'TEST'
# MODE = 'PRODUCT

DB_URL = 'sqlite:///status.db'

GAUGE_URL = 'http://127.0.0.1:8080/'

_config_file = '/etc/room-monitor/config.ini'
if os.path.exists(_config_file):
    parser = ConfigParser.ConfigParser()
    parser.read(_config_file)
    WEIXIN_SECRET = parser.get("weixin", 'secret')
    WEIXIN_CORP_ID = parser.get("weixin", 'copr_id')
    WEIXIN_AGENT_ID = parser.get("weixin", 'agent_id')
    SECRET = parser.get("controller", 'secret')
    DB_URL = parser.get('db', 'url')
    GAUGE_URL = parser.get('server', 'gauge_url')
    MODE = parser.get('server', 'mode')
