# slack_summary.py
import os
import datetime
# import openai
import google.generativeai as genai
from slack_sdk import WebClient

# 기본 설정
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = WebClient(token=SLACK_TOKEN)
# openAiClient = openai.OpenAI(api_key=OPENAI_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

def get_yesterday_messages():
    now = datetime.datetime.now()
    # yesterday = now - datetime.timedelta(days=1)
    yesterday = now
    start = datetime.datetime(yesterday.year, yesterday.month, yesterday.day)
    end = start + datetime.timedelta(days=1)

    raw_messages = get_all_messages(CHANNEL_ID, start.timestamp(), end.timestamp())
    messages = []

    for msg in raw_messages:
        if msg.get("user") == "U092ANCTSKU": #자신 제외
            continue
        content = extract_message_text(msg)
        if content:
            messages.append(content)
    
    return messages

def get_all_messages(channel_id, start_ts, end_ts):
    messages = []
    cursor = None

    while True:
        response = client.conversations_history(
            channel=channel_id,
            oldest=start_ts,
            latest=end_ts,
            limit=200,
            inclusive=True,
            cursor=cursor
        )
        
        messages.extend(response["messages"])
        
        # 다음 페이지 없으면 종료
        if not response.get("has_more"):
            break
        
        # 다음 커서 설정
        cursor = response["response_metadata"]["next_cursor"]

    return messages


def summarize_messages(messages):
    if not messages:
        return "어제는 알림 메시지가 없습니다."

    joined = "\n".join(messages)
    prompt = f"""다음은 오늘 Slack 알림 메시지들의 목록입니다. 아래 기준에 따라 요약해 주세요:
1. 기관별로 어떤 오류가 발생했는지, 오류 종류별 건수를 집계해 항목별로 정리해 주세요.
2. 총 오류 발생 건수를 맨 위에 알려주세요.
3. "[카카오 인증] 거래대사 비교" 항목은, 인증 건수의 최종 차이가 0이면 생략하고, 0이 아닌 경우에만 포함시켜 주세요.
4. 결과는 Slack에서 마크다운(`mrkdwn`) 형식으로 표현할 수 있도록 출력해 주세요.


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
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(prompt)
    return response.text.strip()

def post_summary(summary):
    client.chat_postMessage(
        # channel=CHANNEL_ID,
        channel="C0924850G11",
        text="에러 알림 전일자 요약",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📋 본 요약은 참고용입니다.*\n\n{summary}"
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
    messages = get_yesterday_messages()
    summary = summarize_messages(messages)
    post_summary(summary)
