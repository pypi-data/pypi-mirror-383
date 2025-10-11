"""
Type annotations for neptune-graph service client waiters.

[Documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from aiobotocore.session import get_session

    from types_aiobotocore_neptune_graph.client import NeptuneGraphClient
    from types_aiobotocore_neptune_graph.waiter import (
        ExportTaskCancelledWaiter,
        ExportTaskSuccessfulWaiter,
        GraphAvailableWaiter,
        GraphDeletedWaiter,
        GraphSnapshotAvailableWaiter,
        GraphSnapshotDeletedWaiter,
        GraphStoppedWaiter,
        ImportTaskCancelledWaiter,
        ImportTaskSuccessfulWaiter,
        PrivateGraphEndpointAvailableWaiter,
        PrivateGraphEndpointDeletedWaiter,
    )

    session = get_session()
    async with session.create_client("neptune-graph") as client:
        client: NeptuneGraphClient

        export_task_cancelled_waiter: ExportTaskCancelledWaiter = client.get_waiter("export_task_cancelled")
        export_task_successful_waiter: ExportTaskSuccessfulWaiter = client.get_waiter("export_task_successful")
        graph_available_waiter: GraphAvailableWaiter = client.get_waiter("graph_available")
        graph_deleted_waiter: GraphDeletedWaiter = client.get_waiter("graph_deleted")
        graph_snapshot_available_waiter: GraphSnapshotAvailableWaiter = client.get_waiter("graph_snapshot_available")
        graph_snapshot_deleted_waiter: GraphSnapshotDeletedWaiter = client.get_waiter("graph_snapshot_deleted")
        graph_stopped_waiter: GraphStoppedWaiter = client.get_waiter("graph_stopped")
        import_task_cancelled_waiter: ImportTaskCancelledWaiter = client.get_waiter("import_task_cancelled")
        import_task_successful_waiter: ImportTaskSuccessfulWaiter = client.get_waiter("import_task_successful")
        private_graph_endpoint_available_waiter: PrivateGraphEndpointAvailableWaiter = client.get_waiter("private_graph_endpoint_available")
        private_graph_endpoint_deleted_waiter: PrivateGraphEndpointDeletedWaiter = client.get_waiter("private_graph_endpoint_deleted")
    ```
"""

from __future__ import annotations

import sys

from aiobotocore.waiter import AIOWaiter

