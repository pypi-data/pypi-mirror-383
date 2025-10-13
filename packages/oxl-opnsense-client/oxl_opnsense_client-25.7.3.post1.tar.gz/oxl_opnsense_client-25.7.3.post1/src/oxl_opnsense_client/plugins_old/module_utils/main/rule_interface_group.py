from ..helper.main import validate_int_fields, is_unset
from ..base.cls import BaseModule


class Group(BaseModule):
    FIELD_ID = 'name'
    CMDS = {
        'add': 'addItem',
        'del': 'delItem',
        'set': 'setItem',
        'search': 'get',
    }
    API_KEY_PATH = 'group.ifgroupentry'
    API_KEY_PATH_REQ = 'group'
    API_MOD = 'firewall'
    API_CONT = 'group'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = ['name', 'members', 'gui_group', 'sequence', 'description']
    FIELDS_ALL = [FIELD_ID]
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_BOOL_INVERT = ['gui_group']
    FIELDS_TRANSLATE = {
        'name': 'ifname',
        'description': 'descr',
        'gui_group': 'nogroup'
    }
    FIELDS_TYPING = {
        'bool': ['gui_group'],
        'list': ['members'],
        'select': ['members'],
        'int': ['sequence'],
    }
    INT_VALIDATIONS = {
        'sequence': {'min': 0, 'max': 9999},
    }
    EXIST_ATTR = 'group'

    def __init__(self, m, result: dict):
        BaseModule.__init__(self=self, m=m, r=result)
        self.group = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['members']):
                self.m.fail_json("You need to provide a 'members' to create a rule interface group!")

            validate_int_fields(m=self.m, data=self.p, field_minmax=self.INT_VALIDATIONS)

        self._base_check()

    def update(self) -> None:
        self.b.update(enable_switch=False)
