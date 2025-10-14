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

    This file should stay compatible with as many versions of python as possible
    as its code will be pickled and sent to remote devices which might have very
    old python versions installed.
    Minimal python version we aim at is python3.6
"""

import grp
import hashlib
import os
import pwd
import subprocess
import typing


def hash_file(path: str) -> str:
    """
    Return the sha1sum of the file at path

    :param path: The path of the file to hash the content of
    :return: The sha1sum in a hex string
    """
    sha1sum = hashlib.sha1()
    with open(path, "rb") as f:
        sha1sum.update(f.read())

    return sha1sum.hexdigest()


def read(path: str) -> str:
    """
    Read in the file in path and return its content as string

    :param path: The path of the file to read.
    :return: The string content of the file
    """
    with open(path, "rb") as fd:
        return fd.read().decode("utf-8")


def read_binary(path: str) -> bytes:
    """
    Read in the file in path and return its content as a bytestring

    :param path: The path of the file to read.
    :return: The byte content of the file
    """
    with open(path, "rb") as fd:
        return fd.read()


def run(
    command: str,
    arguments: typing.List[str] = [],
    env: typing.Optional[typing.Dict[str, str]] = None,
    cwd: typing.Optional[str] = None,
    timeout: typing.Optional[int] = None,
) -> typing.Tuple[str, str, int]:
    """
    Execute a command with the given argument and return the result

    :param command: The command to execute.
    :param arguments: The arguments of the command
    :param env: A dictionary with environment variables.
    :param cwd: The working dir to execute the command in.
    :param timeout: The timeout for this command. This parameter is ignored if the command is executed remotely with
                        a python 2 interpreter.
    :return: A tuple with (stdout, stderr, returncode)
    """
    current_env = os.environ.copy()
    if env is not None:
        current_env.update(env)

    if (not env or "PYTHONPATH" not in env) and "PYTHONPATH" in current_env:
        # Remove the inherited python path
        del current_env["PYTHONPATH"]

    cmds = [command] + arguments
    result = subprocess.Popen(
        cmds,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=current_env,
        cwd=cwd,
    )
    data = result.communicate(timeout=timeout)

    return (
        data[0].strip().decode("utf-8"),
        data[1].strip().decode("utf-8"),
        result.returncode,
    )


def file_stat(path: str) -> typing.Dict[str, object]:
    """
    Do a stat call on a file

    :param path: The file or direct to stat
    :return: A dict with the owner, group and permissions of the given path
    """
    stat_result = os.stat(path)

    try:
        owner = pwd.getpwuid(stat_result.st_uid).pw_name
    except KeyError:
        # uid doesn't belong to a named user, fallback to the uid
        owner = str(stat_result.st_uid)

    try:
        group = grp.getgrgid(stat_result.st_gid).gr_name
    except KeyError:
        # gid doesn't belong to a named group, fallback to the gid
        group = str(stat_result.st_gid)

    status = dict(
        owner=owner,
        group=group,
        permissions=int(oct(stat_result.st_mode)[-4:]),
    )

    return status


def islink(path: str) -> bool:
    """
    Test whether a path is a symbolic link

    We need this proxy, because different python versions import os.path in slightly different way.
    With this dedicated function, dereference of `os.path.islink` is deferred to the remote host.
    """
    return os.path.islink(path)


def put(path: str, content: bytes) -> None:
    """
    Put the given content at the given path

    :param path: The location where to write the file
    :param content: The binarystring content to write to the file.
    """
    with open(path, "wb+") as fd:
        fd.write(content)
