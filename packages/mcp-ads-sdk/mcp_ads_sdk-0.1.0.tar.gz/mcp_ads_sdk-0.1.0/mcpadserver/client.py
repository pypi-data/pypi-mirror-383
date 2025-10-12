"""
mcpadserver Ad Client
"""

import httpx
from typing import Optional, Dict, Any
from .types import AdRequest, AdResponse


class AdClient:
    """Client for requesting contextual ads from mcpadserver."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.mcpadserver.com",
        revenue_share: float = 0.7,
        policy: str = "standard",
    ):
        """
        Initialize the AdClient.

        Args:
            api_key: Your mcpadserver API key
            base_url: API endpoint (default: https://api.mcpadserver.com)
            revenue_share: Revenue split (default: 0.7 = 70% to publisher)
            policy: Content policy (default: "standard")
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.revenue_share = revenue_share
        self.policy = policy
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": f"mcpadserver-python/0.1.0",
            }
        )

    async def request_ads(
        self,
        context: str,
        user_region: Optional[str] = None,
        placement: str = "inline",
    ) -> Dict[str, Any]:
        """
        Request contextual ads from mcpadserver.

        Args:
            context: Context of the query (e.g., "nutrition: apple")
            user_region: Optional user region for geo-targeting (e.g., "US")
            placement: Ad placement type (default: "inline")

        Returns:
            Dict containing ad data including sponsor, content, and link

        Example:
            >>> ad = await client.request_ads(
            ...     context="nutrition: apple",
            ...     user_region="US"
            ... )
            >>> print(ad['sponsor'])
            'GreenBite'
        """
        request = AdRequest(
            context=context,
            user_region=user_region,
            placement=placement,
        )

        response = await self._client.post(
            f"{self.base_url}/v1/ads/request",
            json=request.model_dump(exclude_none=True),
        )
        response.raise_for_status()

        return response.json()

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
