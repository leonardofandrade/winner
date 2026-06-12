import httpx

from core.exceptions import ClientError

# Endpoint oficial da Caixa para resultados da Lotofácil
_BASE_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"
_TIMEOUT = 15.0


class LotofacilClient:
    """Cliente HTTP assíncrono para a API de resultados da Caixa."""

    async def fetch_contest(self, number: int | None = None) -> dict:
        """Busca um concurso pelo número, ou o mais recente se number for None."""
        url = f"{_BASE_URL}/{number}" if number is not None else _BASE_URL
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            raise ClientError(
                f"API returned {exc.response.status_code} for contest {number}"
            ) from exc
        except httpx.RequestError as exc:
            raise ClientError(f"Failed to reach Caixa API: {exc}") from exc
