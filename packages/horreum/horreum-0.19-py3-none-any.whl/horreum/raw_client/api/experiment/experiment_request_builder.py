from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_test_item_request_builder import WithTestItemRequestBuilder
    from .models_requests.models_request_builder import ModelsRequestBuilder
    from .run.run_request_builder import RunRequestBuilder

class ExperimentRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/experiment
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ExperimentRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/experiment", path_parameters)
    
    def by_test_id(self,test_id: int) -> WithTestItemRequestBuilder:
        """
        Gets an item from the raw_client.api.experiment.item collection
        param test_id: Test ID to retrieve Experiment Profiles for
        Returns: WithTestItemRequestBuilder
        """
        if test_id is None:
            raise TypeError("test_id cannot be null.")
        from .item.with_test_item_request_builder import WithTestItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["testId"] = test_id
        return WithTestItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    @property
    def models(self) -> ModelsRequestBuilder:
        """
        The models property
        """
        from .models_requests.models_request_builder import ModelsRequestBuilder

        return ModelsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def run(self) -> RunRequestBuilder:
        """
        The run property
        """
        from .run.run_request_builder import RunRequestBuilder

        return RunRequestBuilder(self.request_adapter, self.path_parameters)
    

