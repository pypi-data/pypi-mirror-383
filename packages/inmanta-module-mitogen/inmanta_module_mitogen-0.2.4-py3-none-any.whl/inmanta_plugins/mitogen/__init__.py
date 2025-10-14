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

import collections.abc
import errno
import hashlib
import json
import logging
import os
import shutil
import types
import typing

import mitogen.core  # type: ignore[import-untyped]
import mitogen.master  # type: ignore[import-untyped]
import mitogen.parent  # type: ignore[import-untyped]

import inmanta.agent.handler
import inmanta.ast
import inmanta.ast.attribute
import inmanta.ast.entity
import inmanta.execute.proxy
import inmanta.util
import inmanta_mitogen

LOGGER = logging.getLogger(__name__)
LOGGED_VALUE_MAX_LEN_ENV_VAR = "INMANTA_MITOGEN_LOGGED_VALUE_MAX_LEN"
LOGGED_TRUNCATED_VALUE_ENV_VAR = "INMANTA_MITOGEN_LOGGED_TRUNCATED_VALUE_SUFFIX"

# Decrease logging level for mitogen
logging.getLogger("mitogen").setLevel(logging.INFO)


class PythonNotFoundError(FileNotFoundError):
    """
    Exception raised when the configured version of python can
    not be found on the host targeted by a mitogen context.
    """

    def __init__(self, serialized_context: dict[str, object]) -> None:
        # Get the python_path configured in the context, for better error reporting.
        # Default to "python" for any falsy value as it is the default value of mitogen
        python_path = typing.cast(
            list[str],
            serialized_context.get("python_path") or ["python"],
        )

        # Get a string representing the host on which the python interpreter is supposed
        # to be found on
        host = str(serialized_context["method_name"])
        if (name := serialized_context.get("name", "")) != "":
            host += f".{name}"
        if isinstance(via := serialized_context.get("via"), mitogen.core.Context):
            host += f".{via.name}"

        super().__init__(
            errno.ENOENT,
            f"No such python interpreter on host {host}",
            python_path[0],
        )
        self.add_note(
            "Check the mitogen module documentation for help on resolving this issue."
        )


class FileStat(typing.TypedDict):
    """Results from the file state call"""

    owner: str
    group: str
    permissions: int


def truncate_logged_value(raw_value: object) -> object:
    """
    This function is used to transform any value into a value that can be included
    in the logs of a mitogen-based resource.  We make sure that this value wouldn't
    fill-up the logs of the agent and that it can be serialized correctly.
    """
    # First convert the value into something that is json serializable
    str_value = json.dumps(raw_value, default=repr)
    value = json.loads(str_value)

    # Then make sure that the stringified value is not a string that exceeds the
    # amount of characters we support
    max_len = int(os.getenv(LOGGED_VALUE_MAX_LEN_ENV_VAR, "50"))
    truncated_marker = os.getenv(LOGGED_TRUNCATED_VALUE_ENV_VAR, "<...>")
    if len(str_value) > max_len:
        return str_value[: max_len - len(truncated_marker)] + truncated_marker

    return value


def get_optional_relation(
    entity: inmanta.execute.proxy.DynamicProxy,
    name: str,
    *,
    missing_ok: bool = False,
) -> inmanta.execute.proxy.DynamicProxy | None:
    """
    Get the value of an optional relation, or None if the relation is not set.
    If missing_ok is True, also return None in the even the relation is not even
    defined at the type level, otherwise return an AttributeError in that instance.

    :param entity: The entity bearing the relation
    :param name: The name of the relation
    :param missing_ok: Whether it is okay if the relation is not defined.
    """
    try:
        return typing.cast(inmanta.execute.proxy.DynamicProxy, getattr(entity, name))
    except inmanta.ast.OptionalValueException:
        return None
    except AttributeError:
        # Catch the AttributeError instead of using hasattr() because of
        # https://github.com/inmanta/inmanta-core/issues/7827
        if missing_ok:
            return None
        else:
            raise


