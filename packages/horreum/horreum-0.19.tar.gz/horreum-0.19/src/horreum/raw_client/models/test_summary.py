from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .test_summary_access import TestSummary_access

@dataclass
class TestSummary(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Access rights for the test. This defines the visibility of the Test in the UI
    access: Optional[TestSummary_access] = None
    # Total number of Datasets for the Test
    datasets: Optional[float] = None
    # Datastore id
    datastore_id: Optional[int] = None
    # Description of the test
    description: Optional[str] = None
    # Name of folder that the test is stored in. Folders allow tests to be organised in the UI
    folder: Optional[str] = None
    # ID of tests
    id: Optional[int] = None
    # Test name
    name: Optional[str] = None
    # Name of the team that owns the test. Users must belong to the team that owns a test to make modifications
    owner: Optional[str] = None
    # Total number of Runs for the Test
    runs: Optional[float] = None
    # Subscriptions for each test for authenticated user
    watching: Optional[list[str]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> TestSummary:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: TestSummary
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return TestSummary()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .test_summary_access import TestSummary_access

        from .test_summary_access import TestSummary_access

        fields: dict[str, Callable[[Any], None]] = {
            "access": lambda n : setattr(self, 'access', n.get_enum_value(TestSummary_access)),
            "datasets": lambda n : setattr(self, 'datasets', n.get_float_value()),
            "datastoreId": lambda n : setattr(self, 'datastore_id', n.get_int_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "folder": lambda n : setattr(self, 'folder', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_int_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "owner": lambda n : setattr(self, 'owner', n.get_str_value()),
            "runs": lambda n : setattr(self, 'runs', n.get_float_value()),
            "watching": lambda n : setattr(self, 'watching', n.get_collection_of_primitive_values(str)),
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
        writer.write_float_value("datasets", self.datasets)
        writer.write_int_value("datastoreId", self.datastore_id)
        writer.write_str_value("description", self.description)
        writer.write_str_value("folder", self.folder)
        writer.write_int_value("id", self.id)
        writer.write_str_value("name", self.name)
        writer.write_str_value("owner", self.owner)
        writer.write_float_value("runs", self.runs)
        writer.write_collection_of_primitive_values("watching", self.watching)
        writer.write_additional_data_value(self.additional_data)
    

