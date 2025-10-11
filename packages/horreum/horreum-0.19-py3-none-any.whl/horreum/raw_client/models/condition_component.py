from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .condition_component_properties import ConditionComponent_properties
    from .condition_component_type import ConditionComponent_type

@dataclass
class ConditionComponent(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Change detection model component description
    description: Optional[str] = None
    # Change detection model component name
    name: Optional[str] = None
    # Map of properties for component
    properties: Optional[ConditionComponent_properties] = None
    # Change detection model component title
    title: Optional[str] = None
    # UI Component type
    type: Optional[ConditionComponent_type] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ConditionComponent:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ConditionComponent
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ConditionComponent()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .condition_component_properties import ConditionComponent_properties
        from .condition_component_type import ConditionComponent_type

        from .condition_component_properties import ConditionComponent_properties
        from .condition_component_type import ConditionComponent_type

        fields: dict[str, Callable[[Any], None]] = {
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "properties": lambda n : setattr(self, 'properties', n.get_object_value(ConditionComponent_properties)),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
            "type": lambda n : setattr(self, 'type', n.get_object_value(ConditionComponent_type)),
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
        writer.write_str_value("description", self.description)
        writer.write_str_value("name", self.name)
        writer.write_object_value("properties", self.properties)
        writer.write_str_value("title", self.title)
        writer.write_object_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

