from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.default_query_parameters import QueryParameters
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Optional, TYPE_CHECKING, Union
from warnings import warn

if TYPE_CHECKING:
    from ...models.schema import Schema
    from ...models.schema_query_result import SchemaQueryResult
    from ...models.sort_direction import SortDirection
    from .all_labels.all_labels_request_builder import AllLabelsRequestBuilder
    from .all_transformers.all_transformers_request_builder import AllTransformersRequestBuilder
    from .descriptors.descriptors_request_builder import DescriptorsRequestBuilder
    from .find_usages.find_usages_request_builder import FindUsagesRequestBuilder
    from .id_by_uri.id_by_uri_request_builder import IdByUriRequestBuilder
    from .import_.import_request_builder import ImportRequestBuilder
    from .item.item_request_builder import ItemRequestBuilder

class SchemaRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/schema
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new SchemaRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/schema{?direction*,limit*,name*,page*,roles*,sort*}", path_parameters)
    
    def by_id(self,id: int) -> ItemRequestBuilder:
        """
        Gets an item from the raw_client.api.schema.item collection
        param id: Schema ID to retrieve
        Returns: ItemRequestBuilder
        """
        if id is None:
            raise TypeError("id cannot be null.")
        from .item.item_request_builder import ItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["%2Did"] = id
        return ItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[SchemaRequestBuilderGetQueryParameters]] = None) -> Optional[SchemaQueryResult]:
        """
        Retrieve a paginated list of Schemas with available count
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[SchemaQueryResult]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.schema_query_result import SchemaQueryResult

        return await self.request_adapter.send_async(request_info, SchemaQueryResult, None)
    
    async def post(self,body: Schema, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[int]:
        """
        Save a new Schema
        param body: Data object that describes the schema definition for a test
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[int]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_primitive_async(request_info, "int", None)
    
    async def put(self,body: Schema, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[int]:
        """
        Update an existing Schema
        param body: Data object that describes the schema definition for a test
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[int]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_primitive_async(request_info, "int", None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[SchemaRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Retrieve a paginated list of Schemas with available count
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: Schema, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Save a new Schema
        param body: Data object that describes the schema definition for a test
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def to_put_request_information(self,body: Schema, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Update an existing Schema
        param body: Data object that describes the schema definition for a test
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.PUT, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> SchemaRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: SchemaRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return SchemaRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def all_labels(self) -> AllLabelsRequestBuilder:
        """
        The allLabels property
        """
        from .all_labels.all_labels_request_builder import AllLabelsRequestBuilder

        return AllLabelsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def all_transformers(self) -> AllTransformersRequestBuilder:
        """
        The allTransformers property
        """
        from .all_transformers.all_transformers_request_builder import AllTransformersRequestBuilder

        return AllTransformersRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def descriptors(self) -> DescriptorsRequestBuilder:
        """
        The descriptors property
        """
        from .descriptors.descriptors_request_builder import DescriptorsRequestBuilder

        return DescriptorsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def find_usages(self) -> FindUsagesRequestBuilder:
        """
        The findUsages property
        """
        from .find_usages.find_usages_request_builder import FindUsagesRequestBuilder

        return FindUsagesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def id_by_uri(self) -> IdByUriRequestBuilder:
        """
        The idByUri property
        """
        from .id_by_uri.id_by_uri_request_builder import IdByUriRequestBuilder

        return IdByUriRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def import_(self) -> ImportRequestBuilder:
        """
        The import property
        """
        from .import_.import_request_builder import ImportRequestBuilder

        return ImportRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class SchemaRequestBuilderGetQueryParameters():
        """
        Retrieve a paginated list of Schemas with available count
        """
        # Sort direction
        direction: Optional[SortDirection] = None

        # limit the number of results
        limit: Optional[int] = None

        name: Optional[str] = None

        # filter by page number of a paginated list of Schemas starting from 1
        page: Optional[int] = None

        # __my, __all or a comma delimited  list of roles
        roles: Optional[str] = None

        # Field name to sort results
        sort: Optional[str] = None

    
    @dataclass
    class SchemaRequestBuilderGetRequestConfiguration(RequestConfiguration[SchemaRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class SchemaRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class SchemaRequestBuilderPutRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

