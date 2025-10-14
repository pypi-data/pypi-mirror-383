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

import hashlib
import os

import mitogen.core
import pytest
import ssh_container

import inmanta_plugins.mitogen


def test_remote_ssh_sudo(remote_ssh_container: ssh_container.SshContainer) -> None:
    export_port = remote_ssh_container.get_exposed_port(remote_ssh_container.port)
    with inmanta_plugins.mitogen.Proxy(
        {
            "method_name": "sudo",
            "via": {
                "method_name": "ssh",
                "hostname": remote_ssh_container.get_container_host_ip(),
                "port": export_port,
                "username": "user",
                "python_path": ["/usr/libexec/platform-python"],
                "identity_file": str(remote_ssh_container.private_key_file),
                "check_host_keys": "ignore",
            },
        },
    ) as io:
        assert io.run("whoami") == ("root", "", 0)

        path = "/tmp/test-file"
        content = "this is a test"

        io.put(path, content.encode())
        assert io.read(path) == content
        assert io.read_binary(path) == content.encode()
        assert io.file_stat(path) == {
            "group": "root",
            "owner": "root",
            "permissions": 644,
        }
        assert io.file_exists(path)

        io.chown(path, "user", "user")
        assert io.file_stat(path) == {
            "group": "user",
            "owner": "user",
            "permissions": 644,
        }

        io.chmod(path, "755")
        assert io.file_stat(path) == {
            "group": "user",
            "owner": "user",
            "permissions": 755,
        }

        io.chown(path, 1013, 1014)
        assert io.file_stat(path) == {
            "group": "1014",
            "owner": "1013",
            "permissions": 755,
        }

        sha1sum = hashlib.sha1()
        sha1sum.update(content.encode())
        assert io.hash_file(path) == sha1sum.hexdigest()

        assert not io.is_symlink(path)
        io.symlink(path, path + "2")
        assert io.is_symlink(path + "2")
        assert io.readlink(path + "2") == path

        dir_path = "/tmp/test-dir"
        assert not io.file_exists(dir_path)
        io.mkdir(dir_path)
        assert io.file_exists(dir_path)
        io.rmdir(dir_path)
        assert not io.file_exists(dir_path)

        io.remove(path)
        assert not io.file_exists(path)
        with pytest.raises(inmanta_plugins.mitogen.RemoteException):
            assert io.file_stat(path) == {}

        assert io.run("/bin/echo", ["hello"]) == ("hello", "", 0)
        assert io.run("/bin/false") == ("", "", 1)


def test_remote_ssh(remote_ssh_container: ssh_container.SshContainer) -> None:
    """Test remoting over ssh without any sudo"""
    io = inmanta_plugins.mitogen.Proxy(
        {
            "method_name": "ssh",
            "hostname": remote_ssh_container.get_container_host_ip(),
            "port": remote_ssh_container.get_exposed_port(remote_ssh_container.port),
            "username": "user",
            "python_path": ["/usr/libexec/platform-python"],
            "identity_file": remote_ssh_container.private_key_file,
            "check_host_keys": "ignore",
        },
    )
    io.connect()
    assert io.run("whoami") == ("user", "", 0)
    io.disconnect()


def test_local_sudo(tmpdir_factory: pytest.TempdirFactory) -> None:
    """Validate running commands on the system itself. We keep these limited because they can be "dirty" on the
    machine itself.
    """
    with inmanta_plugins.mitogen.Proxy(
        {
            "method_name": "sudo",
        },
    ) as io:

        assert io.run("whoami") == ("root", "", 0)

        path = str(tmpdir_factory.mktemp("local") / "test-file")
        content = "this is a test"

        io.put(path, content.encode())
        assert io.read(path) == content
        assert io.file_stat(path) == {
            "group": "root",
            "owner": "root",
            "permissions": 644,
        }
        assert io.file_exists(path)
        io.remove(path)
        with pytest.raises(inmanta_plugins.mitogen.RemoteException):
            assert io.file_stat(path) == {}
        assert not io.file_exists(path)


def test_local(tmpdir_factory: pytest.TempdirFactory) -> None:
    """Validate running commands on the system itself without sudo"""
    with inmanta_plugins.mitogen.Proxy(
        {
            "method_name": "local",
        },
    ) as io:

        assert io.run("whoami")[0] != "root"

        path = str(tmpdir_factory.mktemp("local") / "test-file")
        content = "this is a test"

        io.put(path, content.encode())
        assert io.read(path) == content
        assert io.file_exists(path)
        io.remove(path)
        with pytest.raises(inmanta_plugins.mitogen.RemoteException):
            assert io.file_stat(path) == {}
        assert not io.file_exists(path)


def test_channel_error(remote_ssh_container: ssh_container.SshContainer) -> None:
    """
    Validate that we can recover from a remote exception and still use the proxy after it.
    """
    with inmanta_plugins.mitogen.Proxy(
        {
            "method_name": "sudo",
            "via": {
                "method_name": "ssh",
                "hostname": remote_ssh_container.get_container_host_ip(),
                "port": remote_ssh_container.get_exposed_port(
                    remote_ssh_container.port
                ),
                "username": "user",
                "python_path": ["/usr/libexec/platform-python"],
                "identity_file": remote_ssh_container.private_key_file,
                "check_host_keys": "ignore",
            },
        },
    ) as p:
        with pytest.raises(inmanta_plugins.mitogen.RemoteException) as e:
            # This call will fail because mitogen can't pickle the returned
            # value of os.popen
            p.remote_call(os.popen, "whoami")

        assert isinstance(e.value.remote_exception, mitogen.core.ChannelError)

        # Assert that the proxy can still be used after the error
        p.run("whoami")
