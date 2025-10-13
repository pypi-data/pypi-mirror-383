#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/unbound.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.unbound_forward import Forward

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/unbound_forwarding.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/unbound_forwarding.html'


def run_module(module_input):
    module_args = dict(
        domain=dict(
            type='str', required=False, aliases=['dom', 'd'],
            description='Domain of the host. All queries for this domain will be forwarded to the nameserver '
                        'specified. Leave empty to catch all queries and forward them to the nameserver'
        ),
        target=dict(
            type='str', required=True, aliases=['tgt', 'server', 'srv'],
            description='Server to forward the dns queries to'
        ),
        port=dict(
            type='int', required=False, default=53, aliases=['p'],
            description='DNS port of the target server'
        ),
        type=dict(type='str', required=False, choices=['forward'], default='forward'),
        forward_tcp=dict(
            type='bool', required=False, default=False, aliases=['forward_tcp_upstream', 'fwd_tcp'],
            description='Upstream queries use TCP only for transport regardless of global flag tcp-upstream. '
                        'Please note this setting applies to the domain, so when multiple forwarders are '
                        'defined for the same domain, all are assumed to use tcp only.'
        ),
        description=dict(type='str', required=False, aliases=['desc']),
        **RELOAD_MOD_ARG,
        **STATE_MOD_ARG,
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

    module_wrapper(Forward(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
