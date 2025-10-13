#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/plugins/wireguard.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.wireguard_peer import Peer

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/wireguard.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/wireguard.html'


def run_module(module_input):
    module_args = dict(
        name=dict(type='str', required=True),
        public_key=dict(type='str', required=False, aliases=['pubkey', 'pub']),
        psk=dict(type='str', required=False, no_log=True),
        allowed_ips=dict(
            type='list', elements='str', required=False, default=[],
            aliases=[
                'tunnel_ips', 'tunnel_ip', 'tunneladdress', 'tunnel_adresses',
                'addresses', 'address', 'tunnel_address', 'allowed',
            ]
        ),
        server=dict(
            type='str', required=False,
            aliases=['target', 'server_address', 'serveraddress', 'endpoint']
        ),
        port=dict(type='int', required=False),
        keepalive=dict(type='int', required=False),
        servers=dict(type='list', elements='str', required=False, default=[], aliases=['instances']),
        link_servers=dict(
            type='bool', default=False, required=False,
            description="Whether you want to link servers instance by the peer. "
                        "If that is the case - you should disable 'link_peers' on your server-entries. "
                        "Will always be true if you supply any servers"
        ),
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

    module_wrapper(Peer(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
