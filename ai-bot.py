# slack_summary.py
import os
import datetime
import openai
import google.generativeai as genai
from slack_sdk import WebClient

# 기본 설정
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = WebClient(token=SLACK_TOKEN)
openai.api_key = OPENAI_API_KEY

def get_yesterday_messages():
    now = datetime.datetime.now()
    # yesterday = now - datetime.timedelta(days=1)
    yesterday = now
    start = datetime.datetime(yesterday.year, yesterday.month, yesterday.day)
    end = start + datetime.timedelta(days=1)

    response = client.conversations_history(
        channel=CHANNEL_ID,
        oldest=start.timestamp(),
        latest=end.timestamp(),
        limit=1000,
        inclusive=True
    )
    messages = [m["text"] for m in response["messages"] if "subtype" not in m]
    return messages

def summarize_messages(messages):
    if not messages:
        return "어제는 알림 메시지가 없습니다."

    joined = "\n".join(messages)
    prompt = f"""다음은 어제 Slack 알림 메시지 목록입니다. 오류 및 정보성 메시지를 요약해서 항목별로 정리해 주세요. 중요 이벤트는 강조해 주세요.

{joined}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 알림 메시지를 요약하는 비서입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    # model = genai.GenerativeModel('gemini-1.5-pro')
    # response = model.generate_content(prompt)
    # return response.text.strip()
    return response["choices"][0]["message"]["content"]

def post_summary(summary):
    client.chat_postMessage(
        channel=CHANNEL_ID,
        # text=f"📋 어제의 알림 요약 ({(datetime.date.today() - datetime.timedelta(days=1)).isoformat()})\n\n{summary}"
        text=f"📋 알림 요약 ({datetime.date.today().isoformat()})\n\n{summary}"
    )

if __name__ == "__main__":
    messages = get_yesterday_messages()
    summary = summarize_messages(messages)
    post_summary(summary)
