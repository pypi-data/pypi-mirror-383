"""
Copyright 2024 Inmanta

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Contact: code@inmanta.com
"""

import typing

import pytest
from testcontainers.core.container import DockerContainer

import inmanta_plugins.mitogen


@pytest.fixture
def python_container() -> typing.Iterable[DockerContainer]:
    with DockerContainer(image="python:3.6").with_command(
        "sleep infinity"
    ) as container:
        container.get_logs()
        yield container


def test_basic(python_container: DockerContainer) -> None:
    """
    The goal of this test is to make sure that the inmanta_mitogen module can be loaded
    with python3.6.
    """
    with inmanta_plugins.mitogen.Proxy(
        {
            "method_name": "docker",
            "container": python_container._container.id,
            "python_path": ["/usr/local/bin/python3.6"],
        },
    ) as p:
        p.file_stat("/tmp")
