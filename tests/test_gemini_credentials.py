"""Exercise the real Gemini functions with mocked transport and no database."""
import os
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("DJANGO_SECRET_KEY", "test-signing-value-only")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "translation.settings")
import django
django.setup()
from django.test import override_settings
from dashboard.views import call_gemini_llm, call_gemini2_llm


class GeminiCredentialTests(unittest.TestCase):
    @override_settings(GEMINI_API_KEY="")
    @patch("dashboard.views.requests.post")
    def test_missing_key_never_calls_provider(self, post):
        self.assertEqual(call_gemini_llm("{}"), "Translation service is not configured.")
        self.assertEqual(call_gemini2_llm("{}", "{}"), "Translation service is not configured.")
        post.assert_not_called()

    @override_settings(GEMINI_API_KEY="test-provider-value-only")
    @patch("dashboard.views.requests.post")
    def test_both_requests_use_the_server_key(self, post):
        post.return_value = Mock(status_code=200)
        post.return_value.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "translated"}]}}]
        }
        self.assertEqual(call_gemini_llm("{}"), "translated")
        self.assertEqual(call_gemini2_llm("{}", "{}"), "translated")
        self.assertEqual(post.call_count, 2)
        for call in post.call_args_list:
            self.assertEqual(call.kwargs["params"], {"key": "test-provider-value-only"})


if __name__ == "__main__":
    unittest.main()
