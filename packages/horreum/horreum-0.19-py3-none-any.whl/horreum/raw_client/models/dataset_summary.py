from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .dataset_summary_access import DatasetSummary_access
    from .indexed_label_value_map import IndexedLabelValueMap
    from .schema_usage import SchemaUsage
    from .validation_error import ValidationError

@dataclass
class DatasetSummary(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Access rights for the test. This defines the visibility of the Test in the UI
    access: Optional[DatasetSummary_access] = None
    # Dataset description
    description: Optional[str] = None
    # Unique Dataset ID
    id: Optional[int] = None
    # Ordinal position of Dataset Summary on returned List
    ordinal: Optional[int] = None
    # Name of the team that owns the test. Users must belong to the team that owns a test to make modifications
    owner: Optional[str] = None
    # Run ID that Dataset relates to
    run_id: Optional[int] = None
    # List of Schema usages
    schemas: Optional[list[SchemaUsage]] = None
    # Run Start timestamp
    start: Optional[int] = None
    # Run Stop timestamp
    stop: Optional[int] = None
    # Test ID that Dataset relates to
    test_id: Optional[int] = None
    # Test name that the Dataset relates to
    testname: Optional[str] = None
    # List of Validation Errors
    validation_errors: Optional[list[ValidationError]] = None
    # map of view component ids to the LabelValueMap to render the component for this dataset
    view: Optional[IndexedLabelValueMap] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> DatasetSummary:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: DatasetSummary
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return DatasetSummary()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .dataset_summary_access import DatasetSummary_access
        from .indexed_label_value_map import IndexedLabelValueMap
        from .schema_usage import SchemaUsage
        from .validation_error import ValidationError

        from .dataset_summary_access import DatasetSummary_access
        from .indexed_label_value_map import IndexedLabelValueMap
        from .schema_usage import SchemaUsage
        from .validation_error import ValidationError

        fields: dict[str, Callable[[Any], None]] = {
            "access": lambda n : setattr(self, 'access', n.get_enum_value(DatasetSummary_access)),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_int_value()),
            "ordinal": lambda n : setattr(self, 'ordinal', n.get_int_value()),
            "owner": lambda n : setattr(self, 'owner', n.get_str_value()),
            "runId": lambda n : setattr(self, 'run_id', n.get_int_value()),
            "schemas": lambda n : setattr(self, 'schemas', n.get_collection_of_object_values(SchemaUsage)),
            "start": lambda n : setattr(self, 'start', n.get_int_value()),
            "stop": lambda n : setattr(self, 'stop', n.get_int_value()),
            "testId": lambda n : setattr(self, 'test_id', n.get_int_value()),
            "testname": lambda n : setattr(self, 'testname', n.get_str_value()),
            "validationErrors": lambda n : setattr(self, 'validation_errors', n.get_collection_of_object_values(ValidationError)),
            "view": lambda n : setattr(self, 'view', n.get_object_value(IndexedLabelValueMap)),
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
        writer.write_str_value("description", self.description)
        writer.write_int_value("id", self.id)
        writer.write_int_value("ordinal", self.ordinal)
        writer.write_str_value("owner", self.owner)
        writer.write_int_value("runId", self.run_id)
        writer.write_collection_of_object_values("schemas", self.schemas)
        writer.write_int_value("start", self.start)
        writer.write_int_value("stop", self.stop)
        writer.write_int_value("testId", self.test_id)
        writer.write_str_value("testname", self.testname)
        writer.write_collection_of_object_values("validationErrors", self.validation_errors)
        writer.write_object_value("view", self.view)
        writer.write_additional_data_value(self.additional_data)
    

