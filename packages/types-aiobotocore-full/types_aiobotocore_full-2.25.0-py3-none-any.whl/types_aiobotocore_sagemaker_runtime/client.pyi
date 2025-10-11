"""
Type annotations for sagemaker-runtime service Client.

[Documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_runtime/client/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from aiobotocore.session import get_session
    from types_aiobotocore_sagemaker_runtime.client import SageMakerRuntimeClient

    session = get_session()
    async with session.create_client("sagemaker-runtime") as client:
        client: SageMakerRuntimeClient
    ```
"""

from __future__ import annotations

import sys
from types import TracebackType
from typing import Any

from aiobotocore.client import AioBaseClient
from botocore.client import ClientMeta
from botocore.errorfactory import BaseClientExceptions
from botocore.exceptions import ClientError as BotocoreClientError

from .type_defs import (
    InvokeEndpointAsyncInputTypeDef,
    InvokeEndpointAsyncOutputTypeDef,
    InvokeEndpointInputTypeDef,
    InvokeEndpointOutputTypeDef,
    InvokeEndpointWithResponseStreamInputTypeDef,
    InvokeEndpointWithResponseStreamOutputTypeDef,
)

if sys.version_info >= (3, 9):
    from builtins import type as Type
    from collections.abc import Mapping
else:
    from typing import Mapping, Type
if sys.version_info >= (3, 12):
    from typing import Self, Unpack
else:
    from typing_extensions import Self, Unpack

__all__ = ("SageMakerRuntimeClient",)

class Exceptions(BaseClientExceptions):
    ClientError: Type[BotocoreClientError]
    InternalDependencyException: Type[BotocoreClientError]
    InternalFailure: Type[BotocoreClientError]
    InternalStreamFailure: Type[BotocoreClientError]
    ModelError: Type[BotocoreClientError]
    ModelNotReadyException: Type[BotocoreClientError]
    ModelStreamError: Type[BotocoreClientError]
    ServiceUnavailable: Type[BotocoreClientError]
    ValidationError: Type[BotocoreClientError]

class SageMakerRuntimeClient(AioBaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker-runtime.html#SageMakerRuntime.Client)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_runtime/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        SageMakerRuntimeClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker-runtime.html#SageMakerRuntime.Client)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_runtime/client/#exceptions)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker-runtime/client/can_paginate.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_runtime/client/#can_paginate)
        """

    async def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker-runtime/client/generate_presigned_url.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_runtime/client/#generate_presigned_url)
        """

    async def invoke_endpoint(
        self, **kwargs: Unpack[InvokeEndpointInputTypeDef]
    ) -> InvokeEndpointOutputTypeDef:
        """
        After you deploy a model into production using Amazon SageMaker AI hosting
        services, your client applications use this API to get inferences from the
        model hosted at the specified endpoint.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker-runtime/client/invoke_endpoint.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_runtime/client/#invoke_endpoint)
        """

    async def invoke_endpoint_async(
        self, **kwargs: Unpack[InvokeEndpointAsyncInputTypeDef]
    ) -> InvokeEndpointAsyncOutputTypeDef:
        """
        After you deploy a model into production using Amazon SageMaker AI hosting
        services, your client applications use this API to get inferences from the
        model hosted at the specified endpoint in an asynchronous manner.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker-runtime/client/invoke_endpoint_async.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_runtime/client/#invoke_endpoint_async)
        """

    async def invoke_endpoint_with_response_stream(
        self, **kwargs: Unpack[InvokeEndpointWithResponseStreamInputTypeDef]
    ) -> InvokeEndpointWithResponseStreamOutputTypeDef:
        """
        Invokes a model at the specified endpoint to return the inference response as a
        stream.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker-runtime/client/invoke_endpoint_with_response_stream.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_runtime/client/#invoke_endpoint_with_response_stream)
        """

    async def __aenter__(self) -> Self:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker-runtime.html#SageMakerRuntime.Client)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_runtime/client/)
        """

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker-runtime.html#SageMakerRuntime.Client)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sagemaker_runtime/client/)
        """
