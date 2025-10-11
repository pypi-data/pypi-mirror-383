from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .change_detection import ChangeDetection

@dataclass
class Variable(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The calculation property
    calculation: Optional[str] = None
    # The changeDetection property
    change_detection: Optional[list[ChangeDetection]] = None
    # The group property
    group: Optional[str] = None
    # The id property
    id: Optional[int] = None
    # The labels property
    labels: Optional[list[str]] = None
    # The name property
    name: Optional[str] = None
    # The order property
    order: Optional[int] = None
    # The testId property
    test_id: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Variable:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Variable
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Variable()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .change_detection import ChangeDetection

        from .change_detection import ChangeDetection

        fields: dict[str, Callable[[Any], None]] = {
            "calculation": lambda n : setattr(self, 'calculation', n.get_str_value()),
            "changeDetection": lambda n : setattr(self, 'change_detection', n.get_collection_of_object_values(ChangeDetection)),
            "group": lambda n : setattr(self, 'group', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_int_value()),
            "labels": lambda n : setattr(self, 'labels', n.get_collection_of_primitive_values(str)),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "order": lambda n : setattr(self, 'order', n.get_int_value()),
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
        writer.write_str_value("calculation", self.calculation)
        writer.write_collection_of_object_values("changeDetection", self.change_detection)
        writer.write_str_value("group", self.group)
        writer.write_int_value("id", self.id)
        writer.write_collection_of_primitive_values("labels", self.labels)
        writer.write_str_value("name", self.name)
        writer.write_int_value("order", self.order)
        writer.write_int_value("testId", self.test_id)
        writer.write_additional_data_value(self.additional_data)
    

