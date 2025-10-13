from basic.ansible import AnsibleModule

from plugins.module_utils.base.api import \
    Session
from plugins.module_utils.helper.main import \
    get_selected_list, simplify_translate
from plugins.module_utils.base.cls import BaseModule


class SubnetV4(BaseModule):
    CMDS = {
        'add': 'add_subnet',
        'del': 'del_subnet',
        'set': 'set_subnet',
        'search': 'search_subnet',
        'detail': 'get_subnet',
    }
    API_KEY = 'subnet4'
    API_KEY_PATH = 'subnet4'
    API_MOD = 'kea'
    API_CONT = 'dhcpv4'
    API_CONT_REL = 'service'
    FIELDS_CHANGE = [
        'subnet', 'description', 'pools', 'auto_options',
    ]
    FIELDS_ALL = FIELDS_CHANGE
    FIELDS_TYPING = {
        'list': ['gateway', 'dns', 'domain_search', 'ntp_servers', 'time_servers'],  # 'pools',
        'bool': ['auto_options'],
        'int': ['v6_only_preferred'],
    }
    FIELDS_TRANSLATE = {
        'auto_options': 'option_data_autocollect',
    }
    API_ATTR_OPTIONS = 'option_data'
    API_FIELDS_OPTIONS = [
        'gateway', 'routes', 'dns', 'domain', 'domain_search', 'ntp_servers', 'time_servers',
        'next_server', 'tftp_server', 'tftp_file', 'v6_only_preferred',
    ]
    POOL_JOIN_CHAR = '\n'
    FIELDS_TRANSLATE_SPECIAL = {
        'dns': 'domain_name_servers',
        'domain': 'domain_name',
        'gateway': 'routers',
        'routes': 'static_routes',
        'tftp_server': 'tftp_server_name',
        'tftp_file': 'boot_file_name',
    }
    EXIST_ATTR = 'subnet'

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None, fail: dict = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session, f=fail)
        self.subnet = {}
        self.existing_subnets = None

    def _simplify_existing(self, entry: dict) -> dict:
        simple = simplify_translate(
            existing=entry,
            typing=self.FIELDS_TYPING,
            translate=self.FIELDS_TRANSLATE,
            ignore=self.API_FIELDS_OPTIONS,
        )

        simple['pools'] = simple['pools'].split(self.POOL_JOIN_CHAR)
        if self.API_ATTR_OPTIONS in entry:
            # get/details call
            opts = entry[self.API_ATTR_OPTIONS]
            return {
                **simple,
                'dns': get_selected_list(opts[self.FIELDS_TRANSLATE_SPECIAL['dns']]),
                'domain_search': get_selected_list(opts['domain_search']),
                'gateway': get_selected_list(opts[self.FIELDS_TRANSLATE_SPECIAL['gateway']]),
                'routes': opts[self.FIELDS_TRANSLATE_SPECIAL['routes']],
                'domain': opts[self.FIELDS_TRANSLATE_SPECIAL['domain']],
                'ntp_servers': get_selected_list(opts['ntp_servers']),
                'time_servers': get_selected_list(opts['time_servers']),
                'tftp_server': opts[self.FIELDS_TRANSLATE_SPECIAL['tftp_server']],
                'tftp_file': opts[self.FIELDS_TRANSLATE_SPECIAL['tftp_file']],
                'v6_only_preferred': opts['v6_only_preferred'],
            }

        # search-call :'(
        return {
            **simple,
            'dns': entry[f"option_data.{self.FIELDS_TRANSLATE_SPECIAL['dns']}"],
            'domain_search': entry['option_data.domain_search'],
            'gateway': entry[f"option_data.{self.FIELDS_TRANSLATE_SPECIAL['gateway']}"],
            'routes': entry[f"option_data.{self.FIELDS_TRANSLATE_SPECIAL['routes']}"],
            'domain': entry[f"option_data.{self.FIELDS_TRANSLATE_SPECIAL['domain']}"],
            'ntp_servers': entry['option_data.ntp_servers'],
            'time_servers': entry['option_data.time_servers'],
            'tftp_server': entry[f"option_data.{self.FIELDS_TRANSLATE_SPECIAL['tftp_server']}"],
            'tftp_file': entry[f"option_data.{self.FIELDS_TRANSLATE_SPECIAL['tftp_file']}"],
            'v6_only_preferred': entry['option_data.v6_only_preferred'],
        }

    def _build_request(self) -> dict:
        raw_request = self.b.build_request(ignore_fields=self.API_FIELDS_OPTIONS)

        raw_request[self.API_KEY]['pools'] = self.POOL_JOIN_CHAR.join(self.p['pools'])
        raw_request[self.API_KEY][self.API_ATTR_OPTIONS] = {
            self.FIELDS_TRANSLATE_SPECIAL['dns']: self.b.RESP_JOIN_CHAR.join(self.p['dns']),
            self.FIELDS_TRANSLATE_SPECIAL['gateway']: self.b.RESP_JOIN_CHAR.join(self.p['gateway']),
            self.FIELDS_TRANSLATE_SPECIAL['routes']: self.p['routes'],
            self.FIELDS_TRANSLATE_SPECIAL['domain']: self.p['domain'],
            self.FIELDS_TRANSLATE_SPECIAL['tftp_server']: self.p['tftp_server'],
            self.FIELDS_TRANSLATE_SPECIAL['tftp_file']: self.p['tftp_file'],
            'ntp_servers': self.b.RESP_JOIN_CHAR.join(self.p['ntp_servers']),
            'time_servers': self.b.RESP_JOIN_CHAR.join(self.p['time_servers']),
            'domain_search': self.b.RESP_JOIN_CHAR.join(self.p['domain_search']),
            'v6_only_preferred': self.p['v6_only_preferred'],
        }

        return raw_request
