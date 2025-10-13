#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/firewall.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, PURGE_MOD_ARGS, INFO_MOD_ARG, RELOAD_MOD_ARG

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/alias.html'
# EXAMPLES = 'https://github.com/O-X-L/ansible-opnsense/blob/latest/docs/tests/alias.yml'


def run_module(module_input):
    module_args = dict(
        aliases=dict(
            type='dict', required=False, default={},
            description='Configured aliases - compared against existing ones'
        ),
        fail_all=dict(
            type='bool', required=False, default=False, aliases=['fail'],
            description='Fail module if single alias fails to be purged.'
        ),
        **RELOAD_MOD_ARG,
        **INFO_MOD_ARG,
        **PURGE_MOD_ARGS,
        **OPN_MOD_ARGS,
    )

    AnsibleModule(
        module_input=module_input,
        argument_spec=module_args,
        supports_check_mode=True,
    ).fail_json('This module was deprecated in favor of: https://ansible-opnsense.oxl.app/modules/1_multi.html')







if __name__ == '__main__':
    pass
