from ..helper.main import validate_int_fields, is_unset
from ..base.cls import BaseModule


class Vlan(BaseModule):
    FIELD_ID = 'description'
    CMDS = {
        'add': 'addItem',
        'del': 'delItem',
        'set': 'setItem',
        'search': 'get',
    }
    API_KEY_PATH = 'vlan.vlan'
    API_MOD = 'interfaces'
    API_CONT = 'vlan_settings'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = ['interface', 'vlan', 'priority', 'device']
    FIELDS_ALL = [FIELD_ID]
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_TRANSLATE = {
        'device': 'vlanif',
        'interface': 'if',
        'vlan': 'tag',
        'priority': 'pcp',
        'description': 'descr',
    }
    FIELDS_TYPING = {
        'select': ['interface', 'priority'],
        'int': ['vlan', 'priority'],
    }
    INT_VALIDATIONS = {
        'vlan': {'min': 1, 'max': 4096},
        'priority': {'min': 0, 'max': 7},
    }
    EXIST_ATTR = 'vlan'

    def __init__(self, m, result: dict):
        BaseModule.__init__(self=self, m=m, r=result)
        self.vlan = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['interface']):
                self.m.fail_json("You need to provide an 'interface' to create a vlan!")

            if is_unset(self.p['vlan']):
                self.m.fail_json("You need to provide a 'vlan' to create a vlan-interface!")

            if is_unset(self.p['device']):
                self.p['device'] = f"vlan0.{self.p['vlan']}"  # OPNSense forces us to start with 'vlan0' for some reason

            validate_int_fields(m=self.m, data=self.p, field_minmax=self.INT_VALIDATIONS)

        self._base_check()

    def update(self) -> None:
        self.b.update(enable_switch=False)
