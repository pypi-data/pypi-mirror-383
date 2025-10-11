from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .collector_api_datastore_config import CollectorApiDatastoreConfig
    from .elasticsearch_datastore_config import ElasticsearchDatastoreConfig
    from .postgres_datastore_config import PostgresDatastoreConfig

@dataclass
class Datastore_config(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes CollectorApiDatastoreConfig, ElasticsearchDatastoreConfig, PostgresDatastoreConfig
    """
    # Composed type representation for type CollectorApiDatastoreConfig
    collector_api_datastore_config: Optional[CollectorApiDatastoreConfig] = None
    # Composed type representation for type ElasticsearchDatastoreConfig
    elasticsearch_datastore_config: Optional[ElasticsearchDatastoreConfig] = None
    # Composed type representation for type PostgresDatastoreConfig
    postgres_datastore_config: Optional[PostgresDatastoreConfig] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Datastore_config:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Datastore_config
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = Datastore_config()
        if mapping_value and mapping_value.casefold() == "CollectorApiDatastoreConfig".casefold():
            from .collector_api_datastore_config import CollectorApiDatastoreConfig

            result.collector_api_datastore_config = CollectorApiDatastoreConfig()
        elif mapping_value and mapping_value.casefold() == "ElasticsearchDatastoreConfig".casefold():
            from .elasticsearch_datastore_config import ElasticsearchDatastoreConfig

            result.elasticsearch_datastore_config = ElasticsearchDatastoreConfig()
        elif mapping_value and mapping_value.casefold() == "PostgresDatastoreConfig".casefold():
            from .postgres_datastore_config import PostgresDatastoreConfig

            result.postgres_datastore_config = PostgresDatastoreConfig()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .collector_api_datastore_config import CollectorApiDatastoreConfig
        from .elasticsearch_datastore_config import ElasticsearchDatastoreConfig
        from .postgres_datastore_config import PostgresDatastoreConfig

        if self.collector_api_datastore_config:
            return self.collector_api_datastore_config.get_field_deserializers()
        if self.elasticsearch_datastore_config:
            return self.elasticsearch_datastore_config.get_field_deserializers()
        if self.postgres_datastore_config:
            return self.postgres_datastore_config.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.collector_api_datastore_config:
            writer.write_object_value(None, self.collector_api_datastore_config)
        elif self.elasticsearch_datastore_config:
            writer.write_object_value(None, self.elasticsearch_datastore_config)
        elif self.postgres_datastore_config:
            writer.write_object_value(None, self.postgres_datastore_config)
    

