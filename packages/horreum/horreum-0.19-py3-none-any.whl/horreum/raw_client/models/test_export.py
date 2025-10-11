from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .action import Action
    from .datastore import Datastore
    from .experiment_profile import ExperimentProfile
    from .missing_data_rule import MissingDataRule
    from .test_export_access import TestExport_access
    from .transformer import Transformer
    from .variable import Variable
    from .watch import Watch

@dataclass
class TestExport(AdditionalDataHolder, Parsable):
    """
    Represents a Test with all associated data used for export/import operations.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Access rights for the test. This defines the visibility of the Test in the UI
    access: Optional[TestExport_access] = None
    # Array of Actions associated with test
    actions: Optional[list[Action]] = None
    # URL to external service that can be called to compare runs.  This is typically an external reporting/visulization service
    compare_url: Optional[str] = None
    # Datastore associated with test
    datastore: Optional[Datastore] = None
    # backend ID for backing datastore
    datastore_id: Optional[int] = None
    # Description of the test
    description: Optional[str] = None
    # Array of ExperimentProfiles associated with test
    experiments: Optional[list[ExperimentProfile]] = None
    # Filter function to filter out datasets that are comparable for the purpose of change detection
    fingerprint_filter: Optional[str] = None
    # Array of Label names that are used to create a fingerprint 
    fingerprint_labels: Optional[list[str]] = None
    # Name of folder that the test is stored in. Folders allow tests to be organised in the UI
    folder: Optional[str] = None
    # Unique Test id
    id: Optional[int] = None
    # Array of MissingDataRules associated with test
    missing_data_rules: Optional[list[MissingDataRule]] = None
    # Test name
    name: Optional[str] = None
    # Are notifications enabled for the test
    notifications_enabled: Optional[bool] = None
    # Name of the team that owns the test. Users must belong to the team that owns a test to make modifications
    owner: Optional[str] = None
    # Watcher object associated with test
    subscriptions: Optional[Watch] = None
    # Label function to modify timeline labels to a produce a value used for ordering datapoints
    timeline_function: Optional[str] = None
    # List of label names that are used for determining metric to use as the time series
    timeline_labels: Optional[list[str]] = None
    # Array for transformers defined for the Test
    transformers: Optional[list[Transformer]] = None
    # Array of Variables associated with test
    variables: Optional[list[Variable]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> TestExport:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: TestExport
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return TestExport()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .action import Action
        from .datastore import Datastore
        from .experiment_profile import ExperimentProfile
        from .missing_data_rule import MissingDataRule
        from .test_export_access import TestExport_access
        from .transformer import Transformer
        from .variable import Variable
        from .watch import Watch

        from .action import Action
        from .datastore import Datastore
        from .experiment_profile import ExperimentProfile
        from .missing_data_rule import MissingDataRule
        from .test_export_access import TestExport_access
        from .transformer import Transformer
        from .variable import Variable
        from .watch import Watch

        fields: dict[str, Callable[[Any], None]] = {
            "access": lambda n : setattr(self, 'access', n.get_enum_value(TestExport_access)),
            "actions": lambda n : setattr(self, 'actions', n.get_collection_of_object_values(Action)),
            "compareUrl": lambda n : setattr(self, 'compare_url', n.get_str_value()),
            "datastore": lambda n : setattr(self, 'datastore', n.get_object_value(Datastore)),
            "datastoreId": lambda n : setattr(self, 'datastore_id', n.get_int_value()),
            "description": lambda n : setattr(self, 'description', n.get_str_value()),
            "experiments": lambda n : setattr(self, 'experiments', n.get_collection_of_object_values(ExperimentProfile)),
            "fingerprintFilter": lambda n : setattr(self, 'fingerprint_filter', n.get_str_value()),
            "fingerprintLabels": lambda n : setattr(self, 'fingerprint_labels', n.get_collection_of_primitive_values(str)),
            "folder": lambda n : setattr(self, 'folder', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_int_value()),
            "missingDataRules": lambda n : setattr(self, 'missing_data_rules', n.get_collection_of_object_values(MissingDataRule)),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "notificationsEnabled": lambda n : setattr(self, 'notifications_enabled', n.get_bool_value()),
            "owner": lambda n : setattr(self, 'owner', n.get_str_value()),
            "subscriptions": lambda n : setattr(self, 'subscriptions', n.get_object_value(Watch)),
            "timelineFunction": lambda n : setattr(self, 'timeline_function', n.get_str_value()),
            "timelineLabels": lambda n : setattr(self, 'timeline_labels', n.get_collection_of_primitive_values(str)),
            "transformers": lambda n : setattr(self, 'transformers', n.get_collection_of_object_values(Transformer)),
            "variables": lambda n : setattr(self, 'variables', n.get_collection_of_object_values(Variable)),
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
        writer.write_collection_of_object_values("actions", self.actions)
        writer.write_str_value("compareUrl", self.compare_url)
        writer.write_object_value("datastore", self.datastore)
        writer.write_int_value("datastoreId", self.datastore_id)
        writer.write_str_value("description", self.description)
        writer.write_collection_of_object_values("experiments", self.experiments)
        writer.write_str_value("fingerprintFilter", self.fingerprint_filter)
        writer.write_collection_of_primitive_values("fingerprintLabels", self.fingerprint_labels)
        writer.write_str_value("folder", self.folder)
        writer.write_int_value("id", self.id)
        writer.write_collection_of_object_values("missingDataRules", self.missing_data_rules)
        writer.write_str_value("name", self.name)
        writer.write_bool_value("notificationsEnabled", self.notifications_enabled)
        writer.write_str_value("owner", self.owner)
        writer.write_object_value("subscriptions", self.subscriptions)
        writer.write_str_value("timelineFunction", self.timeline_function)
        writer.write_collection_of_primitive_values("timelineLabels", self.timeline_labels)
        writer.write_collection_of_object_values("transformers", self.transformers)
        writer.write_collection_of_object_values("variables", self.variables)
        writer.write_additional_data_value(self.additional_data)
    

