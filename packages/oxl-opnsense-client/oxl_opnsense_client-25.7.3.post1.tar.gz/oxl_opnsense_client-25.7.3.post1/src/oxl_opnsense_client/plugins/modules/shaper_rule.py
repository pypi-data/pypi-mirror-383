#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/core/trafficshaper.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.rule import \
        RULE_MOD_ARG_ALIASES
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.shaper_rule import Rule

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/shaper.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/shaper.html'


def run_module(module_input):
    module_args = dict(
        target_pipe=dict(type='str', required=False, aliases=['pipe']),
        target_queue=dict(type='str', required=False, aliases=['queue']),
        sequence=dict(
            type='int', required=False, default=1, aliases=RULE_MOD_ARG_ALIASES['sequence']
        ),
        interface=dict(
            type='str', required=False, default='lan', aliases=RULE_MOD_ARG_ALIASES['interface'],
            description='Matching packets traveling to/from interface',
        ),
        interface2=dict(
            type='str', required=False, aliases=['int2', 'i2'],
            description='Secondary interface, matches packets traveling to/from interface '
                        '(1) to/from interface (2). can be combined with direction.',
        ),
        protocol=dict(
            type='str', required=False, default='ip', aliases=RULE_MOD_ARG_ALIASES['protocol'],
            description="Protocol like 'ip', 'ipv4', 'tcp', 'udp' and so on."
        ),
        max_packet_length=dict(
            type='int', required=False, aliases=['max_packet_len', 'packet_len', 'iplen'],
        ),
        source_invert=dict(
            type='bool', required=False, default=False,
            aliases=RULE_MOD_ARG_ALIASES['source_invert'],
        ),
        source_net=dict(
            type='list', elements='str', required=False, default='any', aliases=RULE_MOD_ARG_ALIASES['source_net'],
            description="Source ip or network, examples 10.0.0.0/24, 10.0.0.1"
        ),
        source_port=dict(
            type='str', required=False, default='any', aliases=RULE_MOD_ARG_ALIASES['source_port'],
        ),
        destination_invert=dict(
            type='bool', required=False, default=False,
            aliases=RULE_MOD_ARG_ALIASES['destination_invert'],
        ),
        destination_net=dict(
            type='list', elements='str', required=False, default='any', aliases=RULE_MOD_ARG_ALIASES['destination_net'],
            description='Destination ip or network, examples 10.0.0.0/24, 10.0.0.1'
        ),
        destination_port=dict(
            type='str', required=False, default='any',
            aliases=RULE_MOD_ARG_ALIASES['destination_port'],
        ),
        dscp=dict(
            type='list', required=False, elements='str', default=[],
            description='One or multiple DSCP values',
            choices=[
                'be', 'ef', 'af11', 'af12', 'af13', 'af21', 'af22', 'af23', 'af31', 'af32', 'af33',
                'af41', 'af42', 'af43', 'cs1', 'cs2', 'cs3', 'cs4', 'cs5', 'cs6', 'cs7',
            ]
        ),
        direction=dict(
            type='str', required=False, aliases=RULE_MOD_ARG_ALIASES['direction'],
            choices=['in', 'out'], description='Leave empty for both'
        ),
        description=dict(type='str', required=True, aliases=['desc']),
        reset=dict(
            type='bool', required=False, default=False, aliases=['flush'],
            description='If the running config should be flushed and reloaded on change - '
                        'will take some time. This might have impact on other services using '
                        'the same technology underneath (such as Captive portal)'
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

    module_wrapper(Rule(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
