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

import os
import sys

import mitogen.master
import pytest_inmanta.plugin
import remote

import inmanta_plugins.mitogen


def test_basic(project: pytest_inmanta.plugin.Project) -> None:
    """
    Test that the entity tree of Context objects can be serialized and then converted to
    a mitogen object context.
    """

    model = f"""
        import mitogen

        mitogen::Local(
            name="test",
            remote_name="test",
            python_path=[{repr(sys.executable)}],
            via=mitogen::Sudo(
                name="test",
                remote_name="test",
            ),
        )
    """

    project.compile(model, no_dedent=False)

    # Get the root instance that should be serialized
    local_instances = [
        inst
        for inst in project.get_instances("mitogen::Context")
        if inst.method_name == "local"
    ]
    assert len(local_instances) == 1, str(local_instances)
    root_instance = local_instances[0]

    # Test the serialization
    serialized = inmanta_plugins.mitogen.serialize_context(root_instance)
    assert serialized == {
        "remote_name": "test",
        "name": "test",
        "method_name": "local",
        "python_path": [sys.executable],
        "via": {
            "method_name": "sudo",
            "name": "test",
            "remote_name": "test",
        },
    }

    # Test the construction of the mitogen context
    router = mitogen.master.Router()
    context = inmanta_plugins.mitogen.build_context(serialized, router=router)
    assert context.call(remote.get_executable) == sys.executable
    assert context.call(os.getuid) == 0
