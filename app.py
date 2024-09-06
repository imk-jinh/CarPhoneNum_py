# 차량번호 등록과 전화번호 등록 후 data.json 파일에 저장 가능, 차량번호 및 전화번호 정규식 패턴 지정 완료. -> index.html
# 개별 실행시 오류 x

import json
import os
import re
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB 연결 설정
client = MongoClient(MONGODB_URI)
db = client.dbcarNum
collection = db['car_info']

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        car_number = request.form.get('car_number')
        phone_number = request.form.get('phone_number')
        
        # 차량번호의 정규식 패턴: 2-3자리 숫자 + 한글문자 + 4자리 숫자
        valid_characters = '가나다라마거너더러머버서어저고노도로모보소오조구누두루무부수우주하허호배아바사자'
        car_number_pattern = r'^\d{2,3}[' + valid_characters + r']\d{4}$'
        
        # 전화번호의 정규식 패턴: 010 + 8자리 숫자
        phone_number_pattern = r'^010\d{8}$'
        
        if re.match(car_number_pattern, car_number) and re.match(phone_number_pattern, phone_number):
            car_info = {
                "car_number": car_number,
                "phone_number": phone_number
            }
            
            # MongoDB에 저장
            collection.insert_one(car_info)
            
            print("save done!!!!")
        else:
            print("error number!!!")
            return "유효하지 않은 차량번호 또는 전화번호 입니다."
    return render_template('index.html')
    #         data = load_data()
    #         data[car_number] = phone_number
    #         save_data(data)
    #         print("save done!!!!")
    #     else:
    #         print("error number!!!")
    #         return "유효하지 않은 차량번호 또는 전화번호 입니다."
    # return render_template('index.html')
    


@app.route('/api/get_data', methods=['POST'])
def get_data():
    car_number = request.form.get('search_car_number')
    
    car_info = collection.find_one({"car_number": car_number})
    
    if car_info:
        phone_number = car_info["phone_number"]
        return render_template('index.html', result={"car_number": car_number, "phone_number": phone_number})
    else:
        return render_template('index.html', error="차량번호를 찾을 수 없습니다.")
    
    # data = load_data()
    # if car_number in data:
    #     return render_template('index.html', result={"car_number": car_number, "phone_number": data[car_number]})
    # else:
    #     return render_template('index.html', error="차량번호를 찾을 수 없습니다.")

if __name__ == '__main__':
    app.run(debug=True)
