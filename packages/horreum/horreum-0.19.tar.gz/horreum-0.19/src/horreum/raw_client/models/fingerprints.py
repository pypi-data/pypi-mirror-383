from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .fingerprint_value import FingerprintValue

@dataclass
class Fingerprints(AdditionalDataHolder, Parsable):
    """
    A list of Fingerprints representing one dataset
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The values property
    values: Optional[list[FingerprintValue]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Fingerprints:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Fingerprints
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Fingerprints()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .fingerprint_value import FingerprintValue

        from .fingerprint_value import FingerprintValue

        fields: dict[str, Callable[[Any], None]] = {
            "values": lambda n : setattr(self, 'values', n.get_collection_of_object_values(FingerprintValue)),
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
        writer.write_collection_of_object_values("values", self.values)
        writer.write_additional_data_value(self.additional_data)
    

