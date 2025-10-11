"""
Type annotations for omics service client waiters.

[Documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from aiobotocore.session import get_session

    from types_aiobotocore_omics.client import OmicsClient
    from types_aiobotocore_omics.waiter import (
        AnnotationImportJobCreatedWaiter,
        AnnotationStoreCreatedWaiter,
        AnnotationStoreDeletedWaiter,
        AnnotationStoreVersionCreatedWaiter,
        AnnotationStoreVersionDeletedWaiter,
        ReadSetActivationJobCompletedWaiter,
        ReadSetExportJobCompletedWaiter,
        ReadSetImportJobCompletedWaiter,
        ReferenceImportJobCompletedWaiter,
        RunCompletedWaiter,
        RunRunningWaiter,
        TaskCompletedWaiter,
        TaskRunningWaiter,
        VariantImportJobCreatedWaiter,
        VariantStoreCreatedWaiter,
        VariantStoreDeletedWaiter,
        WorkflowActiveWaiter,
        WorkflowVersionActiveWaiter,
    )

    session = get_session()
    async with session.create_client("omics") as client:
        client: OmicsClient

        annotation_import_job_created_waiter: AnnotationImportJobCreatedWaiter = client.get_waiter("annotation_import_job_created")
        annotation_store_created_waiter: AnnotationStoreCreatedWaiter = client.get_waiter("annotation_store_created")
        annotation_store_deleted_waiter: AnnotationStoreDeletedWaiter = client.get_waiter("annotation_store_deleted")
        annotation_store_version_created_waiter: AnnotationStoreVersionCreatedWaiter = client.get_waiter("annotation_store_version_created")
        annotation_store_version_deleted_waiter: AnnotationStoreVersionDeletedWaiter = client.get_waiter("annotation_store_version_deleted")
        read_set_activation_job_completed_waiter: ReadSetActivationJobCompletedWaiter = client.get_waiter("read_set_activation_job_completed")
        read_set_export_job_completed_waiter: ReadSetExportJobCompletedWaiter = client.get_waiter("read_set_export_job_completed")
        read_set_import_job_completed_waiter: ReadSetImportJobCompletedWaiter = client.get_waiter("read_set_import_job_completed")
        reference_import_job_completed_waiter: ReferenceImportJobCompletedWaiter = client.get_waiter("reference_import_job_completed")
        run_completed_waiter: RunCompletedWaiter = client.get_waiter("run_completed")
        run_running_waiter: RunRunningWaiter = client.get_waiter("run_running")
        task_completed_waiter: TaskCompletedWaiter = client.get_waiter("task_completed")
        task_running_waiter: TaskRunningWaiter = client.get_waiter("task_running")
        variant_import_job_created_waiter: VariantImportJobCreatedWaiter = client.get_waiter("variant_import_job_created")
        variant_store_created_waiter: VariantStoreCreatedWaiter = client.get_waiter("variant_store_created")
        variant_store_deleted_waiter: VariantStoreDeletedWaiter = client.get_waiter("variant_store_deleted")
        workflow_active_waiter: WorkflowActiveWaiter = client.get_waiter("workflow_active")
        workflow_version_active_waiter: WorkflowVersionActiveWaiter = client.get_waiter("workflow_version_active")
    ```
"""

from __future__ import annotations

import sys

from aiobotocore.waiter import AIOWaiter

