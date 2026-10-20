from entrevecinos.application.communities.ports import CommunityRepository
from entrevecinos.application.pagination import PageRequest, PageResult
from entrevecinos.domain.communities.entities import Community, CommunitySearch


class SearchCommunities:
    def __init__(self, communities: CommunityRepository) -> None:
        self._communities = communities

    def execute(self, filters: CommunitySearch, page: PageRequest) -> PageResult[Community]:
        return self._communities.search(filters, page)
