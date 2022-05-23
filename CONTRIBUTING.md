# Contribution Guide

Below you will find the information needed to contribute to this project.

Note that by contributing to this collection, you agree with the code of conduct you can find [here.](https://github.com/maxhoesel/ansible-collection-caddy/blob/main/CODE_OF_CONDUCT.md)

## Requirements

To begin development on this collection, you need to have the following dependencies installed:

- Docker, accessible by your local user account
- Python 2.7 or 3.6+. CI tests run specifically against either 2.7 or 3.6, but to make things easier we just use whatever version is available locally

## Quick Start

1. Fork the repository and clone it to your local machine
2. Run `./scripts/setup.sh` to configure a local dev environment (virtualenv) with all required dependencies
3. Activate the virtualenv with `source .venv/bin/activate`
4. Make your changes and commit them to a new branch
5. Run the tests locally with `./scripts/test.sh`. This will run the full test suite that also runs in the CI
6. Once you're done, commit your changes (make sure that you are in the venv).
   Pre-commit will format your code and check for any obvious errors when you do so.

## Hints for Development

For Modules:
- Make sure that you have read the [Ansible module conventions](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_best_practices.html)
- Make sure to use the doc fragment and utils already present when possible.
- If you need to troubleshoot inside the ansible-test container, add `--docker-terminate never` to the
  call inside the testing script. The container will then persist even on failure, and you can debug it

For Roles:
- None so far

In general:
- Don't be afraid to rewrite your local branch history to clean up your commit messages!
  You should familiarize yourself with `git rebase -i` if you haven't done so already.

## Testing Framework

We use `molecule` to test all roles and the `ansible-test` suite to test modules. Calls to these are handled by `tox` and the [`tox-ansible` extension]( https://github.com/ansible-community/tox-ansible).
You can run all the required tests for this project with `./scripts/test.sh`. You can also open that file to view the individual test stages.

Note that you **can't** just run `tox`, as the `sanity` and `integration` environments need extra parameters passed to
`ansible-test`. Without these, they will fail. In addition, the `tox-ansible` plugin (which automatically generate scenario envs)
also adds a few unneeded environments to the list, such as `env`.

#### Creating new module tests

We currently only run integration tests for our modules via `ansible-test`. If you added a new module (or added new functionality to an already existing module),
you will need to write new tests for it. Each module has its own integration target in `tests/integration/targets`. To start, copy an existing targets directory
and adjust the test tasks for your module.

Some additional hints:

- All targets are run sequentially on the same host. Make sure to clean up after yourself! You don't need to handle failures gracefully however,
  as the testing environment is destroyed on the first error.
- All targets call the `setup_caddy` target via the dependency declared in `meta/main.yml`. This target installs a caddy server for the modules to run against.
- See `targets/setup_caddy/defaults/main.yml` for some variables you can use in your tests

## Release Workflow

This project uses sematic versioning. Name versions accordingly.

For now, releases are simply tags on the main branch, with no separate release branch currently in use.

To create a release, simply run the "Create Release" GitHub Action with the desired version number (e.g. "0.3.0").
This action will:

1. Bump the version number in `galaxy.yml`
2. Update the changelog
3. Commit the changes in a "Release" commit and push it
4. Create a GitHub release (which will also create a tag at that commit)
5. Build the collection and publish the new release on galaxy