def get_resource_context(
    entity: inmanta.execute.proxy.DynamicProxy,
) -> dict[str, object]:
    """
    Extract the mitogen context from a resource in the model.  The context can
    be provided in different ways, here is how we proceed to resolve it:
    1. If the resource has a `via` relation, and it is set, then we assume this
        is a valid mitogen::Context tree, and we serialize it.
    2. Otherwise, if the resource has a `host` relation set towards an `std::Host`
        entity, and the `via` relation of the host is set, then we assume this
        is a valid mitogen::Context tree, and we serialize it.
    3. Otherwise, if the resource has a `host` relation set towards an `std::Host`
        entity, and the `ip` attribute of this entity is not null, then we construct
        a valid serialized context, matching the host attributes (remote_user,
        remote_port, ip).
    4. Otherwise, we raise an exception, the use needs to provide more information if
        it needs to use the mitogen io.

    :param entity: The entity of the resource that should be serialized, and that
        contains the io information.
    """
    if (via := get_optional_relation(entity, "via", missing_ok=True)) is not None:
        # (1) Get context from via relation
        return serialize_context(via)

    # (2, 3) Get the host relation if it exists
    host_instance = get_optional_relation(entity, "host", missing_ok=True)
    if host_instance is None:
        raise NotImplementedError(
            "[No host relation] Cannot serialize a mitogen::Context from the current entity, it doesn't "
            "define any of the expected relations."
        )

    # Get the type of the entity, this is not part of the stable api, but we need it
    # https://github.com/inmanta/inmanta-core/issues/7741
    host_entity_type: inmanta.ast.entity.Entity = host_instance._type()
    host_entity_type_mro = [
        host_entity_type.get_full_name(),
        *host_entity_type.get_all_parent_names(),
    ]
    if "std::Host" not in host_entity_type_mro:
        raise NotImplementedError(
            "[No std::Host entity] Cannot serialize a mitogen::Context from the current entity, it doesn't "
            "define any of the expected relations."
        )

    if (via := get_optional_relation(host_instance, "via")) is not None:
        # (2) Get context from via relation on host
        return serialize_context(via)

    if host_instance.ip is not None:
        # (3) Build the context based on the host attributes
        context = {
            "method_name": "ssh",
            "name": host_instance.name,
            "hostname": host_instance.ip,
            "username": host_instance.remote_user,
            "port": host_instance.remote_port,
            # https://github.com/inmanta/inmanta-core/blob/7e62ce18f2536fb17b787f888df348a3bd2f052a/src/inmanta/agent/io/remote.py#L120
            "check_host_keys": "ignore",
            "ssh_args": [
                "-o",
                "UserKnownHostsFile=/dev/null",
                "-o",
                "PasswordAuthentication=no",
            ],
        }
        # Checking if the python_cmd attribute still exists, as it might disappear in the future.
        if (
            hasattr(host_instance.os, "python_cmd")
            and host_instance.os.python_cmd is not None
        ):
            # https://github.com/inmanta/std/blob/bbf396b40d4bd2cda0e9daf66816cc3ac820e564/templates/host_uri.j2
            context["python_path"] = [host_instance.os.python_cmd]
        else:
            # Default to python3
            context["python_path"] = ["python3"]

        if host_instance.remote_user == "root":
            return context
        else:
            return {
                "method_name": "sudo",
                "name": "",
                "via": context,
            }

    raise NotImplementedError(
        "[No ip] Cannot serialize a mitogen::Context from the current entity, it doesn't "
        "define any of the expected relations."
    )


def serialize_context(
    instance: inmanta.execute.proxy.DynamicProxy,
) -> dict[str, object]:
    """
    Serialize the context entity into a dict structure that can later be used to build
    the mitogen context that has been designed in the model.

    :param instance: The instance to serialize, its type should be a subclass of mitogen::Context
    """
    # Get the type of the entity, and make sure it is a mitogen::Context entity
    # This is not part of the stable api, but we need it
    # https://github.com/inmanta/inmanta-core/issues/7741
    entity_type: inmanta.ast.entity.Entity = instance._type()

    # Make sure that this entity is an instance of mitogen::Context
    if "mitogen::Context" not in entity_type.get_all_parent_names():
        raise ValueError(
            f"Cannot serialize instance {instance}, it is not an instance of mitogen::Context"
        )

    # Get all the attributes which are not relations
    attributes = [
        attr
        for attr in entity_type.get_all_attribute_names()
        if not isinstance(
            entity_type.get_attribute(attr), inmanta.ast.attribute.RelationAttribute
        )
    ]

    # Serialize the instance by getting the value of each non-None attribute
    serialized = {
        attr: (
            inmanta.util.api_boundary_json_encoder(value)
            if isinstance(value, inmanta.util.JSONSerializable)
            else value
        )
        for attr in attributes
        if (value := getattr(instance, attr)) is not None
    }

    if (via := get_optional_relation(instance, "via")) is not None:
        # If the via relation is defined, serialize the instance it points to
        serialized["via"] = serialize_context(via)

    return serialized


