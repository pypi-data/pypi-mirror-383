"""
Main interface for neptune-graph service.

[Documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_neptune_graph/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from aiobotocore.session import get_session
    from types_aiobotocore_neptune_graph import (
        Client,
        ExportTaskCancelledWaiter,
        ExportTaskSuccessfulWaiter,
        GraphAvailableWaiter,
        GraphDeletedWaiter,
        GraphSnapshotAvailableWaiter,
        GraphSnapshotDeletedWaiter,
        GraphStoppedWaiter,
        ImportTaskCancelledWaiter,
        ImportTaskSuccessfulWaiter,
        ListExportTasksPaginator,
        ListGraphSnapshotsPaginator,
        ListGraphsPaginator,
        ListImportTasksPaginator,
        ListPrivateGraphEndpointsPaginator,
        NeptuneGraphClient,
        PrivateGraphEndpointAvailableWaiter,
        PrivateGraphEndpointDeletedWaiter,
    )

    session = get_session()
    async with session.create_client("neptune-graph") as client:
        client: NeptuneGraphClient
        ...


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

    list_export_tasks_paginator: ListExportTasksPaginator = client.get_paginator("list_export_tasks")
    list_graph_snapshots_paginator: ListGraphSnapshotsPaginator = client.get_paginator("list_graph_snapshots")
    list_graphs_paginator: ListGraphsPaginator = client.get_paginator("list_graphs")
    list_import_tasks_paginator: ListImportTasksPaginator = client.get_paginator("list_import_tasks")
    list_private_graph_endpoints_paginator: ListPrivateGraphEndpointsPaginator = client.get_paginator("list_private_graph_endpoints")
    ```
"""

from .client import NeptuneGraphClient
from .paginator import (
    ListExportTasksPaginator,
    ListGraphSnapshotsPaginator,
    ListGraphsPaginator,
    ListImportTasksPaginator,
    ListPrivateGraphEndpointsPaginator,
)
from .waiter import (
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

Client = NeptuneGraphClient

__all__ = (
    "Client",
    "ExportTaskCancelledWaiter",
    "ExportTaskSuccessfulWaiter",
    "GraphAvailableWaiter",
    "GraphDeletedWaiter",
    "GraphSnapshotAvailableWaiter",
    "GraphSnapshotDeletedWaiter",
    "GraphStoppedWaiter",
    "ImportTaskCancelledWaiter",
    "ImportTaskSuccessfulWaiter",
    "ListExportTasksPaginator",
    "ListGraphSnapshotsPaginator",
    "ListGraphsPaginator",
    "ListImportTasksPaginator",
    "ListPrivateGraphEndpointsPaginator",
    "NeptuneGraphClient",
    "PrivateGraphEndpointAvailableWaiter",
    "PrivateGraphEndpointDeletedWaiter",
)
