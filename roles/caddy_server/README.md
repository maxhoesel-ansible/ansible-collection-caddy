# maxhoesel.caddy.caddy_server

Install and initialize a Caddy server.

This role installs the stable version of `caddy` from the official [repositories](https://caddyserver.com/docs/install) and performs basic configuration.
The role will configure the server so that it can be managed with the modules in this collection.
Alternatively, you can also configure caddy with a Caddyfile by passing it to this role.

## Requirements

- The following distributions are currently supported and tested:
  - Ubuntu: 20.04 LTS, 22.04 LTS
  - Debian: 10, 11, 12
  - RockyLinux: 8, 9
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
- Default: `""`


### Advanced Repository Configuration

By default this role uses the upstream Caddy repositories (cloudsmith/COPR) to install Caddy on your System.
It is possible to overwrite these package repositories for Caddy, for example to use internal mirrors of Caddy.
This is done by overwriting the respective variables:
- `caddy_apt_repo` and probably `caddy_apt_key` as well for apt/deb based repos.
- `caddy_rpm_repo` and probably `caddy_rpm_key` as well for yum/dnf/rpm based repos.

#### `caddy_apt_repo`
- A string containing the repo url, distribution, component
- Default: `https://dl.cloudsmith.io/public/caddy/stable/deb/debian any-version main`

#### `caddy_apt_key`
- Url for the apt repo key
- Default: `https://dl.cloudsmith.io/public/caddy/stable/gpg.key`

#### `caddy_apt_keyring`
- Path to where the caddy apt keyring should be stored
- Default: `/usr/share/keyrings/caddy-stable-archive-keyring.gpg`

#### `caddy_rpm_repo`
- Url for the rpm repo
- Default: `https://download.copr.fedorainfracloud.org/results/@caddy/caddy/{{ 'fedora' if ansible_distribution | lower == 'fedora'
  else 'epel' }}-$releasever-$basearch/`

#### `caddy_rpm_key`
- Url for the rpm repo gpg key
- Default: `https://download.copr.fedorainfracloud.org/results/@caddy/caddy/pubkey.gpg`


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
