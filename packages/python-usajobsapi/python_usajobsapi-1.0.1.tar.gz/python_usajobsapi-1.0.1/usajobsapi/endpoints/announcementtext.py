"""
Wrapper for the Announcement Text API.

Fetch the rendered job announcement text for a single job opportunity announcement.

Pair this endpoint with a control number discovered from [`SearchEndpoint.JOAItem`][usajobsapi.endpoints.search.SearchEndpoint.JOAItem] to pull the full HTML description.
"""

from typing import Dict

from pydantic import BaseModel

from usajobsapi.utils import _dump_by_alias


class AnnouncementTextEndpoint(BaseModel):
    """
    Declarative wrapper around the [Announcement Text API](https://developer.usajobs.gov/api-reference/get-api-announcementtext).
    """

    METHOD: str = "GET"
    PATH: str = "/api/historicjoa/announcementtext"

    class Params(BaseModel):
        def to_params(self) -> Dict[str, str]:
            return _dump_by_alias(self)

    class Response(BaseModel):
        pass
