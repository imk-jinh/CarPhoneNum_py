# 이미지 업로드 후 텍스트 분석 추출 완료 extracted_text.json에 저장 완료. -> 연결 index2.html
# 개별 실행시 오류 x

from flask import Flask, render_template, request
import requests
import uuid
import time
import json
import re

app = Flask(__name__)

# 네이버 Clova OCR API 설정
api_url = 'https://a4zjwhwgh9.apigw.ntruss.com/custom/v1/24664/e99ca576399da962039f6d16f0761a416a1b76c782c3d9b6f5c10016e842eef1/general'
secret_key = OCR_SECRET_KEY
# 차량번호 정규식 패턴
valid_characters = '가나다라마거너더러머버서어저고노도로모보소오조구누두루무부수우주하허호배아바사자'
car_number_pattern = r'^\d{2,3}[' + valid_characters + r']\d{4}$'

@app.route('/', methods=['GET', 'POST'])
def index():
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
        for item in result_text['images'][0]['fields']:
            text = item['inferText']
            if re.match(car_number_pattern, text):
                extracted_text += text + '\n'

        
            
        # JSON 파일로 저장
        save_path = 'extracted_text.json'
        with open(save_path, 'w') as json_file:
            json.dump(result_text, json_file, indent=4)
        
        print("텍스트 추출 결과========", extracted_text)
        return render_template('index2.html', extracted_text=extracted_text)
    
    return render_template('index2.html')

if __name__ == '__main__':
    app.run(debug=True)
