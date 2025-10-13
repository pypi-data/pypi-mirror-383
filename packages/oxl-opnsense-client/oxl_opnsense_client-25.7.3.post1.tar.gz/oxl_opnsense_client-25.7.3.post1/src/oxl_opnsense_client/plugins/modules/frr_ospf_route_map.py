#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/plugins/quagga.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.frr_ospf_route_map import RouteMap

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/frr_ospf.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/frr_ospf.html'


def run_module(module_input):
    module_args = dict(
        name=dict(type='str', required=True),
        action=dict(type='str', required=False, options=['permit', 'deny']),
        id=dict(
            type='int', required=False,
            description='Route-map ID between 10 and 99. Be aware that the sorting '
                        'will be done under the hood, so when you add an entry between '
                        "it get's to the right position"
        ),
        prefix_list=dict(
            type='list', elements='str', required=False, default=[], aliases=['prefix']
        ),
        set=dict(
            type='str', required=False,
            description='Free text field for your set, please be careful! '
                        'You can set e.g. "local-preference 300" or "community 1:1" '
                        '(http://www.nongnu.org/quagga/docs/docs-multi/'
                        'Route-Map-Set-Command.html#Route-Map-Set-Command)'
        ),
        **STATE_MOD_ARG,
        **RELOAD_MOD_ARG,
        **OPN_MOD_ARGS,
    )

    result = dict(
        changed=False,
        diff={
            'before': {},
            'after': {},
        }
    )

    module = AnsibleModule(
        module_input=module_input,
        argument_spec=module_args,
        supports_check_mode=True,
    )

    module_wrapper(RouteMap(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
