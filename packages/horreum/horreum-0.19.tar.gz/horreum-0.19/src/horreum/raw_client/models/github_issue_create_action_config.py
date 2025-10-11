from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class GithubIssueCreateActionConfig(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Object markdown formatter
    formatter: Optional[str] = None
    # GitHub repo owner
    owner: Optional[str] = None
    # GitHub repo name
    repo: Optional[str] = None
    # GitHub issue title
    title: Optional[str] = None
    # Action type
    type: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GithubIssueCreateActionConfig:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GithubIssueCreateActionConfig
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GithubIssueCreateActionConfig()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "formatter": lambda n : setattr(self, 'formatter', n.get_str_value()),
            "owner": lambda n : setattr(self, 'owner', n.get_str_value()),
            "repo": lambda n : setattr(self, 'repo', n.get_str_value()),
            "title": lambda n : setattr(self, 'title', n.get_str_value()),
            "type": lambda n : setattr(self, 'type', n.get_str_value()),
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
        writer.write_str_value("formatter", self.formatter)
        writer.write_str_value("owner", self.owner)
        writer.write_str_value("repo", self.repo)
        writer.write_str_value("title", self.title)
        writer.write_str_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

