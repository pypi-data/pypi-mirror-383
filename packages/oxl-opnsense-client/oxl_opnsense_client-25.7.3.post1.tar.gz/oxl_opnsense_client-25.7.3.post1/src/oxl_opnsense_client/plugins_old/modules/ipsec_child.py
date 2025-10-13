from ..module_input import validate_input, ModuleInput, valid_results
from ..module_utils.helper.wrapper import module_wrapper
from ..module_utils.defaults.main import RELOAD_MOD_ARG, STATE_MOD_ARG
from ..module_utils.main.ipsec_child import Child


def run_module(module_input: ModuleInput, result: dict = None) -> dict:
    result = valid_results(result)

    module_args = dict(
        name=dict(
            type='str', required=True, aliases=['description', 'desc'],
            description='Unique name to identify the entry'
        ),
        connection=dict(
            type='str', required=False, aliases=['tunnel', 'conn', 'tun'],
            description='Connection to link this child to'
        ),
        mode=dict(
            type='str', required=False, default='tunnel',
            choices=['tunnel', 'transport', 'pass', 'drop'],
            description='IPsec Mode to establish CHILD_SA with. tunnel negotiates the CHILD_SA in IPsec Tunnel '
                        'Mode whereas transport uses IPsec Transport Mode. pass and drop are used to install '
                        'shunt policies which explicitly bypass the defined traffic from IPsec processing or '
                        'drop it, respectively',
        ),
        request_id=dict(
            type='str', required=False, aliases=['req_id', 'reqid'],
            description='This might be helpful in some scenarios, like route based tunnels (VTI), but works only if '
                        'each CHILD_SA configuration is instantiated not more than once. The default uses dynamic '
                        'reqids, allocated incrementally',
        ),
        esp_proposals=dict(
            type='list', elements='str', required=False, default=['default'],
            aliases=['esp_props', 'esp'],
        ),
        sha256_96=dict(
            type='bool', required=False, default=False, aliases=['sha256'],
            description='HMAC-SHA-256 is used with 128-bit truncation with IPsec. For compatibility with '
                        'implementations that incorrectly use 96-bit truncation this option may be enabled to '
                        'configure the shorter truncation length in the kernel. This is not negotiated, so this '
                        'only works with peers that use the incorrect truncation length (or have this option enabled)',
        ),
        start_action=dict(
            type='str', required=False, aliases=['start'], default='start',
            choices=['none', 'trap|start', 'route', 'start', 'trap'],
            description='Action to perform after loading the configuration. The default of none loads the connection '
                        'only, which then can be manually initiated or used as a responder configuration. The value '
                        'trap installs a trap policy which triggers the tunnel as soon as matching traffic has been '
                        'detected. The value start initiates the connection actively. To immediately initiate a '
                        'connection for which trap policies have been installed, user Trap|start',
        ),
        close_action=dict(
            type='str', required=False, aliases=['close'], default='none',
            choices=['none', 'trap', 'start'],
        ),
        dpd_action=dict(
            type='str', required=False, aliases=['dpd'], default='clear',
            choices=['clear', 'trap', 'start'],
        ),
        policies=dict(
            type='bool', required=False, default=True, aliases=['pols'],
            description='Whether to install IPsec policies or not. Disabling this can be useful in some scenarios '
                        'e.g. VTI where policies are not managed by the IKE daemon',
        ),
        local_net=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['local_traffic_selectors', 'local_cidr', 'local_ts', 'local'],
            description='List of local traffic selectors to include in CHILD_SA. Each selector is a CIDR '
                        'subnet definition',
        ),
        remote_net=dict(
            type='list', elements='str', required=False, default=[],
            aliases=['remote_traffic_selectors', 'remote_cidr', 'remote_ts', 'remote'],
            description='List of remote traffic selectors to include in CHILD_SA. Each selector is a CIDR '
                        'subnet definition',
        ),
        rekey_seconds=dict(
            type='int', default=3600, required=False, aliases=['rekey_time', 'rekey'],
        ),
        **RELOAD_MOD_ARG,
        **STATE_MOD_ARG,
    )

    validate_input(i=module_input, definition=module_args)
    module_wrapper(Child(m=module_input, result=result))
    return result
