#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/firmware.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.helper.utils import profiler
    from plugins.module_utils.main.package_main import process
    from plugins.module_utils.defaults.main import OPN_MOD_ARGS

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/package.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/package.html'


def run_module(module_input):
    module_args = dict(
        name=dict(
            type='list', required=True, elements='str',
            description='Package or list of packages to process'
        ),
        action=dict(
            type='str', required=True,
            choices=['install', 'reinstall', 'remove', 'lock', 'unlock']
        ),
        post_sleep=dict(
            type='int', required=False, default=3,
            description='The firewall needs some time to update package info'
        ),
        **OPN_MOD_ARGS
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

    if module.params['profiling'] or module.params['debug']:
        profiler(
            check=process, kwargs=dict(
                m=module, p=module.params, r=result,
            ),
        )

    else:
        process(m=module, p=module.params, r=result)

    return result






if __name__ == '__main__':
    pass
