from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .schema import Schema

@dataclass
class SchemaQueryResult(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Count of available Schemas. This is a count of Schemas that the current user has access to
    count: Optional[int] = None
    # Array of Schemas
    schemas: Optional[list[Schema]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SchemaQueryResult:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SchemaQueryResult
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SchemaQueryResult()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .schema import Schema

        from .schema import Schema

        fields: dict[str, Callable[[Any], None]] = {
            "count": lambda n : setattr(self, 'count', n.get_int_value()),
            "schemas": lambda n : setattr(self, 'schemas', n.get_collection_of_object_values(Schema)),
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
        writer.write_int_value("count", self.count)
        writer.write_collection_of_object_values("schemas", self.schemas)
        writer.write_additional_data_value(self.additional_data)
    

