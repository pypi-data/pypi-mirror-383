# mitogen base module

This module isn't an adapter, it serves as a base for many other modules which need to interact with remote hosts.  It uses the `mitogen` library to easily setup a python environment on any remote host and execute the requested code on them.

## Environment variables

The behavior of the module can be influenced by setting some environment variables.

| **Env var name** | **Default value** | **Description** |
| --- | --- | --- |
| `INMANTA_MITOGEN_LOGGED_VALUE_MAX_LEN` | `50` | When executing any function on a remote host, the mitogen `Proxy` helper will log the arguments and returned values in resource actions.  To avoid filling up these logs too easily, we set a limit on the amount of characters that the representation of each of these values can take in the log.  This environment variable allows to configure this maximum value.  When a value exceeds this length, it is truncated and a truncated suffix is added to it. |
| `INMANTA_MITOGEN_LOGGED_TRUNCATED_VALUE_SUFFIX` | `<...>` | If a logged value is truncated because it is too long to be logged completely (cf. `INMANTA_MITOGEN_LOGGED_VALUE_MAX_LEN` env var), a suffix is added to it, this option allows to change the content of that suffix. |

## Exceptions

1. `inmanta_plugins.mitogen.PythonNotFoundError`: This exception is raised when the python interpreter provided to mitogen can not be found on the host where mitogen is instantiating a context.  The path of this python interpreter can be provided in two ways:
    - If you are constructing the `mitogen::Context` entities in the model, you can change the value of the `python_path` attribute of your entity to match a python path that exists on the host.
    - If you are using the implicit context that comes with the `std::Host` entity (that the resource attaches itself to using the `host` relation), then you can update the `python_cmd` attribute of the `std::OS` entity attached to that host, as it will be what determines the python path.

    Knowing which python path to use is not always straightforward.  The mitogen module always expects a python3.9+ binary, which on most linux distributions can be found using `python3` as a python path.  Here is a list of distributions which will require you to use a different path:
    | **Distro** | **Path** |
    | ---------- | -------- |
    | `RHEL/Rocky/Alma 8` | `/usr/libexec/platform-python` |



```{toctree}
:maxdepth: 1
autodoc.rst
CHANGELOG.md
```