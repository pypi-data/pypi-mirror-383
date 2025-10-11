from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class Watch(AdditionalDataHolder, Parsable):
    """
    Watcher object associated with test
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The id property
    id: Optional[int] = None
    # The optout property
    optout: Optional[list[str]] = None
    # The teams property
    teams: Optional[list[str]] = None
    # The testId property
    test_id: Optional[int] = None
    # The users property
    users: Optional[list[str]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Watch:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Watch
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Watch()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "id": lambda n : setattr(self, 'id', n.get_int_value()),
            "optout": lambda n : setattr(self, 'optout', n.get_collection_of_primitive_values(str)),
            "teams": lambda n : setattr(self, 'teams', n.get_collection_of_primitive_values(str)),
            "testId": lambda n : setattr(self, 'test_id', n.get_int_value()),
            "users": lambda n : setattr(self, 'users', n.get_collection_of_primitive_values(str)),
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
        writer.write_int_value("id", self.id)
        writer.write_collection_of_primitive_values("optout", self.optout)
        writer.write_collection_of_primitive_values("teams", self.teams)
        writer.write_int_value("testId", self.test_id)
        writer.write_collection_of_primitive_values("users", self.users)
        writer.write_additional_data_value(self.additional_data)
    

