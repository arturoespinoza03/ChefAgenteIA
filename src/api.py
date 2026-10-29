"""Local, read-only API for the desktop application's Supabase queries."""
import logging
import os
import re
import threading
import unicodedata
from typing import Literal
from urllib.parse import urlparse
import webbrowser

import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"))

LOGGER = logging.getLogger("chef.api")
TABLES = {
    "chef_kaggle_recipes",
    "chef_kaggle_steps",
    "chef_kaggle_images",
    "chef_themealdb_recipes",
    "chef_themealdb_ingredients",
}
SUPABASE_HOST = "uochnxgzsdslcgsznqso.supabase.co"
SEARCH_TERM = re.compile(r"^[\w\s.'’\-]+$", re.UNICODE)
SPANISH_SEARCH_WORDS = {
    "ajo", "albóndigas", "almendra", "almendras", "almuerzo", "arroz", "atún",
    "bacalao", "berenjena", "bistec", "brócoli", "calabaza", "caldo", "camarón",
    "carne", "cebolla", "cena", "cerdo",
    "champiñon", "champiñones", "chile", "chiles", "cocinar",
    "comida", "con", "cordero", "costillas", "crema", "de", "del", "desayunar",
    "desayuno", "empanada", "empanadas", "ensalada", "espinacas", "filete",
    "fresa", "fruta", "frutas", "fideos", "frijoles", "garbanzo", "garbanzos",
    "guiso", "hacer", "hamburguesa", "harina", "helado", "hierbas", "horno",
    "huevo", "huevos", "jamon", "jamón", "judias", "judías", "la", "las",
    "leche", "lentejas", "limon", "limón", "los", "maiz", "maíz", "mariscos",
    "mantequilla", "manzana", "masa", "mejillones", "naranja", "papas", "pan",
    "para", "patata", "patatas", "pavo", "pescado", "pimiento", "pimientos",
    "platano", "plátano", "pollo", "postre", "preparar", "pulpo", "que",
    "queso", "receta", "recetas", "relleno", "res", "salmón", "se", "sopa",
    "tacos", "tarta", "ternera", "tomate", "un", "una", "verduras", "vinagre",
    "yogur", "yogurt", "quiero", "quieres", "zanahoria",
}
LOCAL_SEARCH_TRANSLATIONS = {
    "ajo": "garlic",
    "albondiga": "meatball",
    "albondigas": "meatballs",
    "arroz": "rice",
    "atun": "tuna",
    "bacalao": "cod",
    "berenjena": "eggplant",
    "brocoli": "broccoli",
    "calabaza": "pumpkin",
    "caldo": "broth",
    "camaron": "shrimp",
    "camarones": "shrimp",
    "carne": "meat",
    "cebolla": "onion",
    "cerdo": "pork",
    "champinon": "mushroom",
    "champinones": "mushrooms",
    "chile": "chili",
    "cordero": "lamb",
    "costillas": "ribs",
    "crema": "cream",
    "empanada": "pastry",
    "ensalada": "salad",
    "espinacas": "spinach",
    "fideos": "noodles",
    "frijoles": "beans",
    "garbanzo": "chickpea",
    "garbanzos": "chickpeas",
    "guiso": "stew",
    "hamburguesa": "burger",
    "harina": "flour",
    "helado": "ice cream",
    "huevo": "egg",
    "huevos": "eggs",
    "jamon": "ham",
    "judias": "beans",
    "leche": "milk",
    "lentejas": "lentils",
    "limon": "lemon",
    "maiz": "corn",
    "mantequilla": "butter",
    "manzana": "apple",
    "mejillones": "mussels",
    "naranja": "orange",
    "papas": "potatoes",
    "patata": "potato",
    "patatas": "potatoes",
    "pavo": "turkey",
    "pescado": "fish",
    "pimiento": "pepper",
    "pimientos": "peppers",
    "platano": "banana",
    "pollo": "chicken",
    "pulpo": "octopus",
    "queso": "cheese",
    "salmon": "salmon",
    "sopa": "soup",
    "ternera": "beef",
    "tomate": "tomato",
    "tomates": "tomatoes",
    "zanahoria": "carrot",
    "zanahorias": "carrots",
}
SPANISH_SEARCH_STOP_WORDS = {
    "a", "al", "con", "de", "del", "el", "en", "la", "las", "los",
    "para", "por", "receta", "recetas", "sin", "un", "una", "y",
}
KAGGLE_ID = re.compile(r"^[A-Za-z0-9_]+$")
THEMEALDB_ID = re.compile(r"^[0-9]+$")

