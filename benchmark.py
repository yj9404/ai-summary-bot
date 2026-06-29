import time
import importlib
import sys
from unittest.mock import MagicMock

# Mock modules to avoid initialization errors
import os
os.environ['SLACK_BOT_TOKEN'] = 'dummy'
os.environ['SLACK_CHANNEL_ID'] = 'dummy'
os.environ['GEMINI_API_KEY'] = 'dummy'

google_mock = MagicMock()
google_mock.__path__ = []
sys.modules['google'] = google_mock
sys.modules['google.genai'] = MagicMock()
sys.modules['google.genai.types'] = MagicMock()
sys.modules['slack_sdk'] = MagicMock()
sys.modules['slack_sdk.errors'] = MagicMock()

ai_bot = importlib.import_module("ai-bot")

# Mock the Slack WebClient
mock_client = MagicMock()
ai_bot.client = mock_client

def run_benchmark(num_pages=10):
    def mock_conversations_history(*args, **kwargs):
        cursor = kwargs.get('cursor')
        if cursor is None:
            page = 0
        else:
            page = int(cursor)

        has_more = page < num_pages - 1
        next_cursor = str(page + 1) if has_more else ""

        return {
            "messages": [{"text": f"message from page {page}"}],
            "has_more": has_more,
            "response_metadata": {"next_cursor": next_cursor}
        }

    mock_client.conversations_history.side_effect = mock_conversations_history

    start_time = time.time()
    ai_bot.get_all_messages("C123", 0, 100)
    end_time = time.time()

    return end_time - start_time

if __name__ == "__main__":
    duration = run_benchmark(20)
    print(f"Benchmark for 20 pages: {duration:.4f} seconds")
