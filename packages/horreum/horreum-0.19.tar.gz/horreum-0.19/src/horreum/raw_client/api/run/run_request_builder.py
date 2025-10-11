from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .autocomplete.autocomplete_request_builder import AutocompleteRequestBuilder
    from .by_schema.by_schema_request_builder import BySchemaRequestBuilder
    from .count.count_request_builder import CountRequestBuilder
    from .data.data_request_builder import DataRequestBuilder
    from .item.run_item_request_builder import RunItemRequestBuilder
    from .list_.list_request_builder import ListRequestBuilder
    from .recalculate_all.recalculate_all_request_builder import RecalculateAllRequestBuilder
    from .test.test_request_builder import TestRequestBuilder

class RunRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/run
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new RunRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/run", path_parameters)
    
    def by_id(self,id: int) -> RunItemRequestBuilder:
        """
        Gets an item from the raw_client.api.run.item collection
        param id: Run ID
        Returns: RunItemRequestBuilder
        """
        if id is None:
            raise TypeError("id cannot be null.")
        from .item.run_item_request_builder import RunItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["id"] = id
        return RunItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    @property
    def autocomplete(self) -> AutocompleteRequestBuilder:
        """
        The autocomplete property
        """
        from .autocomplete.autocomplete_request_builder import AutocompleteRequestBuilder

        return AutocompleteRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def by_schema(self) -> BySchemaRequestBuilder:
        """
        The bySchema property
        """
        from .by_schema.by_schema_request_builder import BySchemaRequestBuilder

        return BySchemaRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def count(self) -> CountRequestBuilder:
        """
        The count property
        """
        from .count.count_request_builder import CountRequestBuilder

        return CountRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def data(self) -> DataRequestBuilder:
        """
        The data property
        """
        from .data.data_request_builder import DataRequestBuilder

        return DataRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def list_(self) -> ListRequestBuilder:
        """
        The list property
        """
        from .list_.list_request_builder import ListRequestBuilder

        return ListRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def recalculate_all(self) -> RecalculateAllRequestBuilder:
        """
        The recalculateAll property
        """
        from .recalculate_all.recalculate_all_request_builder import RecalculateAllRequestBuilder

        return RecalculateAllRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def test(self) -> TestRequestBuilder:
        """
        The test property
        """
        from .test.test_request_builder import TestRequestBuilder

        return TestRequestBuilder(self.request_adapter, self.path_parameters)
    

