"""
Type annotations for ssm-sap service client paginators.

[Documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from aiobotocore.session import get_session

    from types_aiobotocore_ssm_sap.client import SsmSapClient
    from types_aiobotocore_ssm_sap.paginator import (
        ListApplicationsPaginator,
        ListComponentsPaginator,
        ListConfigurationCheckDefinitionsPaginator,
        ListConfigurationCheckOperationsPaginator,
        ListDatabasesPaginator,
        ListOperationEventsPaginator,
        ListOperationsPaginator,
        ListSubCheckResultsPaginator,
        ListSubCheckRuleResultsPaginator,
    )

    session = get_session()
    with session.create_client("ssm-sap") as client:
        client: SsmSapClient

        list_applications_paginator: ListApplicationsPaginator = client.get_paginator("list_applications")
        list_components_paginator: ListComponentsPaginator = client.get_paginator("list_components")
        list_configuration_check_definitions_paginator: ListConfigurationCheckDefinitionsPaginator = client.get_paginator("list_configuration_check_definitions")
        list_configuration_check_operations_paginator: ListConfigurationCheckOperationsPaginator = client.get_paginator("list_configuration_check_operations")
        list_databases_paginator: ListDatabasesPaginator = client.get_paginator("list_databases")
        list_operation_events_paginator: ListOperationEventsPaginator = client.get_paginator("list_operation_events")
        list_operations_paginator: ListOperationsPaginator = client.get_paginator("list_operations")
        list_sub_check_results_paginator: ListSubCheckResultsPaginator = client.get_paginator("list_sub_check_results")
        list_sub_check_rule_results_paginator: ListSubCheckRuleResultsPaginator = client.get_paginator("list_sub_check_rule_results")
    ```
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from aiobotocore.paginate import AioPageIterator, AioPaginator

from .type_defs import (
    ListApplicationsInputPaginateTypeDef,
    ListApplicationsOutputTypeDef,
    ListComponentsInputPaginateTypeDef,
    ListComponentsOutputTypeDef,
    ListConfigurationCheckDefinitionsInputPaginateTypeDef,
    ListConfigurationCheckDefinitionsOutputTypeDef,
    ListConfigurationCheckOperationsInputPaginateTypeDef,
    ListConfigurationCheckOperationsOutputTypeDef,
    ListDatabasesInputPaginateTypeDef,
    ListDatabasesOutputTypeDef,
    ListOperationEventsInputPaginateTypeDef,
    ListOperationEventsOutputTypeDef,
    ListOperationsInputPaginateTypeDef,
    ListOperationsOutputTypeDef,
    ListSubCheckResultsInputPaginateTypeDef,
    ListSubCheckResultsOutputTypeDef,
    ListSubCheckRuleResultsInputPaginateTypeDef,
    ListSubCheckRuleResultsOutputTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Unpack
else:
    from typing_extensions import Unpack

__all__ = (
    "ListApplicationsPaginator",
    "ListComponentsPaginator",
    "ListConfigurationCheckDefinitionsPaginator",
    "ListConfigurationCheckOperationsPaginator",
    "ListDatabasesPaginator",
    "ListOperationEventsPaginator",
    "ListOperationsPaginator",
    "ListSubCheckResultsPaginator",
    "ListSubCheckRuleResultsPaginator",
)

if TYPE_CHECKING:
    _ListApplicationsPaginatorBase = AioPaginator[ListApplicationsOutputTypeDef]
else:
    _ListApplicationsPaginatorBase = AioPaginator  # type: ignore[assignment]

class ListApplicationsPaginator(_ListApplicationsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListApplications.html#SsmSap.Paginator.ListApplications)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listapplicationspaginator)
    """
    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListApplicationsInputPaginateTypeDef]
    ) -> AioPageIterator[ListApplicationsOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListApplications.html#SsmSap.Paginator.ListApplications.paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listapplicationspaginator)
        """

if TYPE_CHECKING:
    _ListComponentsPaginatorBase = AioPaginator[ListComponentsOutputTypeDef]
else:
    _ListComponentsPaginatorBase = AioPaginator  # type: ignore[assignment]

class ListComponentsPaginator(_ListComponentsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListComponents.html#SsmSap.Paginator.ListComponents)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listcomponentspaginator)
    """
    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListComponentsInputPaginateTypeDef]
    ) -> AioPageIterator[ListComponentsOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListComponents.html#SsmSap.Paginator.ListComponents.paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listcomponentspaginator)
        """

if TYPE_CHECKING:
    _ListConfigurationCheckDefinitionsPaginatorBase = AioPaginator[
        ListConfigurationCheckDefinitionsOutputTypeDef
    ]
else:
    _ListConfigurationCheckDefinitionsPaginatorBase = AioPaginator  # type: ignore[assignment]

class ListConfigurationCheckDefinitionsPaginator(_ListConfigurationCheckDefinitionsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListConfigurationCheckDefinitions.html#SsmSap.Paginator.ListConfigurationCheckDefinitions)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listconfigurationcheckdefinitionspaginator)
    """
    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListConfigurationCheckDefinitionsInputPaginateTypeDef]
    ) -> AioPageIterator[ListConfigurationCheckDefinitionsOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListConfigurationCheckDefinitions.html#SsmSap.Paginator.ListConfigurationCheckDefinitions.paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listconfigurationcheckdefinitionspaginator)
        """

if TYPE_CHECKING:
    _ListConfigurationCheckOperationsPaginatorBase = AioPaginator[
        ListConfigurationCheckOperationsOutputTypeDef
    ]
else:
    _ListConfigurationCheckOperationsPaginatorBase = AioPaginator  # type: ignore[assignment]

class ListConfigurationCheckOperationsPaginator(_ListConfigurationCheckOperationsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListConfigurationCheckOperations.html#SsmSap.Paginator.ListConfigurationCheckOperations)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listconfigurationcheckoperationspaginator)
    """
    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListConfigurationCheckOperationsInputPaginateTypeDef]
    ) -> AioPageIterator[ListConfigurationCheckOperationsOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListConfigurationCheckOperations.html#SsmSap.Paginator.ListConfigurationCheckOperations.paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listconfigurationcheckoperationspaginator)
        """

if TYPE_CHECKING:
    _ListDatabasesPaginatorBase = AioPaginator[ListDatabasesOutputTypeDef]
else:
    _ListDatabasesPaginatorBase = AioPaginator  # type: ignore[assignment]

class ListDatabasesPaginator(_ListDatabasesPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListDatabases.html#SsmSap.Paginator.ListDatabases)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listdatabasespaginator)
    """
    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListDatabasesInputPaginateTypeDef]
    ) -> AioPageIterator[ListDatabasesOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListDatabases.html#SsmSap.Paginator.ListDatabases.paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listdatabasespaginator)
        """

if TYPE_CHECKING:
    _ListOperationEventsPaginatorBase = AioPaginator[ListOperationEventsOutputTypeDef]
else:
    _ListOperationEventsPaginatorBase = AioPaginator  # type: ignore[assignment]

class ListOperationEventsPaginator(_ListOperationEventsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListOperationEvents.html#SsmSap.Paginator.ListOperationEvents)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listoperationeventspaginator)
    """
    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListOperationEventsInputPaginateTypeDef]
    ) -> AioPageIterator[ListOperationEventsOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListOperationEvents.html#SsmSap.Paginator.ListOperationEvents.paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listoperationeventspaginator)
        """

if TYPE_CHECKING:
    _ListOperationsPaginatorBase = AioPaginator[ListOperationsOutputTypeDef]
else:
    _ListOperationsPaginatorBase = AioPaginator  # type: ignore[assignment]

class ListOperationsPaginator(_ListOperationsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListOperations.html#SsmSap.Paginator.ListOperations)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listoperationspaginator)
    """
    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListOperationsInputPaginateTypeDef]
    ) -> AioPageIterator[ListOperationsOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListOperations.html#SsmSap.Paginator.ListOperations.paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listoperationspaginator)
        """

if TYPE_CHECKING:
    _ListSubCheckResultsPaginatorBase = AioPaginator[ListSubCheckResultsOutputTypeDef]
else:
    _ListSubCheckResultsPaginatorBase = AioPaginator  # type: ignore[assignment]

class ListSubCheckResultsPaginator(_ListSubCheckResultsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListSubCheckResults.html#SsmSap.Paginator.ListSubCheckResults)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listsubcheckresultspaginator)
    """
    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListSubCheckResultsInputPaginateTypeDef]
    ) -> AioPageIterator[ListSubCheckResultsOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListSubCheckResults.html#SsmSap.Paginator.ListSubCheckResults.paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listsubcheckresultspaginator)
        """

if TYPE_CHECKING:
    _ListSubCheckRuleResultsPaginatorBase = AioPaginator[ListSubCheckRuleResultsOutputTypeDef]
else:
    _ListSubCheckRuleResultsPaginatorBase = AioPaginator  # type: ignore[assignment]

class ListSubCheckRuleResultsPaginator(_ListSubCheckRuleResultsPaginatorBase):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListSubCheckRuleResults.html#SsmSap.Paginator.ListSubCheckRuleResults)
    [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listsubcheckruleresultspaginator)
    """
    def paginate(  # type: ignore[override]
        self, **kwargs: Unpack[ListSubCheckRuleResultsInputPaginateTypeDef]
    ) -> AioPageIterator[ListSubCheckRuleResultsOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm-sap/paginator/ListSubCheckRuleResults.html#SsmSap.Paginator.ListSubCheckRuleResults.paginate)
        [Show types-aiobotocore documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ssm_sap/paginators/#listsubcheckruleresultspaginator)
        """
