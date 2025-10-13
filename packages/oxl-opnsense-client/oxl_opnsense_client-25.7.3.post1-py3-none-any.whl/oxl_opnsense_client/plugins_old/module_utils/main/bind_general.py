from ..helper.main import simplify_translate, validate_int_fields, is_ip, is_unset
from ..base.cls import GeneralModule


class General(GeneralModule):
    CMDS = {
        'set': 'set',
        'search': 'get',
    }
    API_KEY_PATH = 'general'
    API_MOD = 'bind'
    API_CONT = 'general'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reconfigure'
    FIELDS_CHANGE = [
        'ipv6', 'response_policy_zones', 'port', 'listen_ipv4', 'listen_ipv6',
        'query_source_ipv4', 'query_source_ipv6', 'transfer_source_ipv4', 'transfer_source_ipv6',
        'forwarders', 'filter_aaaa_v4', 'filter_aaaa_v6', 'filter_aaaa_acl', 'log_size',
        'cache_size', 'recursion_acl', 'transfer_acl', 'dnssec_validation', 'hide_hostname',
        'hide_version', 'prefetch', 'ratelimit', 'ratelimit_count', 'ratelimit_except',
        'enabled'
    ]
    FIELDS_ALL = FIELDS_CHANGE
    FIELDS_TRANSLATE = {
        'ipv6': 'disablev6',
        'response_policy_zones': 'enablerpz',
        'listen_ipv4': 'listenv4',
        'listen_ipv6': 'listenv6',
        'query_source_ipv4': 'querysource',
        'query_source_ipv6': 'querysourcev6',
        'transfer_source_ipv4': 'transfersource',
        'transfer_source_ipv6': 'transfersourcev6',
        'filter_aaaa_v4': 'filteraaaav4',
        'filter_aaaa_v6': 'filteraaaav6',
        'filter_aaaa_acl': 'filteraaaaacl',
        'log_size': 'logsize',
        'cache_size': 'maxcachesize',
        'recursion_acl': 'recursion',
        'transfer_acl': 'allowtransfer',
        'query_acl': 'allowquery',
        'dnssec_validation': 'dnssecvalidation',
        'hide_hostname': 'hidehostname',
        'hide_version': 'hideversion',
        'prefetch': 'disableprefetch',
        'ratelimit': 'enableratelimiting',
        'ratelimit_count': 'ratelimitcount',
        'ratelimit_except': 'ratelimitexcept',
    }
    FIELDS_BOOL_INVERT = ['ipv6', 'prefetch']
    FIELDS_TYPING = {
        'bool': [
            'ipv6', 'response_policy_zones', 'filter_aaaa_v4', 'filter_aaaa_v6', 'hide_hostname',
            'hide_version', 'prefetch', 'ratelimit', 'enabled',
        ],
        'list': [
            'ratelimit_except', 'filter_aaaa_acl', 'forwarders', 'listen_ipv6', 'listen_ipv4',
            'transfer_acl', 'query_acl', 'recursion_acl',
        ],
        'select': ['dnssec_validation'],
    }
    INT_VALIDATIONS = {
        'ratelimit_count': {'min': 1, 'max': 1000},
        'cache_size': {'min': 1, 'max': 99},
        'log_size': {'min': 1, 'max': 1000},
        'port': {'min': 1, 'max': 65535},
    }

    def __init__(self, m, result: dict):
        GeneralModule.__init__(self=self, m=m, r=result)
        self.existing_acls = None
        self.acls_needed = False

    def check(self) -> None:
        # pylint: disable=W0201
        validate_int_fields(m=self.m, data=self.p, field_minmax=self.INT_VALIDATIONS)

        for field in [
            'listen_ipv4', 'query_source_ipv4', 'transfer_source_ipv4',
            'listen_ipv6', 'query_source_ipv6', 'transfer_source_ipv6',
        ]:
            if isinstance(self.p[field], list):
                for ip in self.p[field]:
                    if not is_ip(ip, ignore_empty=True):
                        self.m.fail(
                            f"It seems you provided an invalid IP address as '{field}': '{ip}'"
                        )

                if is_unset(self.p[field]):
                    self.m.fail(
                        f"You need to supply at least one value as '{field}'! "
                        'Leave it empty to only use localhost.'
                    )

            else:
                ip = self.p[field]
                if not is_ip(ip, ignore_empty=True):
                    self.m.fail(
                        f"It seems you provided an invalid IP address as '{field}': '{ip}'"
                    )

        if not is_unset(self.p['recursion_acl']) or len(self.p['transfer_acl']) > 0 or len(self.p['query_acl']) > 0:
            # to save time on call if not needed
            self.acls_needed = True

        self.settings = self.get_existing()

        if self.acls_needed:
            self.b.find_multiple_links(
                field='recursion_acl',
                existing=self.existing_acls,
            )
            self.b.find_multiple_links(
                field='transfer_acl',
                existing=self.existing_acls,
            )
            self.b.find_multiple_links(
                field='query_acl',
                existing=self.existing_acls,
            )

        self._build_diff()

    def get_existing(self) -> dict:
        if self.acls_needed:
            self.existing_acls = self.s.get(cnf={
                **self.call_cnf, **{'command': self.CMDS['search'], 'controller': 'acl'}
            })['acl']['acls']['acl']

        return simplify_translate(
            existing=self.s.get(cnf={
                **self.call_cnf, **{'command': self.CMDS['search']}
            })[self.API_KEY_PATH],
            translate=self.FIELDS_TRANSLATE,
            typing=self.FIELDS_TYPING,
            bool_invert=self.FIELDS_BOOL_INVERT,
        )
