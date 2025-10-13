from ..helper.main import validate_int_fields, is_unset
from ..base.cls import BaseModule


class Interface(BaseModule):
    CMDS = {
        'add': 'addInterface',
        'del': 'delInterface',
        'set': 'setInterface',
        'search': 'get',
        'toggle': 'toggleInterface',
    }
    API_KEY_PATH = 'ospf.interfaces.interface'
    API_MOD = 'quagga'
    API_CONT = 'ospfsettings'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = [
        'interface', 'area', 'auth_type', 'auth_key', 'auth_key_id', 'cost',
        'hello_interval', 'dead_interval', 'retransmit_interval', 'transmit_delay',
        'priority', 'network_type', 'carp_depend_on', 'cost_demoted',
    ]
    FIELDS_ALL = ['enabled']
    FIELDS_ALL.extend(FIELDS_CHANGE)
    INT_VALIDATIONS = {
        'cost': {'min': 1, 'max': 65535},
        'hello_interval': {'min': 0, 'max': 4294967295},
        'dead_interval': {'min': 0, 'max': 4294967295},
        'retransmit_interval': {'min': 0, 'max': 4294967295},
        'transmit_delay': {'min': 0, 'max': 4294967295},
        'priority': {'min': 0, 'max': 4294967295},
        'cost_demoted': {'min': 1, 'max': 65535},
        'auth_key_id': {'min': 1, 'max': 255},
    }
    FIELDS_TRANSLATE = {
        'interface': 'interfacename',
        'hello_interval': 'hellointerval',
        'dead_interval': 'deadinterval',
        'retransmit_interval': 'retransmitinterval',
        'transmit_delay': 'transmitdelay',
        'network_type': 'networktype',
        'auth_type': 'authtype',
        'auth_key': 'authkey',
        'auth_key_id': 'authkey_id',
    }
    FIELDS_TYPING = {
        'bool': ['enabled'],
        'select': ['interface', 'carp_depend_on', 'network_type', 'auth_type'],
    }
    EXIST_ATTR = 'int'

    def __init__(self, m, result: dict):
        BaseModule.__init__(self=self, m=m, r=result)
        self.int = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['area']):
                self.m.fail_json(
                    'To create a OSPF interface you need to provide its area!'
                )

            if not is_unset(self.p['auth_type']) and is_unset(self.p['auth_key']):
                self.m.fail_json(
                    'You need to provide an authentication-key if you enable authentication!'
                )

            validate_int_fields(m=self.m, data=self.p, field_minmax=self.INT_VALIDATIONS)

        self._base_check()
