# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Max Hösel <ansible@maxhoesel.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
from json.decoder import JSONDecodeError
from typing import Dict, List, Union

__metaclass__ = type

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from ansible.module_utils.basic import AnsibleModule


class CaddyServer:

    def __init__(self, module: AnsibleModule, addr: str):
        if not HAS_REQUESTS:
            module.fail_json(msg="The 'requests' python package is required to run this module")
        self.module = module
        # If the user does not specify a protocol we assume Caddys default: HTTP
        if not addr.startswith("http"):
            self.addr = f"http://{addr}"
        else:
            self.addr = addr

    def config_load(self, config, return_error=False):
        return self._make_request("load", "POST", data=config, return_error=return_error)

    def config_get(self, path: str, return_error=False):
        return self._make_request(f"config/{path.lstrip('/')}", return_error=return_error)

    def config_put(self, path: str, config, return_error=False):
        return self._make_request(f"config/{path.lstrip('/')}", "PUT", data=config, return_error=return_error)

    def config_post(self, path: str, config, return_error=False):
        return self._make_request(f"config/{path.lstrip('/')}", "POST", data=config, return_error=return_error)

    def config_patch(self, path: str, config, return_error=False):
        return self._make_request(f"config/{path.lstrip('/')}", "PATCH", data=config, return_error=return_error)

    def config_delete(self, path: str, return_error=False):
        return self._make_request(f"config/{path.lstrip('/')}", "DELETE", return_error=return_error)

    def _make_request(self, path: str, method: str = "GET", data=None, return_error=False) -> Union[None, Dict, List, str, int, bool]:
        """
        Makes a request to the Caddy API server and returns its content (None unless method is GET or an error occurred and return_error is True)
        Path is a path relative to the Caddy API root.
        Method is any valid Caddy HTTP API Method ("GET", "POST", "PUT", "PATCH", "DELETE")
        Data is a valid data type for the Caddy API.
        If return_error is set and an error occurs, the status code and error body will be returned. If False, the module will fail.
        """
        url = f"{self.addr}/{path}"

        if self.module.check_mode and method != "GET":
            return {}

        try:
            if method == "GET":
                r = requests.get(url)
            elif method == "POST":
                r = requests.post(url, json=data)
            elif method == "PUT":
                r = requests.put(url, json=data)
            elif method == "PATCH":
                r = requests.patch(url, json=data)
            elif method == "DELETE":
                r = requests.delete(url, json=data)
            else:
                self.module.fail_json(msg=f"Invalid HTTP method for accessing the Caddy API: {method}")
                return
        except (requests.exceptions.RequestException, ConnectionError) as e:
            self.module.fail_json(msg=f"Error accessing the Caddy API: {repr(e)}", url=url, method=method)
            return

        if not r.ok:
            error = r.json()
            if not return_error:
                self.module.fail_json(
                    msg=f"Error durning processing of the request ({r.reason}): {error['error']}", url=url, method=method)
            else:
                error["status_code"] = r.status_code
                return error

        try:
            json = r.json()
        except JSONDecodeError:
            return
        return json
