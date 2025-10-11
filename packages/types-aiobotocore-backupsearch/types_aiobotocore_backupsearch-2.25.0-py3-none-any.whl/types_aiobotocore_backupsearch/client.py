"""
Type annotations for backupsearch service Client.

[Documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from aiobotocore.session import get_session
    from types_aiobotocore_backupsearch.client import BackupSearchClient

    session = get_session()
    async with session.create_client("backupsearch") as client:
        client: BackupSearchClient
    ```
"""

from __future__ import annotations

import sys
from types import TracebackType
from typing import Any, overload

from aiobotocore.client import AioBaseClient
from botocore.client import ClientMeta
from botocore.errorfactory import BaseClientExceptions
from botocore.exceptions import ClientError as BotocoreClientError

from .paginator import (
    ListSearchJobBackupsPaginator,
    ListSearchJobResultsPaginator,
    ListSearchJobsPaginator,
    ListSearchResultExportJobsPaginator,
)
from .type_defs import (
    GetSearchJobInputTypeDef,
    GetSearchJobOutputTypeDef,
    GetSearchResultExportJobInputTypeDef,
    GetSearchResultExportJobOutputTypeDef,
    ListSearchJobBackupsInputTypeDef,
    ListSearchJobBackupsOutputTypeDef,
    ListSearchJobResultsInputTypeDef,
    ListSearchJobResultsOutputTypeDef,
    ListSearchJobsInputTypeDef,
    ListSearchJobsOutputTypeDef,
    ListSearchResultExportJobsInputTypeDef,
    ListSearchResultExportJobsOutputTypeDef,
    ListTagsForResourceRequestTypeDef,
    ListTagsForResourceResponseTypeDef,
    StartSearchJobInputTypeDef,
    StartSearchJobOutputTypeDef,
    StartSearchResultExportJobInputTypeDef,
    StartSearchResultExportJobOutputTypeDef,
    StopSearchJobInputTypeDef,
    TagResourceRequestTypeDef,
    UntagResourceRequestTypeDef,
)

if sys.version_info >= (3, 9):
    from builtins import dict as Dict
    from builtins import type as Type
    from collections.abc import Mapping
else:
    from typing import Dict, Mapping, Type
if sys.version_info >= (3, 12):
    from typing import Literal, Self, Unpack
else:
    from typing_extensions import Literal, Self, Unpack


__all__ = ("BackupSearchClient",)


class Exceptions(BaseClientExceptions):
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    InternalServerException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]
    ThrottlingException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]


class BackupSearchClient(AioBaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch.html#BackupSearch.Client)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        BackupSearchClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch.html#BackupSearch.Client)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#exceptions)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/can_paginate.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#can_paginate)
        """

    async def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/generate_presigned_url.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#generate_presigned_url)
        """

    async def get_search_job(
        self, **kwargs: Unpack[GetSearchJobInputTypeDef]
    ) -> GetSearchJobOutputTypeDef:
        """
        This operation retrieves metadata of a search job, including its progress.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/get_search_job.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#get_search_job)
        """

    async def get_search_result_export_job(
        self, **kwargs: Unpack[GetSearchResultExportJobInputTypeDef]
    ) -> GetSearchResultExportJobOutputTypeDef:
        """
        This operation retrieves the metadata of an export job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/get_search_result_export_job.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#get_search_result_export_job)
        """

    async def list_search_job_backups(
        self, **kwargs: Unpack[ListSearchJobBackupsInputTypeDef]
    ) -> ListSearchJobBackupsOutputTypeDef:
        """
        This operation returns a list of all backups (recovery points) in a paginated
        format that were included in the search job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/list_search_job_backups.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#list_search_job_backups)
        """

    async def list_search_job_results(
        self, **kwargs: Unpack[ListSearchJobResultsInputTypeDef]
    ) -> ListSearchJobResultsOutputTypeDef:
        """
        This operation returns a list of a specified search job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/list_search_job_results.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#list_search_job_results)
        """

    async def list_search_jobs(
        self, **kwargs: Unpack[ListSearchJobsInputTypeDef]
    ) -> ListSearchJobsOutputTypeDef:
        """
        This operation returns a list of search jobs belonging to an account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/list_search_jobs.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#list_search_jobs)
        """

    async def list_search_result_export_jobs(
        self, **kwargs: Unpack[ListSearchResultExportJobsInputTypeDef]
    ) -> ListSearchResultExportJobsOutputTypeDef:
        """
        This operation exports search results of a search job to a specified
        destination S3 bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/list_search_result_export_jobs.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#list_search_result_export_jobs)
        """

    async def list_tags_for_resource(
        self, **kwargs: Unpack[ListTagsForResourceRequestTypeDef]
    ) -> ListTagsForResourceResponseTypeDef:
        """
        This operation returns the tags for a resource type.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/list_tags_for_resource.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#list_tags_for_resource)
        """

    async def start_search_job(
        self, **kwargs: Unpack[StartSearchJobInputTypeDef]
    ) -> StartSearchJobOutputTypeDef:
        """
        This operation creates a search job which returns recovery points filtered by
        SearchScope and items filtered by ItemFilters.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/start_search_job.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#start_search_job)
        """

    async def start_search_result_export_job(
        self, **kwargs: Unpack[StartSearchResultExportJobInputTypeDef]
    ) -> StartSearchResultExportJobOutputTypeDef:
        """
        This operations starts a job to export the results of search job to a
        designated S3 bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/start_search_result_export_job.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#start_search_result_export_job)
        """

    async def stop_search_job(self, **kwargs: Unpack[StopSearchJobInputTypeDef]) -> Dict[str, Any]:
        """
        This operations ends a search job.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/stop_search_job.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#stop_search_job)
        """

    async def tag_resource(self, **kwargs: Unpack[TagResourceRequestTypeDef]) -> Dict[str, Any]:
        """
        This operation puts tags on the resource you indicate.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/tag_resource.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#tag_resource)
        """

    async def untag_resource(self, **kwargs: Unpack[UntagResourceRequestTypeDef]) -> Dict[str, Any]:
        """
        This operation removes tags from the specified resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/untag_resource.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#untag_resource)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_search_job_backups"]
    ) -> ListSearchJobBackupsPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/get_paginator.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_search_job_results"]
    ) -> ListSearchJobResultsPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/get_paginator.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_search_jobs"]
    ) -> ListSearchJobsPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/get_paginator.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_search_result_export_jobs"]
    ) -> ListSearchResultExportJobsPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch/client/get_paginator.html)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/#get_paginator)
        """

    async def __aenter__(self) -> Self:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch.html#BackupSearch.Client)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/)
        """

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/backupsearch.html#BackupSearch.Client)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_backupsearch/client/)
        """
