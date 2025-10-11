from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ....models.user_data import UserData

@dataclass
class CreateUserPostRequestBody(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The password property
    password: Optional[str] = None
    # The roles property
    roles: Optional[list[str]] = None
    # The team property
    team: Optional[str] = None
    # The user property
    user: Optional[UserData] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CreateUserPostRequestBody:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CreateUserPostRequestBody
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CreateUserPostRequestBody()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from ....models.user_data import UserData

        from ....models.user_data import UserData

        fields: dict[str, Callable[[Any], None]] = {
            "password": lambda n : setattr(self, 'password', n.get_str_value()),
            "roles": lambda n : setattr(self, 'roles', n.get_collection_of_primitive_values(str)),
            "team": lambda n : setattr(self, 'team', n.get_str_value()),
            "user": lambda n : setattr(self, 'user', n.get_object_value(UserData)),
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
        writer.write_str_value("password", self.password)
        writer.write_collection_of_primitive_values("roles", self.roles)
        writer.write_str_value("team", self.team)
        writer.write_object_value("user", self.user)
        writer.write_additional_data_value(self.additional_data)
    

