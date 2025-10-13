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
    from plugins.module_utils.main.frr_ospf3_redistribution import \
        Redistribution

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/frr_ospf.html#oxlorg-opnsense-frr-ospf3-redistribution'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/frr_ospf.html#id2'


def run_module(module_input):
    module_args = dict(
        redistribute=dict(type='str', required=False, choices=['bgp', 'connected', 'kernel', 'rip', 'static']),
        description=dict(type='str', required=False, aliases=['desc']),
        route_map=dict(
            type='str', required=False, aliases=['map', 'rm']
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

    module_wrapper(Redistribution(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
