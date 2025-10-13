from ..helper.main import is_ip4, is_ip6, valid_hostname, to_digit, simplify_translate, is_unset
from ..helper.unbound import validate_domain
from ..base.cls import BaseModule


class Host(BaseModule):
    CMDS = {
        'add': 'addHostOverride',
        'del': 'delHostOverride',
        'set': 'setHostOverride',
        'search': 'get',
        'toggle': 'toggleHostOverride',
    }
    API_KEY = 'host'
    API_KEY_PATH = f'unbound.hosts.{API_KEY}'
    API_MOD = 'unbound'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = [
        'hostname', 'domain', 'record_type', 'prio', 'value',
        'description',
    ]
    FIELDS_ALL = ['enabled']
    FIELDS_ALL.extend(FIELDS_CHANGE)
    EXIST_ATTR = 'host'
    FIELDS_TYPING = {
        'bool': ['enabled'],
        'select': ['record_type'],
    }
    FIELDS_TRANSLATE = {
        'record_type': 'rr',
        # 'prio': 'mxprio',
        # 'value': 'mx',  # mx or server
    }

    def __init__(self, m, result: dict):
        BaseModule.__init__(self=self, m=m, r=result)
        self.host = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['value']):
                self.m.fail(
                    "You need to provide a 'value' to create a host-override!"
                )

            validate_domain(m=self.m, domain=self.p['domain'])

        if self.p['record_type'] == 'MX':
            if not valid_hostname(self.p['value']):
                self.m.fail(f"Value '{self.p['value']}' is not a valid hostname!")

        else:
            self.p['prio'] = None

            if self.p['state'] == 'present':
                if self.p['record_type'] == 'A' and not is_ip4(self.p['value']):
                    self.m.fail(f"Value '{self.p['value']}' is not a valid IPv4-address!")
                elif self.p['record_type'] == 'AAAA' and not is_ip6(self.p['value']):
                    self.m.fail(f"Value '{self.p['value']}' is not a valid IPv6-address!")

        self._base_check()

    def _simplify_existing(self, host: dict) -> dict:
        simple = simplify_translate(
            existing=host,
            typing=self.FIELDS_TYPING,
            translate=self.FIELDS_TRANSLATE,
        )

        if simple['record_type'] == 'MX':
            simple['prio'] = host['mxprio']
            simple['value'] = host['mx']

        else:
            simple['value'] = host['server']
            simple['prio'] = ''

        return simple

    def _build_request(self) -> dict:
        data = {
            'enabled': to_digit(self.p['enabled']),
            'hostname': self.p['hostname'],
            'domain': self.p['domain'],
            'rr': self.p['record_type'],  # A/AAAA/MX
            'description': self.p['description'],
        }

        if self.p['record_type'] == 'MX':
            data['mxprio'] = self.p['prio']
            data['mx'] = self.p['value']

        else:
            data['server'] = self.p['value']

        return {
            self.API_KEY: data
        }
