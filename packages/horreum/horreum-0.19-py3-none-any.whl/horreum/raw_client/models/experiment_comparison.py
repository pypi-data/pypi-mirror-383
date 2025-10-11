from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class ExperimentComparison(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Model JSON configuration
    config: Optional[str] = None
    # Name of comparison model
    model: Optional[str] = None
    # Variable ID to run experiment against
    variable_id: Optional[int] = None
    # Variable Name to run experiment against
    variable_name: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ExperimentComparison:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ExperimentComparison
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ExperimentComparison()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "config": lambda n : setattr(self, 'config', n.get_str_value()),
            "model": lambda n : setattr(self, 'model', n.get_str_value()),
            "variableId": lambda n : setattr(self, 'variable_id', n.get_int_value()),
            "variableName": lambda n : setattr(self, 'variable_name', n.get_str_value()),
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
        writer.write_str_value("config", self.config)
        writer.write_str_value("model", self.model)
        writer.write_int_value("variableId", self.variable_id)
        writer.write_str_value("variableName", self.variable_name)
        writer.write_additional_data_value(self.additional_data)
    

