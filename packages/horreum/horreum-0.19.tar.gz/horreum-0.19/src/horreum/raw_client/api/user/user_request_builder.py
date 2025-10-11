from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .administrators.administrators_request_builder import AdministratorsRequestBuilder
    from .all_teams.all_teams_request_builder import AllTeamsRequestBuilder
    from .apikey.apikey_request_builder import ApikeyRequestBuilder
    from .create_user.create_user_request_builder import CreateUserRequestBuilder
    from .default_team.default_team_request_builder import DefaultTeamRequestBuilder
    from .info.info_request_builder import InfoRequestBuilder
    from .item.with_username_item_request_builder import WithUsernameItemRequestBuilder
    from .roles.roles_request_builder import RolesRequestBuilder
    from .search.search_request_builder import SearchRequestBuilder
    from .team.team_request_builder import TeamRequestBuilder
    from .teams.teams_request_builder import TeamsRequestBuilder

class UserRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /api/user
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new UserRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/api/user", path_parameters)
    
    def by_username(self,username: str) -> WithUsernameItemRequestBuilder:
        """
        Gets an item from the raw_client.api.user.item collection
        param username: Username to remove
        Returns: WithUsernameItemRequestBuilder
        """
        if username is None:
            raise TypeError("username cannot be null.")
        from .item.with_username_item_request_builder import WithUsernameItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["username"] = username
        return WithUsernameItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    @property
    def administrators(self) -> AdministratorsRequestBuilder:
        """
        The administrators property
        """
        from .administrators.administrators_request_builder import AdministratorsRequestBuilder

        return AdministratorsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def all_teams(self) -> AllTeamsRequestBuilder:
        """
        The allTeams property
        """
        from .all_teams.all_teams_request_builder import AllTeamsRequestBuilder

        return AllTeamsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def apikey(self) -> ApikeyRequestBuilder:
        """
        The apikey property
        """
        from .apikey.apikey_request_builder import ApikeyRequestBuilder

        return ApikeyRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def create_user(self) -> CreateUserRequestBuilder:
        """
        The createUser property
        """
        from .create_user.create_user_request_builder import CreateUserRequestBuilder

        return CreateUserRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def default_team(self) -> DefaultTeamRequestBuilder:
        """
        The defaultTeam property
        """
        from .default_team.default_team_request_builder import DefaultTeamRequestBuilder

        return DefaultTeamRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def info(self) -> InfoRequestBuilder:
        """
        The info property
        """
        from .info.info_request_builder import InfoRequestBuilder

        return InfoRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def roles(self) -> RolesRequestBuilder:
        """
        The roles property
        """
        from .roles.roles_request_builder import RolesRequestBuilder

        return RolesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def search(self) -> SearchRequestBuilder:
        """
        The search property
        """
        from .search.search_request_builder import SearchRequestBuilder

        return SearchRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def team(self) -> TeamRequestBuilder:
        """
        The team property
        """
        from .team.team_request_builder import TeamRequestBuilder

        return TeamRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def teams(self) -> TeamsRequestBuilder:
        """
        The teams property
        """
        from .teams.teams_request_builder import TeamsRequestBuilder

        return TeamsRequestBuilder(self.request_adapter, self.path_parameters)
    

