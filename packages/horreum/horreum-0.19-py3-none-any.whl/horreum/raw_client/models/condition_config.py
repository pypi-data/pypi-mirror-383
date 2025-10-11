from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .condition_component import ConditionComponent
    from .condition_config_defaults import ConditionConfig_defaults

@dataclass
class ConditionConfig(AdditionalDataHolder, Parsable):
    """
    A configuration object for Change detection models
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # A dictionary of UI default configuration items for dynamically building the UI components
    defaults: Optional[ConditionConfig_defaults] = None
    # Change detection model description
    description: Optional[str] = None
    # Name of Change detection model
    name: Optional[str] = None
    # UI name for change detection model
    title: Optional[str] = None
    # A list of UI components for dynamically building the UI components
    ui: Optional[list[ConditionComponent]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ConditionConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ConditionConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ConditionConfig()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .condition_component import ConditionComponent
        from .condition_config_defaults import ConditionConfig_defaults

        from .condition_component import ConditionComponent
        from .condition_config_defaults import ConditionConfig_defaults

        fields: dict[str, Callable[[Any], None]] = {
            "defaults": lambda n : setattr(self, 'defaults', n.get_object_value(ConditionConfig_defaults)),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
            "ui": lambda n : setattr(self, 'ui', n.get_collection_of_object_values(ConditionComponent)),
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
        writer.write_object_value("defaults", self.defaults)
        writer.write_str_value("description", self.description)
        writer.write_str_value("name", self.name)
        writer.write_str_value("title", self.title)
        writer.write_collection_of_object_values("ui", self.ui)
        writer.write_additional_data_value(self.additional_data)
    

