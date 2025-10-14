"""Module for a session to a LabOne Kernel.

A Kernel is a remote server that provides access to a defined set of nodes.
It can be a device kernel that provides access to the device nodes but it
can also be a kernel that provides additional functionality, e.g. the
Data Server (ZI) kernel.

Every Kernel provides the same interface and can therefore be handled
in the same way. The only difference is the set of nodes that are available
on the kernel.

The number of sessions to a kernel is not limited. However, due to the
asynchronous interface, it is often not necessary to have multiple sessions
to the same kernel.
"""

from __future__ import annotations

from typing import TypeAlias

import zhinst.comms
from packaging import version

from zhinst.comms_schemas.labone import hpk_schema
from zhinst.comms_schemas.labone.core.errors import async_translate_comms_error
from zhinst.comms_schemas.labone.core.helper import ZIContext, get_default_context
from zhinst.comms_schemas.labone.core.session import Session

KernelInfo: TypeAlias = zhinst.comms.DestinationParams
HPK_SCHEMA_ID = 0xA621130A90860008


class KernelSession(Session):
    """Session to a LabOne kernel.

    Representation of a single session to a LabOne kernel. This class
    encapsulates the labone interaction and exposes a Python native API.
    All functions are exposed as they are implemented in the kernel
    interface and are directly forwarded to the kernel.

    Each function implements the required error handling both for the
    socket communication and the server errors. This means unless an Exception
    is raised the call was successful.

    The KernelSession class is instantiated through the staticmethod
    `create()`.
    This is due to the fact that the instantiation is done asynchronously.
    To call the constructor directly an already existing connection
    must be provided.

    !!! note

        Due to the asynchronous interface, one needs to use the static method
        `create` instead of the `__init__` method.

    ```python
    session = await KernelSession(
            ZIContext.zi_connection(),
            host = "localhost",
            port = 8004,
        )
    ```

    Args:
        core_session: The underlying zhinst.comms session.
        host: The hostname of the server.
        port: The port of the server.
        context: The context in which the session is running.
        capability_version: The capability version the server reported.
    """

    def __init__(
        self,
        core_session: zhinst.comms.DynamicClient,
        *,
        host: str,
        port: int,
        context: ZIContext,
        capability_version: version.Version,
    ) -> None:
        super().__init__(
            core_session,
            context=context,
            capability_version=capability_version,
        )
        self._host = host
        self._port = port

    @staticmethod
    @async_translate_comms_error
    async def create(
        *,
        kernel_info: KernelInfo,
        host: str,
        port: int,
        context: ZIContext | None = None,
        timeout: int = 5000,
    ) -> KernelSession:
        """Create a new session to a LabOne kernel.

        Since the creation of a new session happens asynchronously, this method
        is required, instead of a simple constructor (since a constructor can
        not be asynchronous).

        Args:
            kernel_info: Information about the target kernel.
            host: Hostname of the server.
            port: Port of the server.
            context: Context in which the session should run. If not provided
                the default context will be used which is in most cases the
                desired behavior.
            timeout: Timeout in milliseconds for the connection setup.

        Returns:
            A new session to the specified kernel.

        Raises:
            UnavailableError: If the kernel was not found or unable to connect.
            BadRequestError: If there is a generic problem interpreting the incoming
                request
            InternalError: If the kernel could not be launched or another internal
                error occurred.
            LabOneCoreError: If another error happens during the session creation.
        """
        if context is None:
            context = get_default_context()
        core_session = await context.connect_labone(
            host,
            port,
            kernel_info,
            schema=hpk_schema.get_schema_loader().get_interface_schema(HPK_SCHEMA_ID),
            timeout=timeout,
        )
        compatibility_version = version.Version(
            (await core_session.getSessionVersion()).version,
        )
        return KernelSession(
            core_session,
            host=host,
            port=port,
            context=context,
            capability_version=compatibility_version,
        )

    @property
    def host(self) -> str:
        """Server host address."""
        return self._host

    @property
    def port(self) -> int:
        """Server port."""
        return self._port
