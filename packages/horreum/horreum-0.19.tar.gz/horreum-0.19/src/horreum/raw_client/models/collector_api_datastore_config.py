from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .collector_api_datastore_config_authentication import CollectorApiDatastoreConfig_authentication

@dataclass
class CollectorApiDatastoreConfig(AdditionalDataHolder, Parsable):
    """
    Type of backend datastore
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The authentication property
    authentication: Optional[CollectorApiDatastoreConfig_authentication] = None
    # Built In
    built_in: Optional[bool] = None
    # Collector url, e.g. https://collector.foci.life/api/v1/image-stats
    url: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CollectorApiDatastoreConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CollectorApiDatastoreConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CollectorApiDatastoreConfig()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .collector_api_datastore_config_authentication import CollectorApiDatastoreConfig_authentication

        from .collector_api_datastore_config_authentication import CollectorApiDatastoreConfig_authentication

        fields: dict[str, Callable[[Any], None]] = {
            "authentication": lambda n : setattr(self, 'authentication', n.get_object_value(CollectorApiDatastoreConfig_authentication)),
            "builtIn": lambda n : setattr(self, 'built_in', n.get_bool_value()),
            "url": lambda n : setattr(self, 'url', n.get_str_value()),
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
        writer.write_str_value("url", self.url)
        writer.write_additional_data_value(self.additional_data)
    

