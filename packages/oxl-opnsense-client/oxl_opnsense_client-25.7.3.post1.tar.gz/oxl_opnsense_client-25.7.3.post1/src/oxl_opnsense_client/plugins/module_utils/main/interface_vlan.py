from basic.ansible import AnsibleModule

from plugins.module_utils.base.api import \
    Session
from plugins.module_utils.helper.validate import \
    is_unset
from plugins.module_utils.base.cls import BaseModule


class Vlan(BaseModule):
    FIELD_ID = 'description'
    CMDS = {
        'add': 'add_item',
        'del': 'del_item',
        'set': 'set_item',
        'search': 'get',
    }
    API_KEY_PATH = 'vlan.vlan'
    API_MOD = 'interfaces'
    API_CONT = 'vlan_settings'
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

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None, fail: dict = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session, f=fail)
        self.vlan = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['interface']):
                self.m.fail_json("You need to provide an 'interface' to create a vlan!")

            if is_unset(self.p['vlan']):
                self.m.fail_json("You need to provide a 'vlan' to create a vlan-interface!")

            if is_unset(self.p['device']):
                self.p['device'] = f"vlan0.{self.p['vlan']}"  # OPNSense forces us to start with 'vlan0' for some reason

        self._base_check()

    def update(self) -> None:
        self.b.update(enable_switch=False)
