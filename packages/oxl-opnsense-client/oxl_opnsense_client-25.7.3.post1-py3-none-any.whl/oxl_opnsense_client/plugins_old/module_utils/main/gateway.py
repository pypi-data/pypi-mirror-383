from ipaddress import ip_address

from ..helper.main import validate_int_fields, is_ip6
from ..base.cls import BaseModule


class Gw(BaseModule):
    FIELD_ID = 'name'
    CMDS = {
        'add': 'addGateway',
        'del': 'delGateway',
        'set': 'setGateway',
        'search': 'get',
        'toggle': 'toggleGateway',
    }
    API_KEY_PATH = 'gateways.gateway_item'
    API_MOD = 'routing'
    API_CONT = 'settings'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = [
        'name', 'interface', 'gateway', 'default_gw', 'far_gw', 'monitor_disable', 'monitor_noroute', 'monitor',
        'force_down', 'priority', 'weight', 'latency_low', 'latency_high', 'loss_low', 'loss_high', 'interval',
        'time_period', 'loss_interval', 'data_length', 'description', 'ip_protocol',
    ]
    FIELDS_ALL = ['enabled']
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_BOOL_INVERT = ['enabled']
    FIELDS_TRANSLATE = {
        'description': 'descr',
        'ip_protocol': 'ipprotocol',
        'enabled': 'disabled',
        'default_gw': 'defaultgw',
        'far_gw': 'fargw',
        'latency_low': 'latencylow',
        'latency_high': 'latencyhigh',
        'loss_low': 'losslow',
        'loss_high': 'losshigh',
    }
    FIELDS_TYPING = {
        'bool': ['enabled', 'default_gw', 'far_gw', 'monitor_disable', 'monitor_noroute', 'force_down'],
        'int': [
            'priority', 'weight', 'latency_low', 'latency_high', 'loss_low', 'loss_high', 'interval', 'time_period',
            'loss_interval', 'data_length',
        ],
        'select': ['interface', 'ip_protocol'],
    }
    INT_VALIDATIONS = {
        'priority': {'min': 0, 'max': 255},
        'weight': {'min': 1, 'max': 5},
        'latency_low': {'min': 1, 'max': 9999},
        'latency_high': {'min': 1, 'max': 9999},
        'loss_low': {'min': 1, 'max': 99},
        'loss_high': {'min': 1, 'max': 99},
        'interval': {'min': 1, 'max': 9999},
        'time_period': {'min': 1, 'max': 9999},
        'data_length': {'min': 0, 'max': 9999},
    }
    EXIST_ATTR = 'gw'

    def __init__(self, m, result: dict):
        BaseModule.__init__(self=self, m=m, r=result)
        self.gw = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            validate_int_fields(m=self.m, data=self.p, field_minmax=self.INT_VALIDATIONS)

            try:
                ip_address(self.p['gateway'])

            except ValueError:
                self.m.fail(f"Value '{self.p['gateway']}' is not a valid gateway!")

            if self.p['monitor']:
                try:
                    ip_address(self.p['monitor'])

                except ValueError:
                    self.m.fail(f"Value '{self.p['monitor']}' is not a valid monitor address!")

            if not self.p['interface']:
                self.m.fail('You need to provide a value for the interface!')

            if not self.p['gateway']:
                self.m.fail('You need to provide a value for the gateway!')

            if is_ip6(self.p['gateway']):
                self.p['ip_protocol'] = 'inet6'

            else:
                self.p['ip_protocol'] = 'inet'

        self._base_check()
