from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .fixed_threshold_detection_config_model import FixedThresholdDetectionConfig_model
    from .fix_threshold_config import FixThresholdConfig

@dataclass
class FixedThresholdDetectionConfig(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Built In
    built_in: Optional[bool] = None
    # Upper bound for acceptable datapoint values
    max: Optional[FixThresholdConfig] = None
    # Lower bound for acceptable datapoint values
    min: Optional[FixThresholdConfig] = None
    # The model property
    model: Optional[FixedThresholdDetectionConfig_model] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> FixedThresholdDetectionConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: FixedThresholdDetectionConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return FixedThresholdDetectionConfig()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .fixed_threshold_detection_config_model import FixedThresholdDetectionConfig_model
        from .fix_threshold_config import FixThresholdConfig

        from .fixed_threshold_detection_config_model import FixedThresholdDetectionConfig_model
        from .fix_threshold_config import FixThresholdConfig

        fields: dict[str, Callable[[Any], None]] = {
            "builtIn": lambda n : setattr(self, 'built_in', n.get_bool_value()),
            "max": lambda n : setattr(self, 'max', n.get_object_value(FixThresholdConfig)),
            "min": lambda n : setattr(self, 'min', n.get_object_value(FixThresholdConfig)),
            "model": lambda n : setattr(self, 'model', n.get_enum_value(FixedThresholdDetectionConfig_model)),
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
        writer.write_object_value("max", self.max)
        writer.write_object_value("min", self.min)
        writer.write_enum_value("model", self.model)
        writer.write_additional_data_value(self.additional_data)
    

