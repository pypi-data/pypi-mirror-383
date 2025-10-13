from ..helper.main import validate_int_fields, validate_str_fields, is_ip, validate_port, is_ip_or_network, \
    is_unset
from ..base.cls import BaseModule
from ..helper.validate import is_valid_domain


class Peer(BaseModule):
    FIELD_ID = 'name'
    CMDS = {
        'add': 'addClient',
        'del': 'delClient',
        'set': 'setClient',
        'search': 'searchClient',
        'detail': 'getClient',
        'toggle': 'toggleClient',
    }
    API_KEY_PATH = 'client'
    API_MOD = 'wireguard'
    API_CONT = 'client'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = [
        'public_key', 'psk', 'port', 'allowed_ips', 'server', 'keepalive',
    ]
    FIELDS_ALL = [FIELD_ID, 'enabled']
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_TRANSLATE = {
        'public_key': 'pubkey',
        'allowed_ips': 'tunneladdress',
        'server': 'serveraddress',
        'port': 'serverport',
    }
    FIELDS_TYPING = {
        'bool': ['enabled'],
        'list': ['allowed_ips'],
        'int': ['port', 'keepalive'],
    }
    FIELDS_IGNORE = ['endpoint']  # empty field ?!
    FIELDS_DIFF_NO_LOG = ['psk']
    INT_VALIDATIONS = {
        'keepalive': {'min': 1, 'max': 86400},
    }
    STR_VALIDATIONS = {
        'name': r'^([0-9a-zA-Z._\-]){1,64}$'
    }
    EXIST_ATTR = 'peer'

    def __init__(self, m, result: dict):
        BaseModule.__init__(self=self, m=m, r=result)
        self.peer = {}
        self.existing_peers = None

    def check(self) -> None:
        if self.p['state'] == 'present':
            validate_port(m=self.m, port=self.p['port'])
            validate_int_fields(m=self.m, data=self.p, field_minmax=self.INT_VALIDATIONS)
            validate_str_fields(
                m=self.m, data=self.p,
                field_regex=self.STR_VALIDATIONS,
            )

            if is_unset(self.p['public_key']):
                self.m.fail_json(
                    "You need to provide a 'public_key' if you want to create a peer!"
                )

            if is_unset(self.p['allowed_ips']):
                self.m.fail_json(
                    "You need to provide at least one 'allowed_ips' entry "
                    "of the peer to create!"
                )

        for entry in self.p['allowed_ips']:
            if not is_ip_or_network(entry):
                self.m.fail_json(
                    f"Allowed-ip entry '{entry}' is neither a valid IP-address "
                    f"nor a valid network!"
                )

        if not is_unset(self.p['server']) and \
                not is_ip(self.p['server']) and not is_valid_domain(self.p['server']):
            self.m.fail_json(
                f"Peer endpoint/server '{self.p['server']}' is neither a valid IP-address "
                f"nor a valid domain!"
            )

        self._base_check()
