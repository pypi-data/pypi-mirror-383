from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .test_access import Test_access
    from .transformer import Transformer

@dataclass
class Test(AdditionalDataHolder, Parsable):
    """
    Represents a Test. Tests are typically equivalent to a particular benchmark
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Access rights for the test. This defines the visibility of the Test in the UI
    access: Optional[Test_access] = None
    # URL to external service that can be called to compare runs.  This is typically an external reporting/visulization service
    compare_url: Optional[str] = None
    # backend ID for backing datastore
    datastore_id: Optional[int] = None
    # Description of the test
    description: Optional[str] = None
    # Filter function to filter out datasets that are comparable for the purpose of change detection
    fingerprint_filter: Optional[str] = None
    # Array of Label names that are used to create a fingerprint 
    fingerprint_labels: Optional[list[str]] = None
    # Name of folder that the test is stored in. Folders allow tests to be organised in the UI
    folder: Optional[str] = None
    # Unique Test id
    id: Optional[int] = None
    # Test name
    name: Optional[str] = None
    # Are notifications enabled for the test
    notifications_enabled: Optional[bool] = None
    # Name of the team that owns the test. Users must belong to the team that owns a test to make modifications
    owner: Optional[str] = None
    # Label function to modify timeline labels to a produce a value used for ordering datapoints
    timeline_function: Optional[str] = None
    # List of label names that are used for determining metric to use as the time series
    timeline_labels: Optional[list[str]] = None
    # Array for transformers defined for the Test
    transformers: Optional[list[Transformer]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Test:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Test
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Test()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .test_access import Test_access
        from .transformer import Transformer

        from .test_access import Test_access
        from .transformer import Transformer

        fields: dict[str, Callable[[Any], None]] = {
            "access": lambda n : setattr(self, 'access', n.get_enum_value(Test_access)),
            "compareUrl": lambda n : setattr(self, 'compare_url', n.get_str_value()),
            "datastoreId": lambda n : setattr(self, 'datastore_id', n.get_int_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "fingerprintFilter": lambda n : setattr(self, 'fingerprint_filter', n.get_str_value()),
            "fingerprintLabels": lambda n : setattr(self, 'fingerprint_labels', n.get_collection_of_primitive_values(str)),
            "folder": lambda n : setattr(self, 'folder', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_int_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "notificationsEnabled": lambda n : setattr(self, 'notifications_enabled', n.get_bool_value()),
            "owner": lambda n : setattr(self, 'owner', n.get_str_value()),
            "timelineFunction": lambda n : setattr(self, 'timeline_function', n.get_str_value()),
            "timelineLabels": lambda n : setattr(self, 'timeline_labels', n.get_collection_of_primitive_values(str)),
            "transformers": lambda n : setattr(self, 'transformers', n.get_collection_of_object_values(Transformer)),
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
        writer.write_str_value("compareUrl", self.compare_url)
        writer.write_int_value("datastoreId", self.datastore_id)
        writer.write_str_value("description", self.description)
        writer.write_str_value("fingerprintFilter", self.fingerprint_filter)
        writer.write_collection_of_primitive_values("fingerprintLabels", self.fingerprint_labels)
        writer.write_str_value("folder", self.folder)
        writer.write_int_value("id", self.id)
        writer.write_str_value("name", self.name)
        writer.write_bool_value("notificationsEnabled", self.notifications_enabled)
        writer.write_str_value("owner", self.owner)
        writer.write_str_value("timelineFunction", self.timeline_function)
        writer.write_collection_of_primitive_values("timelineLabels", self.timeline_labels)
        writer.write_collection_of_object_values("transformers", self.transformers)
        writer.write_additional_data_value(self.additional_data)
    

