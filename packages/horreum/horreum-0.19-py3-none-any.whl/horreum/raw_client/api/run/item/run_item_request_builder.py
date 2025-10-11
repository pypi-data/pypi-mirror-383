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
    from ....models.run_extended import RunExtended
    from .data.data_request_builder import DataRequestBuilder
    from .description.description_request_builder import DescriptionRequestBuilder
    from .label_values.label_values_request_builder import LabelValuesRequestBuilder
    from .metadata.metadata_request_builder import MetadataRequestBuilder
    from .recalculate.recalculate_request_builder import RecalculateRequestBuilder
    from .schema.schema_request_builder import SchemaRequestBuilder
    from .summary.summary_request_builder import SummaryRequestBuilder
    from .trash.trash_request_builder import TrashRequestBuilder
    from .update_access.update_access_request_builder import UpdateAccessRequestBuilder

class RunItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/run/{id}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new RunItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/run/{id}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[RunExtended]:
        """
        Get extended Run information by Run ID
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[RunExtended]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.run_extended import RunExtended

        return await self.request_adapter.send_async(request_info, RunExtended, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Get extended Run information by Run ID
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> RunItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: RunItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return RunItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def data(self) -> DataRequestBuilder:
        """
        The data property
        """
        from .data.data_request_builder import DataRequestBuilder

        return DataRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def description(self) -> DescriptionRequestBuilder:
        """
        The description property
        """
        from .description.description_request_builder import DescriptionRequestBuilder

        return DescriptionRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def label_values(self) -> LabelValuesRequestBuilder:
        """
        The labelValues property
        """
        from .label_values.label_values_request_builder import LabelValuesRequestBuilder

        return LabelValuesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def metadata(self) -> MetadataRequestBuilder:
        """
        The metadata property
        """
        from .metadata.metadata_request_builder import MetadataRequestBuilder

        return MetadataRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def recalculate(self) -> RecalculateRequestBuilder:
        """
        The recalculate property
        """
        from .recalculate.recalculate_request_builder import RecalculateRequestBuilder

        return RecalculateRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def schema(self) -> SchemaRequestBuilder:
        """
        The schema property
        """
        from .schema.schema_request_builder import SchemaRequestBuilder

        return SchemaRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def summary(self) -> SummaryRequestBuilder:
        """
        The summary property
        """
        from .summary.summary_request_builder import SummaryRequestBuilder

        return SummaryRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def trash(self) -> TrashRequestBuilder:
        """
        The trash property
        """
        from .trash.trash_request_builder import TrashRequestBuilder

        return TrashRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def update_access(self) -> UpdateAccessRequestBuilder:
        """
        The updateAccess property
        """
        from .update_access.update_access_request_builder import UpdateAccessRequestBuilder

        return UpdateAccessRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class RunItemRequestBuilderGetRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

