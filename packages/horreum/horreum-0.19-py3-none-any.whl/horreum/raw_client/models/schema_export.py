from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .label import Label
    from .schema_export_access import SchemaExport_access
    from .transformer import Transformer

@dataclass
class SchemaExport(AdditionalDataHolder, Parsable):
    """
    Represents a Schema with all associated data used for export/import operations.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Access rights for the test. This defines the visibility of the Test in the UI
    access: Optional[SchemaExport_access] = None
    # Schema Description
    description: Optional[str] = None
    # Unique Schema ID
    id: Optional[int] = None
    # Array of Labels associated with schema
    labels: Optional[list[Label]] = None
    # Schema name
    name: Optional[str] = None
    # Name of the team that owns the test. Users must belong to the team that owns a test to make modifications
    owner: Optional[str] = None
    # JSON validation schema. Used to validate uploaded JSON documents
    schema: Optional[str] = None
    # Array of Transformers associated with schema
    transformers: Optional[list[Transformer]] = None
    # Unique, versioned schema URI
    uri: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SchemaExport:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SchemaExport
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SchemaExport()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .label import Label
        from .schema_export_access import SchemaExport_access
        from .transformer import Transformer

        from .label import Label
        from .schema_export_access import SchemaExport_access
        from .transformer import Transformer

        fields: dict[str, Callable[[Any], None]] = {
            "access": lambda n : setattr(self, 'access', n.get_enum_value(SchemaExport_access)),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_int_value()),
            "labels": lambda n : setattr(self, 'labels', n.get_collection_of_object_values(Label)),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "owner": lambda n : setattr(self, 'owner', n.get_str_value()),
            "schema": lambda n : setattr(self, 'schema', n.get_str_value()),
            "transformers": lambda n : setattr(self, 'transformers', n.get_collection_of_object_values(Transformer)),
            "uri": lambda n : setattr(self, 'uri', n.get_str_value()),
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
        writer.write_enum_value("access", self.access)
        writer.write_str_value("description", self.description)
        writer.write_int_value("id", self.id)
        writer.write_collection_of_object_values("labels", self.labels)
        writer.write_str_value("name", self.name)
        writer.write_str_value("owner", self.owner)
        writer.write_str_value("schema", self.schema)
        writer.write_collection_of_object_values("transformers", self.transformers)
        writer.write_str_value("uri", self.uri)
        writer.write_additional_data_value(self.additional_data)
    

