#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Max Hösel <ansible@maxhoesel.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: caddy_config_info
author: Max Hösel (@maxhoesel)
short_description: Get the current Caddy configuration for a given path
version_added: '0.1.0'
description: Returns the currently running configuration for any given path
notes:
options:
  path:
    aliases:
      - name
    description: >
      Path from which the configuration content will be read. Note that C(config/) is automatically
      appended. Example: "apps/http/servers/myservice"
    type: path
    required: yes

extends_documentation_fragment: maxhoesel.caddy.caddy_host_fragment
"""

EXAMPLES = r"""
- name: Get config for an HTTP server
  maxhoesel.caddy.caddy_config_info:
    path: apps/http/servers/myserver
  register: myserver_cfg
- debug:
    msg: "{{ myserver_cfg.config }}"
"""

RETURN = r"""
config:
  description: Configuration at the requested path as a mapping/list
  returned: success
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.caddyserver import CaddyServer
from ..module_utils.caddy_host_argspec import caddyhost_argspec


def run_module():
    module_args = dict(
        path=dict(type="path", aliases=["name"], required=True),
    )

    module_args.update(caddyhost_argspec)
    module = AnsibleModule(module_args, supports_check_mode=True)

    server = CaddyServer(module, module.params["caddy_host"])
    config = server.config_get(module.params["path"])

    module.exit_json(changed=False, config=config)


def main():
    run_module()


if __name__ == "__main__":
    main()
