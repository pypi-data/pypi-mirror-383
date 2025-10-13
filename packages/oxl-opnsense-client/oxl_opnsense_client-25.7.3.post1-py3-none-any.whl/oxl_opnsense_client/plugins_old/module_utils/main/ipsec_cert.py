from ..helper.main import get_selected, is_unset
from ..base.cls import BaseModule


class KeyPair(BaseModule):
    FIELD_ID = 'name'
    CMDS = {
        'add': 'addItem',
        'del': 'delItem',
        'set': 'setItem',
        'search': 'searchItem',
        'detail': 'getItem',
    }
    API_KEY_PATH = 'keyPair'
    API_MOD = 'ipsec'
    API_CONT = 'key_pairs'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = ['public_key']
    FIELDS_ALL = ['name', 'private_key', 'type']
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_TRANSLATE = {
        'type': 'keyType',
        'public_key': 'publicKey',
        'private_key': 'privateKey',
    }
    FIELDS_DIFF_NO_LOG = ['private_key']
    EXIST_ATTR = 'key'
    FIELDS_TYPING = {}
    TIMEOUT = 30.0  # ipsec reload

    def __init__(self, m, result: dict):
        BaseModule.__init__(self=self, m=m, r=result)
        self.key = {}

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['public_key']) or is_unset(self.p['private_key']):
                self.m.fail(
                    "You need to supply both 'public_key' and "
                    "'private_key' to create an IPSec certificate!"
                )

            pub_start, pub_end = '-----BEGIN PUBLIC KEY-----', '-----END PUBLIC KEY-----'
            if self.p['public_key'].find(pub_start) == -1 or \
                    self.p['public_key'].find(pub_end) == -1:
                self.m.fail("The provided 'public_key' has an invalid format!")

            priv_start, priv_end = '-----BEGIN RSA PRIVATE KEY-----', '-----END RSA PRIVATE KEY-----'
            if self.p['private_key'].find(priv_start) == -1 or self.p['private_key'].find(priv_end) == -1:
                self.m.fail(
                    "The provided 'private_key' has an invalid format - should be "
                    "'RSA PRIVATE KEY'!"
                )

            self.p['public_key'] = self.p['public_key'].strip()
            self.p['private_key'] = self.p['private_key'].strip()

        self._base_check()

    def _simplify_existing(self, key: dict) -> dict:
        # makes processing easier
        simple = {
            'type': get_selected(key['keyType']),
            'public_key': key['publicKey'].strip(),
            'private_key': key['privateKey'].strip(),
            'name': key['name'],
        }

        if 'uuid' in key:
            simple['uuid'] = key['uuid']

        elif self.key is not None and 'uuid' in self.key:
            simple['uuid'] = self.key['uuid']

        else:
            simple['uuid'] = None

        return simple

    def update(self) -> None:
        self.b.update(enable_switch=False)
