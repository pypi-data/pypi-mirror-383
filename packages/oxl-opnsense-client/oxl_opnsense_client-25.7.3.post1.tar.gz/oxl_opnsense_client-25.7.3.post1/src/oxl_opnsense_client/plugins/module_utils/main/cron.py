from basic.ansible import AnsibleModule

from plugins.module_utils.helper.main import \
    is_unset
from plugins.module_utils.base.api import \
    Session
from plugins.module_utils.base.cls import BaseModule


class CronJob(BaseModule):
    FIELD_ID = 'description'
    CMDS = {
        'add': 'add_job',
        'del': 'del_job',
        'set': 'set_job',
        'search': 'get',
        'toggle': 'toggle_job', # test
    }
    API_KEY_PATH = 'job.jobs.job'
    API_MOD = 'cron'
    API_CONT = 'settings'
    API_CONT_REL = 'service'
    FIELDS_CHANGE = [
        'minutes', 'hours', 'days', 'months',
        'weekdays', 'command', 'who', 'parameters'
    ]
    FIELDS_TYPING = {
        'bool': ['enabled'],
        'select': ['command'],
        'int': ['minutes', 'hours', 'days', 'months', 'weekdays'],
    }
    FIELDS_ALL = ['description', 'enabled']
    FIELDS_ALL.extend(FIELDS_CHANGE)
    EXIST_ATTR = 'cron'

    def __init__(self, module: AnsibleModule, result: dict, session: Session = None, fail: dict = None):
        BaseModule.__init__(self=self, m=module, r=result, s=session, f=fail)
        self.cron = {}
        self.available_commands = []

    def check(self) -> None:
        if self.p['state'] == 'present' and is_unset(self.p['command']):
            self.m.fail_json("You need to provide a 'command' if you want to create a cron-job!")

        self.b.find(match_fields=[self.FIELD_ID])

        if self.p['state'] == 'present':
            if self.p['command'] is not None and len(self.available_commands) > 0 and \
                    self.p['command'] not in self.available_commands:
                self.m.fail_json(
                    'Got unsupported command! '
                    f"Available ones are: {', '.join(self.available_commands)}"
                )

        self._base_check()

    def _build_all_available_cmds(self, raw_cmds: dict):
        if len(self.available_commands) == 0:
            for cmd in raw_cmds.keys():
                if cmd not in self.available_commands:
                    self.available_commands.append(cmd)

    def _simplify_existing(self, existing: dict) -> dict:
        simple = self.b.simplify_existing(existing)
        simple.pop('origin')
        self._build_all_available_cmds(existing['command'])
        return simple
