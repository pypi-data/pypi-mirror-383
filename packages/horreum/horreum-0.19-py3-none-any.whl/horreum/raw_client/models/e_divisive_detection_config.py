from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .e_divisive_detection_config_model import EDivisiveDetectionConfig_model

@dataclass
class EDivisiveDetectionConfig(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Built In
    built_in: Optional[bool] = None
    # The model property
    model: Optional[EDivisiveDetectionConfig_model] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> EDivisiveDetectionConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: EDivisiveDetectionConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return EDivisiveDetectionConfig()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .e_divisive_detection_config_model import EDivisiveDetectionConfig_model

        from .e_divisive_detection_config_model import EDivisiveDetectionConfig_model

        fields: dict[str, Callable[[Any], None]] = {
            "builtIn": lambda n : setattr(self, 'built_in', n.get_bool_value()),
            "model": lambda n : setattr(self, 'model', n.get_enum_value(EDivisiveDetectionConfig_model)),
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
        writer.write_enum_value("model", self.model)
        writer.write_additional_data_value(self.additional_data)
    

