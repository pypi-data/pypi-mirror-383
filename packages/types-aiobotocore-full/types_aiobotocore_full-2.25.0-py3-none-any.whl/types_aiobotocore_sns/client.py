"""
Type annotations for sns service Client.

[Documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from aiobotocore.session import get_session
    from types_aiobotocore_sns.client import SNSClient

    session = get_session()
    async with session.create_client("sns") as client:
        client: SNSClient
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
    ListEndpointsByPlatformApplicationPaginator,
    ListOriginationNumbersPaginator,
    ListPhoneNumbersOptedOutPaginator,
    ListPlatformApplicationsPaginator,
    ListSMSSandboxPhoneNumbersPaginator,
    ListSubscriptionsByTopicPaginator,
    ListSubscriptionsPaginator,
    ListTopicsPaginator,
)
from .type_defs import (
    AddPermissionInputTypeDef,
    CheckIfPhoneNumberIsOptedOutInputTypeDef,
    CheckIfPhoneNumberIsOptedOutResponseTypeDef,
    ConfirmSubscriptionInputTypeDef,
    ConfirmSubscriptionResponseTypeDef,
    CreateEndpointResponseTypeDef,
    CreatePlatformApplicationInputTypeDef,
    CreatePlatformApplicationResponseTypeDef,
    CreatePlatformEndpointInputTypeDef,
    CreateSMSSandboxPhoneNumberInputTypeDef,
    CreateTopicInputTypeDef,
    CreateTopicResponseTypeDef,
    DeleteEndpointInputTypeDef,
    DeletePlatformApplicationInputTypeDef,
    DeleteSMSSandboxPhoneNumberInputTypeDef,
    DeleteTopicInputTypeDef,
    EmptyResponseMetadataTypeDef,
    GetDataProtectionPolicyInputTypeDef,
    GetDataProtectionPolicyResponseTypeDef,
    GetEndpointAttributesInputTypeDef,
    GetEndpointAttributesResponseTypeDef,
    GetPlatformApplicationAttributesInputTypeDef,
    GetPlatformApplicationAttributesResponseTypeDef,
    GetSMSAttributesInputTypeDef,
    GetSMSAttributesResponseTypeDef,
    GetSMSSandboxAccountStatusResultTypeDef,
    GetSubscriptionAttributesInputTypeDef,
    GetSubscriptionAttributesResponseTypeDef,
    GetTopicAttributesInputTypeDef,
    GetTopicAttributesResponseTypeDef,
    ListEndpointsByPlatformApplicationInputTypeDef,
    ListEndpointsByPlatformApplicationResponseTypeDef,
    ListOriginationNumbersRequestTypeDef,
    ListOriginationNumbersResultTypeDef,
    ListPhoneNumbersOptedOutInputTypeDef,
    ListPhoneNumbersOptedOutResponseTypeDef,
    ListPlatformApplicationsInputTypeDef,
    ListPlatformApplicationsResponseTypeDef,
    ListSMSSandboxPhoneNumbersInputTypeDef,
    ListSMSSandboxPhoneNumbersResultTypeDef,
    ListSubscriptionsByTopicInputTypeDef,
    ListSubscriptionsByTopicResponseTypeDef,
    ListSubscriptionsInputTypeDef,
    ListSubscriptionsResponseTypeDef,
    ListTagsForResourceRequestTypeDef,
    ListTagsForResourceResponseTypeDef,
    ListTopicsInputTypeDef,
    ListTopicsResponseTypeDef,
    OptInPhoneNumberInputTypeDef,
    PublishBatchInputTypeDef,
    PublishBatchResponseTypeDef,
    PublishInputTypeDef,
    PublishResponseTypeDef,
    PutDataProtectionPolicyInputTypeDef,
    RemovePermissionInputTypeDef,
    SetEndpointAttributesInputTypeDef,
    SetPlatformApplicationAttributesInputTypeDef,
    SetSMSAttributesInputTypeDef,
    SetSubscriptionAttributesInputTypeDef,
    SetTopicAttributesInputTypeDef,
    SubscribeInputTypeDef,
    SubscribeResponseTypeDef,
    TagResourceRequestTypeDef,
    UnsubscribeInputTypeDef,
    UntagResourceRequestTypeDef,
    VerifySMSSandboxPhoneNumberInputTypeDef,
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


__all__ = ("SNSClient",)


class Exceptions(BaseClientExceptions):
    AuthorizationErrorException: Type[BotocoreClientError]
    BatchEntryIdsNotDistinctException: Type[BotocoreClientError]
    BatchRequestTooLongException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConcurrentAccessException: Type[BotocoreClientError]
    EmptyBatchRequestException: Type[BotocoreClientError]
    EndpointDisabledException: Type[BotocoreClientError]
    FilterPolicyLimitExceededException: Type[BotocoreClientError]
    InternalErrorException: Type[BotocoreClientError]
    InvalidBatchEntryIdException: Type[BotocoreClientError]
    InvalidParameterException: Type[BotocoreClientError]
    InvalidParameterValueException: Type[BotocoreClientError]
    InvalidSecurityException: Type[BotocoreClientError]
    InvalidStateException: Type[BotocoreClientError]
    KMSAccessDeniedException: Type[BotocoreClientError]
    KMSDisabledException: Type[BotocoreClientError]
    KMSInvalidStateException: Type[BotocoreClientError]
    KMSNotFoundException: Type[BotocoreClientError]
    KMSOptInRequired: Type[BotocoreClientError]
    KMSThrottlingException: Type[BotocoreClientError]
    NotFoundException: Type[BotocoreClientError]
    OptedOutException: Type[BotocoreClientError]
    PlatformApplicationDisabledException: Type[BotocoreClientError]
    ReplayLimitExceededException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    StaleTagException: Type[BotocoreClientError]
    SubscriptionLimitExceededException: Type[BotocoreClientError]
    TagLimitExceededException: Type[BotocoreClientError]
    TagPolicyException: Type[BotocoreClientError]
    ThrottledException: Type[BotocoreClientError]
    TooManyEntriesInBatchRequestException: Type[BotocoreClientError]
    TopicLimitExceededException: Type[BotocoreClientError]
    UserErrorException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]
    VerificationException: Type[BotocoreClientError]


class SNSClient(AioBaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        SNSClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#exceptions)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/can_paginate.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#can_paginate)
        """

    async def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/generate_presigned_url.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#generate_presigned_url)
        """

    async def add_permission(
        self, **kwargs: Unpack[AddPermissionInputTypeDef]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Adds a statement to a topic's access control policy, granting access for the
        specified Amazon Web Services accounts to the specified actions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/add_permission.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#add_permission)
        """

    async def check_if_phone_number_is_opted_out(
        self, **kwargs: Unpack[CheckIfPhoneNumberIsOptedOutInputTypeDef]
    ) -> CheckIfPhoneNumberIsOptedOutResponseTypeDef:
        """
        Accepts a phone number and indicates whether the phone holder has opted out of
        receiving SMS messages from your Amazon Web Services account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/check_if_phone_number_is_opted_out.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#check_if_phone_number_is_opted_out)
        """

    async def confirm_subscription(
        self, **kwargs: Unpack[ConfirmSubscriptionInputTypeDef]
    ) -> ConfirmSubscriptionResponseTypeDef:
        """
        Verifies an endpoint owner's intent to receive messages by validating the token
        sent to the endpoint by an earlier <code>Subscribe</code> action.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/confirm_subscription.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#confirm_subscription)
        """

    async def create_platform_application(
        self, **kwargs: Unpack[CreatePlatformApplicationInputTypeDef]
    ) -> CreatePlatformApplicationResponseTypeDef:
        """
        Creates a platform application object for one of the supported push
        notification services, such as APNS and GCM (Firebase Cloud Messaging), to
        which devices and mobile apps may register.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/create_platform_application.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#create_platform_application)
        """

    async def create_platform_endpoint(
        self, **kwargs: Unpack[CreatePlatformEndpointInputTypeDef]
    ) -> CreateEndpointResponseTypeDef:
        """
        Creates an endpoint for a device and mobile app on one of the supported push
        notification services, such as GCM (Firebase Cloud Messaging) and APNS.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/create_platform_endpoint.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#create_platform_endpoint)
        """

    async def create_sms_sandbox_phone_number(
        self, **kwargs: Unpack[CreateSMSSandboxPhoneNumberInputTypeDef]
    ) -> Dict[str, Any]:
        """
        Adds a destination phone number to an Amazon Web Services account in the SMS
        sandbox and sends a one-time password (OTP) to that phone number.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/create_sms_sandbox_phone_number.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#create_sms_sandbox_phone_number)
        """

    async def create_topic(
        self, **kwargs: Unpack[CreateTopicInputTypeDef]
    ) -> CreateTopicResponseTypeDef:
        """
        Creates a topic to which notifications can be published.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/create_topic.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#create_topic)
        """

    async def delete_endpoint(
        self, **kwargs: Unpack[DeleteEndpointInputTypeDef]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes the endpoint for a device and mobile app from Amazon SNS.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/delete_endpoint.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#delete_endpoint)
        """

    async def delete_platform_application(
        self, **kwargs: Unpack[DeletePlatformApplicationInputTypeDef]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes a platform application object for one of the supported push
        notification services, such as APNS and GCM (Firebase Cloud Messaging).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/delete_platform_application.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#delete_platform_application)
        """

    async def delete_sms_sandbox_phone_number(
        self, **kwargs: Unpack[DeleteSMSSandboxPhoneNumberInputTypeDef]
    ) -> Dict[str, Any]:
        """
        Deletes an Amazon Web Services account's verified or pending phone number from
        the SMS sandbox.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/delete_sms_sandbox_phone_number.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#delete_sms_sandbox_phone_number)
        """

    async def delete_topic(
        self, **kwargs: Unpack[DeleteTopicInputTypeDef]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes a topic and all its subscriptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/delete_topic.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#delete_topic)
        """

    async def get_data_protection_policy(
        self, **kwargs: Unpack[GetDataProtectionPolicyInputTypeDef]
    ) -> GetDataProtectionPolicyResponseTypeDef:
        """
        Retrieves the specified inline <code>DataProtectionPolicy</code> document that
        is stored in the specified Amazon SNS topic.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_data_protection_policy.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_data_protection_policy)
        """

    async def get_endpoint_attributes(
        self, **kwargs: Unpack[GetEndpointAttributesInputTypeDef]
    ) -> GetEndpointAttributesResponseTypeDef:
        """
        Retrieves the endpoint attributes for a device on one of the supported push
        notification services, such as GCM (Firebase Cloud Messaging) and APNS.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_endpoint_attributes.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_endpoint_attributes)
        """

    async def get_platform_application_attributes(
        self, **kwargs: Unpack[GetPlatformApplicationAttributesInputTypeDef]
    ) -> GetPlatformApplicationAttributesResponseTypeDef:
        """
        Retrieves the attributes of the platform application object for the supported
        push notification services, such as APNS and GCM (Firebase Cloud Messaging).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_platform_application_attributes.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_platform_application_attributes)
        """

    async def get_sms_attributes(
        self, **kwargs: Unpack[GetSMSAttributesInputTypeDef]
    ) -> GetSMSAttributesResponseTypeDef:
        """
        Returns the settings for sending SMS messages from your Amazon Web Services
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_sms_attributes.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_sms_attributes)
        """

    async def get_sms_sandbox_account_status(self) -> GetSMSSandboxAccountStatusResultTypeDef:
        """
        Retrieves the SMS sandbox status for the calling Amazon Web Services account in
        the target Amazon Web Services Region.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_sms_sandbox_account_status.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_sms_sandbox_account_status)
        """

    async def get_subscription_attributes(
        self, **kwargs: Unpack[GetSubscriptionAttributesInputTypeDef]
    ) -> GetSubscriptionAttributesResponseTypeDef:
        """
        Returns all of the properties of a subscription.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_subscription_attributes.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_subscription_attributes)
        """

    async def get_topic_attributes(
        self, **kwargs: Unpack[GetTopicAttributesInputTypeDef]
    ) -> GetTopicAttributesResponseTypeDef:
        """
        Returns all of the properties of a topic.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_topic_attributes.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_topic_attributes)
        """

    async def list_endpoints_by_platform_application(
        self, **kwargs: Unpack[ListEndpointsByPlatformApplicationInputTypeDef]
    ) -> ListEndpointsByPlatformApplicationResponseTypeDef:
        """
        Lists the endpoints and endpoint attributes for devices in a supported push
        notification service, such as GCM (Firebase Cloud Messaging) and APNS.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/list_endpoints_by_platform_application.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#list_endpoints_by_platform_application)
        """

    async def list_origination_numbers(
        self, **kwargs: Unpack[ListOriginationNumbersRequestTypeDef]
    ) -> ListOriginationNumbersResultTypeDef:
        """
        Lists the calling Amazon Web Services account's dedicated origination numbers
        and their metadata.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/list_origination_numbers.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#list_origination_numbers)
        """

    async def list_phone_numbers_opted_out(
        self, **kwargs: Unpack[ListPhoneNumbersOptedOutInputTypeDef]
    ) -> ListPhoneNumbersOptedOutResponseTypeDef:
        """
        Returns a list of phone numbers that are opted out, meaning you cannot send SMS
        messages to them.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/list_phone_numbers_opted_out.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#list_phone_numbers_opted_out)
        """

    async def list_platform_applications(
        self, **kwargs: Unpack[ListPlatformApplicationsInputTypeDef]
    ) -> ListPlatformApplicationsResponseTypeDef:
        """
        Lists the platform application objects for the supported push notification
        services, such as APNS and GCM (Firebase Cloud Messaging).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/list_platform_applications.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#list_platform_applications)
        """

    async def list_sms_sandbox_phone_numbers(
        self, **kwargs: Unpack[ListSMSSandboxPhoneNumbersInputTypeDef]
    ) -> ListSMSSandboxPhoneNumbersResultTypeDef:
        """
        Lists the calling Amazon Web Services account's current verified and pending
        destination phone numbers in the SMS sandbox.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/list_sms_sandbox_phone_numbers.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#list_sms_sandbox_phone_numbers)
        """

    async def list_subscriptions(
        self, **kwargs: Unpack[ListSubscriptionsInputTypeDef]
    ) -> ListSubscriptionsResponseTypeDef:
        """
        Returns a list of the requester's subscriptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/list_subscriptions.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#list_subscriptions)
        """

    async def list_subscriptions_by_topic(
        self, **kwargs: Unpack[ListSubscriptionsByTopicInputTypeDef]
    ) -> ListSubscriptionsByTopicResponseTypeDef:
        """
        Returns a list of the subscriptions to a specific topic.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/list_subscriptions_by_topic.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#list_subscriptions_by_topic)
        """

    async def list_tags_for_resource(
        self, **kwargs: Unpack[ListTagsForResourceRequestTypeDef]
    ) -> ListTagsForResourceResponseTypeDef:
        """
        List all tags added to the specified Amazon SNS topic.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/list_tags_for_resource.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#list_tags_for_resource)
        """

    async def list_topics(
        self, **kwargs: Unpack[ListTopicsInputTypeDef]
    ) -> ListTopicsResponseTypeDef:
        """
        Returns a list of the requester's topics.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/list_topics.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#list_topics)
        """

    async def opt_in_phone_number(
        self, **kwargs: Unpack[OptInPhoneNumberInputTypeDef]
    ) -> Dict[str, Any]:
        """
        Use this request to opt in a phone number that is opted out, which enables you
        to resume sending SMS messages to the number.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/opt_in_phone_number.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#opt_in_phone_number)
        """

    async def publish(self, **kwargs: Unpack[PublishInputTypeDef]) -> PublishResponseTypeDef:
        """
        Sends a message to an Amazon SNS topic, a text message (SMS message) directly
        to a phone number, or a message to a mobile platform endpoint (when you specify
        the <code>TargetArn</code>).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/publish.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#publish)
        """

    async def publish_batch(
        self, **kwargs: Unpack[PublishBatchInputTypeDef]
    ) -> PublishBatchResponseTypeDef:
        """
        Publishes up to 10 messages to the specified topic in a single batch.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/publish_batch.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#publish_batch)
        """

    async def put_data_protection_policy(
        self, **kwargs: Unpack[PutDataProtectionPolicyInputTypeDef]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Adds or updates an inline policy document that is stored in the specified
        Amazon SNS topic.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/put_data_protection_policy.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#put_data_protection_policy)
        """

    async def remove_permission(
        self, **kwargs: Unpack[RemovePermissionInputTypeDef]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Removes a statement from a topic's access control policy.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/remove_permission.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#remove_permission)
        """

    async def set_endpoint_attributes(
        self, **kwargs: Unpack[SetEndpointAttributesInputTypeDef]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Sets the attributes for an endpoint for a device on one of the supported push
        notification services, such as GCM (Firebase Cloud Messaging) and APNS.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/set_endpoint_attributes.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#set_endpoint_attributes)
        """

    async def set_platform_application_attributes(
        self, **kwargs: Unpack[SetPlatformApplicationAttributesInputTypeDef]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Sets the attributes of the platform application object for the supported push
        notification services, such as APNS and GCM (Firebase Cloud Messaging).

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/set_platform_application_attributes.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#set_platform_application_attributes)
        """

    async def set_sms_attributes(
        self, **kwargs: Unpack[SetSMSAttributesInputTypeDef]
    ) -> Dict[str, Any]:
        """
        Use this request to set the default settings for sending SMS messages and
        receiving daily SMS usage reports.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/set_sms_attributes.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#set_sms_attributes)
        """

    async def set_subscription_attributes(
        self, **kwargs: Unpack[SetSubscriptionAttributesInputTypeDef]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Allows a subscription owner to set an attribute of the subscription to a new
        value.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/set_subscription_attributes.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#set_subscription_attributes)
        """

    async def set_topic_attributes(
        self, **kwargs: Unpack[SetTopicAttributesInputTypeDef]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Allows a topic owner to set an attribute of the topic to a new value.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/set_topic_attributes.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#set_topic_attributes)
        """

    async def subscribe(self, **kwargs: Unpack[SubscribeInputTypeDef]) -> SubscribeResponseTypeDef:
        """
        Subscribes an endpoint to an Amazon SNS topic.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/subscribe.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#subscribe)
        """

    async def tag_resource(self, **kwargs: Unpack[TagResourceRequestTypeDef]) -> Dict[str, Any]:
        """
        Add tags to the specified Amazon SNS topic.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/tag_resource.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#tag_resource)
        """

    async def unsubscribe(
        self, **kwargs: Unpack[UnsubscribeInputTypeDef]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes a subscription.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/unsubscribe.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#unsubscribe)
        """

    async def untag_resource(self, **kwargs: Unpack[UntagResourceRequestTypeDef]) -> Dict[str, Any]:
        """
        Remove tags from the specified Amazon SNS topic.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/untag_resource.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#untag_resource)
        """

    async def verify_sms_sandbox_phone_number(
        self, **kwargs: Unpack[VerifySMSSandboxPhoneNumberInputTypeDef]
    ) -> Dict[str, Any]:
        """
        Verifies a destination phone number with a one-time password (OTP) for the
        calling Amazon Web Services account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/verify_sms_sandbox_phone_number.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#verify_sms_sandbox_phone_number)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_endpoints_by_platform_application"]
    ) -> ListEndpointsByPlatformApplicationPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_origination_numbers"]
    ) -> ListOriginationNumbersPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_phone_numbers_opted_out"]
    ) -> ListPhoneNumbersOptedOutPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_platform_applications"]
    ) -> ListPlatformApplicationsPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_sms_sandbox_phone_numbers"]
    ) -> ListSMSSandboxPhoneNumbersPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_subscriptions_by_topic"]
    ) -> ListSubscriptionsByTopicPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_subscriptions"]
    ) -> ListSubscriptionsPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_paginator)
        """

    @overload  # type: ignore[override]
    def get_paginator(  # type: ignore[override]
        self, operation_name: Literal["list_topics"]
    ) -> ListTopicsPaginator:
        """
        Create a paginator for an operation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns/client/get_paginator.html)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/#get_paginator)
        """

    async def __aenter__(self) -> Self:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/)
        """

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_sns/client/)
        """
