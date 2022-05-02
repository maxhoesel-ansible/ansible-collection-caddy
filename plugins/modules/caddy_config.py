#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Max Hösel <ansible@maxhoesel.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: caddy_config
author: Max Hösel (@maxhoesel)
short_description: Push configuration to a given path in the caddy config
version_added: '0.1.0'
description: >
  This modules can update the configuration stored at any valid path in the caddy config API.
  It is idempotent in that it will not change the config if no changes are present.
  You can select between all update modes supported by Caddy
notes:
  - Check mode is supported.
options:
  append:
    description: >
      If set and I(path) points to an existing array or array index, the module will tell Caddy to append/insert to the array
      (using the APIs C(POST/PUT) method), instead of replacing the array/array index (API C(PATCH) method).
      See the L(Caddy API Documentation, https://caddyserver.com/docs/api\#patch-configpath) for details.
    type: bool
    default: no
  content:
    aliases:
      - config
      - value
    description: >
      Content to push to the specified I(path). Must be a dict or list corresponding to the API JSON format.
      Required if I(state=present).
    type: json
  force:
    description: >
        By default, this module only pushes configurations if changes have been made compared to the currently running config.
        Set I(force=True) if you always want to push the configuration, even if no changes will be made.
        Settings this will cause the module to always return C(changed=True)
    type: bool
    default: no
  path:
    aliases:
      - name
    description: >
      Configuration path to which the configuration content will be pushed. Note that C(config/) is automatically
      appended. Example: "apps/http/servers/myservice"
    type: path
    required: yes
  state:
    description: >
      If C(present), the configuration content at I(path) will be created or updated.
      If C(absent), any existing configuration at I(path) will be removed.
    choices:
      - present
      - absent
    default: present
    type: str

extends_documentation_fragment: maxhoesel.caddy.caddy_host_fragment
"""

EXAMPLES = r"""
- name: Ensure HTTP server configuration is present
  maxhoesel.caddy.caddy_config:
    path: apps/http/servers/myserver
    content:
      listen:
        - ":2015"
      routes:
        - handle:
          - handler: static_response
            body: Hello World!

- name: Ensure HTTP server config is absent
  maxhoesel.caddy.caddy_config:
    path: apps/http/servers/myserver
    state: absent
"""

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.caddyserver import CaddyServer
from ..module_utils.caddy_host_argspec import caddyhost_argspec


def create_or_update_config(module, server):
    """
    Creates or updates the configuration at the given path.
    Returns a result dictionary for module.exit_json()

    If append is set, the POST method will be used, else, PATCH will be used. POST will append to an array at path, while PATCH wil overwrite it.
    If force is set, will always push the configuration, even if no change would be made.
    """
    path = module.params['path']
    config = module.params["config"]

    # We first test for an existing config object and create it right away if none is found
    current_config = server.config_get(path, return_error=True)

    if current_config != config or module.params["force"]:
        if module.params["append"] and path.split("/")[-1].isdigit():
            # Insert at array index with PUT
            server.config_put(path, config)
        elif module.params["append"]:
            server.config_post(path, config)
        else:
            server.config_patch(path, config)
        return {"changed": True}
    return {"changed": False}


def delete_config(module, server):
    """
    Deletes the configuration at path if configuration is present.
    If force is set, will always push the configuration, even if no change would be made.
    """
    path = module.params["path"]

    current_config_or_error = server.config_get(path, return_error=True)
    if "status_code" in current_config_or_error and not module.params["force"]:
        if "invalid traversal path at" in current_config_or_error.get("error", False):
            # The object doesn't exist, nothing to delete
            return {"changed": False}
        else:
            module.fail_json(msg="Error while retrieving current configuration: {current_config_or_error['error']}".format(**locals()))
    server.config_delete(path)
    return {"changed": True}


def run_module():
    module_args = dict(
        append=dict(type="bool", default=False),
        content=dict(aliases=["config", "value"], type="json"),
        force=dict(type="bool", default=False),
        path=dict(type="path", aliases=["name"], required=True),
        state=dict(type="str", choices=["present", "absent"], default="present")
    )
    module_args.update(caddyhost_argspec)
    module = AnsibleModule(module_args, supports_check_mode=True)

    server = CaddyServer(module, module.params["caddy_host"])

    if module.params["state"] == "present":
        result = create_or_update_config(module, server)
    elif module.params["state"] == "absent":
        result = delete_config(module, server)
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
