#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/plugins/bind.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.defaults.legacy_multi import \
        FAIL_MOD_ARG_MULTI, INFO_MOD_ARG
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, RELOAD_MOD_ARG, STATE_MOD_ARG

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/bind.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/bind.html'


def run_module(module_input):
    module_args = dict(
        records=dict(type='dict', required=True),
        match_fields=dict(
            type='list', required=False, elements='str',
            description='Fields that are used to match configured records with the running config - '
                        "if any of those fields are changed, the module will think it's a new entry",
            choices=['domain', 'name', 'type', 'value'],
            default=['domain', 'name', 'type'],
        ),
        **FAIL_MOD_ARG_MULTI,
        **STATE_MOD_ARG,
        **INFO_MOD_ARG,
        **OPN_MOD_ARGS,
        **RELOAD_MOD_ARG,
    )

    AnsibleModule(
        module_input=module_input,
        argument_spec=module_args,
        supports_check_mode=True,
    ).fail_json('This module was deprecated in favor of: https://ansible-opnsense.oxl.app/modules/1_multi.html')







if __name__ == '__main__':
    pass
