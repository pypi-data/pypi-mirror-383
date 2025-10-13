from ..helper.main import validate_int_fields, is_unset
from ..base.cls import BaseModule


class AsPath(BaseModule):
    FIELD_ID = 'description'
    CMDS = {
        'add': 'addAspath',
        'del': 'delAspath',
        'set': 'setAspath',
        'search': 'get',
        'toggle': 'toggleAspath',
    }
    API_KEY_PATH = 'bgp.aspaths.aspath'
    API_MOD = 'quagga'
    API_CONT = 'bgp'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = ['number', 'action', 'as_pattern']
    FIELDS_ALL = [FIELD_ID, 'enabled']
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_TRANSLATE = {
        'as_pattern': 'as',
    }
    FIELDS_TYPING = {
        'bool': ['enabled'],
        'select': ['action'],
    }
    INT_VALIDATIONS = {
        'number': {'min': 10, 'max': 99},
    }
    EXIST_ATTR = 'as_path'

    def __init__(self, m, result: dict):
        BaseModule.__init__(self=self, m=m, r=result)
        self.as_path = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['number']) or is_unset(self.p['as_pattern']) or is_unset(self.p['action']):
                self.m.fail_json(
                    'To create a BGP as-path you need to provide a number, '
                    'as_pattern and action!'
                )

            validate_int_fields(m=self.m, data=self.p, field_minmax=self.INT_VALIDATIONS)

        self._base_check()
