from ..helper.main import validate_int_fields, is_ip, is_unset
from ..base.cls import BaseModule


class Vxlan(BaseModule):
    FIELD_ID = 'id'
    CMDS = {
        'add': 'addItem',
        'del': 'delItem',
        'set': 'setItem',
        'search': 'get',
    }
    API_KEY_PATH = 'vxlan.vxlan'
    API_MOD = 'interfaces'
    API_CONT = 'vxlan_settings'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = ['interface', 'local', 'remote', 'group']
    FIELDS_ALL = [FIELD_ID]
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_TRANSLATE = {
        # 'name': 'deviceId',  # can't be configured
        'id': 'vxlanid',
        'local': 'vxlanlocal',
        'remote': 'vxlanremote',
        'group': 'vxlangroup',
        'interface': 'vxlandev',
    }
    FIELDS_TYPING = {
        'select': ['interface'],
        'int': ['id'],
    }
    INT_VALIDATIONS = {
        'id': {'min': 0, 'max': 16777215},
    }
    FIELDS_IP = ['local', 'remote', 'group']
    EXIST_ATTR = 'vxlan'

    def __init__(self, m, result: dict):
        BaseModule.__init__(self=self, m=m, r=result)
        self.vxlan = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['local']):
                self.m.fail_json("You need to provide a 'local' ip to create a vxlan!")

            for field in self.FIELDS_IP:
                if not is_unset(self.p[field]) and not is_ip(self.p[field]):
                    self.m.fail_json(
                        f"Value '{self.p[field]}' is not a valid IP-address!"
                    )

            validate_int_fields(m=self.m, data=self.p, field_minmax=self.INT_VALIDATIONS)

        self._base_check()

    def update(self) -> None:
        self.b.update(enable_switch=False)
