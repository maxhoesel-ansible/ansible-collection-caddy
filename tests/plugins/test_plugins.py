# pylint: disable=redefined-outer-name

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

INTEGRATION_CONFIG_DIR = Path("tests/integration/")
INTEGRATION_CONFIG_TEMPLATE = "integration_config.yml.j2"
INTEGRATION_CONFIG_FILE = "integration_config.yml"


def render_integration_config(template, dest: Path, **kwargs):
    env = Environment(loader=FileSystemLoader(INTEGRATION_CONFIG_DIR))
    template = env.get_template(template)
    content = template.render(**kwargs)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(f"{content}\n")


def test_plugins_integration(test_versions, remote_caddy_container, ansible_test_env):
    render_integration_config(
        INTEGRATION_CONFIG_TEMPLATE,
        ansible_test_env.cwd / "tests" / "integration" / INTEGRATION_CONFIG_FILE,
        admin_url=remote_caddy_container.caddy_url,
    )

    ansible_test_env.run([
        "ansible-test", "integration", "--color", "-v",
        "--controller", "docker:default",
        "--target", f"docker:default,python={test_versions.node_python_version}",
        "--docker-network", remote_caddy_container.ct_network,
    ])


def test_plugins_sanity(ansible_test_env, test_versions):
    ansible_test_env.run([
        "ansible-test",
        "sanity", "--docker", "--color", "-v",
        "--python", test_versions.node_python_version,
    ])
