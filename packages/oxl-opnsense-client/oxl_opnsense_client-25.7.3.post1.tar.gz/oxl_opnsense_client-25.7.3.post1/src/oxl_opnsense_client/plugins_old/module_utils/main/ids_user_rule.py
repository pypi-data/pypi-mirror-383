from ..base.cls import BaseModule


class Rule(BaseModule):
    FIELD_ID = 'description'
    CMDS = {
        'add': 'addUserRule',
        'set': 'setUserRule',
        'del': 'delUserRule',
        'search': 'searchUserRule',
        'detail': 'getUserRule',
        'toggle': 'toggleUserRule',
    }
    API_KEY = 'rule'
    API_KEY_PATH = f'userDefinedRules.{API_KEY}'
    API_MOD = 'ids'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    API_CMD_REL = 'reloadRules'
    FIELDS_CHANGE = ['source_ip', 'destination_ip', 'ssl_fingerprint', 'action', 'bypass']
    FIELDS_ALL = ['enabled', FIELD_ID]
    FIELDS_ALL.extend(FIELDS_CHANGE)
    FIELDS_TRANSLATE = {
        'source_ip': 'source',
        'destination_ip': 'destination',
        'ssl_fingerprint': 'fingerprint',
    }
    FIELDS_TYPING = {
        'bool': ['enabled', 'bypass'],
        'select': ['action'],
    }
    EXIST_ATTR = 'rule'
    QUERY_MAX_RULES = 5000

    def __init__(self, m, result: dict):
        BaseModule.__init__(self=self, m=m, r=result)
        self.rule = {}
        self.exists = False

    def check(self):
        self._search_call()
        self.r['diff']['after'] = self.b.build_diff(data=self.p)

    def get_existing(self) -> list:
        return self._search_call()

    def _search_call(self) -> list:
        existing = self.s.post(cnf={
            **self.call_cnf,
            'command': self.CMDS['search'],
            'data': {'current': 1, 'rowCount': self.QUERY_MAX_RULES, 'sort': self.FIELD_ID},
        })['rows']

        if self.FIELD_ID in self.p:  # list module
            for rule in existing:
                if rule[self.FIELD_ID] == self.p[self.FIELD_ID]:
                    self.exists = True
                    self.call_cnf['params'] = [rule['uuid']]
                    self.rule = self.b.simplify_existing(
                        self.s.get(cnf={
                            **self.call_cnf,
                            'command': self.CMDS['detail'],
                        })[self.API_KEY]
                    )
                    self.rule['uuid'] = rule['uuid']
                    self.r['diff']['before'] = self.rule

        return existing