app = FastAPI(title="Chef Personal API", docs_url=None, redoc_url=None)
WEB_ROOT = os.path.join(ROOT, "src", "web")
app.mount("/static", StaticFiles(directory=os.path.join(WEB_ROOT, "static")), name="static")


@app.get("/")
def home():
    return FileResponse(os.path.join(WEB_ROOT, "index.html"))


def _supabase_request(table: str, params: dict[str, str]) -> list[dict]:
    if table not in TABLES:
        raise HTTPException(status_code=500, detail="Tabla no permitida.")

    base_url = os.getenv("SUPABASE_URL", "").rstrip("/")
    publishable_key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    parsed_url = urlparse(base_url)
    if (
        parsed_url.scheme != "https"
        or parsed_url.hostname != SUPABASE_HOST
        or not publishable_key
    ):
        raise HTTPException(
            status_code=503,
            detail=(
                "Backend sin configurar. Define SUPABASE_URL y "
                "SUPABASE_PUBLISHABLE_KEY en el archivo .env local."
            ),
        )

    try:
        response = httpx.get(
            f"{base_url}/rest/v1/{table}",
            params=params,
            headers={
                "apikey": publishable_key,
            },
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.TimeoutException as error:
        LOGGER.exception("Timeout consultando la tabla Supabase %s", table)
        raise HTTPException(
            status_code=504,
            detail="Supabase no respondió dentro del tiempo límite.",
        ) from error
    except httpx.HTTPStatusError as error:
        LOGGER.error(
            "Supabase devolvió HTTP %s al consultar %s",
            error.response.status_code,
            table,
        )
        raise HTTPException(
            status_code=502,
            detail=f"Supabase rechazó la consulta (HTTP {error.response.status_code}).",
        ) from error
    except httpx.RequestError as error:
        LOGGER.exception("Error de red consultando la tabla Supabase %s", table)
        raise HTTPException(
            status_code=502,
            detail="No se pudo conectar con Supabase.",
        ) from error

    try:
        data = response.json()
    except ValueError as error:
        LOGGER.exception("Respuesta JSON no válida desde la tabla %s", table)
        raise HTTPException(
            status_code=502,
            detail="Supabase devolvió una respuesta no válida.",
        ) from error

    if not isinstance(data, list):
        LOGGER.error("Formato inesperado desde la tabla Supabase %s", table)
        raise HTTPException(
            status_code=502,
            detail="Supabase devolvió un formato de respuesta no válido.",
        )
    return data


def _search_pattern(term: str) -> str:
    normalized = term.strip()
    if not SEARCH_TERM.fullmatch(normalized):
        raise HTTPException(
            status_code=422,
            detail="Usa letras, números, espacios, apóstrofos, puntos o guiones.",
        )
    escaped = normalized.replace("_", "\\_")
    return f"*{escaped}*"


def _is_spanish_search(term: str) -> bool:
    if re.search(r"[áéíóúüñ¿¡]", term, re.IGNORECASE):
        return True
    words = set(re.findall(r"\w+", term.casefold()))
    return bool(words & SPANISH_SEARCH_WORDS)


def _local_search_translations(term: str) -> list[str]:
    words = re.findall(r"\w+", term.casefold())
    translated_words = []
    for word in words:
        normalized = "".join(
            character
            for character in unicodedata.normalize("NFKD", word)
            if not unicodedata.combining(character)
        )
        if normalized in SPANISH_SEARCH_STOP_WORDS:
            continue
        translated = LOCAL_SEARCH_TRANSLATIONS.get(normalized)
        if translated:
            translated_words.extend(translated.split())

    if not translated_words:
        return []

    candidates = [" ".join(translated_words)]
    if len(translated_words) > 1:
        candidates.extend(translated_words)
    original = term.strip().casefold()
    return list(dict.fromkeys(
        candidate
        for candidate in candidates
        if candidate and candidate.casefold() != original
    ))


def _libretranslate(
    text: str,
    source: str,
    target: str,
    timeout: float = 30.0,
) -> str:
    endpoint = os.getenv(
        "LIBRETRANSLATE_URL",
        "https://libretranslate.com/translate",
    ).strip()
    parsed_endpoint = urlparse(endpoint)
    local_endpoint = parsed_endpoint.hostname in {"localhost", "127.0.0.1", "::1"}
    if (
        parsed_endpoint.scheme not in ({"https", "http"} if local_endpoint else {"https"})
        or not parsed_endpoint.hostname
        or parsed_endpoint.username
        or parsed_endpoint.password
        or parsed_endpoint.query
        or parsed_endpoint.fragment
    ):
        raise HTTPException(
            status_code=503,
            detail="Configura una URL HTTPS válida de LibreTranslate (o localhost).",
        )

    body = {"q": text, "source": source, "target": target, "format": "text"}
    api_key = os.getenv("LIBRETRANSLATE_API_KEY", "").strip()
    if api_key:
        body["api_key"] = api_key
    try:
        response = httpx.post(endpoint, json=body, timeout=timeout)
        response.raise_for_status()
        result = response.json()
    except httpx.TimeoutException as error:
        LOGGER.exception("Timeout del servicio LibreTranslate")
        raise HTTPException(
            status_code=504,
            detail="El servicio de traducción no respondió a tiempo.",
        ) from error
    except httpx.HTTPStatusError as error:
        LOGGER.error("LibreTranslate devolvió HTTP %s", error.response.status_code)
        raise HTTPException(
            status_code=502,
            detail=(
                "LibreTranslate rechazó la solicitud "
                f"(HTTP {error.response.status_code}). Revisa URL y clave API."
            ),
        ) from error
    except httpx.RequestError as error:
        LOGGER.exception("Error de red con LibreTranslate")
        raise HTTPException(
            status_code=502,
            detail="No se pudo conectar con LibreTranslate.",
        ) from error
    except ValueError as error:
        LOGGER.exception("LibreTranslate devolvió JSON no válido")
        raise HTTPException(
            status_code=502,
            detail="LibreTranslate devolvió una respuesta no válida.",
        ) from error

    translated_text = result.get("translatedText") if isinstance(result, dict) else None
    if not isinstance(translated_text, str):
        LOGGER.error("Formato inesperado desde LibreTranslate")
        raise HTTPException(
            status_code=502,
            detail="LibreTranslate devolvió una respuesta no válida.",
        )
    return translated_text


def _search_kaggle(pattern: str) -> list[dict]:
    rows = _supabase_request(
        "chef_kaggle_recipes",
        {
            "select": "id,name",
            "name": f"ilike.{pattern}",
            "order": "name.asc",
            "limit": "1000",
        },
    )
    step_rows = _supabase_request(
        "chef_kaggle_steps",
        {
            "select": "recipe_id",
            "instruction": f"ilike.{pattern}",
            "limit": "1000",
        },
    )
    recipe_ids = list(
        dict.fromkeys(
            row["recipe_id"]
            for row in step_rows
            if isinstance(row.get("recipe_id"), str)
            and KAGGLE_ID.fullmatch(row["recipe_id"])
        )
    )
    if recipe_ids:
        rows.extend(
            _supabase_request(
                "chef_kaggle_recipes",
                {
                    "select": "id,name",
                    "id": f"in.({','.join(recipe_ids)})",
                    "order": "name.asc",
                    "limit": "1000",
                },
            )
        )
    unique_rows = {row["id"]: row for row in rows}
    return [{**row, "source": "kaggle"} for row in unique_rows.values()]


def _search_themealdb(pattern: str) -> list[dict]:
    rows = _supabase_request(
        "chef_themealdb_recipes",
        {
            "select": "id,name,category,area",
            "name": f"ilike.{pattern}",
            "order": "name.asc",
            "limit": "1000",
        },
    )
    ingredient_rows = _supabase_request(
        "chef_themealdb_ingredients",
        {
            "select": "recipe_id",
            "ingredient": f"ilike.{pattern}",
            "limit": "1000",
        },
    )
    recipe_ids = list(
        dict.fromkeys(
            row["recipe_id"]
            for row in ingredient_rows
            if isinstance(row.get("recipe_id"), str)
            and THEMEALDB_ID.fullmatch(row["recipe_id"])
        )
    )
    if recipe_ids:
        rows.extend(
            _supabase_request(
                "chef_themealdb_recipes",
                {
                    "select": "id,name,category,area",
                    "id": f"in.({','.join(recipe_ids)})",
                    "order": "name.asc",
                    "limit": "1000",
                },
            )
        )
    unique_rows = {row["id"]: row for row in rows}
    return [{**row, "source": "themealdb"} for row in unique_rows.values()]


@app.get("/health")
def health() -> dict[str, bool | str]:
    configured = bool(
        os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_PUBLISHABLE_KEY")
    )
    return {
        "status": "ok",
        "supabase_configured": configured,
    }


@app.get("/api/recipes/search")
def search_recipes(
    q: str = Query(min_length=1, max_length=80),
    source: Literal["all", "kaggle", "themealdb"] = "all",
) -> list[dict]:
    _search_pattern(q)
    terms = [q.strip()]
    if _is_spanish_search(q):
        terms.extend(_local_search_translations(q))
        if len(terms) == 1:
            try:
                translated_term = _libretranslate(
                    q.strip(),
                    "auto",
                    "en",
                    timeout=5.0,
                ).strip()
            except HTTPException as error:
                LOGGER.warning(
                    "Traducción opcional no disponible para búsqueda (HTTP %s); "
                    "se buscará el término original.",
                    error.status_code,
                )
            else:
                if translated_term and translated_term.casefold() != q.strip().casefold():
                    terms.append(translated_term)

    searchers = {
        "kaggle": (_search_kaggle,),
        "themealdb": (_search_themealdb,),
        "all": (_search_kaggle, _search_themealdb),
    }
    results_by_id = {}
    for term in terms:
        pattern = _search_pattern(term)
        for searcher in searchers[source]:
            for recipe in searcher(pattern):
                results_by_id[(recipe["source"], recipe["id"])] = recipe
    return list(results_by_id.values())


@app.get("/api/recipes/{source}/{recipe_id}")
def recipe_detail(
    source: Literal["kaggle", "themealdb"],
    recipe_id: str,
) -> dict:
    if source == "kaggle":
        if not KAGGLE_ID.fullmatch(recipe_id):
            raise HTTPException(status_code=422, detail="Identificador Kaggle no válido.")
        recipes = _supabase_request(
            "chef_kaggle_recipes",
            {"select": "id,name", "id": f"eq.{recipe_id}", "limit": "1"},
        )
        if not recipes:
            raise HTTPException(status_code=404, detail="Receta no encontrada.")
        recipe = recipes[0]
        recipe["steps"] = _supabase_request(
            "chef_kaggle_steps",
            {
                "select": "position,instruction",
                "recipe_id": f"eq.{recipe_id}",
                "order": "position.asc",
            },
        )
        images = _supabase_request(
            "chef_kaggle_images",
            {
                "select": "relative_path",
                "recipe_id": f"eq.{recipe_id}",
                "order": "position.asc",
            },
        )
        recipe["images"] = [image["relative_path"] for image in images]
        recipe["source"] = source
        return recipe

    if not THEMEALDB_ID.fullmatch(recipe_id):
        raise HTTPException(status_code=422, detail="Identificador TheMealDB no válido.")
    recipes = _supabase_request(
        "chef_themealdb_recipes",
        {
            "select": "id,name,category,area,instructions,source_url,api_url",
            "id": f"eq.{recipe_id}",
            "limit": "1",
        },
    )
    if not recipes:
        raise HTTPException(status_code=404, detail="Receta no encontrada.")
    recipe = recipes[0]
    recipe["ingredients"] = _supabase_request(
        "chef_themealdb_ingredients",
        {
            "select": "ingredient,measure_raw",
            "recipe_id": f"eq.{recipe_id}",
            "order": "position.asc",
        },
    )
    recipe["source"] = source
    return recipe


@app.post("/api/translate")
def translate_texts(payload: dict) -> dict[str, list[str]]:
    texts = payload.get("texts")
    if (
        not isinstance(texts, list)
        or not texts
        or len(texts) > 30
        or any(not isinstance(text, str) or not text.strip() or len(text) > 4000 for text in texts)
    ):
        raise HTTPException(
            status_code=422,
            detail="Envía entre 1 y 30 textos no vacíos, de hasta 4.000 caracteres cada uno.",
        )

    translations = [_libretranslate(text, "auto", "es") for text in texts]

    return {"translations": translations}


if __name__ == "__main__":
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:8765")).start()
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
