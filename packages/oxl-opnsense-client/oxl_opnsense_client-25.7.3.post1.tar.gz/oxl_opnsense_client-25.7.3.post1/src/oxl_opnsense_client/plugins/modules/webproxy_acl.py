#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (C) 2025, Pascal Rath <contact+opnsense@OXL.at>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

from basic.ansible import AnsibleModule

from plugins.module_utils.base.handler import \
    module_dependency_error, MODULE_EXCEPTIONS

try:
    from plugins.module_utils.base.wrapper import module_wrapper
    from plugins.module_utils.defaults.main import \
        OPN_MOD_ARGS, RELOAD_MOD_ARG
    from plugins.module_utils.main.webproxy_acl import General

except MODULE_EXCEPTIONS:
    module_dependency_error()


# DOCUMENTATION = 'https://ansible-opnsense.oxl.app/modules/webproxy.html'
# EXAMPLES = 'https://ansible-opnsense.oxl.app/modules/webproxy.html'


def run_module(module_input):
    module_args = dict(
        allow=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['allow_subnets', 'subnets'],
            description='IPs and Subnets you want to allow access to the '
                        'proxy server'
        ),
        exclude=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['unrestricted', 'ignore'],
            description='IPs and Subnets you want to bypass the proxy server'
        ),
        banned=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['blocked', 'block', 'ban'],
            description='IPs and Subnets you want to deny access to the '
                        'proxy server'
        ),
        exclude_domains=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['safe_list', 'whitelist'],
            description='Whitelist destination domains. You may use a regular expression, use a '
                        'comma or press Enter for new item. Examples: "mydomain.com" matches on '
                        '"*.mydomain.com"; "^https?:\\/\\/([a-zA-Z]+)\\.mydomain\\." matches on '
                        '"http(s)://textONLY.mydomain.*"; "\\.gif$" matches on "\\*.gif" but not on '
                        '"\\*.gif\\test"; "\\[0-9]+\\.gif$" matches on "\\123.gif" but not on "\\test.gif"'
        ),
        block_domains=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['block', 'block_list', 'blacklist'],
            description='Blacklist destination domains. You may use a regular expression, '
                        'use a comma or press Enter for new item. Examples: "mydomain.com" '
                        'matches on "*.mydomain.com"; "^https?:\\/\\/([a-zA-Z]+)\\.mydomain\\." '
                        'matches on "http(s)://textONLY.mydomain.*"; "\\.gif$" matches on "*.gif" '
                        'but not on "\\*.gif\\test"; "\\[0-9]+\\.gif$" matches on "\\123.gif" but '
                        'not on "\\test.gif"'
        ),
        block_user_agents=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['block_ua', 'block_list_ua'],
            description='Block user-agents. You may use a regular expression, use a comma or '
                        'press Enter for new item. Examples: "^(.)+Macintosh(.)+Firefox/37\\.0" '
                        'matches on "Macintosh version of Firefox revision 37.0"; "^Mozilla" '
                        'matches on "all Mozilla based browsers"'
        ),
        block_mime_types=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['block_mime', 'block_list_mime'],
            description='Block specific MIME type reply. You may use a regular expression, '
                        'use a comma or press Enter for new item. Examples: "video/flv" matches '
                        'on "Flash Video"; "application/x-javascript" matches on "javascripts"'
        ),
        exclude_google=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['safe_list_google'],
            description='The domain that will be allowed to use Google GSuite. '
                        'All accounts that are not in this domain will be blocked to use it'
        ),
        youtube_filter=dict(
            type='str', required=False, aliases=['youtube'],
            choices=['strict', 'moderate'], description='Youtube filter level'
        ),
        ports_tcp=dict(
            type='list', elements='str', required=False, aliases=['p_tcp'],
            default=[
                '80:http', '21:ftp', '443:https', '70:gopher', '210:wais', '1025-65535:unregistered ports',
                '280:http-mgmt', '488:gss-http', '591:filemaker', '777:multiling http'
            ],
            description='Allowed destination TCP ports, you may use ranges (ex. 222-226) and '
                        'add comments with colon (ex. 22:ssh)'
        ),
        ports_ssl=dict(
            type='list', elements='str', required=False,
            default=['443:https'], aliases=['p_ssl'],
            description='Allowed destination SSL ports, you may use ranges (ex. 222-226) and '
                        'add comments with colon (ex. 22:ssh)'
        ),
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

    module_wrapper(General(module=module, result=result))
    return result






if __name__ == '__main__':
    pass
