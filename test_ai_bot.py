import unittest
import sys
from unittest.mock import MagicMock
import importlib

# Mock sys.modules for google.generativeai, slack_sdk, and openai before importing
sys.modules['google'] = MagicMock()
sys.modules['google.generativeai'] = MagicMock()
sys.modules['slack_sdk'] = MagicMock()
sys.modules['slack_sdk.errors'] = MagicMock()
sys.modules['openai'] = MagicMock()

# Import ai-bot using importlib due to the hyphen
ai_bot = importlib.import_module("ai-bot")

class TestAIBot(unittest.TestCase):
    def test_summarize_messages_empty_list(self):
        result = ai_bot.summarize_messages([])
        self.assertEqual(result, "어제는 알림 메시지가 없습니다.")

    def test_summarize_messages_single_item(self):
        result = ai_bot.summarize_messages(["single message"])
        self.assertEqual(result, "어제는 알림 메시지가 없습니다.")

if __name__ == '__main__':
    unittest.main()
