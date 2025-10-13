from basic.ansible import AnsibleModule

from plugins.module_utils.base.api import \
    Session
from plugins.module_utils.base.cls import BaseModule


class Queue(BaseModule):
    FIELD_ID = 'description'
    CMDS = {
        'add': 'add_queue',
        'del': 'del_queue',
        'set': 'set_queue',
        'search': 'get',
        'toggle': 'toggle_queue',
    }
    API_KEY_PATH = 'ts.queues.queue'
    API_MOD = 'trafficshaper'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    FIELDS_CHANGE = [
        'codel_enable', 'codel_ecn_enable', 'pie_enable',  'mask',
        'pipe', 'buckets', 'codel_target', 'codel_interval', 'weight',
    ]
    FIELDS_ALL = ['enabled', FIELD_ID]
    FIELDS_ALL.extend(FIELDS_CHANGE)
    INT_VALIDATIONS = {
        'weight': {'min': 1, 'max': 100},
        'buckets': {'min': 1, 'max': 65535},
        'codel_target': {'min': 1, 'max': 10000},
        'codel_interval': {'min': 1, 'max': 10000},
    }
    FIELDS_TYPING = {
        'bool': ['enabled', 'pie_enable', 'codel_enable', 'codel_ecn_enable'],
        'select': ['mask', 'pipe'],
    }
    EXIST_ATTR = 'queue'
    TIMEOUT = 20.0  # 'get' timeout
    SEARCH_ADDITIONAL = {
        'existing_pipes': 'ts.pipes.pipe',
    }

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None, fail: dict = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session, f=fail)
        self.queue = {}
        self.existing_pipes = None

    def check(self) -> None:
        self.b.find(match_fields=[self.FIELD_ID])

        if self.p['state'] == 'present':
            if self.p['pipe'] in [None, '']:
                self.m.fail_json("You need to provide a 'pipe' to create a shaper queue!")

            if self.p['weight'] in [None, '']:
                if not self.exists:
                    self.m.fail_json("You need to provide 'weight' to create a shaper queue!")

                else:
                    self.p['weight'] = self.queue['weight']

        if self.p['state'] == 'present':
            self.b.find_single_link(
                field='pipe',
                existing=self.existing_pipes,
                existing_field_id='description',
            )

        self._base_check()

    def get_existing(self) -> list:
        existing = []

        for entry in self.b.get_existing():
            entry['pipe'] = self.existing_pipes[entry['pipe']]['description']
            existing.append(entry)

        return existing

    def reload(self) -> None:
        if self.p['reset']:
            self.API_CMD_REL = 'flushreload'

        self.b.reload()
