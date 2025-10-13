from ..helper.main import is_unset
from ..base.cls import BaseModule


class Key(BaseModule):
    FIELD_ID = 'name'
    CMDS = {
        'add': 'add_static_key',
        'del': 'del_static_key',
        'set': 'set_static_key',
        'search': 'search_static_key',
        'detail': 'get_static_key',
        'gen': 'gen_key',
    }
    API_KEY_PATH = 'statickey'
    API_MOD = 'openvpn'
    API_CONT = 'instances'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = ['mode', 'key']
    FIELDS_ALL = [FIELD_ID]
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_TRANSLATE = {
        'name': 'description',
    }
    FIELDS_TYPING = {
        'select': ['mode'],
    }
    EXIST_ATTR = 'key'
    FIELDS_DIFF_NO_LOG = ['key']

    def __init__(self, m, result: dict):
        BaseModule.__init__(self=self, m=m, r=result)
        self.key = {}

    def check(self) -> None:
        self._base_check()

        if self.p['state'] == 'present':
            if is_unset(self.p['key']):
                if self.exists:
                    self.p['key'] = self.key['key']

                else:
                    self.p['key'] = self.s.get({
                        **self.call_cnf,
                        'command': self.CMDS['gen'],
                    })['key']

            self.r['diff']['after'] = self.b.build_diff(data=self.p)
