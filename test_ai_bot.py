import unittest
import sys
import os
from unittest.mock import MagicMock

# Mocking missing dependencies before importing the module under test
google_mock = MagicMock()
google_mock.__path__ = []
sys.modules["google"] = google_mock
sys.modules["google.genai"] = MagicMock()
sys.modules["google.genai.types"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["slack_sdk"] = MagicMock()
sys.modules["slack_sdk.errors"] = MagicMock()
sys.modules["openai"] = MagicMock()

os.environ["SLACK_BOT_TOKEN"] = "dummy_token"
os.environ["SLACK_CHANNEL_ID"] = "dummy_channel"
os.environ["GEMINI_API_KEY"] = "dummy_api_key"

import importlib
# Import the module with a hyphen in its name
ai_bot = importlib.import_module("ai-bot")

class TestSplitTextIntoChunks(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(ai_bot.split_text_into_chunks("", chunk_size=5), [])

    def test_short_string(self):
        text = "Hello"
        self.assertEqual(ai_bot.split_text_into_chunks(text, chunk_size=10), ["Hello"])

    def test_exact_chunk_size(self):
        text = "12345"
        self.assertEqual(ai_bot.split_text_into_chunks(text, chunk_size=5), ["12345"])

    def test_multiple_chunks(self):
        text = "abcdefghij"
        self.assertEqual(ai_bot.split_text_into_chunks(text, chunk_size=3), ["abc", "def", "ghi", "j"])

    def test_exact_multiple_chunks(self):
        text = "abcdef"
        self.assertEqual(ai_bot.split_text_into_chunks(text, chunk_size=3), ["abc", "def"])

    def test_default_chunk_size(self):
        text = "a" * 3001
        chunks = ai_bot.split_text_into_chunks(text)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), 3000)
        self.assertEqual(len(chunks[1]), 1)

class TestExtractMessageText(unittest.TestCase):
    def test_missing_blocks(self):
        message = {"text": "Hello, world!"}
        self.assertIsNone(ai_bot.extract_message_text(message))

    def test_empty_blocks(self):
        message = {"blocks": []}
        self.assertIsNone(ai_bot.extract_message_text(message))

    def test_no_matching_block_id(self):
        message = {
            "blocks": [
                {"block_id": "header", "text": {"text": "Header text"}},
                {"block_id": "footer", "text": {"text": "Footer text"}},
            ]
        }
        self.assertIsNone(ai_bot.extract_message_text(message))

    def test_single_matching_block(self):
        message = {
            "blocks": [
                {"block_id": "contents", "text": {"text": "This is the content"}},
            ]
        }
        self.assertEqual(ai_bot.extract_message_text(message), "This is the content")

    def test_multiple_matching_blocks(self):
        message = {
            "blocks": [
                {"block_id": "contents", "text": {"text": "Line 1"}},
                {"block_id": "other", "text": {"text": "Ignore me"}},
                {"block_id": "contents", "text": {"text": "Line 2"}},
            ]
        }
        self.assertEqual(ai_bot.extract_message_text(message), "Line 1\nLine 2")

    def test_matching_block_missing_text_attribute(self):
        # A block with block_id="contents" but no "text" key, or "text" without "text" subkey.
        message = {
            "blocks": [
                {"block_id": "contents"},  # no 'text' dictionary at all
                {"block_id": "contents", "text": {}},  # 'text' dictionary but no 'text' value
            ]
        }
        # block.get("text", {}).get("text", "") -> ""
        # Joins with "\n" -> "\n"
        self.assertEqual(ai_bot.extract_message_text(message), "\n")

if __name__ == "__main__":
    unittest.main()
