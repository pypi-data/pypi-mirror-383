from ..base.cls import GeneralModule


class Traffic(GeneralModule):
    CMDS = {
        'set': 'set',
        'search': 'get',
    }
    API_KEY_PATH = 'proxy.general.traffic'
    API_KEY_PATH_REQ = API_KEY_PATH
    API_MOD = 'proxy'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = [
        'download_kb_max', 'upload_kb_max', 'throttle_kb_bandwidth',
        'throttle_kb_host_bandwidth', 'enabled',
    ]
    FIELDS_ALL = FIELDS_CHANGE
    FIELDS_TRANSLATE = {
        'download_kb_max': 'maxDownloadSize',
        'upload_kb_max': 'maxUploadSize',
        'throttle_kb_bandwidth': 'OverallBandwidthTrotteling',
        'throttle_kb_host_bandwidth': 'perHostTrotteling',
    }
    FIELDS_TYPING = {
        'int': [
            'download_kb_max', 'upload_kb_max', 'throttle_kb_bandwidth',
            'throttle_kb_host_bandwidth',
        ],
        'bool': ['enabled']
    }

    def __init__(self, m, result: dict):
        GeneralModule.__init__(self=self, m=m, r=result)
