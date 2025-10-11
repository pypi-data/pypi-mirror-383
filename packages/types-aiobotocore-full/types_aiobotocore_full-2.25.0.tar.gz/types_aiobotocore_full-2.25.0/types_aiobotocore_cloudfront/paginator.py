"""
Type annotations for cloudfront service client paginators.

[Documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from aiobotocore.session import get_session

    from types_aiobotocore_cloudfront.client import CloudFrontClient
    from types_aiobotocore_cloudfront.paginator import (
        ListCloudFrontOriginAccessIdentitiesPaginator,
        ListConnectionGroupsPaginator,
        ListDistributionTenantsByCustomizationPaginator,
        ListDistributionTenantsPaginator,
        ListDistributionsByConnectionModePaginator,
        ListDistributionsPaginator,
        ListDomainConflictsPaginator,
        ListInvalidationsForDistributionTenantPaginator,
        ListInvalidationsPaginator,
        ListKeyValueStoresPaginator,
        ListOriginAccessControlsPaginator,
        ListPublicKeysPaginator,
        ListStreamingDistributionsPaginator,
    )

    session = get_session()
    with session.create_client("cloudfront") as client:
        client: CloudFrontClient

        list_cloud_front_origin_access_identities_paginator: ListCloudFrontOriginAccessIdentitiesPaginator = client.get_paginator("list_cloud_front_origin_access_identities")
        list_connection_groups_paginator: ListConnectionGroupsPaginator = client.get_paginator("list_connection_groups")
        list_distribution_tenants_by_customization_paginator: ListDistributionTenantsByCustomizationPaginator = client.get_paginator("list_distribution_tenants_by_customization")
        list_distribution_tenants_paginator: ListDistributionTenantsPaginator = client.get_paginator("list_distribution_tenants")
        list_distributions_by_connection_mode_paginator: ListDistributionsByConnectionModePaginator = client.get_paginator("list_distributions_by_connection_mode")
        list_distributions_paginator: ListDistributionsPaginator = client.get_paginator("list_distributions")
        list_domain_conflicts_paginator: ListDomainConflictsPaginator = client.get_paginator("list_domain_conflicts")
        list_invalidations_for_distribution_tenant_paginator: ListInvalidationsForDistributionTenantPaginator = client.get_paginator("list_invalidations_for_distribution_tenant")
        list_invalidations_paginator: ListInvalidationsPaginator = client.get_paginator("list_invalidations")
        list_key_value_stores_paginator: ListKeyValueStoresPaginator = client.get_paginator("list_key_value_stores")
        list_origin_access_controls_paginator: ListOriginAccessControlsPaginator = client.get_paginator("list_origin_access_controls")
        list_public_keys_paginator: ListPublicKeysPaginator = client.get_paginator("list_public_keys")
        list_streaming_distributions_paginator: ListStreamingDistributionsPaginator = client.get_paginator("list_streaming_distributions")
    ```
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from aiobotocore.paginate import AioPageIterator, AioPaginator

from .type_defs import (
    ListCloudFrontOriginAccessIdentitiesRequestPaginateTypeDef,
    ListCloudFrontOriginAccessIdentitiesResultTypeDef,
    ListConnectionGroupsRequestPaginateTypeDef,
    ListConnectionGroupsResultTypeDef,
    ListDistributionsByConnectionModeRequestPaginateTypeDef,
    ListDistributionsByConnectionModeResultTypeDef,
    ListDistributionsRequestPaginateTypeDef,
    ListDistributionsResultTypeDef,
    ListDistributionTenantsByCustomizationRequestPaginateTypeDef,
    ListDistributionTenantsByCustomizationResultTypeDef,
    ListDistributionTenantsRequestPaginateTypeDef,
    ListDistributionTenantsResultTypeDef,
    ListDomainConflictsRequestPaginateTypeDef,
    ListDomainConflictsResultTypeDef,
    ListInvalidationsForDistributionTenantRequestPaginateTypeDef,
    ListInvalidationsForDistributionTenantResultTypeDef,
    ListInvalidationsRequestPaginateTypeDef,
    ListInvalidationsResultTypeDef,
    ListKeyValueStoresRequestPaginateTypeDef,
    ListKeyValueStoresResultTypeDef,
    ListOriginAccessControlsRequestPaginateTypeDef,
    ListOriginAccessControlsResultTypeDef,
    ListPublicKeysRequestPaginateTypeDef,
    ListPublicKeysResultTypeDef,
    ListStreamingDistributionsRequestPaginateTypeDef,
    ListStreamingDistributionsResultTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Unpack
else:
    from typing_extensions import Unpack


__all__ = (
    "ListCloudFrontOriginAccessIdentitiesPaginator",
    "ListConnectionGroupsPaginator",
    "ListDistributionTenantsByCustomizationPaginator",
    "ListDistributionTenantsPaginator",
    "ListDistributionsByConnectionModePaginator",
    "ListDistributionsPaginator",
    "ListDomainConflictsPaginator",
    "ListInvalidationsForDistributionTenantPaginator",
    "ListInvalidationsPaginator",
    "ListKeyValueStoresPaginator",
    "ListOriginAccessControlsPaginator",
    "ListPublicKeysPaginator",
    "ListStreamingDistributionsPaginator",
)


if TYPE_CHECKING:
    _ListCloudFrontOriginAccessIdentitiesPaginatorBase = AioPaginator[
        ListCloudFrontOriginAccessIdentitiesResultTypeDef
    ]
else:
    _ListCloudFrontOriginAccessIdentitiesPaginatorBase = AioPaginator  # type: ignore[assignment]


class ListCloudFrontOriginAccessIdentitiesPaginator(
    _ListCloudFrontOriginAccessIdentitiesPaginatorBase
):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListCloudFrontOriginAccessIdentities.html#CloudFront.Paginator.ListCloudFrontOriginAccessIdentities)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listcloudfrontoriginaccessidentitiespaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListCloudFrontOriginAccessIdentitiesRequestPaginateTypeDef]
    ) -> AioPageIterator[ListCloudFrontOriginAccessIdentitiesResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListCloudFrontOriginAccessIdentities.html#CloudFront.Paginator.ListCloudFrontOriginAccessIdentities.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listcloudfrontoriginaccessidentitiespaginator)
        """


