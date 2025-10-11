from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_team_item_request_builder import WithTeamItemRequestBuilder

class TeamRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/user/team
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new TeamRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/user/team", path_parameters)
    
    def by_team(self,team: str) -> WithTeamItemRequestBuilder:
        """
        Gets an item from the raw_client.api.user.team.item collection
        param team: Name of the team to be removed
        Returns: WithTeamItemRequestBuilder
        """
        if team is None:
            raise TypeError("team cannot be null.")
        from .item.with_team_item_request_builder import WithTeamItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["team"] = team
        return WithTeamItemRequestBuilder(self.request_adapter, url_tpl_params)
    

