"""Loopback-only HTTP client used by the desktop application."""
import ipaddress
import os
from urllib.parse import urlsplit

import httpx


DEFAULT_API_URL = "http://127.0.0.1:8765"


class ApiError(Exception):
    """A safe, user-presentable error returned by the local API client."""


def _base_url() -> str:
    base_url = os.getenv("CHEF_API_URL", DEFAULT_API_URL).rstrip("/")
    try:
        parsed = urlsplit(base_url)
        port = parsed.port
        loopback = parsed.hostname is not None and (
            parsed.hostname == "localhost"
            or ipaddress.ip_address(parsed.hostname).is_loopback
        )
    except ValueError as error:
        raise ApiError("La URL del backend local no es válida.") from error
    if parsed.scheme != "http" or not loopback or port is None:
        raise ApiError("La API debe estar en un puerto local (localhost/127.0.0.1).")
    return base_url


def _get(path: str, params: dict[str, str] | None = None):
    try:
        response = httpx.get(
            f"{_base_url()}{path}",
            params=params,
            timeout=12.0,
        )
    except httpx.RequestError as error:
        raise ApiError(
            "No se pudo conectar con el backend local. "
            "Inícialo con «python src/api.py»."
        ) from error

    if response.is_error:
        try:
            payload = response.json()
            detail = payload.get("detail") if isinstance(payload, dict) else None
        except ValueError:
            detail = None
        raise ApiError(
            str(detail)
            if detail
            else f"El backend local devolvió HTTP {response.status_code}."
        )

    try:
        return response.json()
    except ValueError as error:
        raise ApiError("El backend local devolvió una respuesta no válida.") from error


def search_recipes(term: str, source: str) -> list[dict]:
    results = _get(
        "/api/recipes/search",
        {"q": term, "source": source},
    )
    if not isinstance(results, list):
        raise ApiError("La respuesta de búsqueda no tiene el formato esperado.")
    return results


def get_recipe_detail(source: str, recipe_id: str) -> dict:
    recipe = _get(f"/api/recipes/{source}/{recipe_id}")
    if not isinstance(recipe, dict):
        raise ApiError("La respuesta de receta no tiene el formato esperado.")
    return recipe
