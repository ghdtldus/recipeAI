from flask import Flask, request, jsonify, render_template
import openai
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from collections import Counter


# 환경 변수 로드
load_dotenv()


# MongoDB 연결
mongo_client = MongoClient(os.getenv("MONGO_URI"))  # 환경변수에서 MongoDB URI 가져오기
db = mongo_client["cooking_bot"]  # 데이터베이스 선택
chat_collection = db["chats"]  # 대화 기록을 저장할 컬렉션


# API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        # 기본 레시피 생성
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """당신은 요리 전문가입니다. 사용자가 입력한 재료를 기반으로 최소 3가지 요리 레시피를 제안하세요. 각 요리는 사용자가 제공한 재료만을 활용해야 합니다. 사용자가 제공하지 않은 소금과 같은 기본 조미료들은 추가하지 마세요.
                        각 요리 레시피는 

                       보기 좋은 HTML 형식으로 응답하세요. 
                        각 요리는 🍳 이모지와 함께 제공하세요."""
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            max_tokens=1000,
            temperature=0.8
        )

        reply = response['choices'][0]['message']['content']

         # HTML 형식으로 변환
        formatted_reply = "<h3>🍽️ 추천 레시피</h3><ul>"
        for idx, recipe in enumerate(reply.split("\n\n"), start=1):
            formatted_reply += f"<li><strong>{recipe}</strong></li>"
        formatted_reply += "</ul>"

        # MongoDB에 대화 데이터 저장
        chat_data = {"user_input": user_input, "bot_reply": reply}
        chat_collection.insert_one(chat_data)

        return jsonify({"reply": formatted_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate-image", methods=["POST"])
def generate_image():
    description = request.json.get("description", "")

    if not description:
        return jsonify({"error": "No description provided"}), 400

    try:
        # DALL·E 이미지 생성
        image_response = openai.Image.create(
            prompt=description,
            n=1,
            size="512x512"
        )
        image_url = image_response['data'][0]['url']
        return jsonify({"image_url": image_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/history", methods=["GET"])
def get_history():
    history = list(chat_collection.find({}, {"_id": 0}).sort("_id", -1).limit(10))  
    return jsonify({"history": history})

@app.route("/popular-ingredients", methods=["GET"])
def get_popular_ingredients():
    chats = list(chat_collection.find({}, {"_id": 0, "user_input": 1}))  # 유저 입력만 가져옴
    ingredient_counter = Counter()

    for chat in chats:
        ingredients = chat["user_input"].split(", ")  # 입력된 재료를 리스트로 변환
        ingredient_counter.update(ingredients)  # 등장 횟수 카운트

    top_ingredients = ingredient_counter.most_common(5)  # 가장 많이 등장한 5가지 재료
    return jsonify({"popular_ingredients": top_ingredients})



if __name__ == "__main__":
    app.run(debug=True)
