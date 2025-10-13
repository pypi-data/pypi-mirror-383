#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/plugins/firewall.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.defaults.main import OPN_MOD_ARGS
    from plugins.module_utils.main.savepoint import SavePoint

except MODULE_EXCEPTIONS:
    module_dependency_error()

# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/savepoint.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/savepoint.html'


def run_module(module_input):
    module_args = dict(
        action=dict(
            type='str', required=False, default='create',
            choices=['create', 'revert', 'apply', 'cancel_rollback', 'cancel'],
        ),
        revision=dict(
            type='str', required=False,
            description='Savepoint revision to apply, revert or cancel_rollback'
        ),
        controller=dict(
            type='str', required=False, default='filter', description='Target API controller',
            choices=['source_nat', 'filter', 'one_to_one']
        ),
        api_module=dict(type='str', required=False, default='firewall', choices=['firewall']),
        **OPN_MOD_ARGS
    )

    result = dict(
        changed=False,
        diff={
            'before': {},
            'after': {},
        },
        revision='',
    )

    module = AnsibleModule(
        module_input=module_input,
        argument_spec=module_args,
        supports_check_mode=True,
    )

    sp = SavePoint(module=module, result=result)

    if module.params['action'] == 'create':
        result['revision'] = sp.create()

    else:
        if module.params['revision'] is None:
            module.fail_json('You need to provide a revision to execute this action!')

        if module.params['action'] == 'apply':
            sp.apply()

        elif module.params['action'] == 'revert':
            sp.revert()

        else:
            sp.cancel_rollback()
    return result






if __name__ == '__main__':
    pass
