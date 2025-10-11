from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.dataset_item_request_builder import DatasetItemRequestBuilder
    from .list_.list_request_builder import ListRequestBuilder

class DatasetRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/dataset
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new DatasetRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/dataset", path_parameters)
    
    def by_dataset_id(self,dataset_id: int) -> DatasetItemRequestBuilder:
        """
        Gets an item from the raw_client.api.dataset.item collection
        param dataset_id: Dataset ID to retrieve
        Returns: DatasetItemRequestBuilder
        """
        if dataset_id is None:
            raise TypeError("dataset_id cannot be null.")
        from .item.dataset_item_request_builder import DatasetItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["dataset%2Did"] = dataset_id
        return DatasetItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    @property
    def list_(self) -> ListRequestBuilder:
        """
        The list property
        """
        from .list_.list_request_builder import ListRequestBuilder

        return ListRequestBuilder(self.request_adapter, self.path_parameters)
    

