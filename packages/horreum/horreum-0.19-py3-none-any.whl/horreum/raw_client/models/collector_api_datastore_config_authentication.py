from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .a_p_i_key_auth import APIKeyAuth
    from .no_auth import NoAuth
    from .username_pass_auth import UsernamePassAuth

@dataclass
class CollectorApiDatastoreConfig_authentication(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes APIKeyAuth, NoAuth, UsernamePassAuth
    """
    # Composed type representation for type APIKeyAuth
    a_p_i_key_auth: Optional[APIKeyAuth] = None
    # Composed type representation for type NoAuth
    no_auth: Optional[NoAuth] = None
    # Composed type representation for type UsernamePassAuth
    username_pass_auth: Optional[UsernamePassAuth] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CollectorApiDatastoreConfig_authentication:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CollectorApiDatastoreConfig_authentication
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("type")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = CollectorApiDatastoreConfig_authentication()
        if mapping_value and mapping_value.casefold() == "api-key".casefold():
            from .a_p_i_key_auth import APIKeyAuth

            result.a_p_i_key_auth = APIKeyAuth()
        elif mapping_value and mapping_value.casefold() == "none".casefold():
            from .no_auth import NoAuth

            result.no_auth = NoAuth()
        elif mapping_value and mapping_value.casefold() == "username".casefold():
            from .username_pass_auth import UsernamePassAuth

            result.username_pass_auth = UsernamePassAuth()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .a_p_i_key_auth import APIKeyAuth
        from .no_auth import NoAuth
        from .username_pass_auth import UsernamePassAuth

        if self.a_p_i_key_auth:
            return self.a_p_i_key_auth.get_field_deserializers()
        if self.no_auth:
            return self.no_auth.get_field_deserializers()
        if self.username_pass_auth:
            return self.username_pass_auth.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.a_p_i_key_auth:
            writer.write_object_value(None, self.a_p_i_key_auth)
        elif self.no_auth:
            writer.write_object_value(None, self.no_auth)
        elif self.username_pass_auth:
            writer.write_object_value(None, self.username_pass_auth)
    

