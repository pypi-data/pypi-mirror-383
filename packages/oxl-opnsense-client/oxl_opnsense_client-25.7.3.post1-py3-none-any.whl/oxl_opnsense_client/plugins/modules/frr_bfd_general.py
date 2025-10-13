#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/plugins/wireguard.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, EN_ONLY_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.base.api import Session
    from plugins.module_utils.helper.main import \
        is_true, to_digit

except MODULE_EXCEPTIONS:
    module_dependency_error()

# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/frr_bfd.html#oxlorg-opnsense-frr-bfd-general'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/frr_bfd.html#id1'


def run_module(module_input):
    module_args = dict(
        **EN_ONLY_MOD_ARG,
        **OPN_MOD_ARGS,
        **RELOAD_MOD_ARG,
    )

    module = AnsibleModule(
        module_input=module_input,
        argument_spec=module_args,
        supports_check_mode=True,
    )

    result = dict(
        changed=False,
        diff={
            'before': {},
            'after': {'enabled': module.params['enabled']},
        }
    )

    with Session(module=module) as s:
        is_enabled = is_true(
            s.get(cnf={
                'module': 'quagga',
                'controller': 'bfd',
                'command': 'get',
            })['bfd']['enabled']
        )
        result['diff']['before']['enabled'] = is_enabled

        if is_enabled != module.params['enabled']:
            result['changed'] = True

            if not module.check_mode:
                s.post(cnf={
                    'module': 'quagga',
                    'controller': 'bfd',
                    'command': 'set',
                    'data': {'bfd': {'enabled': to_digit(module.params['enabled'])}}
                })
                s.post(cnf={
                    'module': 'quagga',
                    'controller': 'service',
                    'command': 'reconfigure',
                })

    return result






if __name__ == '__main__':
    pass
