import unittest
from unittest.mock import patch, MagicMock
import sys
import importlib

# Mock the required modules before importing ai-bot
sys.modules['google.generativeai'] = MagicMock()
sys.modules['slack_sdk'] = MagicMock()
sys.modules['slack_sdk.errors'] = MagicMock()
sys.modules['openai'] = MagicMock()

# Import the module
ai_bot = importlib.import_module("ai-bot")

class TestAIBot(unittest.TestCase):

    def test_extract_message_text_with_contents(self):
        message = {
            "blocks": [
                {
                    "block_id": "header",
                    "text": {"text": "Header Text"}
                },
                {
                    "block_id": "contents",
                    "text": {"text": "Hello, world!"}
                }
            ]
        }
        result = ai_bot.extract_message_text(message)
        self.assertEqual(result, "Hello, world!")

    def test_extract_message_text_without_contents(self):
        message = {
            "blocks": [
                {
                    "block_id": "header",
                    "text": {"text": "Header Text"}
                }
            ]
        }
        result = ai_bot.extract_message_text(message)
        self.assertIsNone(result)

    def test_extract_message_text_multiple_contents(self):
        message = {
            "blocks": [
                {
                    "block_id": "contents",
                    "text": {"text": "First part."}
                },
                {
                    "block_id": "contents",
                    "text": {"text": "Second part."}
                }
            ]
        }
        result = ai_bot.extract_message_text(message)
        self.assertEqual(result, "First part.\nSecond part.")

    def test_extract_message_text_no_blocks(self):
        message = {"text": "Plain text"}
        result = ai_bot.extract_message_text(message)
        self.assertIsNone(result)

    def test_split_text_into_chunks(self):
        text = "A" * 5000
        result = ai_bot.split_text_into_chunks(text, chunk_size=3000)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 3000)
        self.assertEqual(len(result[1]), 2000)

    def test_split_text_into_chunks_exact_multiple(self):
        text = "A" * 6000
        result = ai_bot.split_text_into_chunks(text, chunk_size=3000)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 3000)
        self.assertEqual(len(result[1]), 3000)

    def test_split_text_into_chunks_small_text(self):
        text = "A" * 1000
        result = ai_bot.split_text_into_chunks(text, chunk_size=3000)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 1000)
        self.assertEqual(result[0], "A" * 1000)

    def test_summarize_messages_less_than_two(self):
        messages = ["Only one message"]
        result = ai_bot.summarize_messages(messages)
        self.assertEqual(result, "어제는 알림 메시지가 없습니다.")

        messages = []
        result = ai_bot.summarize_messages(messages)
        self.assertEqual(result, "어제는 알림 메시지가 없습니다.")

    def test_summarize_messages_calls_gemini(self):
        # We manually mock genai instead of @patch because ai-bot has a hyphen
        mock_genai = sys.modules['google.generativeai']
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "This is a summary."
        mock_model.generate_content.return_value = mock_response

        messages = ["Message 1", "Message 2"]
        result = ai_bot.summarize_messages(messages)

        self.assertEqual(result, "This is a summary.")
        mock_genai.GenerativeModel.assert_called_with('gemini-2.5-flash')
        mock_model.generate_content.assert_called_once()
        # Verify prompt structure
        called_args = mock_model.generate_content.call_args[0][0]
        self.assertIn("Message 1", called_args)
        self.assertIn("Message 2", called_args)

if __name__ == '__main__':
    unittest.main()
