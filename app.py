import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# CHZZK OAuth2 설정
CLIENT_ID = "1afd076e-b2c7-4c29-a0bb-4343ffdd2fd5"
CLIENT_SECRET = "B_TGVsg0Zv0INfx2P95aivOLunkKeVlIS_8EbadEffs"
TOKEN_URL = "https://auth.chzzk.com/oauth/token"

# CHZZK API 설정
API_BASE_URL = "https://api.chzzk.com/open/v1"
HEADERS = {
    "Content-Type": "application/json"
}

# Access Token 저장
ACCESS_TOKEN = None


# Access Token 갱신 함수
def get_access_token():
    global ACCESS_TOKEN
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        token_response = response.json()
        ACCESS_TOKEN = token_response.get("access_token")
        HEADERS["Authorization"] = f"Bearer {ACCESS_TOKEN}"
        print("Access Token 갱신 성공!")
    else:
        print(f"Access Token 갱신 실패: {response.status_code}, {response.text}")


# 메시지 전송 함수
def send_chat_message(message):
    if ACCESS_TOKEN is None:
        get_access_token()

    url = f"{API_BASE_URL}/chats/send"
    payload = {"message": message}
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        print("메시지 전송 성공!")
    else:
        print(f"메시지 전송 실패: {response.status_code}, {response.text}")
        # Access Token 만료 시 갱신 후 재시도
        if response.status_code == 401:
            print("Access Token 만료, 갱신 시도 중...")
            get_access_token()
            send_chat_message(message)


# Webhook Endpoint: 채팅 메시지 감지
@app.route("/webhook/chat", methods=["POST"])
def chat_webhook():
    data = request.json
    if not data:
        return jsonify({"message": "No data received"}), 400

    # 메시지 내용 감지
    message = data.get("message", "")
    sender = data.get("sender", "Unknown")

    print(f"채팅 메시지 감지: {sender} - {message}")

    # 특정 메시지 조건
    if "김하룽바보" in message:
        send_chat_message("인정합니다!")

    return jsonify({"message": "OK"}), 200


if __name__ == "__main__":
    # 서버 시작 전 Access Token 갱신
    get_access_token()
    app.run(debug=True, port=5000)
