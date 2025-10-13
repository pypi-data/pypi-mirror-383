#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_ONLY_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.interface_gif import Gif

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/interface.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/interface.html'


def run_module(module_input):
    module_args = dict(
        description=dict(
            type='str', required=True, aliases=['desc'],
            description='The unique description used to match the configured entries to the existing ones.',
        ),
        local=dict(
            type='str', required=False, aliases=['l', 'local_addr'],
            description='The local address or interface to use.',
        ),
        remote=dict(
            type='str', required=False, aliases=['r', 'remote_addr'],
            description='Peer address where encapsulated gif packets will be sent.',
        ),
        tunnel_local=dict(
            type='str', required=False, aliases=['tl', 'tunnel_local_addr'],
            description='Local gif tunnel endpoint.',
        ),
        tunnel_remote=dict(
            type='str', required=False, aliases=['tr', 'tunnel_remote_addr'],
            description='Remote gif tunnel endpoint.',
        ),
        tunnel_remote_net=dict(
            type='int', required=False, default=32,
            description="Netmask 'ipv4' or prefix 'ipv6' to use for this tunnel",
        ),
        ingress_filtering=dict(
            type='bool', required=False, default=True, aliases=['filtering'],
            description='Enable ingress filtering on outer tunnel source tunnel',
        ),
        ecn_friendly=dict(
            type='bool', required=False, default=False, aliases=['ecn'],
            description='Enable ECN friendly behavior this violates RFC2893',
        ),
        **RELOAD_MOD_ARG,
        **STATE_ONLY_MOD_ARG,
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
        required_if=[
            ('state', 'present', ('local', 'remote', 'tunnel_local', 'tunnel_remote')),
        ],
    )

    module_wrapper(Gif(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
