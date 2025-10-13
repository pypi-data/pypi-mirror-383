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
    from plugins.module_utils.main.wireguard_server import Server

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/wireguard.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/wireguard.html'


def run_module(module_input):
    module_args = dict(
        name=dict(type='str', required=True),
        public_key=dict(type='str', required=False, aliases=['pubkey', 'pub']),
        private_key=dict(type='str', required=False, no_log=True, aliases=['privkey', 'priv']),
        port=dict(type='int', required=False),
        mtu=dict(type='int', required=False, default=1420),
        dns_servers=dict(
            type='list', elements='str', required=False, default=[], aliases=['dns'],
        ),
        allowed_ips=dict(
            type='list', elements='str', required=False, default=[],
            aliases=[
                'tunnel_ips', 'tunnel_ip', 'tunneladdress', 'tunnel_adresses',
                'addresses', 'address', 'tunnel_address', 'allowed',
            ]
        ),
        disable_routes=dict(type='bool', default=False, required=False, aliases=['disableroutes']),
        gateway=dict(type='str', required=False, aliases=['gw']),
        vip=dict(
            type='str', required=False,
            aliases=['vip_depend', 'carp', 'carp_depend'],
            description='The Virtual-CARP-IP (CARP VHID) to depend on. '
                        'When this virtual address is not in master state, then the instance will be shutdown'
        ),
        peers=dict(type='list', elements='str', required=False, default=[], aliases=['clients']),
        link_peers=dict(
            type='bool', default=True, required=False,
            description="Whether you want to link peers by the server instance. "
                        "If that is the case - you should disable 'link_servers' on your peer-entries. "
                        "Will always be true if you supply any peers."
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

    module_wrapper(Server(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
