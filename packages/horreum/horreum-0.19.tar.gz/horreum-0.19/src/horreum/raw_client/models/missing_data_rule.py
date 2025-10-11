from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class MissingDataRule(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The condition property
    condition: Optional[str] = None
    # The id property
    id: Optional[int] = None
    # The labels property
    labels: Optional[list[str]] = None
    # The lastNotification property
    last_notification: Optional[datetime.datetime] = None
    # The maxStaleness property
    max_staleness: Optional[int] = None
    # The name property
    name: Optional[str] = None
    # The testId property
    test_id: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> MissingDataRule:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: MissingDataRule
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return MissingDataRule()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "condition": lambda n : setattr(self, 'condition', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_int_value()),
            "labels": lambda n : setattr(self, 'labels', n.get_collection_of_primitive_values(str)),
            "lastNotification": lambda n : setattr(self, 'last_notification', n.get_datetime_value()),
            "maxStaleness": lambda n : setattr(self, 'max_staleness', n.get_int_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "testId": lambda n : setattr(self, 'test_id', n.get_int_value()),
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
        writer.write_str_value("condition", self.condition)
        writer.write_int_value("id", self.id)
        writer.write_collection_of_primitive_values("labels", self.labels)
        writer.write_datetime_value("lastNotification", self.last_notification)
        writer.write_int_value("maxStaleness", self.max_staleness)
        writer.write_str_value("name", self.name)
        writer.write_int_value("testId", self.test_id)
        writer.write_additional_data_value(self.additional_data)
    

