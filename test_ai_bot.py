import unittest
import sys
from unittest.mock import MagicMock

# Mock out external dependencies before importing ai-bot
# We need to mock 'google' and 'google.generativeai'
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['slack_sdk'] = MagicMock()
sys.modules['slack_sdk.errors'] = MagicMock()
sys.modules['openai'] = MagicMock()

import importlib
ai_bot = importlib.import_module("ai-bot")

class TestAIBot(unittest.TestCase):
    def test_extract_message_text_with_contents(self):
        message = {
            "blocks": [
                {"block_id": "other", "text": {"text": "ignore me"}},
                {"block_id": "contents", "text": {"text": "hello"}},
                {"block_id": "contents", "text": {"text": "world"}},
            ]
        }
        self.assertEqual(ai_bot.extract_message_text(message), "hello\nworld")

    def test_extract_message_text_no_blocks(self):
        message = {"other_key": "value"}
        self.assertIsNone(ai_bot.extract_message_text(message))

    def test_extract_message_text_no_contents(self):
        message = {
            "blocks": [
                {"block_id": "other", "text": {"text": "ignore me"}}
            ]
        }
        self.assertIsNone(ai_bot.extract_message_text(message))

    def test_extract_message_text_empty_contents(self):
        message = {
            "blocks": [
                {"block_id": "contents", "text": {"text": ""}}
            ]
        }
        self.assertEqual(ai_bot.extract_message_text(message), "")

if __name__ == '__main__':
    unittest.main()
