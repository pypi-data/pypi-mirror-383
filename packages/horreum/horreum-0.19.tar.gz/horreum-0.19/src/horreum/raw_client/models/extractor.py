from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class Extractor(AdditionalDataHolder, Parsable):
    """
    An Extractor defines how values are extracted from a JSON document, for use in Labels etc.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Does the JSON path expression reference an Array?
    isarray: Optional[bool] = None
    # JSON path expression defining the location of the extractor value in the JSON document. This is a pSQL json path expression
    jsonpath: Optional[str] = None
    # Name of extractor. This name is used in Combination Functions to refer to values by name
    name: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Extractor:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Extractor
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Extractor()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "isarray": lambda n : setattr(self, 'isarray', n.get_bool_value()),
            "jsonpath": lambda n : setattr(self, 'jsonpath', n.get_str_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
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
        writer.write_bool_value("isarray", self.isarray)
        writer.write_str_value("jsonpath", self.jsonpath)
        writer.write_str_value("name", self.name)
        writer.write_additional_data_value(self.additional_data)
    

