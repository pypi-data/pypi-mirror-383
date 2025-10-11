from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from warnings import warn

@dataclass
class ValidationError_error(AdditionalDataHolder, Parsable):
    """
    Validation Error Details
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The arguments property
    arguments: Optional[list[str]] = None
    # The code property
    code: Optional[str] = None
    # The details property
    details: Optional[str] = None
    # The evaluationPath property
    evaluation_path: Optional[str] = None
    # The instanceLocation property
    instance_location: Optional[str] = None
    # The message property
    message: Optional[str] = None
    # The messageKey property
    message_key: Optional[str] = None
    # The path property
    path: Optional[str] = None
    # The property property
    property_: Optional[str] = None
    # The schemaLocation property
    schema_location: Optional[str] = None
    # The schemaPath property
    schema_path: Optional[str] = None
    # Validation Error type
    type: Optional[str] = None
    # The valid property
    valid: Optional[bool] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ValidationError_error:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ValidationError_error
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ValidationError_error()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "arguments": lambda n : setattr(self, 'arguments', n.get_collection_of_primitive_values(str)),
            "code": lambda n : setattr(self, 'code', n.get_str_value()),
            "details": lambda n : setattr(self, 'details', n.get_str_value()),
            "evaluationPath": lambda n : setattr(self, 'evaluation_path', n.get_str_value()),
            "instanceLocation": lambda n : setattr(self, 'instance_location', n.get_str_value()),
            "message": lambda n : setattr(self, 'message', n.get_str_value()),
            "messageKey": lambda n : setattr(self, 'message_key', n.get_str_value()),
            "path": lambda n : setattr(self, 'path', n.get_str_value()),
            "property": lambda n : setattr(self, 'property_', n.get_str_value()),
            "schemaLocation": lambda n : setattr(self, 'schema_location', n.get_str_value()),
            "schemaPath": lambda n : setattr(self, 'schema_path', n.get_str_value()),
            "type": lambda n : setattr(self, 'type', n.get_str_value()),
            "valid": lambda n : setattr(self, 'valid', n.get_bool_value()),
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
        writer.write_collection_of_primitive_values("arguments", self.arguments)
        writer.write_str_value("code", self.code)
        writer.write_str_value("details", self.details)
        writer.write_str_value("evaluationPath", self.evaluation_path)
        writer.write_str_value("instanceLocation", self.instance_location)
        writer.write_str_value("message", self.message)
        writer.write_str_value("messageKey", self.message_key)
        writer.write_str_value("path", self.path)
        writer.write_str_value("property", self.property_)
        writer.write_str_value("schemaLocation", self.schema_location)
        writer.write_str_value("schemaPath", self.schema_path)
        writer.write_str_value("type", self.type)
        writer.write_bool_value("valid", self.valid)
        writer.write_additional_data_value(self.additional_data)
    

