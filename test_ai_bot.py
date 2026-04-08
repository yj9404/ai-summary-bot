import sys
import unittest
from unittest.mock import MagicMock
import importlib

# Mock the dependencies before importing ai-bot
sys.modules['slack_sdk'] = MagicMock()
sys.modules['slack_sdk.errors'] = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['openai'] = MagicMock()

# Import ai-bot using importlib since it has a hyphen in the filename
ai_bot = importlib.import_module("ai-bot")

class TestAIBot(unittest.TestCase):

    def test_extract_message_text_no_blocks(self):
        message = {"text": "Just some text without blocks"}
        self.assertIsNone(ai_bot.extract_message_text(message))

    def test_extract_message_text_empty_blocks(self):
        message = {"blocks": []}
        self.assertIsNone(ai_bot.extract_message_text(message))

    def test_extract_message_text_no_contents_block(self):
        message = {
            "blocks": [
                {"block_id": "header", "text": {"text": "Header text"}}
            ]
        }
        self.assertIsNone(ai_bot.extract_message_text(message))

    def test_extract_message_text_contents_no_text(self):
        message = {
            "blocks": [
                {"block_id": "contents"}
            ]
        }
        self.assertEqual(ai_bot.extract_message_text(message), "")

    def test_extract_message_text_contents_empty_text(self):
        message = {
            "blocks": [
                {"block_id": "contents", "text": {}}
            ]
        }
        self.assertEqual(ai_bot.extract_message_text(message), "")

    def test_extract_message_text_single_contents(self):
        message = {
            "blocks": [
                {"block_id": "contents", "text": {"text": "Hello world!"}}
            ]
        }
        self.assertEqual(ai_bot.extract_message_text(message), "Hello world!")

    def test_extract_message_text_multiple_contents(self):
        message = {
            "blocks": [
                {"block_id": "contents", "text": {"text": "Hello"}},
                {"block_id": "other", "text": {"text": "Ignore me"}},
                {"block_id": "contents", "text": {"text": "World!"}}
            ]
        }
        self.assertEqual(ai_bot.extract_message_text(message), "Hello\nWorld!")

if __name__ == '__main__':
    unittest.main()
