from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .extractor import Extractor
    from .label_access import Label_access

@dataclass
class Label(AdditionalDataHolder, Parsable):
    """
    A Label is a core component of Horreum, defining which components of the JSON document are part of a KPI and how the metric values are calculated
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Access rights for the test. This defines the visibility of the Test in the UI
    access: Optional[Label_access] = None
    # A collection of Extractors, that will be combined in the Combination Function
    extractors: Optional[list[Extractor]] = None
    # Is Label a filtering label? Filtering labels contains values that are used to filter datasets for comparison
    filtering: Optional[bool] = None
    # A Combination Function that defines how values from Extractors are combined to produce a Label Value
    function: Optional[str] = None
    # Unique ID for Label
    id: Optional[int] = None
    # Is Label a metrics label? Metrics labels are contain Metrics that are used for comparison
    metrics: Optional[bool] = None
    # Name for label. NOTE: all Labels are considered to have the same semantic meaning throughout the entire system
    name: Optional[str] = None
    # Name of the team that owns the test. Users must belong to the team that owns a test to make modifications
    owner: Optional[str] = None
    # Schema ID that the Label relates to
    schema_id: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Label:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Label
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Label()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .extractor import Extractor
        from .label_access import Label_access

        from .extractor import Extractor
        from .label_access import Label_access

        fields: dict[str, Callable[[Any], None]] = {
            "access": lambda n : setattr(self, 'access', n.get_enum_value(Label_access)),
            "extractors": lambda n : setattr(self, 'extractors', n.get_collection_of_object_values(Extractor)),
            "filtering": lambda n : setattr(self, 'filtering', n.get_bool_value()),
            "function": lambda n : setattr(self, 'function', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_int_value()),
            "metrics": lambda n : setattr(self, 'metrics', n.get_bool_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "owner": lambda n : setattr(self, 'owner', n.get_str_value()),
            "schemaId": lambda n : setattr(self, 'schema_id', n.get_int_value()),
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
        writer.write_collection_of_object_values("extractors", self.extractors)
        writer.write_bool_value("filtering", self.filtering)
        writer.write_str_value("function", self.function)
        writer.write_int_value("id", self.id)
        writer.write_bool_value("metrics", self.metrics)
        writer.write_str_value("name", self.name)
        writer.write_str_value("owner", self.owner)
        writer.write_int_value("schemaId", self.schema_id)
        writer.write_additional_data_value(self.additional_data)
    

