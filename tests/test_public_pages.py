"""Exercise the public pages through Django's request handling."""
import os
from pathlib import Path
import unittest

import django
from django.test import SimpleTestCase
from django.test.utils import setup_test_environment, teardown_test_environment


def setUpModule():
    os.environ.setdefault("DJANGO_SECRET_KEY", "test-signing-value-only")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "translation.settings")
    django.setup()
    setup_test_environment()
    unittest.addModuleCleanup(teardown_test_environment)


class PublicPageTests(SimpleTestCase):
    def test_public_pages_render_from_their_template_directory(self):
        for route, marker in (
            ("/", "Hello this is my app"),
            ("/dashboard/", 'name="insert_doc"'),
        ):
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertContains(response, marker)

                # A case-insensitive filesystem can open a misspelled directory.
                directory = Path(response.templates[0].origin.name).parent
                self.assertIn(
                    directory.name,
                    {entry.name for entry in directory.parent.iterdir()},
                    f"Template directory has incorrect casing: {directory}",
                )
