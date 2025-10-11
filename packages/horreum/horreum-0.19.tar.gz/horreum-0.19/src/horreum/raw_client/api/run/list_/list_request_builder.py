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
    from ....models.runs_summary import RunsSummary
    from ....models.sort_direction import SortDirection
    from .item.with_test_item_request_builder import WithTestItemRequestBuilder

class ListRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/run/list
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ListRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/run/list{?direction*,limit*,matchAll*,page*,query*,roles*,sort*,trashed*}", path_parameters)
    
    def by_test_id(self,test_id: int) -> WithTestItemRequestBuilder:
        """
        Gets an item from the raw_client.api.run.list.item collection
        param test_id: Test ID
        Returns: WithTestItemRequestBuilder
        """
        if test_id is None:
            raise TypeError("test_id cannot be null.")
        from .item.with_test_item_request_builder import WithTestItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["testId"] = test_id
        return WithTestItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[ListRequestBuilderGetQueryParameters]] = None) -> Optional[RunsSummary]:
        """
        Retrieve a paginated list of Runs with available count
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[RunsSummary]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.runs_summary import RunsSummary

        return await self.request_adapter.send_async(request_info, RunsSummary, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[ListRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Retrieve a paginated list of Runs with available count
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> ListRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: ListRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return ListRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class ListRequestBuilderGetQueryParameters():
        """
        Retrieve a paginated list of Runs with available count
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "match_all":
                return "matchAll"
            if original_name == "direction":
                return "direction"
            if original_name == "limit":
                return "limit"
            if original_name == "page":
                return "page"
            if original_name == "query":
                return "query"
            if original_name == "roles":
                return "roles"
            if original_name == "sort":
                return "sort"
            if original_name == "trashed":
                return "trashed"
            return original_name
        
        # Sort direction
        direction: Optional[SortDirection] = None

        # limit the number of results
        limit: Optional[int] = None

        # match all Runs?
        match_all: Optional[bool] = None

        # filter by page number of a paginated list of Tests starting from 1
        page: Optional[int] = None

        # query string to filter runs
        query: Optional[str] = None

        # __my, __all or a comma delimited  list of roles
        roles: Optional[str] = None

        # Field name to sort results
        sort: Optional[str] = None

        # show trashed runs
        trashed: Optional[bool] = None

    
    @dataclass
    class ListRequestBuilderGetRequestConfiguration(RequestConfiguration[ListRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

