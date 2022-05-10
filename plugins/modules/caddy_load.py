#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Max Hösel <ansible@maxhoesel.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: caddy_load
author: Max Hösel (@maxhoesel)
short_description: Load a new configuration into Caddy
version_added: '0.1.0'
description: >
  This module pushes a caddy configuration to the server via the /load API endpoint.
  If no change between the currently running and future configuration is found, no changes will be made.
notes:
  - Check mode is supported.
options:
  content:
    aliases:
      - config
      - value
    description: Configuration for caddy. Needs to be a mapping corresponding to the API JSON format.
    type: raw
  force:
    description: >
        By default, this module only pushes configurations if changes have been made compared to the currently running config.
        Set I(force=True) if you always want to push the configuration, even if no changes will be made.
        Settings this will cause the module to always return C(changed=True)
    type: bool
    default: no

extends_documentation_fragment: maxhoesel.caddy.caddy_host_fragment
"""

EXAMPLES = r"""
- name: Load Caddy config
  maxhoesel.caddy.caddy_load:
    content:
      apps:
        http:
          servers:
            example:
              listen:
                - ":80"
              routes:
                - handle:
                    - handler: "static_response"
                      body: "Hello, world!"
"""


from ansible.module_utils.basic import AnsibleModule
from ..module_utils.caddyserver import CaddyServer
from ..module_utils.caddy_host_argspec import caddyhost_argspec


def run_module():
    module_args = dict(
        content=dict(aliases=["config", "value"], type="raw"),
        force=dict(type="bool", default=False),
    )
    module_args.update(caddyhost_argspec)
    module = AnsibleModule(module_args, supports_check_mode=True)

    server = CaddyServer(module, module.params["caddy_host"])

    current_config = server.config_get("")
    if current_config != module.params["content"] or module.params["force"]:
        if not module.check_mode:
            server.config_load(module.params["content"])
        module.exit_json(changed=True)
    module.exit_json(changed=False)


def main():
    run_module()


if __name__ == "__main__":
    main()
