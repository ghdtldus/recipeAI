from pymongo import MongoClient

# MongoDB Atlas 연결 정보 (올바른 URI 형식)
MONGO_URI = "mongodb+srv://ghdtldus03a:6VuFcuZB3Fe6TAPf@cluster0.hh3dg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)  # MongoDB 클라이언트 생성
    db = client.test  # 기본 데이터베이스 접근 (test DB)
    print("MongoDB Atlas에 성공적으로 연결되었습니다!")
except Exception as e:
    print(f"MongoDB 연결 실패: {e}")
