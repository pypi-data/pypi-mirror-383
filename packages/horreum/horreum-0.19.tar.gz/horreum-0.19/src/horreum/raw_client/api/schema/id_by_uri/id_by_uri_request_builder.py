from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_uri_item_request_builder import WithUriItemRequestBuilder

class IdByUriRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/schema/idByUri
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new IdByUriRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/schema/idByUri", path_parameters)
    
    def by_uri(self,uri: str) -> WithUriItemRequestBuilder:
        """
        Gets an item from the raw_client.api.schema.idByUri.item collection
        param uri: Schema uri
        Returns: WithUriItemRequestBuilder
        """
        if uri is None:
            raise TypeError("uri cannot be null.")
        from .item.with_uri_item_request_builder import WithUriItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["uri"] = uri
        return WithUriItemRequestBuilder(self.request_adapter, url_tpl_params)
    

