#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/monit.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_ONLY_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.monit_test import Test

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/monit.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/monit.html'


def run_module(module_input):
    module_args = dict(
        name=dict(type='str', required=True, description='Unique test name'),
        type=dict(
            type='str', required=False, default='Custom',
            choices=[
                'Existence', 'SystemResource', 'ProcessResource', 'ProcessDiskIO',
                'FileChecksum', 'Timestamp', 'FileSize', 'FileContent', 'FilesystemMountFlags',
                'SpaceUsage', 'InodeUsage', 'DiskIO', 'Permisssion', 'UID', 'GID', 'PID', 'PPID',
                'Uptime', 'ProgramStatus', 'NetworkInterface', 'NetworkPing', 'Connection', 'Custom',
            ],
            description='Custom will not be idempotent - will be translated on the server-side. '
                        "See 'list' module output for details"
        ),
        condition=dict(
            type='str', required=False,
            description="The test condition. Per example: "
                        "'cpu is greater than 50%' or "
                        "'failed host 127.0.0.1 port 22 protocol ssh'"
        ),
        action=dict(
            type='str', required=False, default='alert',
            choices=['alert', 'restart', 'start', 'stop', 'exec', 'unmonitor']
        ),
        path=dict(
            type='path', required=False,
            description='The absolute path to the script to execute - if action is '
                        "set to 'execute'. "
                        "Make sure the script is executable by the Monit service"
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
    )

    module_wrapper(Test(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
