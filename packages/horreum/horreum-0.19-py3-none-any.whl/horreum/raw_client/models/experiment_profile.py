from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .experiment_comparison import ExperimentComparison

@dataclass
class ExperimentProfile(AdditionalDataHolder, Parsable):
    """
    Experiment profile that results relates to
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Selector filter to apply to Baseline label values
    baseline_filter: Optional[str] = None
    # Array of selector labels for comparison Baseline
    baseline_labels: Optional[list[str]] = None
    # Collection of Experiment Comparisons to run during an Experiment evaluation
    comparisons: Optional[list[ExperimentComparison]] = None
    # These labels are not used by Horreum but are added to the result event and therefore can be used e.g. when firing an Action.
    extra_labels: Optional[list[str]] = None
    # Experiment Profile unique ID
    id: Optional[int] = None
    # Name of Experiment Profile
    name: Optional[str] = None
    # Selector filter to apply to Selector label values
    selector_filter: Optional[str] = None
    # Array of selector labels
    selector_labels: Optional[list[str]] = None
    # Test ID that Experiment Profile relates to
    test_id: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ExperimentProfile:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ExperimentProfile
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ExperimentProfile()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .experiment_comparison import ExperimentComparison

        from .experiment_comparison import ExperimentComparison

        fields: dict[str, Callable[[Any], None]] = {
            "baselineFilter": lambda n : setattr(self, 'baseline_filter', n.get_str_value()),
            "baselineLabels": lambda n : setattr(self, 'baseline_labels', n.get_collection_of_primitive_values(str)),
            "comparisons": lambda n : setattr(self, 'comparisons', n.get_collection_of_object_values(ExperimentComparison)),
            "extraLabels": lambda n : setattr(self, 'extra_labels', n.get_collection_of_primitive_values(str)),
            "id": lambda n : setattr(self, 'id', n.get_int_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "selectorFilter": lambda n : setattr(self, 'selector_filter', n.get_str_value()),
            "selectorLabels": lambda n : setattr(self, 'selector_labels', n.get_collection_of_primitive_values(str)),
            "testId": lambda n : setattr(self, 'test_id', n.get_int_value()),
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
        writer.write_str_value("baselineFilter", self.baseline_filter)
        writer.write_collection_of_primitive_values("baselineLabels", self.baseline_labels)
        writer.write_collection_of_object_values("comparisons", self.comparisons)
        writer.write_collection_of_primitive_values("extraLabels", self.extra_labels)
        writer.write_int_value("id", self.id)
        writer.write_str_value("name", self.name)
        writer.write_str_value("selectorFilter", self.selector_filter)
        writer.write_collection_of_primitive_values("selectorLabels", self.selector_labels)
        writer.write_int_value("testId", self.test_id)
        writer.write_additional_data_value(self.additional_data)
    

