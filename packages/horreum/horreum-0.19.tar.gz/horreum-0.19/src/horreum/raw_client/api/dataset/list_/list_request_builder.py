from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .by_run.by_run_request_builder import ByRunRequestBuilder
    from .by_schema.by_schema_request_builder import BySchemaRequestBuilder
    from .by_test.by_test_request_builder import ByTestRequestBuilder

class ListRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/dataset/list
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ListRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/dataset/list", path_parameters)
    
    @property
    def by_run(self) -> ByRunRequestBuilder:
        """
        The byRun property
        """
        from .by_run.by_run_request_builder import ByRunRequestBuilder

        return ByRunRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def by_schema(self) -> BySchemaRequestBuilder:
        """
        The bySchema property
        """
        from .by_schema.by_schema_request_builder import BySchemaRequestBuilder

        return BySchemaRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def by_test(self) -> ByTestRequestBuilder:
        """
        The byTest property
        """
        from .by_test.by_test_request_builder import ByTestRequestBuilder

        return ByTestRequestBuilder(self.request_adapter, self.path_parameters)
    

