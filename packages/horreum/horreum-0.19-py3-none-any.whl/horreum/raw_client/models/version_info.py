from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class VersionInfo(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Commit of Horreum
    commit: Optional[str] = None
    # Privacy statement
    privacy_statement: Optional[str] = None
    # Timestamp of server startup
    start_timestamp: Optional[int] = None
    # Version of Horreum
    version: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VersionInfo:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VersionInfo
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VersionInfo()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "commit": lambda n : setattr(self, 'commit', n.get_str_value()),
            "privacyStatement": lambda n : setattr(self, 'privacy_statement', n.get_str_value()),
            "startTimestamp": lambda n : setattr(self, 'start_timestamp', n.get_int_value()),
            "version": lambda n : setattr(self, 'version', n.get_str_value()),
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
        writer.write_str_value("commit", self.commit)
        writer.write_str_value("privacyStatement", self.privacy_statement)
        writer.write_int_value("startTimestamp", self.start_timestamp)
        writer.write_str_value("version", self.version)
        writer.write_additional_data_value(self.additional_data)
    

