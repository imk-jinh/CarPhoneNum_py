import json
import os
import re
from flask import Flask, render_template, request, jsonify
import requests
import uuid
import time
from dotenv import load_dotenv
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/')
def main():
    if request.method == 'POST':
        # POST 요청 처리 코드
        return "POST 요청 처리 결과"
    else:
        return render_template('home.html')

# data_file = 'data.json'

# # json 파일이 없으면 생성한다.
# if not os.path.exists(data_file):
#     with open(data_file, 'w') as f:
#         json.dump({}, f)

# def load_data():
#     with open(data_file, 'r') as f:
#         data = json.load(f)
#     return data

# def save_data(data):
#     with open(data_file, 'w') as f:
#         json.dump(data, f)

# # 더미 데이터 생성 및 저장
# dummy_data = {
#     "156하2334": "010-1234-5678",
#     "23로9323": "010-9876-5432"
# }
# save_data(dummy_data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        car_number = request.form.get('car_number')
        phone_number = request.form.get('phone_number')
        
        # 차량번호의 정규식 패턴: 2-3자리 숫자 + 한글문자 + 4자리 숫자
        valid_characters = '가나다라마거너더러머버서어저고노도로모보소오조구누두루무부수우주하허호배아바사자'
        car_number_pattern = r'^\d{2,3}[' + valid_characters + r']\d{4}$'
        
        # 전화번호의 정규식 패턴: 010 + 8자리 숫자
        phone_number_pattern = r'^010\d{8}$'
        
        if re.match (car_number_pattern, car_number) and re.match(phone_number_pattern, phone_number):
            car_info = {
                "car_number": car_number,
                "phone_number": phone_number
            }
            
            # MongoDB에 저장
            collection.insert_one(car_info)
            
            # data = load_data()
            # data[car_number] = phone_number
            # save_data(data)
            print("save done!!!!")
            print(car_number, phone_number)
        else:
            print("error number!!!")
            return render_template('register.html', error="차량번호 또는 전화번호가 잘못된 형식입니다.")
    else:
        return render_template('register.html')
    return render_template('register.html',car_number=car_number, phone_number=phone_number)

# MongoDB 연결 설정
client = MongoClient(MONGODB_URI)
db = client.dbcarNum
collection = db['car_info']

# 네이버 Clova OCR API 설정
api_url = 'https://a4zjwhwgh9.apigw.ntruss.com/custom/v1/24664/e99ca576399da962039f6d16f0761a416a1b76c782c3d9b6f5c10016e842eef1/general'
secret_key = OCR_SECRET_KEY

# 차량번호 정규식 패턴
valid_characters = '가나다라마거너더러머버서어저고노도로모보소오조구누두루무부수우주하허호배아바사자'
car_number_pattern = r'^\d{2,3}[' + valid_characters + r']\d{4}$'

def satisfies_condition(text):
    # 2~3개의 숫자와 1개의 한글 문자로 구성되는지 체크
    if len(text) >= 3 and len(text) <= 6:
        digit_count = 0
        hangul_count = 0

        for char in text:
            if char.isdigit():
                digit_count += 1
            elif char.isalpha() and '가' <= char <= '힣':
                hangul_count += 1

        if digit_count >= 2 and hangul_count == 1:
            return True

    return False

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # 업로드된 이미지 파일을 가져옴
        image_file = request.files['image']
        
        # API 요청을 위한 JSON 데이터 구성
        request_json = {
            'images': [
                {
                    'format': 'jpg',
                    'name': 'uploaded_image'
                }
            ],
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': int(round(time.time() * 1000))
        }
        
        payload = {'message': json.dumps(request_json).encode('UTF-8')}
        files = [
            ('file', image_file)
        ]
        
        headers = {
            'X-OCR-SECRET': secret_key
        }
        
        # API 요청 보내기
        response = requests.post(api_url, headers=headers, data=payload, files=files)
        result_text = response.json()
        
        # 추출된 텍스트 가져오기
        extracted_text = ""
        car_numbers = []
        front_text = ""
        back_text = ""
        for item in result_text['images'][0]['fields']:
            text = item['inferText']
            print(text)
            
            if re.match(car_number_pattern, text):
                extracted_text += text + '\n'
                car_numbers.append(text)
            
            elif satisfies_condition(text):
                if len(front_text) < 2:
                    front_text += text
            elif text.isdigit() and len(text) == 4:
                back_text = text
                
            if front_text or back_text:
                text = front_text + back_text
                car_numbers.append(text)
                
                

            print("Front Text:", front_text)
            print("Back Text:", back_text)
            print(text)
                
                # 차량번호에 대응하는 전화번호 가져오기
                # data = load_data()
                # if text in data:
                #     extracted_text += "전화번호: " + data[text] + '\n'
            
        # JSON 파일로 저장
        save_path = 'extracted_text.json'
        with open(save_path, 'w') as json_file:
            json.dump(result_text, json_file, indent=4)
        
        print("텍스트 추출 결과========", extracted_text)
        print("조회할 차량번호=========", car_numbers)
        
        # 차량번호에 대응하는 전화번호 가져오기
        phone_numbers = {}
        for car_number in car_numbers:
            car_info = collection.find_one({"car_number": car_number})
            if car_info:
                phone_number = car_info["phone_number"]
                phone_numbers[car_number] = phone_number
                return render_template('search.html', result={"car_number": car_number, "phone_number": phone_number})
            else:
                return render_template('search.html', error="등록되지 않은 차량번호 입니다.")
        
        return render_template('search.html', result={"car_number": car_number, "phone_number": phone_number})
    
    return render_template('search.html')

@app.route('/api/get_data', methods=['POST'])
def get_data():
    car_number = request.form.get('search_car_number')
    
    car_info = collection.find_one({"car_number": car_number})
    
    if car_info:
        phone_number = car_info["phone_number"]
        return render_template('search.html', result={"car_number": car_number, "phone_number": phone_number})
    else:
        return render_template('search.html', error="등록되지 않은 차량번호 입니다.")
    
    # data = load_data()
    # if car_number in data:
    #     return render_template('search.html', result={"car_number": car_number, "phone_number": data[car_number]})
    # else:
    #     return render_template('search.html', error="차량번호를 찾을 수 없습니다.")

if __name__ == '__main__':
    app.run(debug=True)