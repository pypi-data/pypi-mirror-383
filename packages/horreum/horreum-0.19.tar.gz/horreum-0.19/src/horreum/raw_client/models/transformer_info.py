from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class TransformerInfo(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Schema ID
    schema_id: Optional[int] = None
    # Schema name
    schema_name: Optional[str] = None
    # Schema uri
    schema_uri: Optional[str] = None
    # Transformer ID
    transformer_id: Optional[int] = None
    # Transformer name
    transformer_name: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> TransformerInfo:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: TransformerInfo
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return TransformerInfo()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "schemaId": lambda n : setattr(self, 'schema_id', n.get_int_value()),
            "schemaName": lambda n : setattr(self, 'schema_name', n.get_str_value()),
            "schemaUri": lambda n : setattr(self, 'schema_uri', n.get_str_value()),
            "transformerId": lambda n : setattr(self, 'transformer_id', n.get_int_value()),
            "transformerName": lambda n : setattr(self, 'transformer_name', n.get_str_value()),
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
        writer.write_int_value("schemaId", self.schema_id)
        writer.write_str_value("schemaName", self.schema_name)
        writer.write_str_value("schemaUri", self.schema_uri)
        writer.write_int_value("transformerId", self.transformer_id)
        writer.write_str_value("transformerName", self.transformer_name)
        writer.write_additional_data_value(self.additional_data)
    

