from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import ComposedTypeWrapper, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .github_issue_comment_action_config import GithubIssueCommentActionConfig
    from .github_issue_create_action_config import GithubIssueCreateActionConfig
    from .http_action_config import HttpActionConfig
    from .slack_channel_message_action_config import SlackChannelMessageActionConfig

@dataclass
class Action_config(ComposedTypeWrapper, Parsable):
    """
    Composed type wrapper for classes GithubIssueCommentActionConfig, GithubIssueCreateActionConfig, HttpActionConfig, SlackChannelMessageActionConfig
    """
    # Composed type representation for type GithubIssueCommentActionConfig
    github_issue_comment_action_config: Optional[GithubIssueCommentActionConfig] = None
    # Composed type representation for type GithubIssueCreateActionConfig
    github_issue_create_action_config: Optional[GithubIssueCreateActionConfig] = None
    # Composed type representation for type HttpActionConfig
    http_action_config: Optional[HttpActionConfig] = None
    # Composed type representation for type SlackChannelMessageActionConfig
    slack_channel_message_action_config: Optional[SlackChannelMessageActionConfig] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Action_config:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Action_config
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        try:
            child_node = parse_node.get_child_node("type")
            mapping_value = child_node.get_str_value() if child_node else None
        except AttributeError:
            mapping_value = None
        result = Action_config()
        if mapping_value and mapping_value.casefold() == "github-issue-comment".casefold():
            from .github_issue_comment_action_config import GithubIssueCommentActionConfig

            result.github_issue_comment_action_config = GithubIssueCommentActionConfig()
        elif mapping_value and mapping_value.casefold() == "github-issue-create".casefold():
            from .github_issue_create_action_config import GithubIssueCreateActionConfig

            result.github_issue_create_action_config = GithubIssueCreateActionConfig()
        elif mapping_value and mapping_value.casefold() == "http".casefold():
            from .http_action_config import HttpActionConfig

            result.http_action_config = HttpActionConfig()
        elif mapping_value and mapping_value.casefold() == "slack-channel-message".casefold():
            from .slack_channel_message_action_config import SlackChannelMessageActionConfig

            result.slack_channel_message_action_config = SlackChannelMessageActionConfig()
        return result
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .github_issue_comment_action_config import GithubIssueCommentActionConfig
        from .github_issue_create_action_config import GithubIssueCreateActionConfig
        from .http_action_config import HttpActionConfig
        from .slack_channel_message_action_config import SlackChannelMessageActionConfig

        if self.github_issue_comment_action_config:
            return self.github_issue_comment_action_config.get_field_deserializers()
        if self.github_issue_create_action_config:
            return self.github_issue_create_action_config.get_field_deserializers()
        if self.http_action_config:
            return self.http_action_config.get_field_deserializers()
        if self.slack_channel_message_action_config:
            return self.slack_channel_message_action_config.get_field_deserializers()
        return {}
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        if self.github_issue_comment_action_config:
            writer.write_object_value(None, self.github_issue_comment_action_config)
        elif self.github_issue_create_action_config:
            writer.write_object_value(None, self.github_issue_create_action_config)
        elif self.http_action_config:
            writer.write_object_value(None, self.http_action_config)
        elif self.slack_channel_message_action_config:
            writer.write_object_value(None, self.slack_channel_message_action_config)
    

