from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .relative_difference_detection_config_model import RelativeDifferenceDetectionConfig_model

@dataclass
class RelativeDifferenceDetectionConfig(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Built In
    built_in: Optional[bool] = None
    # Relative Difference Detection filter
    filter: Optional[str] = None
    # Minimal number of preceding datapoints
    min_previous: Optional[int] = None
    # The model property
    model: Optional[RelativeDifferenceDetectionConfig_model] = None
    # Maximum difference between the aggregated value of last <window> datapoints and the mean of preceding values.
    threshold: Optional[float] = None
    # Number of most recent datapoints used for aggregating the value for comparison.
    window: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RelativeDifferenceDetectionConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RelativeDifferenceDetectionConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RelativeDifferenceDetectionConfig()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .relative_difference_detection_config_model import RelativeDifferenceDetectionConfig_model

        from .relative_difference_detection_config_model import RelativeDifferenceDetectionConfig_model

        fields: dict[str, Callable[[Any], None]] = {
            "builtIn": lambda n : setattr(self, 'built_in', n.get_bool_value()),
            "filter": lambda n : setattr(self, 'filter', n.get_str_value()),
            "minPrevious": lambda n : setattr(self, 'min_previous', n.get_int_value()),
            "model": lambda n : setattr(self, 'model', n.get_enum_value(RelativeDifferenceDetectionConfig_model)),
            "threshold": lambda n : setattr(self, 'threshold', n.get_float_value()),
            "window": lambda n : setattr(self, 'window', n.get_int_value()),
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
        writer.write_bool_value("builtIn", self.built_in)
        writer.write_str_value("filter", self.filter)
        writer.write_int_value("minPrevious", self.min_previous)
        writer.write_enum_value("model", self.model)
        writer.write_float_value("threshold", self.threshold)
        writer.write_int_value("window", self.window)
        writer.write_additional_data_value(self.additional_data)
    

