# slack_summary.py
import os
from datetime import datetime, timedelta, timezone
import time
import google.generativeai as genai
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

KST = timezone(timedelta(hours=9))
kst_now = datetime.now(KST)

# 기본 설정
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = WebClient(token=SLACK_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

def get_yesterday_messages():
    yesterday = kst_now - timedelta(days=1)
    # yesterday = kst_now
    start = datetime(yesterday.year, yesterday.month, yesterday.day, tzinfo=KST)
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
    if len(messages) < 2:
        return "어제는 알림 메시지가 없습니다."

    joined = "\n".join(messages)
    prompt = f"""다음은 오늘 Slack 알림 메시지 목록입니다. 아래 정보를 정리해서 알려주세요
    1. 어떤 기관에서 어떤 오류가 몇 건 발생했는지 요약해서 항목별로 정리해 주세요. 
    2. '[카카오 인증] 거래대사 비교'항목은 가장 최근 메세지 기준으로 건수 차이가 0이면 출력하지 않고 그렇지 않은 경우에만 출력합니다.
    3. 출력 예시는 아래와 같습니다. 아래와 같이 출력할 데이터가 없으면 출력하지 않습니다.
    *총 오류 발생 건수: X건*
    1. 기관이름(기관코드): X건
        • ETC (KafkaReplyTimeoutException): X건
            • API: 청구서 조회(/paybill/kakao/v2/notice): X건
            • API: 납부 가능 조회(/paybill/kakao/v2/prepay): X건
        • KAFKA_ERROR (CommitFailedException): X건
            • API: 납부 가능 조회(/kakao/prepay): X건
            • API: 청구서 조회(/kakao/notice): X건

{joined}
"""
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text.strip()

def split_text_into_chunks(text, chunk_size=3000):
    """Slack block text 제한(3000자)에 맞춰 문자열 분할"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def post_summary(summary):
    # 기본 헤더
    header_text = (
        f"*📋 본 요약은 참고용입니다.*\n"
        f"알림 요약 ({(kst_now - timedelta(days=1)).date().isoformat()})\n"
    )

    # 전체 텍스트 (헤더 + summary)
    full_text = header_text + summary

    # 3000자 제한에 맞춰 분할
    chunks = split_text_into_chunks(full_text, 3000)

    # 블록 생성
    blocks = []
    for chunk in chunks:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": chunk
            }
        })

    # 메시지 전송
    client.chat_postMessage(
        channel=CHANNEL_ID,
        # channel="C0924850G11",
        text="에러 알림 전일자 요약",
        blocks=blocks
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
    messages = get_yesterday_messages()
    summary = summarize_messages(messages)
    post_summary(summary)
