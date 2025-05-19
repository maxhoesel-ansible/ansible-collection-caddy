# maxhoesel.caddy - Ansible Collection for the Caddy webserver

![Release](https://img.shields.io/github/v/release/maxhoesel/ansible-collection-caddy?style=flat-square)
![Build Status](https://img.shields.io/circleci/build/github/maxhoesel-ansible/ansible-collection-caddy/main?style=flat-square)
![License](https://img.shields.io/github/license/maxhoesel/ansible-collection-caddy?style=flat-square)

An Ansible collection containing roles/modules to install, configure and interact with the [caddy webserver](https://github.com/caddyserver/caddy).

## Components

---
**📘 Documentation**

- For role documentation, see their `README.md`s or the online docs [here](https://ansible-collection-caddy.readthedocs.io)
- For modules documentation, see the online docs [here](https://ansible-collection-caddy.readthedocs.io)

---

### Roles

| Role | Description |
|------|-------------|
| [`caddy_server`](roles/caddy_server/README.md) | Install the caddy server on your hosts.

### Modules

| Module  | Description |
|---------|-------------|
| [`caddy_load`](https://ansible-collection-caddy.readthedocs.io/en/latest/collections/maxhoesel/caddy/caddy_load_module.html) | Load a new config into Caddy
| [`caddy_config_info`](https://ansible-collection-caddy.readthedocs.io/en/latest/collections/maxhoesel/caddy/caddy_config_info_module.html) | Retrieve Caddys current configuration for a given path
| [`caddy_config`](https://ansible-collection-caddy.readthedocs.io/en/latest/collections/maxhoesel/caddy/caddy_config_module.html) | Create or update Caddys configuration for a given path

## Installation

### Dependencies

- A recent release of Ansible. This collection officially supports the 2 most recent Ansible releases.
  Older versions might still work, but are not supported
- Python 3.9 or newer on the target host
- The modules require the `requests` python module on the remote host

Individual roles or modules may have additional dependencies, please check their respective documentation.

### Install

Via ansible-galaxy (recommended):

`ansible-galaxy collection install maxhoesel.caddy`

Alternatively, you can download a collection archive from a [previous release](hhttps://github.com/maxhoesel-ansible/ansible-collection-caddy/releases).

You can also clone this repository directly if you want a slightly more up-to-date (and potentially buggy) version.

`ansible-galaxy collection install git+https://github.com/maxhoesel-ansible/ansible-collection-caddy`

## License & Author

Created & Maintained by Max Hösel (@maxhoesel) and Contributors

Licensed under the GPL 3.0 or later
