from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class KeycloakConfig(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Keycloak client ID in Horreum realm for User Interface
    client_id: Optional[str] = None
    # Keycloak realm securing Horreum instance
    realm: Optional[str] = None
    # URL of Keycloak instance securing Horreum
    url: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> KeycloakConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: KeycloakConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return KeycloakConfig()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "clientId": lambda n : setattr(self, 'client_id', n.get_str_value()),
            "realm": lambda n : setattr(self, 'realm', n.get_str_value()),
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
        writer.write_str_value("clientId", self.client_id)
        writer.write_str_value("realm", self.realm)
        writer.write_str_value("url", self.url)
        writer.write_additional_data_value(self.additional_data)
    

