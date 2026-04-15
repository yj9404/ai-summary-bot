import unittest
from unittest.mock import MagicMock
import sys
import importlib

# Mocking modules before importing ai-bot.py
mock_genai = MagicMock()
mock_slack = MagicMock()
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = mock_genai
sys.modules['slack_sdk'] = mock_slack
sys.modules['slack_sdk.errors'] = MagicMock()
sys.modules['openai'] = MagicMock()

# Import ai-bot.py
ai_bot = importlib.import_module("ai-bot")

class TestExtractMessageText(unittest.TestCase):
    def test_no_blocks(self):
        message = {"text": "Hello world"}
        self.assertIsNone(ai_bot.extract_message_text(message))

    def test_no_contents_block(self):
        message = {
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "Something else"}
                }
            ]
        }
        self.assertIsNone(ai_bot.extract_message_text(message))

    def test_single_contents_block(self):
        message = {
            "blocks": [
                {
                    "block_id": "contents",
                    "text": {"type": "mrkdwn", "text": "Real content"}
                }
            ]
        }
        self.assertEqual(ai_bot.extract_message_text(message), "Real content")

    def test_multiple_contents_blocks(self):
        message = {
            "blocks": [
                {
                    "block_id": "contents",
                    "text": {"type": "mrkdwn", "text": "First part"}
                },
                {
                    "block_id": "contents",
                    "text": {"type": "mrkdwn", "text": "Second part"}
                }
            ]
        }
        self.assertEqual(ai_bot.extract_message_text(message), "First part\nSecond part")

    def test_contents_block_missing_text_field(self):
        message = {
            "blocks": [
                {
                    "block_id": "contents"
                }
            ]
        }
        # In the code: texts.append(block.get("text", {}).get("text", ""))
        self.assertEqual(ai_bot.extract_message_text(message), "")

    def test_contents_block_empty_text_nested(self):
        message = {
            "blocks": [
                {
                    "block_id": "contents",
                    "text": {"type": "mrkdwn", "text": ""}
                }
            ]
        }
        self.assertEqual(ai_bot.extract_message_text(message), "")

if __name__ == '__main__':
    unittest.main()
