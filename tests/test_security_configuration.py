"""Run with python -m unittest discover -s tests. No live services or data are used."""
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured

SETTINGS = Path(__file__).resolve().parents[1] / "translation/settings.py"


class SecurityConfigurationTests(unittest.TestCase):
    def load(self, **values):
        with patch.dict(os.environ, values, clear=True):
            return runpy.run_path(str(SETTINGS))

    def test_missing_and_empty_signing_key_refuse_startup(self):
        for values in ({}, {"DJANGO_SECRET_KEY": ""}):
            with self.subTest(values=values):
                with self.assertRaises(ImproperlyConfigured):
                    self.load(**values)

    def test_server_environment_and_private_database_path_are_used(self):
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / "new.sqlite3")
            settings = self.load(
                DJANGO_SECRET_KEY="test-signing-value-only",
                DJANGO_DB_PATH=database,
                DJANGO_ALLOWED_HOSTS=" app.example.invalid, localhost , ",
                GEMINI_API_KEY="test-provider-value-only",
            )
            self.assertEqual(settings["SECRET_KEY"], "test-signing-value-only")
            self.assertEqual(settings["GEMINI_API_KEY"], "test-provider-value-only")
            self.assertEqual(settings["ALLOWED_HOSTS"], ["app.example.invalid", "localhost"])
            self.assertEqual(settings["DATABASES"]["default"]["NAME"], database)
            self.assertFalse(settings["DEBUG"])
            self.assertFalse(Path(database).exists())

    def test_local_database_default_and_explicit_debug(self):
        settings = self.load(DJANGO_SECRET_KEY="test-signing-value-only", DJANGO_DEBUG="true")
        self.assertEqual(settings["DATABASES"]["default"]["NAME"], SETTINGS.parent.parent / "db.sqlite3")
        self.assertTrue(settings["DEBUG"])


if __name__ == "__main__":
    unittest.main()
