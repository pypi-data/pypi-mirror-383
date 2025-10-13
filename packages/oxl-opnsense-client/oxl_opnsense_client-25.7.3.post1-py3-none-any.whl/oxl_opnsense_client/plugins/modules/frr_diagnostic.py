#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/plugins/quagga.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS
    from plugins.module_utils.base.api import single_get

except MODULE_EXCEPTIONS:
    module_dependency_error()

# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/frr_diagnostic.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/frr_diagnostic.html'


def run_module(module_input):
    module_args = dict(
        target=dict(
            type='str', required=True,
            choices=[
                'bgpneighbors', 'bgproute', 'bgproute4', 'bgproute6', 'bgpsummary',
                'generalroute', 'generalroute4', 'generalroute6', 'generalrunningconfig',
                'ospfdatabase', 'ospfinterface', 'ospfneighbor', 'ospfoverview', 'ospfroute',
                'ospfv3database', 'ospfv3interface', 'ospfv3neighbor', 'ospfv3overview',
                'ospfv3route',
            ],
            description='What information to query'
        ),
        **OPN_MOD_ARGS,
    )

    module = AnsibleModule(
        module_input=module_input,
        argument_spec=module_args,
        supports_check_mode=True,
    )

    non_json = ['generalrunningconfig']

    if module.params['target'] in non_json:
        params = []

    else:
        params = ['$format=”json”']

    info = single_get(
        module=module,
        cnf={
            'module': 'quagga',
            'controller': 'diagnostics',
            'command': module.params['target'],
            'params': params,
        }
    )

    if 'response' in info:
        info = info['response']

        if isinstance(info, str):
            info = info.strip()

    return info






if __name__ == '__main__':
    pass
