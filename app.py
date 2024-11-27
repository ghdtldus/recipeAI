import openai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

# API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/")
def index():
    return open("templates/index.html").read()

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        # GPT-3.5 Turbo 모델을 사용한 ChatCompletion 생성
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # gpt-3.5-turbo 모델 선택
            messages=[
                {
                    "role": "system",
                    "content": "You are a chef who suggests recipes based on the ingredients provided by the user. You should only include ingredients that the user has and exclude any ingredients the user does not have."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            max_tokens=150,
            temperature=0.7
        )

        reply = response['choices'][0]['message']['content']
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
