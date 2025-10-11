from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .key_type import KeyType

@dataclass
class ApiKeyResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The access property
    access: Optional[datetime.datetime] = None
    # The creation property
    creation: Optional[datetime.datetime] = None
    # The id property
    id: Optional[int] = None
    # The isRevoked property
    is_revoked: Optional[bool] = None
    # The name property
    name: Optional[str] = None
    # The toExpiration property
    to_expiration: Optional[int] = None
    # The type property
    type: Optional[KeyType] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ApiKeyResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ApiKeyResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ApiKeyResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .key_type import KeyType

        from .key_type import KeyType

        fields: dict[str, Callable[[Any], None]] = {
            "access": lambda n : setattr(self, 'access', n.get_datetime_value()),
            "creation": lambda n : setattr(self, 'creation', n.get_datetime_value()),
            "id": lambda n : setattr(self, 'id', n.get_int_value()),
            "isRevoked": lambda n : setattr(self, 'is_revoked', n.get_bool_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "toExpiration": lambda n : setattr(self, 'to_expiration', n.get_int_value()),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(KeyType)),
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
        writer.write_datetime_value("access", self.access)
        writer.write_datetime_value("creation", self.creation)
        writer.write_int_value("id", self.id)
        writer.write_bool_value("isRevoked", self.is_revoked)
        writer.write_str_value("name", self.name)
        writer.write_int_value("toExpiration", self.to_expiration)
        writer.write_enum_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

