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
    from plugins.module_utils.main.frr_bgp_prefix_list import Prefix

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/frr_bgp.html
#                  #oxlorg-opnsense-frr-bgp-prefix-list'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/frr_bgp.html#id3'


def run_module(module_input):
    module_args = dict(
        name=dict(type='str', required=True),
        seq=dict(type='str', required=True, aliases=['sequence', 'seq_number']),
        network=dict(type='str', required=False, aliases=['net']),
        description=dict(type='str', required=False, aliases=['desc']),
        version=dict(
            type='str', required=False, default='IPv4', options=['IPv4', 'IPv6'],
            aliases=['ipv']
        ),
        action=dict(type='str', required=False, options=['permit', 'deny']),
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

    module_wrapper(Prefix(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