from .type_defs import (
    GetAnnotationImportRequestWaitTypeDef,
    GetAnnotationStoreRequestWaitExtraTypeDef,
    GetAnnotationStoreRequestWaitTypeDef,
    GetAnnotationStoreVersionRequestWaitExtraTypeDef,
    GetAnnotationStoreVersionRequestWaitTypeDef,
    GetReadSetActivationJobRequestWaitTypeDef,
    GetReadSetExportJobRequestWaitTypeDef,
    GetReadSetImportJobRequestWaitTypeDef,
    GetReferenceImportJobRequestWaitTypeDef,
    GetRunRequestWaitExtraTypeDef,
    GetRunRequestWaitTypeDef,
    GetRunTaskRequestWaitExtraTypeDef,
    GetRunTaskRequestWaitTypeDef,
    GetVariantImportRequestWaitTypeDef,
    GetVariantStoreRequestWaitExtraTypeDef,
    GetVariantStoreRequestWaitTypeDef,
    GetWorkflowRequestWaitTypeDef,
    GetWorkflowVersionRequestWaitTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Unpack
else:
    from typing_extensions import Unpack

__all__ = (
    "AnnotationImportJobCreatedWaiter",
    "AnnotationStoreCreatedWaiter",
    "AnnotationStoreDeletedWaiter",
    "AnnotationStoreVersionCreatedWaiter",
    "AnnotationStoreVersionDeletedWaiter",
    "ReadSetActivationJobCompletedWaiter",
    "ReadSetExportJobCompletedWaiter",
    "ReadSetImportJobCompletedWaiter",
    "ReferenceImportJobCompletedWaiter",
    "RunCompletedWaiter",
    "RunRunningWaiter",
    "TaskCompletedWaiter",
    "TaskRunningWaiter",
    "VariantImportJobCreatedWaiter",
    "VariantStoreCreatedWaiter",
    "VariantStoreDeletedWaiter",
    "WorkflowActiveWaiter",
    "WorkflowVersionActiveWaiter",
)

class AnnotationImportJobCreatedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/AnnotationImportJobCreated.html#Omics.Waiter.AnnotationImportJobCreated)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#annotationimportjobcreatedwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetAnnotationImportRequestWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/AnnotationImportJobCreated.html#Omics.Waiter.AnnotationImportJobCreated.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#annotationimportjobcreatedwaiter)
        """

class AnnotationStoreCreatedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/AnnotationStoreCreated.html#Omics.Waiter.AnnotationStoreCreated)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#annotationstorecreatedwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetAnnotationStoreRequestWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/AnnotationStoreCreated.html#Omics.Waiter.AnnotationStoreCreated.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#annotationstorecreatedwaiter)
        """

class AnnotationStoreDeletedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/AnnotationStoreDeleted.html#Omics.Waiter.AnnotationStoreDeleted)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#annotationstoredeletedwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetAnnotationStoreRequestWaitExtraTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/AnnotationStoreDeleted.html#Omics.Waiter.AnnotationStoreDeleted.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#annotationstoredeletedwaiter)
        """

class AnnotationStoreVersionCreatedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/AnnotationStoreVersionCreated.html#Omics.Waiter.AnnotationStoreVersionCreated)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#annotationstoreversioncreatedwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetAnnotationStoreVersionRequestWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/AnnotationStoreVersionCreated.html#Omics.Waiter.AnnotationStoreVersionCreated.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#annotationstoreversioncreatedwaiter)
        """

class AnnotationStoreVersionDeletedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/AnnotationStoreVersionDeleted.html#Omics.Waiter.AnnotationStoreVersionDeleted)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#annotationstoreversiondeletedwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetAnnotationStoreVersionRequestWaitExtraTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/AnnotationStoreVersionDeleted.html#Omics.Waiter.AnnotationStoreVersionDeleted.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#annotationstoreversiondeletedwaiter)
        """

class ReadSetActivationJobCompletedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/ReadSetActivationJobCompleted.html#Omics.Waiter.ReadSetActivationJobCompleted)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#readsetactivationjobcompletedwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetReadSetActivationJobRequestWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/ReadSetActivationJobCompleted.html#Omics.Waiter.ReadSetActivationJobCompleted.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#readsetactivationjobcompletedwaiter)
        """

class ReadSetExportJobCompletedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/ReadSetExportJobCompleted.html#Omics.Waiter.ReadSetExportJobCompleted)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#readsetexportjobcompletedwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetReadSetExportJobRequestWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/ReadSetExportJobCompleted.html#Omics.Waiter.ReadSetExportJobCompleted.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#readsetexportjobcompletedwaiter)
        """

class ReadSetImportJobCompletedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/ReadSetImportJobCompleted.html#Omics.Waiter.ReadSetImportJobCompleted)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#readsetimportjobcompletedwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetReadSetImportJobRequestWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/ReadSetImportJobCompleted.html#Omics.Waiter.ReadSetImportJobCompleted.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#readsetimportjobcompletedwaiter)
        """

class ReferenceImportJobCompletedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/ReferenceImportJobCompleted.html#Omics.Waiter.ReferenceImportJobCompleted)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#referenceimportjobcompletedwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetReferenceImportJobRequestWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/ReferenceImportJobCompleted.html#Omics.Waiter.ReferenceImportJobCompleted.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#referenceimportjobcompletedwaiter)
        """

class RunCompletedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/RunCompleted.html#Omics.Waiter.RunCompleted)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#runcompletedwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetRunRequestWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/RunCompleted.html#Omics.Waiter.RunCompleted.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#runcompletedwaiter)
        """

class RunRunningWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/RunRunning.html#Omics.Waiter.RunRunning)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#runrunningwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetRunRequestWaitExtraTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/RunRunning.html#Omics.Waiter.RunRunning.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#runrunningwaiter)
        """

class TaskCompletedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/TaskCompleted.html#Omics.Waiter.TaskCompleted)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#taskcompletedwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetRunTaskRequestWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/TaskCompleted.html#Omics.Waiter.TaskCompleted.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#taskcompletedwaiter)
        """

class TaskRunningWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/TaskRunning.html#Omics.Waiter.TaskRunning)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#taskrunningwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetRunTaskRequestWaitExtraTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/TaskRunning.html#Omics.Waiter.TaskRunning.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#taskrunningwaiter)
        """

class VariantImportJobCreatedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/VariantImportJobCreated.html#Omics.Waiter.VariantImportJobCreated)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#variantimportjobcreatedwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetVariantImportRequestWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/VariantImportJobCreated.html#Omics.Waiter.VariantImportJobCreated.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#variantimportjobcreatedwaiter)
        """

class VariantStoreCreatedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/VariantStoreCreated.html#Omics.Waiter.VariantStoreCreated)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#variantstorecreatedwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetVariantStoreRequestWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/VariantStoreCreated.html#Omics.Waiter.VariantStoreCreated.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#variantstorecreatedwaiter)
        """

class VariantStoreDeletedWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/VariantStoreDeleted.html#Omics.Waiter.VariantStoreDeleted)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#variantstoredeletedwaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetVariantStoreRequestWaitExtraTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/VariantStoreDeleted.html#Omics.Waiter.VariantStoreDeleted.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#variantstoredeletedwaiter)
        """

class WorkflowActiveWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/WorkflowActive.html#Omics.Waiter.WorkflowActive)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#workflowactivewaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetWorkflowRequestWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/WorkflowActive.html#Omics.Waiter.WorkflowActive.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#workflowactivewaiter)
        """

class WorkflowVersionActiveWaiter(AIOWaiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/WorkflowVersionActive.html#Omics.Waiter.WorkflowVersionActive)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#workflowversionactivewaiter)
    """
    async def wait(  # type: ignore[override]
        self, **kwargs: Unpack[GetWorkflowVersionRequestWaitTypeDef]
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/omics/waiter/WorkflowVersionActive.html#Omics.Waiter.WorkflowVersionActive.wait)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_omics/waiters/#workflowversionactivewaiter)
        """
