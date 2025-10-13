from ..helper.main import is_unset
from ..base.cls import BaseModule


class DhcRelayRelay(BaseModule):
    FIELD_ID = 'interface'
    CMDS = {
        'add': 'addRelay',
        'del': 'delRelay',
        'set': 'setRelay',
        'search': 'get',
        'toggle': 'toggleRelay',
    }
    API_KEY_PATH = 'dhcrelay.relays'
    API_KEY_PATH_REQ = 'relay'
    API_MOD = 'dhcrelay'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = ['destination', 'agent_info']
    FIELDS_ALL = [FIELD_ID, 'enabled']
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_TYPING = {
        'select': ['interface', 'destination'],
        'bool': ['enabled', 'agent_info']
    }
    EXIST_ATTR = 'relay'
    SEARCH_ADDITIONAL = {
        'existing_destinations': 'dhcrelay.destinations',
    }

    def __init__(self, m, result: dict):
        BaseModule.__init__(self=self, m=m, r=result)
        self.relay = {}
        self.existing_destinations = None

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['destination']):
                self.m.fail_json("You need to provide a 'destination' to create a dhcrelay_relay!")

        self._base_check()

        if not is_unset(self.p['destination']) and self.existing_destinations:
            for key, values in self.existing_destinations.items():
                if values['name'] == self.p['destination']:
                    self.p['destination'] = key
                    break

    def get_existing(self) -> list:
        existing = self.b.get_existing()
        for relay in existing:
            relay['destination'] = self.existing_destinations[relay['destination']]['name']
        return existing
