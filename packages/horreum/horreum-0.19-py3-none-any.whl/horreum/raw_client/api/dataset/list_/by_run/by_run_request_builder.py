from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_run_item_request_builder import WithRunItemRequestBuilder

class ByRunRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/dataset/list/byRun
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ByRunRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/dataset/list/byRun", path_parameters)
    
    def by_run_id(self,run_id: int) -> WithRunItemRequestBuilder:
        """
        Gets an item from the raw_client.api.dataset.list.byRun.item collection
        param run_id: Run ID of run to retrieve list of Datasets
        Returns: WithRunItemRequestBuilder
        """
        if run_id is None:
            raise TypeError("run_id cannot be null.")
        from .item.with_run_item_request_builder import WithRunItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["runId"] = run_id
        return WithRunItemRequestBuilder(self.request_adapter, url_tpl_params)
    

