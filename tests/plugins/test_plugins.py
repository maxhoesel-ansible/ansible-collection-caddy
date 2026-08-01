# pylint: disable=redefined-outer-name

def test_plugins_sanity(collection_test_env, test_versions):
    params = [
        "ansible-test",
        "sanity", "--docker", "--color", "-v",
        "--python", test_versions.node_python_version,
    ]

    collection_test_env.run(params)
