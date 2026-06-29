import unittest
import sys
from unittest.mock import MagicMock

# Mocking missing dependencies before importing the module under test
import os
os.environ['SLACK_BOT_TOKEN'] = 'dummy'
os.environ['SLACK_CHANNEL_ID'] = 'dummy'
os.environ['GEMINI_API_KEY'] = 'dummy'

google_mock = MagicMock()
google_mock.__path__ = []
sys.modules["google"] = google_mock
sys.modules["google.genai"] = MagicMock()
sys.modules["google.genai.types"] = MagicMock()
sys.modules["slack_sdk"] = MagicMock()
sys.modules["slack_sdk.errors"] = MagicMock()

import importlib
# Import the module with a hyphen in its name
ai_bot = importlib.import_module("ai-bot")

class TestSplitTextIntoChunks(unittest.TestCase):
    def test_empty_string(self):
        # Current implementation: [""[0:0]] -> [""] ? No, range(0, 0, step) is empty.
        # [text[i:i+chunk_size] for i in range(0, 0, chunk_size)] -> []
        self.assertEqual(ai_bot.split_text_into_chunks("", chunk_size=5), [])

    def test_short_string(self):
        text = "Hello"
        self.assertEqual(ai_bot.split_text_into_chunks(text, chunk_size=10), ["Hello"])

    def test_exact_chunk_size(self):
        text = "12345"
        self.assertEqual(ai_bot.split_text_into_chunks(text, chunk_size=5), ["12345"])

    def test_multiple_chunks(self):
        text = "abcdefghij"
        # chunk_size=3 -> "abc", "def", "ghi", "j"
        self.assertEqual(ai_bot.split_text_into_chunks(text, chunk_size=3), ["abc", "def", "ghi", "j"])

    def test_exact_multiple_chunks(self):
        text = "abcdef"
        self.assertEqual(ai_bot.split_text_into_chunks(text, chunk_size=3), ["abc", "def"])

    def test_default_chunk_size(self):
        # Default is 3000
        text = "a" * 3001
        chunks = ai_bot.split_text_into_chunks(text)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), 3000)
        self.assertEqual(len(chunks[1]), 1)

if __name__ == "__main__":
    unittest.main()
