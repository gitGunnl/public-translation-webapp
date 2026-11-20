"""Exercise the public pages through Django's request handling."""
import os
from pathlib import Path

import django
from django.template.loader import get_template
from django.test import SimpleTestCase, override_settings


def setUpModule():
    os.environ.setdefault("DJANGO_SECRET_KEY", "test-signing-value-only")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "translation.settings")
    django.setup()


@override_settings(ALLOWED_HOSTS=["testserver"])
class PublicPageTests(SimpleTestCase):
    def test_public_pages_render_from_their_template_directory(self):
        for route, template_name, marker in (
            ("/", "index.html", "Hello this is my app"),
            ("/dashboard/", "dashboard.html", 'name="insert_doc"'),
        ):
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertContains(response, marker)

                # A case-insensitive filesystem can open a misspelled directory.
                directory = Path(get_template(template_name).origin.name).parent
                self.assertIn(
                    directory.name,
                    {entry.name for entry in directory.parent.iterdir()},
                    f"Template directory has incorrect casing: {directory}",
                )
