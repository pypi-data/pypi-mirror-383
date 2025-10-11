from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .dataset_info import DatasetInfo
    from .dataset_log import DatasetLog
    from .experiment_profile import ExperimentProfile
    from .experiment_result_results import ExperimentResult_results

@dataclass
class ExperimentResult(AdditionalDataHolder, Parsable):
    """
    Result of running an Experiment
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # A list of Dataset Info for experiment baseline(s)
    baseline: Optional[list[DatasetInfo]] = None
    # Dataset Info about dataset used for experiment
    dataset_info: Optional[DatasetInfo] = None
    # The extraLabels property
    extra_labels: Optional[str] = None
    # A list of log statements recorded while Experiment was evaluated
    logs: Optional[list[DatasetLog]] = None
    # The notify property
    notify: Optional[bool] = None
    # Experiment profile that results relates to
    profile: Optional[ExperimentProfile] = None
    # A Map of all comparisons and results evaluated during an Experiment
    results: Optional[ExperimentResult_results] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ExperimentResult:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ExperimentResult
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ExperimentResult()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .dataset_info import DatasetInfo
        from .dataset_log import DatasetLog
        from .experiment_profile import ExperimentProfile
        from .experiment_result_results import ExperimentResult_results

        from .dataset_info import DatasetInfo
        from .dataset_log import DatasetLog
        from .experiment_profile import ExperimentProfile
        from .experiment_result_results import ExperimentResult_results

        fields: dict[str, Callable[[Any], None]] = {
            "baseline": lambda n : setattr(self, 'baseline', n.get_collection_of_object_values(DatasetInfo)),
            "datasetInfo": lambda n : setattr(self, 'dataset_info', n.get_object_value(DatasetInfo)),
            "extraLabels": lambda n : setattr(self, 'extra_labels', n.get_str_value()),
            "logs": lambda n : setattr(self, 'logs', n.get_collection_of_object_values(DatasetLog)),
            "notify": lambda n : setattr(self, 'notify', n.get_bool_value()),
            "profile": lambda n : setattr(self, 'profile', n.get_object_value(ExperimentProfile)),
            "results": lambda n : setattr(self, 'results', n.get_object_value(ExperimentResult_results)),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_collection_of_object_values("baseline", self.baseline)
        writer.write_object_value("datasetInfo", self.dataset_info)
        writer.write_str_value("extraLabels", self.extra_labels)
        writer.write_collection_of_object_values("logs", self.logs)
        writer.write_bool_value("notify", self.notify)
        writer.write_object_value("profile", self.profile)
        writer.write_object_value("results", self.results)
        writer.write_additional_data_value(self.additional_data)
    

