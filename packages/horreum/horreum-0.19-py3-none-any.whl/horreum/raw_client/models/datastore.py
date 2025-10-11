from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .datastore_access import Datastore_access
    from .datastore_config import Datastore_config
    from .datastore_type import Datastore_type

@dataclass
class Datastore(AdditionalDataHolder, Parsable):
    """
    Instance of backend datastore
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Access rights for the test. This defines the visibility of the Test in the UI
    access: Optional[Datastore_access] = None
    # The config property
    config: Optional[Datastore_config] = None
    # Unique Datastore id
    id: Optional[int] = None
    # Name of the datastore, used to identify the datastore in the Test definition
    name: Optional[str] = None
    # Name of the team that owns the test. Users must belong to the team that owns a test to make modifications
    owner: Optional[str] = None
    # Type of backend datastore
    type: Optional[Datastore_type] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Datastore:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Datastore
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Datastore()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .datastore_access import Datastore_access
        from .datastore_config import Datastore_config
        from .datastore_type import Datastore_type

        from .datastore_access import Datastore_access
        from .datastore_config import Datastore_config
        from .datastore_type import Datastore_type

        fields: dict[str, Callable[[Any], None]] = {
            "access": lambda n : setattr(self, 'access', n.get_enum_value(Datastore_access)),
            "config": lambda n : setattr(self, 'config', n.get_object_value(Datastore_config)),
            "id": lambda n : setattr(self, 'id', n.get_int_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "owner": lambda n : setattr(self, 'owner', n.get_str_value()),
            "type": lambda n : setattr(self, 'type', n.get_enum_value(Datastore_type)),
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
        writer.write_object_value("config", self.config)
        writer.write_int_value("id", self.id)
        writer.write_str_value("name", self.name)
        writer.write_str_value("owner", self.owner)
        writer.write_enum_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