from .type_defs import (
    GetExportTaskInputWaitExtraTypeDef,
    GetExportTaskInputWaitTypeDef,
    GetGraphInputWaitExtraExtraTypeDef,
    GetGraphInputWaitExtraTypeDef,
    GetGraphInputWaitTypeDef,
    GetGraphSnapshotInputWaitExtraTypeDef,
    GetGraphSnapshotInputWaitTypeDef,
    GetImportTaskInputWaitExtraTypeDef,
    GetImportTaskInputWaitTypeDef,
    GetPrivateGraphEndpointInputWaitExtraTypeDef,
    GetPrivateGraphEndpointInputWaitTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Unpack
else:
    from typing_extensions import Unpack


__all__ = (
    "ExportTaskCancelledWaiter",
    "ExportTaskSuccessfulWaiter",
    "GraphAvailableWaiter",
    "GraphDeletedWaiter",
    "GraphSnapshotAvailableWaiter",
    "GraphSnapshotDeletedWaiter",
    "GraphStoppedWaiter",
    "ImportTaskCancelledWaiter",
    "ImportTaskSuccessfulWaiter",
    "PrivateGraphEndpointAvailableWaiter",
    "PrivateGraphEndpointDeletedWaiter",
)


class ExportTaskCancelledWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/ExportTaskCancelled.html#NeptuneGraph.Waiter.ExportTaskCancelled)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#exporttaskcancelledwaiter)
    """

    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetExportTaskInputWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/ExportTaskCancelled.html#NeptuneGraph.Waiter.ExportTaskCancelled.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#exporttaskcancelledwaiter)
        """


class ExportTaskSuccessfulWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/ExportTaskSuccessful.html#NeptuneGraph.Waiter.ExportTaskSuccessful)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#exporttasksuccessfulwaiter)
    """

    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetExportTaskInputWaitExtraTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/ExportTaskSuccessful.html#NeptuneGraph.Waiter.ExportTaskSuccessful.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#exporttasksuccessfulwaiter)
        """


class GraphAvailableWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/GraphAvailable.html#NeptuneGraph.Waiter.GraphAvailable)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#graphavailablewaiter)
    """

    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetGraphInputWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/GraphAvailable.html#NeptuneGraph.Waiter.GraphAvailable.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#graphavailablewaiter)
        """


class GraphDeletedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/GraphDeleted.html#NeptuneGraph.Waiter.GraphDeleted)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#graphdeletedwaiter)
    """

    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetGraphInputWaitExtraTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/GraphDeleted.html#NeptuneGraph.Waiter.GraphDeleted.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#graphdeletedwaiter)
        """


class GraphSnapshotAvailableWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/GraphSnapshotAvailable.html#NeptuneGraph.Waiter.GraphSnapshotAvailable)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#graphsnapshotavailablewaiter)
    """

    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetGraphSnapshotInputWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/GraphSnapshotAvailable.html#NeptuneGraph.Waiter.GraphSnapshotAvailable.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#graphsnapshotavailablewaiter)
        """


class GraphSnapshotDeletedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/GraphSnapshotDeleted.html#NeptuneGraph.Waiter.GraphSnapshotDeleted)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#graphsnapshotdeletedwaiter)
    """

    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetGraphSnapshotInputWaitExtraTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/GraphSnapshotDeleted.html#NeptuneGraph.Waiter.GraphSnapshotDeleted.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#graphsnapshotdeletedwaiter)
        """


class GraphStoppedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/GraphStopped.html#NeptuneGraph.Waiter.GraphStopped)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#graphstoppedwaiter)
    """

    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetGraphInputWaitExtraExtraTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/GraphStopped.html#NeptuneGraph.Waiter.GraphStopped.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#graphstoppedwaiter)
        """


class ImportTaskCancelledWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/ImportTaskCancelled.html#NeptuneGraph.Waiter.ImportTaskCancelled)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#importtaskcancelledwaiter)
    """

    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetImportTaskInputWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/ImportTaskCancelled.html#NeptuneGraph.Waiter.ImportTaskCancelled.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#importtaskcancelledwaiter)
        """


class ImportTaskSuccessfulWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/ImportTaskSuccessful.html#NeptuneGraph.Waiter.ImportTaskSuccessful)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#importtasksuccessfulwaiter)
    """

    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetImportTaskInputWaitExtraTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/ImportTaskSuccessful.html#NeptuneGraph.Waiter.ImportTaskSuccessful.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#importtasksuccessfulwaiter)
        """


class PrivateGraphEndpointAvailableWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/PrivateGraphEndpointAvailable.html#NeptuneGraph.Waiter.PrivateGraphEndpointAvailable)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#privategraphendpointavailablewaiter)
    """

    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetPrivateGraphEndpointInputWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/PrivateGraphEndpointAvailable.html#NeptuneGraph.Waiter.PrivateGraphEndpointAvailable.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#privategraphendpointavailablewaiter)
        """


class PrivateGraphEndpointDeletedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/PrivateGraphEndpointDeleted.html#NeptuneGraph.Waiter.PrivateGraphEndpointDeleted)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#privategraphendpointdeletedwaiter)
    """

    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetPrivateGraphEndpointInputWaitExtraTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/neptune-graph/waiter/PrivateGraphEndpointDeleted.html#NeptuneGraph.Waiter.PrivateGraphEndpointDeleted.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/waiters/#privategraphendpointdeletedwaiter)
        """
