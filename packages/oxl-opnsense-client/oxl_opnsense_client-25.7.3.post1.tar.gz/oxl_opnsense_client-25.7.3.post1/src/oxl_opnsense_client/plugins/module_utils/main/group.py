from basic.ansible import AnsibleModule

from plugins.module_utils.helper.main import \
    is_unset, get_key_by_value_from_selection
from plugins.module_utils.base.api import \
    Session
from plugins.module_utils.base.cls import BaseModule


class Group(BaseModule):
    FIELD_ID = 'name'
    CMDS = {
        'add': 'add',
        'del': 'del',
        'set': 'set',
        'search': 'search',
        'detail': 'get',
    }
    API_KEY_PATH = 'group'
    API_MOD = 'auth'
    API_CONT = 'group'
    FIELDS_CHANGE = ['description', 'source_net', 'privilege', 'member']
    FIELDS_TYPING = {
        'list': ['privilege', 'source_net'],
        'list_value': ['member'],
    }
    FIELDS_TRANSLATE = {
        'privilege': 'priv',
        'source_net': 'source_networks',
    }
    FIELDS_ALL = ['name']
    FIELDS_ALL.extend(FIELDS_CHANGE)
    EXIST_ATTR = 'group'
    STR_VALIDATIONS = {
        'name': r'^[a-zA-Z0-9._-]{1,32}$'
    }

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session)
        self.group = {}

    def delete(self) -> None:
        if self.group['scope'] == 'system':
            self.m.fail_json(f"Not allowed to delete system group {self.group['name']}")

        self.b.delete()

    def _build_request(self) -> dict:
        raw_request = self.b.build_request()

        if not is_unset(self.p['member']):
            # translate user-names to user-id's
            raw_request[self.API_KEY_PATH]['member'] = self.b.RESP_JOIN_CHAR.join([
                get_key_by_value_from_selection(self.b.raw['member'], m)
                for m in self.p['member']
            ])

        return raw_request
