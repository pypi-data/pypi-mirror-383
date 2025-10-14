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

import inmanta.agent.handler
import inmanta.execute
import inmanta.execute.proxy
import inmanta.export
import inmanta.resources
import inmanta_plugins.mitogen


class Resource(inmanta.resources.Resource):
    """
    Base class for all resources that wish to use the remote io capabilities
    of the mitogen module.
    """

    fields = ("via",)
    via: dict[str, object]

    @classmethod
    def get_via(
        cls,
        _: inmanta.export.Exporter,
        entity: inmanta.execute.proxy.DynamicProxy,
    ) -> dict[str, object]:
        return inmanta_plugins.mitogen.get_resource_context(entity)


R = typing.TypeVar("R", bound=Resource)


class Handler(inmanta.agent.handler.HandlerAPI[R]):
    """
    Base class for all resources that with to use the remote io capabilities
    of the mitogen module.  It already sets up the connection to the remote
    host, and handle caching of the connection in case it is used by multiple
    resources.
    """

    proxy: inmanta_plugins.mitogen.Proxy
    proxy_previous_logger: inmanta.agent.handler.LoggerABC

    @inmanta.agent.handler.cache(
        ignore=["serialized_context"],
        call_on_delete=lambda p: p.disconnect(best_effort=True),
    )
    def get_proxy(
        self,
        serialized_context: dict[str, object],
        hash: str,
        agent_name: str,
    ) -> inmanta_plugins.mitogen.Proxy:
        """
        Construct the proxy object, and open the connection.  The proxy is constructed
        using the serialized mitogen context.  The connection is cached using its name, it
        is the responsibility of the caller to make sure the provided name is unique.

        :param serialized_context: The context dict from the resource desired state
            that should be used to build up the proxy object.
        :param hash: An identifier for the context, making sure we can safely cache it.
        :param agent_name: The name of the resource agent using the proxy, we also use
            this to identify the session, as it identifies the thread on which the handler
            is running.  We don't want two handlers on different threads to use the same
            proxy object.
        """
        proxy = inmanta_plugins.mitogen.Proxy(serialized_context)
        proxy.connect()
        return proxy

    def pre(self, ctx: inmanta.agent.handler.HandlerContext, resource: R) -> None:
        """
        Method executed before a handler operation (Facts, dryrun, real deployment, ...) is executed. Override this method
        to run before an operation.

        :param ctx: Context object to report changes and logs to the agent and server.
        :param resource: The resource being handled.
        """
        super().pre(ctx, resource)
        self.proxy = self.get_proxy(
            resource.via,
            hash=inmanta_plugins.mitogen.context_hash(resource.via),
            agent_name=resource.id.get_agent_name(),
        )

        # Save the current logger object to reset it when the resource is done deploying
        self.proxy_previous_logger = self.proxy.logger

        # Update the logger of the proxy, to log each call in the resource actions.
        self.proxy.logger = ctx

    def post(self, ctx: inmanta.agent.handler.HandlerContext, resource: R) -> None:
        """
        Method executed after a handler operation. Override this method to run after an operation.

        :param ctx: Context object to report changes and logs to the agent and server.
        :param resource: The resource being handled.
        """
        if hasattr(self, "proxy") and hasattr(self, "proxy_previous_logger"):
            # Reset the logger of the cached proxy object
            self.proxy.logger = self.proxy_previous_logger

        super().post(ctx, resource)


class ResourceABC(Resource, inmanta.resources.PurgeableResource):  # type: ignore[misc]
    """
    Kept for backward compatibility.
    The original implementation of mitogen handler helpers only supported
    purgeable resources with the CRUDHandler.  The base interface has now
    been made more generic, to also support discovery resources.
    """


PR = typing.TypeVar("PR", bound=ResourceABC)


class HandlerABC(Handler[PR], inmanta.agent.handler.CRUDHandler[PR]):
    """
    Kept for backward compatibility.
    The original implementation of mitogen handler helpers only supported
    purgeable resources with the CRUDHandler.  The base interface has now
    been made more generic, to also support discovery resources.
    """