def build_context(
    serialized_context: dict[str, object],
    *,
    router: mitogen.master.Router,
) -> mitogen.parent.Context:
    """
    Build the context object described in the serialized dict structure.  The dict should represent
    the keyword parameters to give to the `connect` method of the router object.  If the key `via` is
    present in the dict, we first construct the context of the dict assigned to this key.

    :param serialized_context: The dict representing the context to build, as serialized from the
        model by the serialize_context function.
    :param router: The router that should be used to connect to the described context.
    """
    match serialized_context:
        case {"method_name": str() as method_name, "via": dict() as via, **kwargs}:
            # There is another context to base ours on, we construct it here
            # Don't modify the input dict, modify a copy instead
            serialized_context = {
                "method_name": method_name,
                "via": build_context(via, router=router),
                **kwargs,
            }
        case {"method_name": str()}:
            pass
        case _:
            raise ValueError(
                f"Unexpected format for serialized context: {serialized_context} "
                f"(type {type(serialized_context)}, expected dict)"
            )

    try:
        # Construct the context
        return router.connect(**serialized_context)
    except mitogen.parent.EofError as exc:
        if (
            str(exc).strip("\n \t")
            == "mitogen.parent.EofError: EOF on stream; last 100 lines received:"
        ):
            # EofError without any output, this is most likely because the python binary
            # provided in the python_path option doesn't exist in the PATH
            raise PythonNotFoundError(serialized_context) from exc
        else:
            # We have an explicit error message, we let it through
            raise exc
    except mitogen.core.StreamError as exc:
        if isinstance(exc.__context__, FileNotFoundError):
            python_not_found = PythonNotFoundError(serialized_context)
            if exc.__context__.filename == python_not_found.filename:
                # FileNotFoundError on the file that we reference as the python_path
                # Raise an explicit exception to suggest to the user another python path
                raise python_not_found from exc

        raise exc


def context_hash(serialized_context: dict[str, object]) -> str:
    """
    Calculate a hash for the given serialized context.  It will take into account
    all the attributes of the context, recursively.  To calculated hash is the
    hash of the json-serialized representation of the context.

    This is a logic similar to what we do in inmanta-core to detect changes from
    one desired state version to another:
    https://github.com/inmanta/inmanta-core/blob/739c048d96b119609d1d70cb0b95ee7a3c81a2a4/src/inmanta/data/__init__.py#L4573

    :param serialized_context: The mitogen context, in its serialized form.
    """
    return hashlib.md5(
        json.dumps(serialized_context, sort_keys=True).encode("utf-8")
    ).hexdigest()


class RemoteException(Exception):
    """
    Wrapper exception for any error happening on the remote host.
    """

    def __init__(self, remote_exception: Exception, *args: object) -> None:
        super().__init__(*(args or [str(remote_exception)]))
        self.remote_exception = remote_exception


