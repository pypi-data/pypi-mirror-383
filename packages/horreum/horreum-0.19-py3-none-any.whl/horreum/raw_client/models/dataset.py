from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .dataset_access import Dataset_access
    from .validation_error import ValidationError

@dataclass
class Dataset(AdditionalDataHolder, Parsable):
    """
    A dataset is the JSON document used as the basis for all comparisons and reporting
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Access rights for the test. This defines the visibility of the Test in the UI
    access: Optional[Dataset_access] = None
    # Data payload
    data: Optional[str] = None
    # Run description
    description: Optional[str] = None
    # Dataset Unique ID
    id: Optional[int] = None
    # Dataset ordinal for ordered list of Datasets derived from a Run
    ordinal: Optional[int] = None
    # Name of the team that owns the test. Users must belong to the team that owns a test to make modifications
    owner: Optional[str] = None
    # Run ID that Dataset relates to
    run_id: Optional[int] = None
    # Run Start timestamp
    start: Optional[int] = None
    # Run Stop timestamp
    stop: Optional[int] = None
    # Test ID that Dataset relates to
    testid: Optional[int] = None
    # List of Validation Errors
    validation_errors: Optional[list[ValidationError]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Dataset:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Dataset
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Dataset()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .dataset_access import Dataset_access
        from .validation_error import ValidationError

        from .dataset_access import Dataset_access
        from .validation_error import ValidationError

        fields: dict[str, Callable[[Any], None]] = {
            "access": lambda n : setattr(self, 'access', n.get_enum_value(Dataset_access)),
            "data": lambda n : setattr(self, 'data', n.get_str_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_int_value()),
            "ordinal": lambda n : setattr(self, 'ordinal', n.get_int_value()),
            "owner": lambda n : setattr(self, 'owner', n.get_str_value()),
            "runId": lambda n : setattr(self, 'run_id', n.get_int_value()),
            "start": lambda n : setattr(self, 'start', n.get_int_value()),
            "stop": lambda n : setattr(self, 'stop', n.get_int_value()),
            "testid": lambda n : setattr(self, 'testid', n.get_int_value()),
            "validationErrors": lambda n : setattr(self, 'validation_errors', n.get_collection_of_object_values(ValidationError)),
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
        writer.write_str_value("data", self.data)
        writer.write_str_value("description", self.description)
        writer.write_int_value("id", self.id)
        writer.write_int_value("ordinal", self.ordinal)
        writer.write_str_value("owner", self.owner)
        writer.write_int_value("runId", self.run_id)
        writer.write_int_value("start", self.start)
        writer.write_int_value("stop", self.stop)
        writer.write_int_value("testid", self.testid)
        writer.write_collection_of_object_values("validationErrors", self.validation_errors)
        writer.write_additional_data_value(self.additional_data)
    

