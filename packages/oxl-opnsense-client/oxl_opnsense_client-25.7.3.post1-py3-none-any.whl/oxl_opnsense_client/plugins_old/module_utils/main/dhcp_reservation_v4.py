from ..helper.main import is_ip, is_network, is_unset
from ..base.cls import BaseModule


class ReservationV4(BaseModule):
    FIELD_ID = 'ip'
    CMDS = {
        'add': 'addReservation',
        'del': 'delReservation',
        'set': 'setReservation',
        'search': 'searchReservation',
        'detail': 'getReservation',
    }
    API_KEY_PATH = 'reservation'
    API_MOD = 'kea'
    API_CONT = 'dhcpv4'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = [
        'mac', 'hostname', 'description', 'subnet'
    ]
    FIELDS_ALL = [FIELD_ID]
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_TYPING = {
        'select': ['subnet'],
    }
    FIELDS_TRANSLATE = {
        'ip': 'ip_address',
        'mac': 'hw_address',
    }
    FIELDS_IGNORE = ['subnet']  # empty field ?!
    EXIST_ATTR = 'reservation'

    def __init__(self, m, result: dict):
        BaseModule.__init__(self=self, m=m, r=result)
        self.reservation = {}
        self.existing_reservations = None
        self.existing_subnets = None

    def check(self) -> None:
        if self.p['state'] == 'present':
            if is_unset(self.p['mac']):
                self.m.fail_json(
                    "You need to provide a 'mac' if you want to create a reservation!"
                )

            if is_unset(self.p['subnet']) or not is_network(self.p['subnet']):
                self.m.fail_json('The provided subnet is invalid!')

            if not is_ip(self.p['ip']):
                self.m.fail_json('The provided IP is invalid!')

        self._base_check()

        if self.p['state'] == 'present':
            self._search_subnets()
            if not self._find_subnet():
                self.m.fail_json('Provided subnet not found!')

    def _find_subnet(self) -> bool:
        for s in self.existing_subnets:
            if s['subnet'] == self.p['subnet']:
                self.p['subnet'] = s['uuid']
                self.reservation['subnet'] = s['uuid']
                return True

        return False

    def _search_subnets(self):
        self.existing_subnets = self.s.get(cnf={
            **self.call_cnf, **{'command': 'searchSubnet'}
        })['rows']