if TYPE_CHECKING:
    _ListConnectionGroupsPaginatorBase = AioPaginator[ListConnectionGroupsResultTypeDef]
else:
    _ListConnectionGroupsPaginatorBase = AioPaginator  # type: ignore[assignment]


class ListConnectionGroupsPaginator(_ListConnectionGroupsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListConnectionGroups.html#CloudFront.Paginator.ListConnectionGroups)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listconnectiongroupspaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListConnectionGroupsRequestPaginateTypeDef]
    ) -> AioPageIterator[ListConnectionGroupsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListConnectionGroups.html#CloudFront.Paginator.ListConnectionGroups.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listconnectiongroupspaginator)
        """


if TYPE_CHECKING:
    _ListDistributionTenantsByCustomizationPaginatorBase = AioPaginator[
        ListDistributionTenantsByCustomizationResultTypeDef
    ]
else:
    _ListDistributionTenantsByCustomizationPaginatorBase = AioPaginator  # type: ignore[assignment]


class ListDistributionTenantsByCustomizationPaginator(
    _ListDistributionTenantsByCustomizationPaginatorBase
):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListDistributionTenantsByCustomization.html#CloudFront.Paginator.ListDistributionTenantsByCustomization)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listdistributiontenantsbycustomizationpaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListDistributionTenantsByCustomizationRequestPaginateTypeDef]
    ) -> AioPageIterator[ListDistributionTenantsByCustomizationResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListDistributionTenantsByCustomization.html#CloudFront.Paginator.ListDistributionTenantsByCustomization.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listdistributiontenantsbycustomizationpaginator)
        """


if TYPE_CHECKING:
    _ListDistributionTenantsPaginatorBase = AioPaginator[ListDistributionTenantsResultTypeDef]
else:
    _ListDistributionTenantsPaginatorBase = AioPaginator  # type: ignore[assignment]


class ListDistributionTenantsPaginator(_ListDistributionTenantsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListDistributionTenants.html#CloudFront.Paginator.ListDistributionTenants)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listdistributiontenantspaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListDistributionTenantsRequestPaginateTypeDef]
    ) -> AioPageIterator[ListDistributionTenantsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListDistributionTenants.html#CloudFront.Paginator.ListDistributionTenants.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listdistributiontenantspaginator)
        """


if TYPE_CHECKING:
    _ListDistributionsByConnectionModePaginatorBase = AioPaginator[
        ListDistributionsByConnectionModeResultTypeDef
    ]
else:
    _ListDistributionsByConnectionModePaginatorBase = AioPaginator  # type: ignore[assignment]


class ListDistributionsByConnectionModePaginator(_ListDistributionsByConnectionModePaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListDistributionsByConnectionMode.html#CloudFront.Paginator.ListDistributionsByConnectionMode)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listdistributionsbyconnectionmodepaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListDistributionsByConnectionModeRequestPaginateTypeDef]
    ) -> AioPageIterator[ListDistributionsByConnectionModeResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListDistributionsByConnectionMode.html#CloudFront.Paginator.ListDistributionsByConnectionMode.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listdistributionsbyconnectionmodepaginator)
        """


if TYPE_CHECKING:
    _ListDistributionsPaginatorBase = AioPaginator[ListDistributionsResultTypeDef]
else:
    _ListDistributionsPaginatorBase = AioPaginator  # type: ignore[assignment]


class ListDistributionsPaginator(_ListDistributionsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListDistributions.html#CloudFront.Paginator.ListDistributions)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listdistributionspaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListDistributionsRequestPaginateTypeDef]
    ) -> AioPageIterator[ListDistributionsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListDistributions.html#CloudFront.Paginator.ListDistributions.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listdistributionspaginator)
        """


if TYPE_CHECKING:
    _ListDomainConflictsPaginatorBase = AioPaginator[ListDomainConflictsResultTypeDef]
else:
    _ListDomainConflictsPaginatorBase = AioPaginator  # type: ignore[assignment]


class ListDomainConflictsPaginator(_ListDomainConflictsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListDomainConflicts.html#CloudFront.Paginator.ListDomainConflicts)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listdomainconflictspaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListDomainConflictsRequestPaginateTypeDef]
    ) -> AioPageIterator[ListDomainConflictsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListDomainConflicts.html#CloudFront.Paginator.ListDomainConflicts.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listdomainconflictspaginator)
        """


if TYPE_CHECKING:
    _ListInvalidationsForDistributionTenantPaginatorBase = AioPaginator[
        ListInvalidationsForDistributionTenantResultTypeDef
    ]
else:
    _ListInvalidationsForDistributionTenantPaginatorBase = AioPaginator  # type: ignore[assignment]


class ListInvalidationsForDistributionTenantPaginator(
    _ListInvalidationsForDistributionTenantPaginatorBase
):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListInvalidationsForDistributionTenant.html#CloudFront.Paginator.ListInvalidationsForDistributionTenant)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listinvalidationsfordistributiontenantpaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListInvalidationsForDistributionTenantRequestPaginateTypeDef]
    ) -> AioPageIterator[ListInvalidationsForDistributionTenantResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListInvalidationsForDistributionTenant.html#CloudFront.Paginator.ListInvalidationsForDistributionTenant.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listinvalidationsfordistributiontenantpaginator)
        """


if TYPE_CHECKING:
    _ListInvalidationsPaginatorBase = AioPaginator[ListInvalidationsResultTypeDef]
else:
    _ListInvalidationsPaginatorBase = AioPaginator  # type: ignore[assignment]


class ListInvalidationsPaginator(_ListInvalidationsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListInvalidations.html#CloudFront.Paginator.ListInvalidations)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listinvalidationspaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListInvalidationsRequestPaginateTypeDef]
    ) -> AioPageIterator[ListInvalidationsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListInvalidations.html#CloudFront.Paginator.ListInvalidations.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listinvalidationspaginator)
        """


if TYPE_CHECKING:
    _ListKeyValueStoresPaginatorBase = AioPaginator[ListKeyValueStoresResultTypeDef]
else:
    _ListKeyValueStoresPaginatorBase = AioPaginator  # type: ignore[assignment]


class ListKeyValueStoresPaginator(_ListKeyValueStoresPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListKeyValueStores.html#CloudFront.Paginator.ListKeyValueStores)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listkeyvaluestorespaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListKeyValueStoresRequestPaginateTypeDef]
    ) -> AioPageIterator[ListKeyValueStoresResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListKeyValueStores.html#CloudFront.Paginator.ListKeyValueStores.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listkeyvaluestorespaginator)
        """


if TYPE_CHECKING:
    _ListOriginAccessControlsPaginatorBase = AioPaginator[ListOriginAccessControlsResultTypeDef]
else:
    _ListOriginAccessControlsPaginatorBase = AioPaginator  # type: ignore[assignment]


class ListOriginAccessControlsPaginator(_ListOriginAccessControlsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListOriginAccessControls.html#CloudFront.Paginator.ListOriginAccessControls)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listoriginaccesscontrolspaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListOriginAccessControlsRequestPaginateTypeDef]
    ) -> AioPageIterator[ListOriginAccessControlsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListOriginAccessControls.html#CloudFront.Paginator.ListOriginAccessControls.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listoriginaccesscontrolspaginator)
        """


if TYPE_CHECKING:
    _ListPublicKeysPaginatorBase = AioPaginator[ListPublicKeysResultTypeDef]
else:
    _ListPublicKeysPaginatorBase = AioPaginator  # type: ignore[assignment]


class ListPublicKeysPaginator(_ListPublicKeysPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListPublicKeys.html#CloudFront.Paginator.ListPublicKeys)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listpublickeyspaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListPublicKeysRequestPaginateTypeDef]
    ) -> AioPageIterator[ListPublicKeysResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListPublicKeys.html#CloudFront.Paginator.ListPublicKeys.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#listpublickeyspaginator)
        """


if TYPE_CHECKING:
    _ListStreamingDistributionsPaginatorBase = AioPaginator[ListStreamingDistributionsResultTypeDef]
else:
    _ListStreamingDistributionsPaginatorBase = AioPaginator  # type: ignore[assignment]


class ListStreamingDistributionsPaginator(_ListStreamingDistributionsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListStreamingDistributions.html#CloudFront.Paginator.ListStreamingDistributions)
    [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#liststreamingdistributionspaginator)
    """

    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListStreamingDistributionsRequestPaginateTypeDef]
    ) -> AioPageIterator[ListStreamingDistributionsResultTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/paginator/ListStreamingDistributions.html#CloudFront.Paginator.ListStreamingDistributions.paginate)
        [Show types-aiobotocore-full documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_cloudfront/paginators/#liststreamingdistributionspaginator)
        """
