"""
Type annotations for bedrock-agentcore-control service Client.

[Documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from aiobotocore.session import get_session
    from types_aiobotocore_bedrock_agentcore_control.client import BedrockAgentCoreControlPlaneFrontingLayerClient

    session = get_session()
    async with session.create_client("bedrock-agentcore-control") as client:
        client: BedrockAgentCoreControlPlaneFrontingLayerClient
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
    ListAgentRuntimeEndpointsPaginator,
    ListAgentRuntimesPaginator,
    ListAgentRuntimeVersionsPaginator,
    ListApiKeyCredentialProvidersPaginator,
    ListBrowsersPaginator,
    ListCodeInterpretersPaginator,
    ListGatewaysPaginator,
    ListGatewayTargetsPaginator,
    ListMemoriesPaginator,
    ListOauth2CredentialProvidersPaginator,
    ListWorkloadIdentitiesPaginator,
)
from .type_defs import (
    CreateAgentRuntimeEndpointRequestTypeDef,
    CreateAgentRuntimeEndpointResponseTypeDef,
    CreateAgentRuntimeRequestTypeDef,
    CreateAgentRuntimeResponseTypeDef,
    CreateApiKeyCredentialProviderRequestTypeDef,
    CreateApiKeyCredentialProviderResponseTypeDef,
    CreateBrowserRequestTypeDef,
    CreateBrowserResponseTypeDef,
    CreateCodeInterpreterRequestTypeDef,
    CreateCodeInterpreterResponseTypeDef,
    CreateGatewayRequestTypeDef,
    CreateGatewayResponseTypeDef,
    CreateGatewayTargetRequestTypeDef,
    CreateGatewayTargetResponseTypeDef,
    CreateMemoryInputTypeDef,
    CreateMemoryOutputTypeDef,
    CreateOauth2CredentialProviderRequestTypeDef,
    CreateOauth2CredentialProviderResponseTypeDef,
    CreateWorkloadIdentityRequestTypeDef,
    CreateWorkloadIdentityResponseTypeDef,
    DeleteAgentRuntimeEndpointRequestTypeDef,
    DeleteAgentRuntimeEndpointResponseTypeDef,
    DeleteAgentRuntimeRequestTypeDef,
    DeleteAgentRuntimeResponseTypeDef,
    DeleteApiKeyCredentialProviderRequestTypeDef,
    DeleteBrowserRequestTypeDef,
    DeleteBrowserResponseTypeDef,
    DeleteCodeInterpreterRequestTypeDef,
    DeleteCodeInterpreterResponseTypeDef,
    DeleteGatewayRequestTypeDef,
    DeleteGatewayResponseTypeDef,
    DeleteGatewayTargetRequestTypeDef,
    DeleteGatewayTargetResponseTypeDef,
    DeleteMemoryInputTypeDef,
    DeleteMemoryOutputTypeDef,
    DeleteOauth2CredentialProviderRequestTypeDef,
    DeleteWorkloadIdentityRequestTypeDef,
    GetAgentRuntimeEndpointRequestTypeDef,
    GetAgentRuntimeEndpointResponseTypeDef,
    GetAgentRuntimeRequestTypeDef,
    GetAgentRuntimeResponseTypeDef,
    GetApiKeyCredentialProviderRequestTypeDef,
    GetApiKeyCredentialProviderResponseTypeDef,
    GetBrowserRequestTypeDef,
    GetBrowserResponseTypeDef,
    GetCodeInterpreterRequestTypeDef,
    GetCodeInterpreterResponseTypeDef,
    GetGatewayRequestTypeDef,
    GetGatewayResponseTypeDef,
    GetGatewayTargetRequestTypeDef,
    GetGatewayTargetResponseTypeDef,
    GetMemoryInputTypeDef,
    GetMemoryOutputTypeDef,
    GetOauth2CredentialProviderRequestTypeDef,
    GetOauth2CredentialProviderResponseTypeDef,
    GetTokenVaultRequestTypeDef,
    GetTokenVaultResponseTypeDef,
    GetWorkloadIdentityRequestTypeDef,
    GetWorkloadIdentityResponseTypeDef,
    ListAgentRuntimeEndpointsRequestTypeDef,
    ListAgentRuntimeEndpointsResponseTypeDef,
    ListAgentRuntimesRequestTypeDef,
    ListAgentRuntimesResponseTypeDef,
    ListAgentRuntimeVersionsRequestTypeDef,
    ListAgentRuntimeVersionsResponseTypeDef,
    ListApiKeyCredentialProvidersRequestTypeDef,
    ListApiKeyCredentialProvidersResponseTypeDef,
    ListBrowsersRequestTypeDef,
    ListBrowsersResponseTypeDef,
    ListCodeInterpretersRequestTypeDef,
    ListCodeInterpretersResponseTypeDef,
    ListGatewaysRequestTypeDef,
    ListGatewaysResponseTypeDef,
    ListGatewayTargetsRequestTypeDef,
    ListGatewayTargetsResponseTypeDef,
    ListMemoriesInputTypeDef,
    ListMemoriesOutputTypeDef,
    ListOauth2CredentialProvidersRequestTypeDef,
    ListOauth2CredentialProvidersResponseTypeDef,
    ListTagsForResourceRequestTypeDef,
    ListTagsForResourceResponseTypeDef,
    ListWorkloadIdentitiesRequestTypeDef,
    ListWorkloadIdentitiesResponseTypeDef,
    SetTokenVaultCMKRequestTypeDef,
    SetTokenVaultCMKResponseTypeDef,
    TagResourceRequestTypeDef,
    UntagResourceRequestTypeDef,
    UpdateAgentRuntimeEndpointRequestTypeDef,
    UpdateAgentRuntimeEndpointResponseTypeDef,
    UpdateAgentRuntimeRequestTypeDef,
    UpdateAgentRuntimeResponseTypeDef,
    UpdateApiKeyCredentialProviderRequestTypeDef,
    UpdateApiKeyCredentialProviderResponseTypeDef,
    UpdateGatewayRequestTypeDef,
    UpdateGatewayResponseTypeDef,
    UpdateGatewayTargetRequestTypeDef,
    UpdateGatewayTargetResponseTypeDef,
    UpdateMemoryInputTypeDef,
    UpdateMemoryOutputTypeDef,
    UpdateOauth2CredentialProviderRequestTypeDef,
    UpdateOauth2CredentialProviderResponseTypeDef,
    UpdateWorkloadIdentityRequestTypeDef,
    UpdateWorkloadIdentityResponseTypeDef,
)
from .waiter import MemoryCreatedWaiter

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

__all__ = ("BedrockAgentCoreControlPlaneFrontingLayerClient",)

class Exceptions(BaseClientExceptions):
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConcurrentModificationException: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    DecryptionFailure: Type[BotocoreClientError]
    EncryptionFailure: Type[BotocoreClientError]
    InternalServerException: Type[BotocoreClientError]
    ResourceLimitExceededException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]
    ThrottledException: Type[BotocoreClientError]
    ThrottlingException: Type[BotocoreClientError]
    UnauthorizedException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]

class BedrockAgentCoreControlPlaneFrontingLayerClient(AioBaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control.html#BedrockAgentCoreControlPlaneFrontingLayer.Client)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        BedrockAgentCoreControlPlaneFrontingLayerClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control.html#BedrockAgentCoreControlPlaneFrontingLayer.Client)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#exceptions)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/can_paginate.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#can_paginate)
        """

    async def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/generate_presigned_url.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#generate_presigned_url)
        """

    async def create_agent_runtime(
        self, **kwargs: Unpack[CreateAgentRuntimeRequestTypeDef]
    ) -> CreateAgentRuntimeResponseTypeDef:
        """
        Creates an Amazon Bedrock AgentCore Runtime.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/create_agent_runtime.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#create_agent_runtime)
        """

    async def create_agent_runtime_endpoint(
        self, **kwargs: Unpack[CreateAgentRuntimeEndpointRequestTypeDef]
    ) -> CreateAgentRuntimeEndpointResponseTypeDef:
        """
        Creates an AgentCore Runtime endpoint.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/create_agent_runtime_endpoint.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#create_agent_runtime_endpoint)
        """

    async def create_api_key_credential_provider(
        self, **kwargs: Unpack[CreateApiKeyCredentialProviderRequestTypeDef]
    ) -> CreateApiKeyCredentialProviderResponseTypeDef:
        """
        Creates a new API key credential provider.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/create_api_key_credential_provider.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#create_api_key_credential_provider)
        """

    async def create_browser(
        self, **kwargs: Unpack[CreateBrowserRequestTypeDef]
    ) -> CreateBrowserResponseTypeDef:
        """
        Creates a custom browser.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/create_browser.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#create_browser)
        """

    async def create_code_interpreter(
        self, **kwargs: Unpack[CreateCodeInterpreterRequestTypeDef]
    ) -> CreateCodeInterpreterResponseTypeDef:
        """
        Creates a custom code interpreter.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/create_code_interpreter.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#create_code_interpreter)
        """

    async def create_gateway(
        self, **kwargs: Unpack[CreateGatewayRequestTypeDef]
    ) -> CreateGatewayResponseTypeDef:
        """
        Creates a gateway for Amazon Bedrock Agent.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/create_gateway.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#create_gateway)
        """

    async def create_gateway_target(
        self, **kwargs: Unpack[CreateGatewayTargetRequestTypeDef]
    ) -> CreateGatewayTargetResponseTypeDef:
        """
        Creates a target for a gateway.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/create_gateway_target.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#create_gateway_target)
        """

    async def create_memory(
        self, **kwargs: Unpack[CreateMemoryInputTypeDef]
    ) -> CreateMemoryOutputTypeDef:
        """
        Creates a new Amazon Bedrock AgentCore Memory resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/create_memory.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#create_memory)
        """

    async def create_oauth2_credential_provider(
        self, **kwargs: Unpack[CreateOauth2CredentialProviderRequestTypeDef]
    ) -> CreateOauth2CredentialProviderResponseTypeDef:
        """
        Creates a new OAuth2 credential provider.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/create_oauth2_credential_provider.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#create_oauth2_credential_provider)
        """

    async def create_workload_identity(
        self, **kwargs: Unpack[CreateWorkloadIdentityRequestTypeDef]
    ) -> CreateWorkloadIdentityResponseTypeDef:
        """
        Creates a new workload identity.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/create_workload_identity.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#create_workload_identity)
        """

    async def delete_agent_runtime(
        self, **kwargs: Unpack[DeleteAgentRuntimeRequestTypeDef]
    ) -> DeleteAgentRuntimeResponseTypeDef:
        """
        Deletes an Amazon Bedrock AgentCore Runtime.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/delete_agent_runtime.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#delete_agent_runtime)
        """

    async def delete_agent_runtime_endpoint(
        self, **kwargs: Unpack[DeleteAgentRuntimeEndpointRequestTypeDef]
    ) -> DeleteAgentRuntimeEndpointResponseTypeDef:
        """
        Deletes an AAgentCore Runtime endpoint.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/delete_agent_runtime_endpoint.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#delete_agent_runtime_endpoint)
        """

    async def delete_api_key_credential_provider(
        self, **kwargs: Unpack[DeleteApiKeyCredentialProviderRequestTypeDef]
    ) -> Dict[str, Any]:
        """
        Deletes an API key credential provider.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/delete_api_key_credential_provider.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#delete_api_key_credential_provider)
        """

    async def delete_browser(
        self, **kwargs: Unpack[DeleteBrowserRequestTypeDef]
    ) -> DeleteBrowserResponseTypeDef:
        """
        Deletes a custom browser.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/delete_browser.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#delete_browser)
        """

    async def delete_code_interpreter(
        self, **kwargs: Unpack[DeleteCodeInterpreterRequestTypeDef]
    ) -> DeleteCodeInterpreterResponseTypeDef:
        """
        Deletes a custom code interpreter.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/delete_code_interpreter.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#delete_code_interpreter)
        """

    async def delete_gateway(
        self, **kwargs: Unpack[DeleteGatewayRequestTypeDef]
    ) -> DeleteGatewayResponseTypeDef:
        """
        Deletes a gateway.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/delete_gateway.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#delete_gateway)
        """

    async def delete_gateway_target(
        self, **kwargs: Unpack[DeleteGatewayTargetRequestTypeDef]
    ) -> DeleteGatewayTargetResponseTypeDef:
        """
        Deletes a gateway target.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/delete_gateway_target.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#delete_gateway_target)
        """

    async def delete_memory(
        self, **kwargs: Unpack[DeleteMemoryInputTypeDef]
    ) -> DeleteMemoryOutputTypeDef:
        """
        Deletes an Amazon Bedrock AgentCore Memory resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/delete_memory.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#delete_memory)
        """

    async def delete_oauth2_credential_provider(
        self, **kwargs: Unpack[DeleteOauth2CredentialProviderRequestTypeDef]
    ) -> Dict[str, Any]:
        """
        Deletes an OAuth2 credential provider.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/delete_oauth2_credential_provider.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#delete_oauth2_credential_provider)
        """

    async def delete_workload_identity(
        self, **kwargs: Unpack[DeleteWorkloadIdentityRequestTypeDef]
    ) -> Dict[str, Any]:
        """
        Deletes a workload identity.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/delete_workload_identity.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#delete_workload_identity)
        """

    async def get_agent_runtime(
        self, **kwargs: Unpack[GetAgentRuntimeRequestTypeDef]
    ) -> GetAgentRuntimeResponseTypeDef:
        """
        Gets an Amazon Bedrock AgentCore Runtime.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_agent_runtime.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_agent_runtime)
        """

    async def get_agent_runtime_endpoint(
        self, **kwargs: Unpack[GetAgentRuntimeEndpointRequestTypeDef]
    ) -> GetAgentRuntimeEndpointResponseTypeDef:
        """
        Gets information about an Amazon Secure AgentEndpoint.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_agent_runtime_endpoint.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_agent_runtime_endpoint)
        """

    async def get_api_key_credential_provider(
        self, **kwargs: Unpack[GetApiKeyCredentialProviderRequestTypeDef]
    ) -> GetApiKeyCredentialProviderResponseTypeDef:
        """
        Retrieves information about an API key credential provider.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_api_key_credential_provider.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_api_key_credential_provider)
        """

    async def get_browser(
        self, **kwargs: Unpack[GetBrowserRequestTypeDef]
    ) -> GetBrowserResponseTypeDef:
        """
        Gets information about a custom browser.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_browser.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_browser)
        """

    async def get_code_interpreter(
        self, **kwargs: Unpack[GetCodeInterpreterRequestTypeDef]
    ) -> GetCodeInterpreterResponseTypeDef:
        """
        Gets information about a custom code interpreter.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_code_interpreter.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_code_interpreter)
        """

    async def get_gateway(
        self, **kwargs: Unpack[GetGatewayRequestTypeDef]
    ) -> GetGatewayResponseTypeDef:
        """
        Retrieves information about a specific Gateway.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_gateway.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_gateway)
        """

    async def get_gateway_target(
        self, **kwargs: Unpack[GetGatewayTargetRequestTypeDef]
    ) -> GetGatewayTargetResponseTypeDef:
        """
        Retrieves information about a specific gateway target.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_gateway_target.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_gateway_target)
        """

    async def get_memory(self, **kwargs: Unpack[GetMemoryInputTypeDef]) -> GetMemoryOutputTypeDef:
        """
        Retrieve an existing Amazon Bedrock AgentCore Memory resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_memory.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_memory)
        """

    async def get_oauth2_credential_provider(
        self, **kwargs: Unpack[GetOauth2CredentialProviderRequestTypeDef]
    ) -> GetOauth2CredentialProviderResponseTypeDef:
        """
        Retrieves information about an OAuth2 credential provider.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_oauth2_credential_provider.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_oauth2_credential_provider)
        """

    async def get_token_vault(
        self, **kwargs: Unpack[GetTokenVaultRequestTypeDef]
    ) -> GetTokenVaultResponseTypeDef:
        """
        Retrieves information about a token vault.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_token_vault.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_token_vault)
        """

    async def get_workload_identity(
        self, **kwargs: Unpack[GetWorkloadIdentityRequestTypeDef]
    ) -> GetWorkloadIdentityResponseTypeDef:
        """
        Retrieves information about a workload identity.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_workload_identity.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_workload_identity)
        """

    async def list_agent_runtime_endpoints(
        self, **kwargs: Unpack[ListAgentRuntimeEndpointsRequestTypeDef]
    ) -> ListAgentRuntimeEndpointsResponseTypeDef:
        """
        Lists all endpoints for a specific Amazon Secure Agent.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/list_agent_runtime_endpoints.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#list_agent_runtime_endpoints)
        """

    async def list_agent_runtime_versions(
        self, **kwargs: Unpack[ListAgentRuntimeVersionsRequestTypeDef]
    ) -> ListAgentRuntimeVersionsResponseTypeDef:
        """
        Lists all versions of a specific Amazon Secure Agent.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/list_agent_runtime_versions.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#list_agent_runtime_versions)
        """

    async def list_agent_runtimes(
        self, **kwargs: Unpack[ListAgentRuntimesRequestTypeDef]
    ) -> ListAgentRuntimesResponseTypeDef:
        """
        Lists all Amazon Secure Agents in your account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/list_agent_runtimes.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#list_agent_runtimes)
        """

    async def list_api_key_credential_providers(
        self, **kwargs: Unpack[ListApiKeyCredentialProvidersRequestTypeDef]
    ) -> ListApiKeyCredentialProvidersResponseTypeDef:
        """
        Lists all API key credential providers in your account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/list_api_key_credential_providers.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#list_api_key_credential_providers)
        """

    async def list_browsers(
        self, **kwargs: Unpack[ListBrowsersRequestTypeDef]
    ) -> ListBrowsersResponseTypeDef:
        """
        Lists all custom browsers in your account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/list_browsers.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#list_browsers)
        """

    async def list_code_interpreters(
        self, **kwargs: Unpack[ListCodeInterpretersRequestTypeDef]
    ) -> ListCodeInterpretersResponseTypeDef:
        """
        Lists all custom code interpreters in your account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/list_code_interpreters.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#list_code_interpreters)
        """

    async def list_gateway_targets(
        self, **kwargs: Unpack[ListGatewayTargetsRequestTypeDef]
    ) -> ListGatewayTargetsResponseTypeDef:
        """
        Lists all targets for a specific gateway.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/list_gateway_targets.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#list_gateway_targets)
        """

    async def list_gateways(
        self, **kwargs: Unpack[ListGatewaysRequestTypeDef]
    ) -> ListGatewaysResponseTypeDef:
        """
        Lists all gateways in the account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/list_gateways.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#list_gateways)
        """

    async def list_memories(
        self, **kwargs: Unpack[ListMemoriesInputTypeDef]
    ) -> ListMemoriesOutputTypeDef:
        """
        Lists the available Amazon Bedrock AgentCore Memory resources in the current
        Amazon Web Services Region.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/list_memories.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#list_memories)
        """

    async def list_oauth2_credential_providers(
        self, **kwargs: Unpack[ListOauth2CredentialProvidersRequestTypeDef]
    ) -> ListOauth2CredentialProvidersResponseTypeDef:
        """
        Lists all OAuth2 credential providers in your account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/list_oauth2_credential_providers.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#list_oauth2_credential_providers)
        """

    async def list_tags_for_resource(
        self, **kwargs: Unpack[ListTagsForResourceRequestTypeDef]
    ) -> ListTagsForResourceResponseTypeDef:
        """
        Lists the tags associated with the specified resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/list_tags_for_resource.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#list_tags_for_resource)
        """

    async def list_workload_identities(
        self, **kwargs: Unpack[ListWorkloadIdentitiesRequestTypeDef]
    ) -> ListWorkloadIdentitiesResponseTypeDef:
        """
        Lists all workload identities in your account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/list_workload_identities.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#list_workload_identities)
        """

    async def set_token_vault_cmk(
        self, **kwargs: Unpack[SetTokenVaultCMKRequestTypeDef]
    ) -> SetTokenVaultCMKResponseTypeDef:
        """
        Sets the customer master key (CMK) for a token vault.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/set_token_vault_cmk.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#set_token_vault_cmk)
        """

    async def tag_resource(self, **kwargs: Unpack[TagResourceRequestTypeDef]) -> Dict[str, Any]:
        """
        Associates the specified tags to a resource with the specified resourceArn.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/tag_resource.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#tag_resource)
        """

    async def untag_resource(self, **kwargs: Unpack[UntagResourceRequestTypeDef]) -> Dict[str, Any]:
        """
        Removes the specified tags from the specified resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/untag_resource.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#untag_resource)
        """

    async def update_agent_runtime(
        self, **kwargs: Unpack[UpdateAgentRuntimeRequestTypeDef]
    ) -> UpdateAgentRuntimeResponseTypeDef:
        """
        Updates an existing Amazon Secure Agent.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/update_agent_runtime.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#update_agent_runtime)
        """

    async def update_agent_runtime_endpoint(
        self, **kwargs: Unpack[UpdateAgentRuntimeEndpointRequestTypeDef]
    ) -> UpdateAgentRuntimeEndpointResponseTypeDef:
        """
        Updates an existing Amazon Bedrock AgentCore Runtime endpoint.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/update_agent_runtime_endpoint.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#update_agent_runtime_endpoint)
        """

    async def update_api_key_credential_provider(
        self, **kwargs: Unpack[UpdateApiKeyCredentialProviderRequestTypeDef]
    ) -> UpdateApiKeyCredentialProviderResponseTypeDef:
        """
        Updates an existing API key credential provider.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/update_api_key_credential_provider.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#update_api_key_credential_provider)
        """

    async def update_gateway(
        self, **kwargs: Unpack[UpdateGatewayRequestTypeDef]
    ) -> UpdateGatewayResponseTypeDef:
        """
        Updates an existing gateway.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/update_gateway.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#update_gateway)
        """

    async def update_gateway_target(
        self, **kwargs: Unpack[UpdateGatewayTargetRequestTypeDef]
    ) -> UpdateGatewayTargetResponseTypeDef:
        """
        Updates an existing gateway target.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/update_gateway_target.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#update_gateway_target)
        """

    async def update_memory(
        self, **kwargs: Unpack[UpdateMemoryInputTypeDef]
    ) -> UpdateMemoryOutputTypeDef:
        """
        Update an Amazon Bedrock AgentCore Memory resource memory.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/update_memory.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#update_memory)
        """

    async def update_oauth2_credential_provider(
        self, **kwargs: Unpack[UpdateOauth2CredentialProviderRequestTypeDef]
    ) -> UpdateOauth2CredentialProviderResponseTypeDef:
        """
        Updates an existing OAuth2 credential provider.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/update_oauth2_credential_provider.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#update_oauth2_credential_provider)
        """

    async def update_workload_identity(
        self, **kwargs: Unpack[UpdateWorkloadIdentityRequestTypeDef]
    ) -> UpdateWorkloadIdentityResponseTypeDef:
        """
        Updates an existing workload identity.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/update_workload_identity.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#update_workload_identity)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_agent_runtime_endpoints"]
    ) -> ListAgentRuntimeEndpointsPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_agent_runtime_versions"]
    ) -> ListAgentRuntimeVersionsPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_agent_runtimes"]
    ) -> ListAgentRuntimesPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_api_key_credential_providers"]
    ) -> ListApiKeyCredentialProvidersPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_browsers"]
    ) -> ListBrowsersPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_code_interpreters"]
    ) -> ListCodeInterpretersPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_gateway_targets"]
    ) -> ListGatewayTargetsPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_gateways"]
    ) -> ListGatewaysPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_memories"]
    ) -> ListMemoriesPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_oauth2_credential_providers"]
    ) -> ListOauth2CredentialProvidersPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_workload_identities"]
    ) -> ListWorkloadIdentitiesPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_paginator)
        """

    def get_waiter(  # type: ignore[override]
        self, waiter_name: Literal["memory_created"]
    ) -> MemoryCreatedWaiter:
        """
        Returns an object that can wait for some condition.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control/client/get_waiter.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/#get_waiter)
        """

    async def __aenter__(self) -> Self:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control.html#BedrockAgentCoreControlPlaneFrontingLayer.Client)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/)
        """

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agentcore-control.html#BedrockAgentCoreControlPlaneFrontingLayer.Client)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_bedrock_agentcore_control/client/)
        """
