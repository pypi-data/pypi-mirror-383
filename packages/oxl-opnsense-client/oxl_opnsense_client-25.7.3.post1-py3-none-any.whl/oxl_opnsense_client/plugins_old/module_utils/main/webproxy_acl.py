from ..base.cls import GeneralModule


class General(GeneralModule):
    CMDS = {
        'set': 'set',
        'search': 'get',
    }
    API_KEY_PATH = 'proxy.forward.acl'
    API_KEY_PATH_REQ = API_KEY_PATH
    API_MOD = 'proxy'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = [
        'allow', 'exclude', 'banned', 'exclude_domains', 'block_domains',
        'block_user_agents', 'block_mime_types', 'exclude_google', 'youtube_filter',
        'ports_tcp', 'ports_ssl',
    ]
    FIELDS_ALL = FIELDS_CHANGE
    FIELDS_TRANSLATE = {
        'allow': 'allowedSubnets',
        'exclude': 'unrestricted',
        'banned': 'bannedHosts',
        'exclude_domains': 'whiteList',
        'block_domains': 'blackList',
        'block_user_agents': 'browser',
        'block_mime_types': 'mimeType',
        'exclude_google': 'googleapps',
        'youtube_filter': 'youtube',
        'ports_tcp': 'safePorts',
        'ports_ssl': 'sslPorts',
    }
    FIELDS_TYPING = {
        'list': [
            'allow', 'exclude', 'banned', 'exclude_domains', 'block_domains',
            'block_user_agents', 'block_mime_types', 'exclude_google',
            'ports_tcp', 'ports_ssl',
        ],
        'select': ['youtube_filter']
    }
    FIELDS_IGNORE = ['remoteACLs']

    def __init__(self, m, result: dict):
        GeneralModule.__init__(self=self, m=m, r=result)
