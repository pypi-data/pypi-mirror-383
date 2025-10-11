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
    from ...models.test import Test
    from ...models.test_query_result import TestQueryResult
    from .by_name.by_name_request_builder import ByNameRequestBuilder
    from .folders.folders_request_builder import FoldersRequestBuilder
    from .import_.import_request_builder import ImportRequestBuilder
    from .item.test_item_request_builder import TestItemRequestBuilder
    from .summary.summary_request_builder import SummaryRequestBuilder

class TestRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/test
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new TestRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/test{?direction*,limit*,page*,roles*,sort*}", path_parameters)
    
    def by_id(self,id: int) -> TestItemRequestBuilder:
        """
        Gets an item from the raw_client.api.test.item collection
        param id: Unique identifier of the item
        Returns: TestItemRequestBuilder
        """
        if id is None:
            raise TypeError("id cannot be null.")
        from .item.test_item_request_builder import TestItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["id"] = id
        return TestItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[TestRequestBuilderGetQueryParameters]] = None) -> Optional[TestQueryResult]:
        """
        Retrieve a paginated list of Tests with available count
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[TestQueryResult]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.test_query_result import TestQueryResult

        return await self.request_adapter.send_async(request_info, TestQueryResult, None)
    
    async def post(self,body: Test, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[Test]:
        """
        Create a new test
        param body: Represents a Test. Tests are typically equivalent to a particular benchmark
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Test]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.test import Test

        return await self.request_adapter.send_async(request_info, Test, None)
    
    async def put(self,body: Test, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[Test]:
        """
        Update an existing test
        param body: Represents a Test. Tests are typically equivalent to a particular benchmark
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Test]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.test import Test

        return await self.request_adapter.send_async(request_info, Test, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[TestRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Retrieve a paginated list of Tests with available count
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: Test, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Create a new test
        param body: Represents a Test. Tests are typically equivalent to a particular benchmark
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
    
    def to_put_request_information(self,body: Test, request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Update an existing test
        param body: Represents a Test. Tests are typically equivalent to a particular benchmark
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
    
    def with_url(self,raw_url: str) -> TestRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: TestRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return TestRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def by_name(self) -> ByNameRequestBuilder:
        """
        The byName property
        """
        from .by_name.by_name_request_builder import ByNameRequestBuilder

        return ByNameRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def folders(self) -> FoldersRequestBuilder:
        """
        The folders property
        """
        from .folders.folders_request_builder import FoldersRequestBuilder

        return FoldersRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def import_(self) -> ImportRequestBuilder:
        """
        The import property
        """
        from .import_.import_request_builder import ImportRequestBuilder

        return ImportRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def summary(self) -> SummaryRequestBuilder:
        """
        The summary property
        """
        from .summary.summary_request_builder import SummaryRequestBuilder

        return SummaryRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class TestRequestBuilderGetQueryParameters():
        """
        Retrieve a paginated list of Tests with available count
        """
        # Sort direction
        direction: Optional[str] = None

        # limit the number of results
        limit: Optional[int] = None

        # filter by page number of a paginated list of Tests starting from 1
        page: Optional[int] = None

        # __my, __all or a comma delimited  list of roles
        roles: Optional[str] = None

        # Field name to sort results
        sort: Optional[str] = None

    
    @dataclass
    class TestRequestBuilderGetRequestConfiguration(RequestConfiguration[TestRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class TestRequestBuilderPostRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class TestRequestBuilderPutRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

