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
        OPN_MOD_ARGS, STATE_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.monit_service import Service

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/monit.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/monit.html'


def run_module(module_input):
    module_args = dict(
        name=dict(type='str', required=True, description='Unique service name'),
        type=dict(
            type='str', required=False,
            choices=[
                'process', 'file', 'fifo', 'filesystem', 'directory', 'host', 'system',
                'custom', 'network',
            ]
        ),
        pidfile=dict(type='path', required=False),
        match=dict(type='str', required=False),
        path=dict(
            type='path', required=False,
            description='According to the service type path can be a file or a directory',
        ),
        service_timeout=dict(type='int', required=False, default=300, aliases=['svc_timeout']),
        address=dict(
            type='str', required=False,
            description="The target IP address for 'Remote Host' and 'Network' checks",
        ),
        interface=dict(
            type='str', required=False,
            description="The existing Interface for 'Network' checks"
        ),
        start=dict(
            type='str', required=False,
            description='Absolute path to the executable with its arguments to run '
                        'at service-start',
        ),
        stop=dict(
            type='str', required=False,
            description='Absolute path to the executable with its arguments to run '
                        'at service-stop',
        ),
        tests=dict(type='list', elements='str', required=False, default=[]),
        depends=dict(
            type='list', elements='str', required=False, default=[],
            description='Optionally define a (list of) service(s) which are required '
                        'before monitoring this one, if any of the dependencies are either '
                        'stopped or unmonitored this service will stop/unmonitor too',
        ),
        polltime=dict(
            type='str',  required=False,
            description='Set the service poll time. Either as a number of cycles '
                        "'NUMBER CYCLES' or Cron-style '* 8-19 * * 1-5'"
        ),
        description=dict(type='str', required=False, aliases=['desc']),
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

    module_wrapper(Service(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
