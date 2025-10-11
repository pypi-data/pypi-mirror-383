from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .dataset import Dataset
    from .run_access import Run_access
    from .validation_error import ValidationError

@dataclass
class Run(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Access rights for the test. This defines the visibility of the Test in the UI
    access: Optional[Run_access] = None
    # Run result payload
    data: Optional[str] = None
    # Collection of Datasets derived from Run payload
    datasets: Optional[list[Dataset]] = None
    # Run description
    description: Optional[str] = None
    # Unique Run ID
    id: Optional[int] = None
    # JSON metadata related to run, can be tool configuration etc
    metadata: Optional[str] = None
    # Name of the team that owns the test. Users must belong to the team that owns a test to make modifications
    owner: Optional[str] = None
    # Run Start timestamp
    start: Optional[int] = None
    # Run Stop timestamp
    stop: Optional[int] = None
    # Test ID run relates to
    testid: Optional[int] = None
    # Has Run been deleted from UI
    trashed: Optional[bool] = None
    # Collection of Validation Errors in Run payload
    validation_errors: Optional[list[ValidationError]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Run:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Run
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Run()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .dataset import Dataset
        from .run_access import Run_access
        from .validation_error import ValidationError

        from .dataset import Dataset
        from .run_access import Run_access
        from .validation_error import ValidationError

        fields: dict[str, Callable[[Any], None]] = {
            "access": lambda n : setattr(self, 'access', n.get_enum_value(Run_access)),
            "data": lambda n : setattr(self, 'data', n.get_str_value()),
            "datasets": lambda n : setattr(self, 'datasets', n.get_collection_of_object_values(Dataset)),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_int_value()),
            "metadata": lambda n : setattr(self, 'metadata', n.get_str_value()),
            "owner": lambda n : setattr(self, 'owner', n.get_str_value()),
            "start": lambda n : setattr(self, 'start', n.get_int_value()),
            "stop": lambda n : setattr(self, 'stop', n.get_int_value()),
            "testid": lambda n : setattr(self, 'testid', n.get_int_value()),
            "trashed": lambda n : setattr(self, 'trashed', n.get_bool_value()),
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
        writer.write_collection_of_object_values("datasets", self.datasets)
        writer.write_str_value("description", self.description)
        writer.write_int_value("id", self.id)
        writer.write_str_value("metadata", self.metadata)
        writer.write_str_value("owner", self.owner)
        writer.write_int_value("start", self.start)
        writer.write_int_value("stop", self.stop)
        writer.write_int_value("testid", self.testid)
        writer.write_bool_value("trashed", self.trashed)
        writer.write_collection_of_object_values("validationErrors", self.validation_errors)
        writer.write_additional_data_value(self.additional_data)
    

