#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/plugins/firewall.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.rule import \
        RULE_MOD_ARGS
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.nat_source import SNat

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/nat_source.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/nat_source.html'


def run_module(module_input):
    shared_rule_args = {
        'sequence': RULE_MOD_ARGS['sequence'],
        'ip_protocol': RULE_MOD_ARGS['ip_protocol'],
        'protocol': RULE_MOD_ARGS['protocol'],
        'source_invert': RULE_MOD_ARGS['source_invert'],
        'source_net': RULE_MOD_ARGS['source_net'],
        'source_port': RULE_MOD_ARGS['source_port'],
        'destination_invert': RULE_MOD_ARGS['destination_invert'],
        'destination_net': RULE_MOD_ARGS['destination_net'],
        'destination_port': RULE_MOD_ARGS['destination_port'],
        'log': RULE_MOD_ARGS['log'],
        'uuid': RULE_MOD_ARGS['uuid'],
        'description': RULE_MOD_ARGS['description'],
    }

    module_args = dict(
        no_nat=dict(
            type='bool', required=False, default=False,
            description='Enabling this option will disable NAT for traffic matching '
                        'this rule and stop processing Outbound NAT rules.'
        ),
        interface=dict(type='str', required=False, aliases=['int', 'i']),
        target=dict(
            type='str', required=False, aliases=['tgt', 't'],
            description='NAT translation target - Packets matching this rule will be '
                        'mapped to the IP address given here.',
        ),
        target_port=dict(type='int', required=False, aliases=['nat_port', 'np']),
        match_fields=dict(
            type='list', required=True, elements='str',
            description='Fields that are used to match configured rules with the running config - '
                        "if any of those fields are changed, the module will think it's a new rule",
            choices=[
                'sequence', 'interface', 'target', 'target_port', 'ip_protocol', 'protocol',
                'source_invert', 'source_net', 'source_port', 'destination_invert', 'destination_net',
                'destination_port', 'description', 'uuid',
            ]
        ),
        **shared_rule_args,
        **STATE_MOD_ARG,
        **RELOAD_MOD_ARG,
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

    module_wrapper(SNat(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
