from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .datastore.datastore_request_builder import DatastoreRequestBuilder
    from .keycloak.keycloak_request_builder import KeycloakRequestBuilder
    from .version.version_request_builder import VersionRequestBuilder

class ConfigRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/config
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ConfigRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/config", path_parameters)
    
    @property
    def datastore(self) -> DatastoreRequestBuilder:
        """
        The datastore property
        """
        from .datastore.datastore_request_builder import DatastoreRequestBuilder

        return DatastoreRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def keycloak(self) -> KeycloakRequestBuilder:
        """
        The keycloak property
        """
        from .keycloak.keycloak_request_builder import KeycloakRequestBuilder

        return KeycloakRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def version(self) -> VersionRequestBuilder:
        """
        The version property
        """
        from .version.version_request_builder import VersionRequestBuilder

        return VersionRequestBuilder(self.request_adapter, self.path_parameters)
    

