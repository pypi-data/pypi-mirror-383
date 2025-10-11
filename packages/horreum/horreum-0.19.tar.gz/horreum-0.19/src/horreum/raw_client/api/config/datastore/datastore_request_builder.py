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
    from ....models.datastore import Datastore
    from .item.datastore_item_request_builder import DatastoreItemRequestBuilder
    from .types.types_request_builder import TypesRequestBuilder

class DatastoreRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/config/datastore
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new DatastoreRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/config/datastore{?team*}", path_parameters)
    
    def by_id(self,id: int) -> DatastoreItemRequestBuilder:
        """
        Gets an item from the raw_client.api.config.datastore.item collection
        param id: Unique identifier of the item
        Returns: DatastoreItemRequestBuilder
        """
        if id is None:
            raise TypeError("id cannot be null.")
        from .item.datastore_item_request_builder import DatastoreItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["id"] = id
        return DatastoreItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[DatastoreRequestBuilderGetQueryParameters]] = None) -> Optional[list[Datastore]]:
        """
        Obtain list of configured datastores for particular team
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[list[Datastore]]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.datastore import Datastore

        return await self.request_adapter.send_collection_async(request_info, Datastore, None)
    
    async def post(self,body: Datastore, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[int]:
        """
        Create a new Datastore
        param body: Instance of backend datastore
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
    
    async def put(self,body: Datastore, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[int]:
        """
        Update an existing Datastore definition
        param body: Instance of backend datastore
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
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[DatastoreRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Obtain list of configured datastores for particular team
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: Datastore, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Create a new Datastore
        param body: Instance of backend datastore
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
    
    def to_put_request_information(self,body: Datastore, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Update an existing Datastore definition
        param body: Instance of backend datastore
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
    
    def with_url(self,raw_url: str) -> DatastoreRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: DatastoreRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return DatastoreRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def types(self) -> TypesRequestBuilder:
        """
        The types property
        """
        from .types.types_request_builder import TypesRequestBuilder

        return TypesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class DatastoreRequestBuilderGetQueryParameters():
        """
        Obtain list of configured datastores for particular team
        """
        # name of the team to search for defined datastores
        team: Optional[str] = None

    
    @dataclass
    class DatastoreRequestBuilderGetRequestConfiguration(RequestConfiguration[DatastoreRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class DatastoreRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class DatastoreRequestBuilderPutRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

