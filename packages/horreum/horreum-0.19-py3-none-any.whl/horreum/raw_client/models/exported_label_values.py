from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .label_value_map import LabelValueMap

@dataclass
class ExportedLabelValues(AdditionalDataHolder, Parsable):
    """
    A map of label names to label values with the associated datasetId and runId
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # the unique dataset id
    dataset_id: Optional[int] = None
    # the run id that created the dataset
    run_id: Optional[int] = None
    # Start timestamp
    start: Optional[datetime.datetime] = None
    # Stop timestamp
    stop: Optional[datetime.datetime] = None
    # a map of label name to value
    values: Optional[LabelValueMap] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ExportedLabelValues:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ExportedLabelValues
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ExportedLabelValues()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .label_value_map import LabelValueMap

        from .label_value_map import LabelValueMap

        fields: dict[str, Callable[[Any], None]] = {
            "datasetId": lambda n : setattr(self, 'dataset_id', n.get_int_value()),
            "runId": lambda n : setattr(self, 'run_id', n.get_int_value()),
            "start": lambda n : setattr(self, 'start', n.get_datetime_value()),
            "stop": lambda n : setattr(self, 'stop', n.get_datetime_value()),
            "values": lambda n : setattr(self, 'values', n.get_object_value(LabelValueMap)),
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
        writer.write_int_value("datasetId", self.dataset_id)
        writer.write_int_value("runId", self.run_id)
        writer.write_datetime_value("start", self.start)
        writer.write_datetime_value("stop", self.stop)
        writer.write_object_value("values", self.values)
        writer.write_additional_data_value(self.additional_data)
    

