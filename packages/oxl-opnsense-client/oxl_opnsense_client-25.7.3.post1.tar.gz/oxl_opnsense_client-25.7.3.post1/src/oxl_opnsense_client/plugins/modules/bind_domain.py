#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

# see: https://docs.opnsense.org/development/api/plugins/bind.html

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, STATE_MOD_ARG, RELOAD_MOD_ARG
    from plugins.module_utils.main.bind_domain import \
        Domain

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/bind.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/bind.html'


def run_module(module_input):
    module_args = dict(
        name=dict(type='str', required=True, aliases=['domain_name', 'domain']),
        mode=dict(
            type='str', required=False, default='primary', choices=['primary', 'secondary']
        ),
        primary=dict(
            type='list', elements='str', required=False, aliases=['primary_ip', 'master', 'master_ip'], default=[],
            description='Set the IP address of primary server when using secondary mode'
        ),
        transfer_key_algo=dict(
            type='str', required=False,
            choices=[
                'hmac-sha512', 'hmac-sha384', 'hmac-sha256', 'hmac-sha224',
                'hmac-sha1', 'hmac-md5',
            ]
        ),
        transfer_key_name=dict(type='str', required=False),
        transfer_key=dict(type='str', required=False, no_log=True),
        allow_notify=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['allow_notify_secondary', 'allow_notify_slave'],
            description='A list of allowed IP addresses to receive notifies from'
        ),
        transfer_acl=dict(
            type='list', elements='str', required=False, default=[], aliases=['allow_transfer'],
            description='An ACL where you allow which server can retrieve this zone'
        ),
        query_acl=dict(
            type='list', elements='str', required=False, default=[], aliases=['allow_query'],
            description='An ACL where you allow which client are allowed '
                        'to query this zone'
        ),
        ttl=dict(
            type='int', required=False, default=86400,
            description='The general Time To Live for this zone'
        ),
        refresh=dict(
            type='int', required=False, default=21600,
            description='The time in seconds after which name servers should '
                        'refresh the zone information'
        ),
        retry=dict(
            type='int', required=False, default=3600,
            description='The time in seconds after which name servers should '
                        'retry requests if the primary does not respond'
        ),
        expire=dict(
            type='int', required=False, default=3542400,
            description='The time in seconds after which name servers should '
                        'stop answering requests if the primary does not respond'
        ),
        negative=dict(
            type='int', required=False, default=3600,
            description='The time in seconds after which an entry for a '
                        'non-existent record should expire from cache'
        ),
        admin_mail=dict(
            type='str', required=False, default='mail.opnsense.localdomain',
            description='The mail address of zone admin. A @-sign will '
                        'automatically be replaced with a dot in the zone data'
        ),
        server=dict(
            type='str', required=False, default='opnsense.localdomain', aliases=['dns_server'],
            description='Set the DNS server hosting this file. This should usually '
                        'be the FQDN of your firewall where the BIND plugin is installed'
        ),
        # serial=dict(type='str', required=False),
        **STATE_MOD_ARG,
        **OPN_MOD_ARGS,
        **RELOAD_MOD_ARG,
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

    module_wrapper(Domain(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
