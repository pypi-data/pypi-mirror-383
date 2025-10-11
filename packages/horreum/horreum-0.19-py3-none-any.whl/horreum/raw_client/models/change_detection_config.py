from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .e_divisive_detection_config import EDivisiveDetectionConfig
    from .fixed_threshold_detection_config import FixedThresholdDetectionConfig
    from .relative_difference_detection_config import RelativeDifferenceDetectionConfig

@dataclass
class ChangeDetection_config(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes EDivisiveDetectionConfig, FixedThresholdDetectionConfig, RelativeDifferenceDetectionConfig
    """
    # Composed type representation for type EDivisiveDetectionConfig
    e_divisive_detection_config: Optional[EDivisiveDetectionConfig] = None
    # Composed type representation for type FixedThresholdDetectionConfig
    fixed_threshold_detection_config: Optional[FixedThresholdDetectionConfig] = None
    # Composed type representation for type RelativeDifferenceDetectionConfig
    relative_difference_detection_config: Optional[RelativeDifferenceDetectionConfig] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ChangeDetection_config:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ChangeDetection_config
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("model")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = ChangeDetection_config()
        if mapping_value and mapping_value.casefold() == "eDivisive".casefold():
            from .e_divisive_detection_config import EDivisiveDetectionConfig

            result.e_divisive_detection_config = EDivisiveDetectionConfig()
        elif mapping_value and mapping_value.casefold() == "fixedThreshold".casefold():
            from .fixed_threshold_detection_config import FixedThresholdDetectionConfig

            result.fixed_threshold_detection_config = FixedThresholdDetectionConfig()
        elif mapping_value and mapping_value.casefold() == "relativeDifference".casefold():
            from .relative_difference_detection_config import RelativeDifferenceDetectionConfig

            result.relative_difference_detection_config = RelativeDifferenceDetectionConfig()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .e_divisive_detection_config import EDivisiveDetectionConfig
        from .fixed_threshold_detection_config import FixedThresholdDetectionConfig
        from .relative_difference_detection_config import RelativeDifferenceDetectionConfig

        if self.e_divisive_detection_config:
            return self.e_divisive_detection_config.get_field_deserializers()
        if self.fixed_threshold_detection_config:
            return self.fixed_threshold_detection_config.get_field_deserializers()
        if self.relative_difference_detection_config:
            return self.relative_difference_detection_config.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.e_divisive_detection_config:
            writer.write_object_value(None, self.e_divisive_detection_config)
        elif self.fixed_threshold_detection_config:
            writer.write_object_value(None, self.fixed_threshold_detection_config)
        elif self.relative_difference_detection_config:
            writer.write_object_value(None, self.relative_difference_detection_config)
    

