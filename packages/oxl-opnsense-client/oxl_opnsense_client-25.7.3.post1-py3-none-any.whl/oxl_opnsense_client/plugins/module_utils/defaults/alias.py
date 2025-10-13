from plugins.module_utils.defaults.main import \
    OPN_MOD_ARGS, STATE_MOD_ARG

ALIAS_DEFAULTS = {
    'state': 'present',
    'enabled': True,
    'description': '',
    'type': 'host',
    'content': [],
    'debug': False,
    'updatefreq_days': '',
    'interface': None,
    'path_expression': '',
}

ALIAS_MOD_ARG_ALIASES = {
    'name': ['n'],
    'content': ['c', 'cont'],
    'type': ['t'],
    'description': ['desc'],
    'state': ['st'],
    'enabled': ['en'],
    'interface': ['int', 'if'],
    'path_expression': ['pe', 'jq'],
}

ALIAS_MOD_ARGS = dict(
    name=dict(type='str', required=True, aliases=ALIAS_MOD_ARG_ALIASES['name']),
    description=dict(
        type='str', required=False, default=ALIAS_DEFAULTS['description'],
        aliases=ALIAS_MOD_ARG_ALIASES['description']
    ),
    content=dict(
        type='list', required=False, default=ALIAS_DEFAULTS['content'],
        aliases=ALIAS_MOD_ARG_ALIASES['content'], elements='str',
    ),
    type=dict(type='str', required=False, choices=[
        'host', 'network', 'port', 'url', 'urltable', 'geoip', 'networkgroup',
        'mac', 'dynipv6host', 'internal', 'external',
    ], default=ALIAS_DEFAULTS['type'], aliases=ALIAS_MOD_ARG_ALIASES['type']),
    updatefreq_days=dict(
        type='str', default=ALIAS_DEFAULTS['updatefreq_days'], required=False,
        description="Update frequency used by type 'urltable' in days - "
                    "per example '0.5' for 12 hours"
    ),
    interface=dict(
        type='str', default=ALIAS_DEFAULTS['interface'],
        aliases=ALIAS_MOD_ARG_ALIASES['interface'], required=False,
        description=' Select the interface for the V6 dynamic IP.',
    ),
    path_expression=dict(
        type='str', default=ALIAS_DEFAULTS['path_expression'],
        aliases=ALIAS_MOD_ARG_ALIASES['path_expression'], required=False,
        description='Simplified expression to select a field inside a container, a dot is used as field separator. '
                    'Expressions using the jq language are also supported.',
    ),
    **STATE_MOD_ARG,
    **OPN_MOD_ARGS,
)
