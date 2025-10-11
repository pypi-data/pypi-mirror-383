import httpx


class Unlocker:
    def __init__(
        self,
        api_key: str,
        zone: str,
        timeout: float = 30.0,
        country: str | None = None,
    ) -> None:
        self._api_key = api_key
        self._zone = zone
        self._timeout = timeout
        self._country = country

    async def unlock(self, url: str) -> str:
        api_url = "https://api.brightdata.com/request"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
        }
        data = {
            "zone": self._zone,
            "url": url,
            "format": "raw",
        }
        if self._country:
            data["country"] = self._country

        async with httpx.AsyncClient(timeout=httpx.Timeout(self._timeout)) as client:
            response = await client.post(
                api_url,
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            return response.text
