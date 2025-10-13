#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/firmware.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.api import Session
    from plugins.module_utils.defaults.main import OPN_MOD_ARGS
    from plugins.module_utils.helper.system import wait_for_response, \
        wait_for_update, get_upgrade_status

except MODULE_EXCEPTIONS:
    module_dependency_error()

# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/package.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/package.html'


def run_module(module_input):
    module_args = dict(
        action=dict(
            type='str', required=True,
            choices=['poweroff', 'reboot', 'update', 'upgrade', 'audit'],
            description="WARNING: Only use the 'upgrade' option in test-environments. "
                        "In production you should use the WebUI to upgrade!"
        ),
        wait=dict(type='bool', required=False, default=True),
        wait_timeout=dict(type='int', required=False, default=90),
        poll_interval=dict(type='int', required=False, default=2),
        force_upgrade=dict(type='bool', required=False, default=False),
        **OPN_MOD_ARGS
    )

    module = AnsibleModule(
        module_input=module_input,
        argument_spec=module_args,
        supports_check_mode=True,
    )

    result = {
        'changed': True,
        'failed': False,
        'timeout_exceeded': False,
    }

    if module.params['action'] == 'upgrade' and not module.params['force_upgrade']:
        module.fail_json(
            "If you really want to perform an upgrade - you need to additionally supply the 'force_upgrade' argument. "
            "WARNING: Using the 'upgrade' action is only recommended for test-environments. "
            "In production you should use the WebUI to upgrade!"
        )

    if not module.check_mode:
        with Session(module=module) as s:
            upgrade_status = get_upgrade_status(s)
            if upgrade_status['status'] not in ['done', 'error']:
                module.fail_json(
                    f'System may be upgrading! System-actions are currently blocked! Details: {upgrade_status}'
                )

            s.post({
                'command': module.params['action'],
                'module': 'core',
                'controller': 'firmware',
            })

            if module.params['wait']:
                if module.params['debug']:
                    module.warn(f"Waiting for firewall to complete '{module.params['action']}'!")

                try:
                    if module.params['action'] in ['upgrade', 'update']:
                        result['failed'] = not wait_for_update(module=module, s=s)

                    elif module.params['action'] == 'reboot':
                        result['failed'] = not wait_for_response(module=module)

                except TimeoutError:
                    result['timeout_exceeded'] = True

    return result






if __name__ == '__main__':
    pass
