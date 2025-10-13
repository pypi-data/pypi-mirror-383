from basic.ansible import AnsibleModule

from plugins.module_utils.base.api import \
    Session
from plugins.module_utils.base.cls import BaseModule


class SenderBCC(BaseModule):
    FIELD_ID = 'address'
    CMDS = {
        'add': 'addSenderbcc',
        'del': 'delSenderbcc',
        'set': 'setSenderbcc',
        'search': 'get',
        'toggle': 'toggleSenderbcc',
    }
    API_KEY_PATH = 'senderbcc.senderbccs.senderbcc'
    API_MOD = 'postfix'
    API_CONT = 'senderbcc'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = ['to']
    FIELDS_ALL = ['enabled', 'address']
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_TRANSLATE = {'address': 'from'}
    FIELDS_TYPING = {
        'bool': ['enabled'],
        'list': ['to'],
    }
    EXIST_ATTR = 'sender'

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None, fail: dict = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session, f=fail)
        self.sender = {}
