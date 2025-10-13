from os import environ
from socket import setdefaulttimeout

import httpx

from basic.ansible import AnsibleModule

from plugins.module_utils.helper.api import \
    check_host, ssl_verification, check_response, get_params_path, debug_api, \
    check_or_load_credentials, api_pretty_exception
from plugins.module_utils.helper.validate import is_ip6

DEFAULT_TIMEOUT = 20.0
HTTPX_EXCEPTIONS = (
    httpx.ConnectTimeout, httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout,
    httpx.TimeoutException, httpx.PoolTimeout,
)


class Session:
    def __init__(self, module: AnsibleModule, timeout: float = DEFAULT_TIMEOUT):
        self.m = module
        self.s = self._start(timeout)

    def _start(self, timeout: float) -> httpx.Client:
        check_host(module=self.m)
        api_key, api_secret = check_or_load_credentials(module=self.m)
        if api_secret is None:
            api_key = self.m.params['api_key']
            api_secret = self.m.params['api_secret']

        if 'api_timeout' in self.m.params and self.m.params['api_timeout'] is not None:
            timeout = self.m.params['api_timeout']

        setdefaulttimeout(timeout)

        fw = self.m.params['firewall']
        if is_ip6(fw, strip_enclosure=False):
            fw = f"[{fw}]"

        proxy = environ.get('HTTPS_PROXY', None)
        if proxy is not None and not proxy.startswith('http') and not proxy.startswith('sock'):
            proxy = None

        return httpx.Client(
            base_url=f"https://{fw}:{self.m.params['api_port']}/api",
            auth=(api_key, api_secret),
            timeout=httpx.Timeout(timeout=timeout, connect=2.0),
            transport=httpx.HTTPTransport(
                verify=ssl_verification(module=self.m),
                retries=self.m.params['api_retries'],
                proxy=proxy,
            ),
            headers={'User-Agent': 'Ansible'}
        )

    def get(self, cnf: dict) -> dict:
        params_path = get_params_path(cnf=cnf)
        call_url = f"{cnf['module']}/{cnf['controller']}/{cnf['command']}{params_path}"

        debug_api(
            module=self.m,
            method='GET',
            url=f'{self.s.base_url}{call_url}',
        )

        try:
            response = check_response(
                module=self.m,
                cnf=cnf,
                response=self.s.get(url=call_url)
            )

        except HTTPX_EXCEPTIONS as error:
            api_pretty_exception(
                m=self.m, method='GET', error=error,
                url=f'{self.s.base_url}{call_url}',
            )
            raise

        return response

    def post(self, cnf: dict, headers: dict = None) -> dict:
        if headers is None:
            headers = {}

        data = None

        if 'data' in cnf and cnf['data'] is not None and len(cnf['data']) > 0:
            headers['Content-Type'] = 'application/json'
            data = cnf['data']

        params_path = get_params_path(cnf=cnf)
        call_url = f"{cnf['module']}/{cnf['controller']}/{cnf['command']}{params_path}"

        debug_api(
            module=self.m,
            method='POST',
            url=f'{self.s.base_url}{call_url}',
            data=data,
            headers=headers,
        )

        try:
            response = check_response(
                module=self.m,
                cnf=cnf,
                response=self.s.post(
                    url=call_url, json=data, headers=headers
                )
            )

        except HTTPX_EXCEPTIONS as error:
            api_pretty_exception(
                m=self.m, method='POST', error=error,
                url=f'{self.s.base_url}{call_url}',
            )
            raise

        return response

    def close(self) -> None:
        self.s.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def single_get(module: AnsibleModule, cnf: dict, timeout: float = DEFAULT_TIMEOUT) -> dict:
    with Session(module=module, timeout=timeout) as s:
        response = s.get(cnf=cnf)

    return response


def single_post(module: AnsibleModule, cnf: dict, timeout: float = DEFAULT_TIMEOUT, headers: dict = None) -> dict:
    with Session(module=module, timeout=timeout) as s:
        response = s.post(cnf=cnf, headers=headers)

    return response
