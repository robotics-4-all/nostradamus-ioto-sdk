from ..models.common import HealthResponse, ReadyResponse
from ._base import BaseResource


class HealthResource(BaseResource):
    def health(self) -> HealthResponse:
        response = self.client.request("GET", "/health")
        return self.parse_response(response.json(), HealthResponse)

    async def ahealth(self) -> HealthResponse:
        response = await self.client.request("GET", "/health")
        return self.parse_response(response.json(), HealthResponse)

    def ready(self) -> ReadyResponse:
        response = self.client.request("GET", "/ready")
        return self.parse_response(response.json(), ReadyResponse)

    async def aready(self) -> ReadyResponse:
        response = await self.client.request("GET", "/ready")
        return self.parse_response(response.json(), ReadyResponse)
