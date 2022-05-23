# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Max Hösel <ansible@maxhoesel.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class CaddyServer(object):

    def __init__(self, module, addr):
        if not HAS_REQUESTS:
            module.fail_json(msg="The 'requests' python package is required to run this module")
        self.module = module
        # If the user does not specify a protocol we assume Caddys default: HTTP
        if not addr.startswith("http"):
            self.addr = "http://{addr}".format(addr=addr)
        else:
            self.addr = addr

    def config_load(self, config):
        return self._make_request("load", "POST", data=config)

    def config_get(self, path):
        res = self._make_request("config/{path}".format(path=path.lstrip('/')), return_error=True)
        if res is not None and "status_code" in res:
            if "invalid traversal path at" in res.get("error", False):
                return None
            else:
                self.module.exit_json(msg="Error while getting configuration at {path}: {err}".format(
                    path=path, err=res.get('error', '')))
        return res

    def config_put(self, path, config, create_path=True):
        if create_path:
            self._create_path(path)
        return self._make_request("config/{path}".format(path=path.lstrip('/')), "PUT", data=config)

    def config_post(self, path, config, create_path=True):
        if create_path:
            self._create_path(path)
        return self._make_request("config/{path}".format(path=path.lstrip('/')), "POST", data=config)

    def config_patch(self, path, config, create_path=True):
        if create_path:
            self._create_path(path)
        return self._make_request("config/{path}".format(path=path.lstrip('/')), "PATCH", data=config)

    def config_delete(self, path):
        return self._make_request("config/{path}".format(path=path.lstrip('/')), "DELETE")

    # pylint: disable=inconsistent-return-statements
    def _make_request(self, path, method="GET", data=None, return_error=False):
        """
        Makes a request to the Caddy API server and returns its content
        (None unless method is GET or an error occurred and return_error is True)
        Path is a path relative to the Caddy API root.
        Method is any valid Caddy HTTP API Method ("GET", "POST", "PUT", "PATCH", "DELETE")
        Data is a valid data type for the Caddy API.
        If return_error is set and an error occurs, the status code and error body will be returned.
        If False, the module will fail.
        """
        url = "{self.addr}/{path}".format(self=self, path=path)

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
                self.module.fail_json(
                    msg="Invalid HTTP method for accessing the Caddy API: {method}".format(method=method))
                return
        except (requests.exceptions.RequestException, requests.ConnectionError) as e:
            self.module.fail_json(msg="Error accessing the Caddy API: {error}".format(
                error=repr(e)), url=url, method=method)
            return

        if not r.ok:
            error = r.json()
            if not return_error:
                self.module.fail_json(
                    msg="Error durning processing of the request ({r.reason}): {error}".format(
                        r=r, error=error['error']), url=url, method=method)
            else:
                error["status_code"] = r.status_code
                return error

        try:
            json = r.json()
        except ValueError:
            return
        return json

    def _create_path(self, path):
        """
        Recursively walks through a caddy config path and creates objects until the final path object can be created.
        Does nothing if the first object in the path already exists.
        Does not create the final object in the path
        Path segments that are integers will be treated as array indices.

        For example, if the provided path is apps/http/servers/example,
        this will attempt to create apps, then apps/http, then apps/http/servers with content {}.

        Args:
            path (str): The path to create
        """
        segments = path.split("/")
        if len(segments) == 0 or self.config_get(path):
            return

        present = []
        while len(segments) > 1:
            current_path = "/".join(present) + "/" + segments[0]
            if not self.config_get(current_path):
                self.config_put("/".join(present) + "/" + segments[0],
                                [] if segments[1].isdigit() else {}, create_path=False)
            present.append(segments[0])
            segments.pop(0)
