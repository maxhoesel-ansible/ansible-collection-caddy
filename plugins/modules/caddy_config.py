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
  create_path:
    description: >
      Whether to create the path pointing to the configuration if it doesn't exist yet.
      For example, if I(path=apps/http/servers/myservice) and C(apps/http/servers) does not exist yet, the required path entries will be created.
      Note that any digit path segments are treated as array indices.
    type: bool
    default: yes
    version_added: '0.2.0'
  content:
    aliases:
      - config
      - value
    description: >
      Content to push to the specified I(path). Must be a dict or list corresponding to the API JSON format.
      Required if I(state=present).
    type: raw
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
      Configuration path to which the configuration content will be pushed. Note that the path if is automatically
      prefixed with C(config/). Example: C(apps/http/servers/myservice)
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

    If append is set, the POST method will be used, else, PATCH will be used.
    POST will append to an array at path, while PATCH wil overwrite it.
    If force is set, will always push the configuration, even if no change would be made.
    """
    path = module.params['path']
    content = module.params["content"]

    # We first test for an existing config object and create it right away if none is found
    current_config = server.config_get(path)

    if current_config != content or module.params["force"]:
        if module.check_mode:
            pass
        elif module.params["append"] and path.split("/")[-1].isdigit():
            # Insert at array index with PUT
            server.config_put(path, content, create_path=module.params["create_path"])
        elif module.params["append"]:
            # Other appends, post
            server.config_post(path, content, create_path=module.params["create_path"])
        elif current_config:
            server.config_patch(path, content, create_path=module.params["create_path"])
        else:
            # current config doesn't exist, create
            server.config_put(path, content, create_path=module.params["create_path"])
        return {"changed": True}
    return {"changed": False}


def delete_config(module, server):
    """
    Deletes the configuration at path if configuration is present.
    If force is set, will always push the configuration, even if no change would be made.
    """
    path = module.params["path"]

    current_config = server.config_get(path)
    if current_config is None:
        return {"changed": False}
    elif not module.check_mode:
        server.config_delete(path)
    return {"changed": True}


def run_module():
    module_args = dict(
        append=dict(type="bool", default=False),
        content=dict(aliases=["config", "value"], type="raw"),
        create_path=dict(type="bool", default=True),
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
