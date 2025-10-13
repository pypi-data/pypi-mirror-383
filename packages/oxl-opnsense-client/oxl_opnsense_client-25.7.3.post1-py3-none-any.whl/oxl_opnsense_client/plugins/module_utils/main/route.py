from ipaddress import ip_network

from basic.ansible import AnsibleModule

from plugins.module_utils.helper.main import \
    simplify_translate
from plugins.module_utils.base.api import \
    Session
from plugins.module_utils.base.cls import BaseModule


class Route(BaseModule):
    FIELD_ID = 'uuid'
    CMDS = {
        'add': 'addroute',
        'del': 'delroute',
        'set': 'setroute',
        'search': 'get',
        'toggle': 'toggleroute',
    }
    API_KEY_PATH = 'route.route'
    API_MOD = 'routes'
    API_CONT = 'routes'
    FIELDS_CHANGE = ['network', 'gateway', 'description']
    FIELDS_ALL = ['enabled']
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_BOOL_INVERT = ['enabled']
    FIELDS_TRANSLATE = {
        'description': 'descr',
        'enabled': 'disabled',
    }
    FIELDS_TYPING = {
        'bool': ['enabled'],
        'select': ['gateway'],
    }
    EXIST_ATTR = 'route'

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None, fail: dict = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session, f=fail)
        self.route = {}

    def check(self) -> None:
        try:
            ip_network(self.p['network'])

        except ValueError:
            self.m.fail_json(f"Value '{self.p['network']}' is not a valid network!")

        self._base_check()

    def _simplify_existing(self, route: dict) -> dict:
        simple = simplify_translate(
            existing=route,
            typing=self.FIELDS_TYPING,
            translate=self.FIELDS_TRANSLATE,
            bool_invert=self.FIELDS_BOOL_INVERT,
        )
        if simple['gateway'].find(' - ') != -1:
            simple['gateway'] = simple['gateway'].rsplit('-', 1)[0].strip()

        return simple
