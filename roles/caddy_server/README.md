# maxhoesel.caddy.caddy_server

Install and initialize a Caddy server.

This role installs the stable version of `caddy` from the official [repositories](https://caddyserver.com/docs/install) and performs basic configuration.
The role will configure the server so that it can be managed with the modules in this collection.
Alternatively, you can also configure caddy with a Caddyfile by passing it to this role.

## Requirements

- The following distributions are currently supported and tested:
  - Ubuntu 18.04 LTS or newer
  - Debian 10 or newer
  - A CentOS 8-compatible distribution like RockyLinux or AlmaLinux. RockyLinux is used for testing
- The following distributions are supported on a best-effort basis (should work but are not tested in CI):
  - Arch Linux
- Supported architectures: Anything supported by upstream caddy should work
- This role requires root access. Make sure to run this role with `become: yes` or equivalent

## Role Variables

##### `caddy_apply_config`
- Whether to apply/modify the caddy configuration.
- Set to false if you only want to install Caddy.
- Default: `true`

##### `caddy_config_mode`
- If set to `json`, the `caddy-api` service will be enabled and the configuration in `caddy_json_config` will be loaded.
- If set to `Caddyfile`, the `caddy` service will be enabled and a Caddyfile (`caddy_caddyfile`) will be installed.
- Default: `json`

##### `caddy_json_config`
- The Caddy configuration in the format expected by the [Caddy API](https://caddyserver.com/docs/json/).
- See below for an example
- Used if `caddy_config_mode` is set to `json` (default)
- Default: `{}`

##### `caddy_caddyfile`
- Contents of the Caddyfile that the server should run
- See below for an example
- Used if `caddy_config_mode` is set to `Caddyfile`
- Default: ""

## Example Playbooks

```
- name: Install Caddy using a JSON config
  hosts: all
  roles:
    - role: maxhoesel.caddy.caddy_server
      become: yes
      caddy_json_config:
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

- name: Install Caddy using a Caddyfile
  hosts
  roles:
    - role: maxhoesel.caddy.caddy_server
      become: yes
      vars:
        caddy_caddyfile: |
            localhost:80
            respond "Hello, world!"

```
