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
        OPN_MOD_ARGS, EN_ONLY_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.frr_bgp_general import General

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/frr_bgp.html#oxlorg-opnsense-frr-bgp-general'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/frr_bgp.html#id1'


def run_module(module_input):
    module_args = dict(
        as_number=dict(type='int', required=True, aliases=['as', 'as_nr']),
        distance=dict(type='int', required=False),
        id=dict(type='str', required=False, aliases=['router_id']),
        graceful=dict(
            type='bool', required=False, default=False,
            description='BGP graceful restart functionality as defined in '
                        'RFC-4724 defines the mechanisms that allows BGP speaker '
                        'to continue to forward data packets along known routes '
                        'while the routing protocol information is being restored'
        ),
        networks=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['nets'],
            description='Select the network to advertise, you have to set a '
                        'Null route via System -> Routes'
        ),
        network_import_check=dict(
            type='bool', required=False, default=True, aliases=['network_check'],
            description="When enabled (default), BGP only announces networks set at 'Network' "
                        "if they are present in the routers routing table (alternatively, "
                        "you can also set a null-route via System -> Routes). If disabled, "
                        "all configured networks will be announced."
        ),
        log_neighbor_changes=dict(
            type='bool', required=False, default=False, aliases=['log_neigh'],
            description='Enable extended logging of BGP neighbor changes'
        ),
        **RELOAD_MOD_ARG,
        **EN_ONLY_MOD_ARG,
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

    module_wrapper(General(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
