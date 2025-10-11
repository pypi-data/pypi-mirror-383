from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class UserData(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The email property
    email: Optional[str] = None
    # The firstName property
    first_name: Optional[str] = None
    # The id property
    id: Optional[str] = None
    # The lastName property
    last_name: Optional[str] = None
    # The username property
    username: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> UserData:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: UserData
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return UserData()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "email": lambda n : setattr(self, 'email', n.get_str_value()),
            "firstName": lambda n : setattr(self, 'first_name', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "lastName": lambda n : setattr(self, 'last_name', n.get_str_value()),
            "username": lambda n : setattr(self, 'username', n.get_str_value()),
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
        writer.write_str_value("email", self.email)
        writer.write_str_value("firstName", self.first_name)
        writer.write_str_value("id", self.id)
        writer.write_str_value("lastName", self.last_name)
        writer.write_str_value("username", self.username)
        writer.write_additional_data_value(self.additional_data)
    

