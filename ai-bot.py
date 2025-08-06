# slack_summary.py
import os
from datetime import datetime, timedelta, timezone
import time
# import openai
import google.generativeai as genai
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

KST = timezone(timedelta(hours=9))
kst_now = datetime.now(KST)

# 기본 설정
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = WebClient(token=SLACK_TOKEN)
# openAiClient = openai.OpenAI(api_key=OPENAI_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

def get_yesterday_messages():
    yesterday = kst_now - timedelta(days=1)
    # yesterday = kst_now
    start = datetime(yesterday.year, yesterday.month, yesterday.day)
    end = start + timedelta(days=1)

    raw_messages = get_all_messages(CHANNEL_ID, start.timestamp(), end.timestamp())
    messages = []

    for msg in raw_messages:
        if msg.get("user") == "U092ANCTSKU": #자신 제외
            continue
        content = extract_message_text(msg)
        if content:
            messages.append(content)
    print(len(messages))
    
    return messages

def get_all_messages(channel_id, start_ts, end_ts):
    messages = []
    cursor = None

    while True:
        try:
            response = client.conversations_history(
                channel=channel_id,
                oldest=start_ts,
                latest=end_ts,
                limit=999,
                inclusive=True,
                cursor=cursor
            )
            
            messages.extend(response["messages"])
            
            # 다음 페이지 없으면 종료
            if not response.get("has_more"):
                break
            
            # 다음 커서 설정
            cursor = response["response_metadata"]["next_cursor"]
            time.sleep(0.3)
        except SlackApiError as e:
            if e.response["error"] == "ratelimited": #대기..
                retry_after = int(e.response.headers.get("Retry-After", 1))
                print(f"Rate limited. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                continue
            else:
                raise

    return messages


def summarize_messages(messages):
    if not messages:
        return "어제는 알림 메시지가 없습니다."

    joined = "\n".join(messages)
    prompt = f"""다음은 오늘 Slack 알림 메시지 목록입니다. 아래 정보를 정리해서 알려주세요
    1. 어떤 기관에서 어떤 오류가 몇 건 발생했는지 요약해서 항목별로 정리해 주세요. 
    2. '[카카오 인증] 거래대사 비교'항목은 가장 최근 메세지 기준으로 건수 차이가 0이면 출력하지 말고 0이 아니라면 알려주세요.
    3. 출력 예시는 아래와 같습니다.
    *총 오류 발생 건수: 56건*
    1. 기관이름(기관코드): 53건
        • ETC (KafkaReplyTimeoutException): 27건
            • API: 청구서 조회(/paybill/kakao/v2/notice): 11건
            • API: 납부 가능 조회(/paybill/kakao/v2/prepay): 16건
        • KAFKA_ERROR (CommitFailedException): 26건
            • API: 납부 가능 조회(/kakao/prepay): 19건
            • API: 청구서 조회(/kakao/notice): 7건

{joined}
"""
    #oepnAi
    # response = openAiClient.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "당신은 알림 메시지를 요약하는 비서입니다."},
    #         {"role": "user", "content": prompt}
    #     ],
    #     temperature=0.3,
    #     max_tokens=500
    # )
    # return response.choices[0].message.content.strip()

    #Gemini
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text.strip()

def post_summary(summary):
    client.chat_postMessage(
        channel=CHANNEL_ID,
        # channel="C0924850G11",
        text="에러 알림 전일자 요약",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"""*📋 본 요약은 참고용입니다.*
                    알림 요약 ({(kst_now - timedelta(days=1)).date().isoformat()})
                    {summary}"""
                }
            }
        ]
    )


def extract_message_text(message):
    # blocks 안에 있는 텍스트 추출
    if "blocks" in message:
        texts = []
        for block in message["blocks"]:
            if block.get("block_id") == "contents":
                texts.append(block.get("text", {}).get("text", ""))
        return "\n".join(texts) if texts else None

    return None  # 인식 불가


if __name__ == "__main__":
    yesterday = kst_now - timedelta(days=1)
    start = datetime(yesterday.year, yesterday.month, yesterday.day)
    end = start + timedelta(days=1)
    print(kst_now)
    print(yesterday)
    print(start)
    print(end)
    print((kst_now - timedelta(days=1)).date().isoformat())
    # messages = get_yesterday_messages()
    # summary = summarize_messages(messages)
    # post_summary(summary)
