from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .config.config_request_builder import ConfigRequestBuilder
    from .dataset.dataset_request_builder import DatasetRequestBuilder
    from .experiment.experiment_request_builder import ExperimentRequestBuilder
    from .run.run_request_builder import RunRequestBuilder
    from .schema.schema_request_builder import SchemaRequestBuilder
    from .test.test_request_builder import TestRequestBuilder
    from .user.user_request_builder import UserRequestBuilder

class ApiRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ApiRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api", path_parameters)
    
    @property
    def config(self) -> ConfigRequestBuilder:
        """
        The config property
        """
        from .config.config_request_builder import ConfigRequestBuilder

        return ConfigRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def dataset(self) -> DatasetRequestBuilder:
        """
        The dataset property
        """
        from .dataset.dataset_request_builder import DatasetRequestBuilder

        return DatasetRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def experiment(self) -> ExperimentRequestBuilder:
        """
        The experiment property
        """
        from .experiment.experiment_request_builder import ExperimentRequestBuilder

        return ExperimentRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def run(self) -> RunRequestBuilder:
        """
        The run property
        """
        from .run.run_request_builder import RunRequestBuilder

        return RunRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def schema(self) -> SchemaRequestBuilder:
        """
        The schema property
        """
        from .schema.schema_request_builder import SchemaRequestBuilder

        return SchemaRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def test(self) -> TestRequestBuilder:
        """
        The test property
        """
        from .test.test_request_builder import TestRequestBuilder

        return TestRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def user(self) -> UserRequestBuilder:
        """
        The user property
        """
        from .user.user_request_builder import UserRequestBuilder

        return UserRequestBuilder(self.request_adapter, self.path_parameters)
    

