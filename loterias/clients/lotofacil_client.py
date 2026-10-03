import asyncio

import httpx

from core.exceptions import ClientError

# Endpoint oficial da Caixa para resultados da Lotofácil
_BASE_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"
# A Caixa responde 404 para "lotofacil" e 200 para "Lotofacil", às vezes o inverso.
_XLS_URLS = (
    "https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotofacil",
    "https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=lotofacil",
)
_TIMEOUT = 15.0
_XLS_TIMEOUT = 60.0


class LotofacilClient:
    """Cliente HTTP assíncrono para a API de resultados da Caixa."""

    async def fetch_xls(self) -> bytes:
        """Baixa o XLSX com o histórico completo de concursos."""
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
        try:
            async with httpx.AsyncClient(timeout=_XLS_TIMEOUT, headers=headers, follow_redirects=True) as client:
                last_status = None
                for _attempt in range(4):
                    for url in _XLS_URLS:
                        response = await client.get(url)
                        if response.status_code == 404:
                            last_status = 404
                            continue
                        response.raise_for_status()
                        return response.content
                    await asyncio.sleep(1)
        except httpx.HTTPStatusError as exc:
            raise ClientError(
                f"API returned {exc.response.status_code} when downloading XLS"
            ) from exc
        except httpx.RequestError as exc:
            raise ClientError(f"Failed to download XLS from Caixa: {exc}") from exc
        raise ClientError(f"API returned {last_status} when downloading XLS")

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
