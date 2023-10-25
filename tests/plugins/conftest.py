# pylint: disable=redefined-outer-name
from dataclasses import dataclass
from typing import cast, Generator, Optional

import docker
from docker.models.containers import Container
from docker.models.networks import Network
from docker.errors import NotFound
import pytest

from tests.conftest import TestEnv, GALAXY_YML

CADDY_NETWORK = "ansible-collection-caddy-test"
CADDY_CONTAINER_NAME = "ansible-collection-caddy-test-server"
CADDY_HOSTNAME = "caddy"


class AnsibleTestEnv(TestEnv):
    # pylint: disable=redefined-outer-name
    def __init__(self, virtualenv, collection_path, test_versions) -> None:
        self.cwd = collection_path / "ansible_collections" / GALAXY_YML["namespace"] / GALAXY_YML["name"]
        super().__init__(virtualenv)

        self.run(["pip", "install", test_versions.ansible_version_pip])

    def run(self, *args, **kwargs):
        kwargs["cwd"] = self.cwd
        return super().run(*args, **kwargs)


ANSIBLE_TEST_ENV: Optional[AnsibleTestEnv] = None


@pytest.fixture()
# This fixture should be session-scoped, but cannot be since it requires the function-scoped virtualenv fixture
# Use memoization for now.
# pylint: disable=redefined-outer-name
def ansible_test_env(virtualenv, collection_path, test_versions) -> AnsibleTestEnv:
    global ANSIBLE_TEST_ENV  # pylint: disable=global-statement
    if ANSIBLE_TEST_ENV is not None:
        return ANSIBLE_TEST_ENV

    ANSIBLE_TEST_ENV = AnsibleTestEnv(virtualenv, collection_path, test_versions)
    return ANSIBLE_TEST_ENV


@pytest.fixture(scope="session")
def caddy_network() -> Generator[Network, None, None]:
    client = docker.from_env()
    try:
        net = client.networks.get(CADDY_NETWORK)
    except NotFound:
        net = client.networks.create(CADDY_NETWORK)
    net = cast(Network, net)
    yield net

    net.remove()


@dataclass
class CaddyContainerConfig:
    ct: Container
    ct_hostname: str
    ct_network: str
    caddy_url: str


@pytest.fixture(scope="session")
def remote_caddy_container(caddy_network) -> Generator[CaddyContainerConfig, None, None]:
    client = docker.from_env()
    try:
        # cleanup old container to ensure REMOTE_CA_HOSTNAME points to the right container
        ct = cast(Container, client.containers.get(CADDY_CONTAINER_NAME))
        ct.remove(force=True)
    except NotFound:
        pass

    ct = cast(Container, client.containers.run(
        "docker.io/library/caddy:2", detach=True, remove=True,
        name=CADDY_CONTAINER_NAME, hostname=CADDY_HOSTNAME,
        network=caddy_network.name,
        environment={
            "CADDY_ADMIN": "0.0.0.0:2019",
        },
    ))
    # Wait for Caddy to come online
    # pylint: disable=line-too-long
    rc = ct.exec_run(
        "sh -c 'for i in {1..10}; do wget -O /dev/null http://127.0.0.1:2019/config && exit 0 || sleep 1; done && exit 1'")[0]
    assert rc == 0

    yield CaddyContainerConfig(
        ct, ct_hostname=CADDY_HOSTNAME, ct_network=CADDY_NETWORK,
        caddy_url=f"http://{CADDY_HOSTNAME}:2019"
    )

    ct.remove(force=True)
