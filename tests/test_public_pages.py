"""Exercise the public pages through Django's request handling."""
from io import BytesIO
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import django
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.loader import get_template
from django.test import SimpleTestCase, override_settings
from django.utils.html import escape
from docx import Document


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

    def test_upload_preserves_unheaded_and_headed_paragraphs(self):
        scenarios = (
            (
                "headingless",
                [("", "   "), ("", "  Áin rennur.  "), ("", "Áin rennur.")],
                [{"heading": "", "content": ["  Áin rennur.  ", "Áin rennur."]}],
            ),
            (
                "preamble",
                [("", "Kortið er her. "), ("Heading 1", "Leiðin"), ("", "Far norður.")],
                [
                    {"heading": "", "content": ["Kortið er her. "]},
                    {"heading": "Leiðin", "content": ["Far norður."]},
                ],
            ),
            (
                "heading-first",
                [
                    ("Heading 1", "  Byrjan  "),
                    ("Heading 2", ""),
                    ("Heading 3", "Endi"),
                    ("", "Gakk víðari."),
                    ("", "\t "),
                    ("", "Gakk víðari."),
                ],
                [
                    {"heading": "  Byrjan  ", "content": []},
                    {"heading": "", "content": []},
                    {"heading": "Endi", "content": ["Gakk víðari.", "Gakk víðari."]},
                ],
            ),
            ("empty", [], []),
            ("blank", [("", ""), ("", " \t ")], []),
        )
        translated = "Fictional translation"
        comparison = {"Sample": {"Danish": "Et kort.", "Faroese": "Eitt kort."}}

        for name, paragraphs, expected in scenarios:
            with self.subTest(name=name):
                source = Document()
                for style, paragraph in paragraphs:
                    source.add_paragraph(paragraph, style=style or None)
                output = BytesIO()
                source.save(output)
                source_bytes = output.getvalue()
                upload = SimpleUploadedFile(f"{name}.docx", source_bytes)

                # The Django and plain unittest runners both use temporary file
                # storage here. The separate journey exercises the database write.
                with (
                    TemporaryDirectory() as media,
                    override_settings(MEDIA_ROOT=media),
                    patch("dashboard.views.TranslatedDocument.objects.create") as create,
                    patch("dashboard.views.call_gemini_llm", return_value=translated) as translate,
                    patch("dashboard.views.call_gemini2_llm", return_value=json.dumps(comparison)) as compare,
                ):
                    response = self.client.post("/dashboard/", {"insert_doc": upload})
                    self.assertContains(response, escape(json.dumps(comparison)))
                    saved_path = f"documents/{name}.docx"
                    create.assert_called_once_with(original_file=saved_path, user=None)
                    self.assertEqual((Path(media) / saved_path).read_bytes(), source_bytes)
                    translate.assert_called_once()
                    (original_json,) = translate.call_args.args
                    self.assertEqual(json.loads(original_json), expected)
                    compare.assert_called_once_with(original_json, translated)
