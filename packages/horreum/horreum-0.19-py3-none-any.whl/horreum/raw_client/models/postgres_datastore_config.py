from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .postgres_datastore_config_authentication import PostgresDatastoreConfig_authentication

@dataclass
class PostgresDatastoreConfig(AdditionalDataHolder, Parsable):
    """
    Built in backend datastore
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The authentication property
    authentication: Optional[PostgresDatastoreConfig_authentication] = None
    # Built In
    built_in: Optional[bool] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PostgresDatastoreConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PostgresDatastoreConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PostgresDatastoreConfig()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .postgres_datastore_config_authentication import PostgresDatastoreConfig_authentication

        from .postgres_datastore_config_authentication import PostgresDatastoreConfig_authentication

        fields: dict[str, Callable[[Any], None]] = {
            "authentication": lambda n : setattr(self, 'authentication', n.get_object_value(PostgresDatastoreConfig_authentication)),
            "builtIn": lambda n : setattr(self, 'built_in', n.get_bool_value()),
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
        writer.write_object_value("authentication", self.authentication)
        writer.write_bool_value("builtIn", self.built_in)
        writer.write_additional_data_value(self.additional_data)
    