class Proxy:
    """pass
    The class provides handler IO methods, to perform io operations on a remote host
    (described by the serialized_context provided in the constructor).
    Before running any of these io operations, the connection must be established with
    the remote host.  This can be done in two different ways:
    1. By calling the `connect()` method on the io object, make sure to then call the
        `disconnect()` method to tear down the connection once you are done with the
        remote host.

        .. code-block:: python

            p = Proxy({"method_name": "sudo"})
            p.connect()
            assert p.run("whoami")[0] == "root"
            p.disconnect()

    2. By using a context manager on the Proxy object, which will automatically open the
        connection when entering the context, and tear it down when exiting it.

        .. code-block:: python

            with Proxy({"method_name": "sudo"}) as p:
                assert p.run("whoami")[0] == "root"

    """

    def __init__(
        self,
        serialized_context: dict[str, object],
        *,
        logger: inmanta.agent.handler.LoggerABC | None = None,
    ) -> None:
        super().__init__()
        self.serialized_context = serialized_context
        self.logger: inmanta.agent.handler.LoggerABC = (
            logger or inmanta.agent.handler.PythonLogger(LOGGER)
        )

        self._context: mitogen.parent.Context | None = None

    @property
    def context(self) -> mitogen.parent.Context:
        """
        Access the context that has been created for this Proxy class.  This property
        should only be accessed after calling self.connect and before calling
        self.disconnect, otherwise a RuntimeError is raised.
        """
        if self._context is None:
            raise RuntimeError(
                "Cannot access the context because it has not been created.  Did you "
                "call self.connect already?"
            )

        return self._context

    def connect(self, *, exists_ok: bool = False) -> mitogen.parent.Context:
        """
        Create the mitogen context corresponding to this Proxy object, and establish
        the connection to the remote host.  If the connection is already established, simply
        return the existing context object.

        :param exists_ok: When set to True, do not raise an exception if the connection
            already exists, and simply return the existing Context object.
        """
        if self._context is not None and exists_ok:
            # No need to connect, we already did it
            return self._context
        elif self._context is not None:
            # exists_ok is False
            raise RuntimeError(
                "The connection is already open, if this is expected and you don't plan "
                "on closing it before whoever that opened it, you can set exists_ok=True.  "
                "If you expected the connection to be open and just need to access the "
                "context object, use self.context instead."
            )
        else:
            # self._context is None
            # Handle context creation here below
            pass

        # Create the context object, based on its serialized form as provided
        # to the constructor
        self._context = build_context(
            self.serialized_context,
            router=mitogen.master.Router(
                mitogen.master.Broker(),
            ),
        )
        self.logger.debug(
            "Constructed context %(name)s from its serialized form",
            name=self._context.name,
            serialize_context=self.serialized_context,
        )

        return self._context

    def disconnect(self, *, timeout: float = 10.0, best_effort: bool = False) -> None:
        """
        Shutdown the connection to the remote host.  Doesn't do anything if the connection
        hasn't been established or is already closed.

        :param timeout: Maximum amount of seconds we can wait when shuting down the context,
            after this timeout is reached, raise a TimeoutError (unless best_effort is True).
        :param best_effort: Try to close the connection, but catch any exception raised
            in the process and pretend everything went fine.
        """
        if self._context is None:
            # No connection to close, we just exit here
            return

        self.logger.debug("Shutting down context %(name)s", name=self._context.name)

        # Shutdown the context, making sure that any code running remotely
        # is terminated
        latch: mitogen.core.Latch | None = self._context.shutdown(wait=False)
        if latch is not None:
            try:
                latch.get(timeout=timeout)
            except mitogen.core.TimeoutError as e:
                if best_effort:
                    # Suppress error and continue
                    pass
                else:
                    raise TimeoutError(
                        f"Timeout of {timeout} seconds reached when waiting for context to be shutdown"
                    ) from e

        router: mitogen.master.Router = self._context.router
        broker: mitogen.master.Broker = router.broker
        broker.shutdown()
        self._context = None

    def __enter__(self) -> "Proxy":
        # Make sure we don't open the connection a second time
        # We do this as we don't want the close the connection too early when
        # exiting the context.  The code that already opened the connection should
        # be the one taking care of closing it.
        self.connect(exists_ok=False)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        self.disconnect()

    def remote_call(
        self,
        function: collections.abc.Callable[..., object],
        *args: object,
        **kwargs: object,
    ) -> object:
        """
        Perform a remote call and returns the result. When a remote exception occurs the exception and stacktrace
        is packed in RemoteException
        """
        logger_kwargs = dict(
            function=function.__module__ + "." + function.__qualname__,
            context_name=self.context.name,
            args=[truncate_logged_value(arg) for arg in args],
            kwargs={key: truncate_logged_value(value) for key, value in kwargs.items()},
        )
        try:
            result = self.context.call(function, *args, **kwargs)
            logger_kwargs["result"] = truncate_logged_value(result)
            self.logger.debug(
                "Calling function %(function)s in context %(context_name)s: %(result)s",
                **logger_kwargs,
            )
            return result
        except mitogen.core.CallError as e:
            # Translate to our remote exception to not expose mitogen into the caller code
            logger_kwargs["exception"] = truncate_logged_value(str(e))
            self.logger.debug(
                "Calling function %(function)s in context %(context_name)s: %(exception)s",
                **logger_kwargs,
            )
            raise RemoteException(e)
        except mitogen.core.ChannelError as e:
            # The channel is broken, we disconnect and reconnect to make sure it can still
            # be used by other code paths
            self.disconnect(timeout=0, best_effort=True)
            self.connect()

            # Translate to our remote exception to not expose mitogen into the caller code
            logger_kwargs["exception"] = truncate_logged_value(str(e))
            self.logger.debug(
                "Calling function %(function)s in context %(context_name)s: %(exception)s",
                **logger_kwargs,
            )
            raise RemoteException(e)

    # Methods exposed to the user
    def chmod(self, path: str, permissions: str) -> None:
        """
        Change the permissions

        :param path: The path of the file or directory to change the permission of.
        :param permissions: An octal string with the permission to set.
        """
        self.remote_call(os.chmod, path, int(permissions, 8))

    def chown(
        self,
        path: str,
        user: str | int | None = None,
        group: str | int | None = None,
    ) -> None:
        """
        Change the ownership of a file.

        :param path: The path of the file or directory to change the ownership of.
        :param user: The user to change to
        :param group: The group to change to
        """
        self.remote_call(shutil.chown, path, user, group)

    def file_exists(self, path: str) -> bool:
        """
        Check if a given file exists

        :param path: The path to check if it exists.
        :return: Returns true if the file exists
        """
        return bool(self.remote_call(os.path.lexists, path))

    def file_stat(self, path: str) -> FileStat:
        """
        Do a stat call on a file

        :param path: The file or direct to stat
        :return: A dict with the owner, group and permissions of the given path
        """
        result = self.remote_call(inmanta_mitogen.file_stat, path)

        match result:
            case {
                "owner": str() as owner,
                "group": str() as group,
                "permissions": int() as permissions,
            }:
                return FileStat(
                    owner=owner,
                    group=group,
                    permissions=permissions,
                )
            case _:
                expected_format = (
                    """{"owner": str(), "group": str(), "permissions": int()}"""
                )
                raise RemoteException(
                    ValueError(
                        f"Received invalid result, expected dict of the form {expected_format} but got a"
                        f"{type(result)} instead: {result}"
                    ),
                )

    def hash_file(self, path: str) -> str:
        """
        Return the sha1sum of the file at path

        :param path: The path of the file to hash the content of
        :return: The sha1sum in a hex string
        """
        return str(self.remote_call(inmanta_mitogen.hash_file, path))

    def is_symlink(self, path: str) -> bool:
        """
        Is the given path a symlink

        :param path: The path of the symlink
        :return: Returns true if the given path points to a symlink
        """
        return bool(self.remote_call(inmanta_mitogen.islink, path))

    def mkdir(self, path: str) -> None:
        """
        Create a directory

        :param path: Create this directory. The parent needs to exist.
        """
        self.remote_call(os.mkdir, path)

    def put(self, path: str, content: bytes) -> None:
        """
        Put the given content at the given path

        :param path: The location where to write the file
        :param content: The binary string content to write to the file.
        """
        self.remote_call(inmanta_mitogen.put, path, content)

    def read(self, path: str) -> str:
        """
        Read in the file in path and return its content as string

        :param path: The path of the file to read.
        :return: The string content of the file
        """
        return str(self.remote_call(inmanta_mitogen.read, path))

    def read_binary(self, path: str) -> bytes:
        """
        Read in the file in path and return its content as a bytestring

        :param path: The path of the file to read.
        :return: The byte content of the file
        """
        return typing.cast(bytes, self.remote_call(inmanta_mitogen.read_binary, path))

    def readlink(self, path: str) -> str:
        """
        Return the target of the path

        :param path: The symlink to get the target for.
        :return: The target of the symlink
        """
        return str(self.remote_call(os.readlink, path))

    def remove(self, path: str) -> None:
        """
        Remove a file

        :param path: The path of the file to remove.
        """
        self.remote_call(os.remove, path)

    def rmdir(self, path: str) -> None:
        """
        Remove a directory

        :param path: The directory to remove
        """
        self.remote_call(shutil.rmtree, path)

    def run(
        self,
        command: str,
        arguments: list[str] = [],
        env: dict[str, str] | None = None,
        cwd: str | None = None,
        timeout: int | None = None,
    ) -> tuple[str, str, int]:
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
        return typing.cast(
            tuple[str, str, int],
            self.remote_call(
                inmanta_mitogen.run, command, arguments, env, cwd, timeout
            ),
        )

    def symlink(self, source: str, target: str) -> None:
        """
        Symlink source to target

        :param str source: Create a symlink of this path to target
        :param str target: The path of the symlink to create
        """
        self.remote_call(os.symlink, source, target)
