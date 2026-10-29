import os
import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

try:
    import httpx
    from fastapi.testclient import TestClient
    from api import app
except ImportError:
    BACKEND_AVAILABLE = False
else:
    BACKEND_AVAILABLE = True


@unittest.skipUnless(
    BACKEND_AVAILABLE,
    "Install requirements-backend.txt to run backend tests.",
)
class ApiTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(
            os.environ,
            {
                "SUPABASE_URL": "https://uochnxgzsdslcgsznqso.supabase.co",
                "SUPABASE_PUBLISHABLE_KEY": "test-public-key",
            },
        )
        self.environment.start()
        self.client = TestClient(app)

    def tearDown(self):
        self.environment.stop()

    @staticmethod
    def response(data):
        return httpx.Response(
            200,
            json=data,
            request=httpx.Request("GET", "https://example.supabase.co/rest/v1"),
        )

    def test_search_reads_both_catalogs_with_limited_columns_and_rows(self):
        with patch(
            "api.httpx.get",
            side_effect=[
                self.response([{"id": "Ground_Beef_Soup", "name": "Soup"}]),
                self.response([]),
                self.response([{"id": "53151", "name": "Paella", "source": "unused"}]),
                self.response([]),
            ],
        ) as request:
            response = self.client.get(
                "/api/recipes/search",
                params={"q": "soup", "source": "all"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [row["source"] for row in response.json()],
            ["kaggle", "themealdb"],
        )
        self.assertEqual(request.call_count, 4)
        for call, table, limit in zip(
            request.call_args_list,
            (
                "chef_kaggle_recipes",
                "chef_kaggle_steps",
                "chef_themealdb_recipes",
                "chef_themealdb_ingredients",
            ),
            ("1000", "1000", "1000", "1000"),
        ):
            self.assertTrue(call.args[0].endswith(f"/{table}"))
            self.assertEqual(call.kwargs["params"]["limit"], limit)
            self.assertEqual(
                call.kwargs["headers"]["apikey"],
                "test-public-key",
            )
            self.assertNotIn("Authorization", call.kwargs["headers"])

    def test_spanish_search_uses_local_translation_and_matches_catalogs(self):
        meal = {"id": "53151", "name": "Chicken Paella", "category": "Chicken"}
        with (
            patch("api._translate_local") as translation,
            patch(
                "api.httpx.get",
                side_effect=[
                    self.response([]),
                    self.response([]),
                    self.response([]),
                    self.response([{"recipe_id": "53151"}]),
                    self.response([meal]),
                    self.response([{"id": "Baked_Chicken", "name": "Baked Chicken"}]),
                    self.response([]),
                    self.response([]),
                    self.response([{"recipe_id": "53151"}]),
                    self.response([meal]),
                ],
            ) as request,
        ):
            response = self.client.get("/api/recipes/search", params={"q": "pollo"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {(recipe["source"], recipe["id"]) for recipe in response.json()},
            {("themealdb", "53151"), ("kaggle", "Baked_Chicken")},
        )
        translation.assert_not_called()
        self.assertEqual(request.call_count, 10)
        patterns = [
            call.kwargs["params"].get("name") or call.kwargs["params"].get("ingredient")
            or call.kwargs["params"].get("instruction")
            for call in request.call_args_list
        ]
        self.assertEqual(
            [pattern for pattern in patterns if pattern],
            ["ilike.*pollo*"] * 4 + ["ilike.*chicken*"] * 4,
        )

    def test_spanish_phrase_search_uses_local_terms(self):
        with (
            patch("api._translate_local") as translation,
            patch(
                "api.httpx.get",
                side_effect=[self.response([]) for _ in range(8)],
            ) as request,
        ):
            response = self.client.get(
                "/api/recipes/search",
                params={"q": "recetas de pollo"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        translation.assert_not_called()
        patterns = [
            call.kwargs["params"].get("name")
            or call.kwargs["params"].get("ingredient")
            or call.kwargs["params"].get("instruction")
            for call in request.call_args_list
        ]
        self.assertEqual(
            [pattern for pattern in patterns if pattern],
            ["ilike.*recetas de pollo*"] * 4 + ["ilike.*chicken*"] * 4,
        )

    def test_local_translation_normalizes_accents_and_phrase_words(self):
        from api import _local_search_translations

        self.assertEqual(
            _local_search_translations("sopa de champiñones"),
            ["soup mushrooms", "soup", "mushrooms"],
        )

    def test_unmapped_spanish_search_does_not_require_translation_model(self):
        with (
            patch("api._translate_local") as translation,
            patch("api.httpx.get", side_effect=[self.response([]) for _ in range(4)]),
        ):
            response = self.client.get(
                "/api/recipes/search",
                params={"q": "ñame"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        translation.assert_not_called()

    def test_english_search_does_not_call_local_translation(self):
        with (
            patch("api._translate_local") as translation,
            patch(
                "api.httpx.get",
                side_effect=[
                    self.response([]),
                    self.response([]),
                    self.response([]),
                    self.response([]),
                ],
            ),
        ):
            response = self.client.get("/api/recipes/search", params={"q": "chicken"})
        self.assertEqual(response.status_code, 200)
        translation.assert_not_called()

    def test_search_rejects_filter_syntax(self):
        with patch("api.httpx.get") as request:
            response = self.client.get(
                "/api/recipes/search",
                params={"q": "soup,select(*)", "source": "all"},
            )
        self.assertEqual(response.status_code, 422)
        request.assert_not_called()

    def test_api_exposes_no_write_methods(self):
        response = self.client.post(
            "/api/recipes/search",
            params={"q": "soup", "source": "kaggle"},
        )
        self.assertEqual(response.status_code, 405)

    def test_missing_recipe_is_reported(self):
        with patch("api.httpx.get", return_value=self.response([])):
            response = self.client.get("/api/recipes/kaggle/Unknown_Recipe")
        self.assertEqual(response.status_code, 404)

    def test_invalid_recipe_id_is_rejected_before_query(self):
        with patch("api.httpx.get") as request:
            response = self.client.get("/api/recipes/kaggle/id,or")
        self.assertEqual(response.status_code, 422)
        request.assert_not_called()

    def test_missing_credentials_are_reported(self):
        os.environ["SUPABASE_PUBLISHABLE_KEY"] = ""
        response = self.client.get(
            "/api/recipes/search",
            params={"q": "soup", "source": "kaggle"},
        )
        self.assertEqual(response.status_code, 503)

    def test_home_serves_web_frontend(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("Chef", response.text)
        self.assertNotIn("Todos los catálogos", response.text)
        self.assertIn('href="static/styles.css"', response.text)
        self.assertIn('src="static/app.js"', response.text)
        self.assertNotIn("fonts.googleapis.com", response.text)

        for asset in ("styles.css", "app.js"):
            with self.subTest(asset=asset):
                asset_response = self.client.get(f"/static/{asset}")
                self.assertEqual(asset_response.status_code, 200)

    def test_translation_uses_local_model_and_returns_text(self):
        with patch(
            "api._translate_local",
            side_effect=lambda text, source, target: f"{text} traducido",
        ) as translation:
            response = self.client.post(
                "/api/translate",
                json={"texts": ["Roast Chicken", "Fresh herbs"]},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"translations": ["Roast Chicken traducido", "Fresh herbs traducido"]},
        )
        self.assertEqual(
            translation.call_args_list,
            [
                call("Roast Chicken", "en", "es"),
                call("Fresh herbs", "en", "es"),
            ],
        )

    def test_translation_reports_missing_local_model(self):
        from fastapi import HTTPException

        with patch(
            "api._translate_local",
            side_effect=HTTPException(503, "Falta el modelo local inglés-español."),
        ):
            response = self.client.post(
                "/api/translate",
                json={"texts": ["Roast Chicken"]},
            )
        self.assertEqual(response.status_code, 503)
        self.assertIn("modelo local", response.json()["detail"])

    def test_translation_rejects_too_many_texts(self):
        with patch("api._translate_local") as translation:
            response = self.client.post(
                "/api/translate",
                json={"texts": ["recipe"] * 31},
            )
        self.assertEqual(response.status_code, 422)
        translation.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
