import re
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json, datetime
import requests
import numpy as np
# Create your views here.
data = {}

def keyboard(reuquest):
    first_response={
    "type" : "buttons",
    "buttons" : ["위치정보등록"]
}
    return JsonResponse(first_response)

@csrf_exempt
def message(request):
    global data
    user = (request.body).decode("utf-8")
    user = json.loads(user)
    user_key = user["user_key"]
    user_content = user["content"]
    if user_content in ["위치정보등록"]:
        response = first_menu(user_content)
    elif user_content in ['마포','은평','강북','노원','양천','영등포','동작','강남','구로','관악','강동','중구','성동','송파','서대문','서초','도봉','중랑','용산','광진','동대문','남산','성북','종로']:
        temp={user_key:user_content}
        data = {**data, **temp} 
        response = second_menu(user_content)
    elif re.search(r'[ㄱ-힣]{1,3} 기상정보확인', user_content):
        location = data[user_key]
        print(location)
        response = third_menu(user_content,location)
    elif re.search(r'[ㄱ-힣]{1,3} 에너지사용추천', user_content):
        response = fourth_menu(user_content)
    elif user_content in ['에어콘 사용']:
        location = data[user_key]
        response = fifth_menu(user_content,location)
    elif user_content in ['히터 사용']:
        location = data[user_key]
        response = six_menu(user_content,location)
    

    return JsonResponse(response)

def message_maker(reply, buttons, menu=["example"]):
    response={
    "message":{
        "text" : reply
    }   
    }
    if buttons is True:
        response["keyboard"]={
                'type': 'buttons',
                'buttons': menu            
            }
    else:
        response["keyboard"]={
            'type': 'text'
        }
    return response

def first_menu(content):
    ans = "마포, 은평, 강북, 노원, 양천, 영등포, 동작, 강남, 구로, 관악, 강동, 중구, 성동, 송파, 서대문, 서초, 도봉, 중랑, 용산, 광진, 동대문, 남산, 성북, 종로"

    ans = ans + "중에 입력해주세요"
    final_ans = message_maker(reply=ans, buttons=False)
    return final_ans
def second_menu(content):
    second_ans = message_maker(reply= "선택해주세요" , buttons=True, menu = ["%s구 기상정보확인"%content, "%s구 에너지사용추천"%content])
    return second_ans
def third_menu(content,location): #실시간 기상정보 전송
    
    today_date = datetime.date.today().strftime("%m월 %d일")

    infor = weather(location)

    answer = today_date + location + '의 기상정보입니다' + '온도' + str(infor[0]) + '강수' + str(infor[1]) + '습도' + str(infor[2])

    final_answer = message_maker(reply=answer, buttons=True, menu=["그만하기", "%s구 에너지사용추천"%location,"위치정보등록"])
    print(final_answer)
    return final_answer
def fourth_menu(content): #가전제품 정보 전송

    fourth_ans = message_maker(reply= "선택해주세요" , buttons=True, menu = ["에어콘 사용", "히터 사용"])
    return fourth_ans
def fifth_menu(content,location): #에어콘 모델정보 전송

    result = weather_airconditon(location)

    fifth_ans = message_maker(reply = result, buttons=True, menu =['히터사용','%s구 기상정보확인'%location])
    return fifth_ans

def six_menu(content,location):

    result = weather_heater(location)

    six_ans = message_maker(reply = result, buttons=True, menu =['에어콘 사용','%s구 기상정보확인'%location])
    return six_ans
    





def weather(content):
    #실시간 데이터 연동
    weatherURL = "http://openapi.seoul.go.kr:8088/4477637a6c6d756e3130384e616b6859/json/RealtimeWeatherStation/0/24"

    conf = requests.get(url=weatherURL)

    weatherdata = conf.json()

    weatherlist= []
    # 위치별 기온 강수 습도 
    for i in range(0,24):
        if content == weatherdata["RealtimeWeatherStation"]["row"][i]["STN_NM"]:
            x = weatherdata["RealtimeWeatherStation"]["row"][i]["SAWS_TA_AVG"]
            x1 = weatherdata["RealtimeWeatherStation"]["row"][i]["SAWS_RN_SUM"]
            x2 = weatherdata["RealtimeWeatherStation"]["row"][i]["SAWS_HD"]

    weatherlist = [x,x1,x2]
    return  weatherlist


def sigmoid(x): # 시그모이드함수
    return 1 / (1 +np.exp(-x))

def weather_airconditon(content): # 에어콘 추천 모델
    #실시간 데이터 연동
    weatherURL = "http://openapi.seoul.go.kr:8088/4477637a6c6d756e3130384e616b6859/json/RealtimeWeatherStation/0/24"

    conf = requests.get(url=weatherURL)

    weatherdata = conf.json()


    # 위치별 기온 강수 습도 순으로 indexing
    for i in range(0,24):
        if content == weatherdata["RealtimeWeatherStation"]["row"][i]["STN_NM"]:
            x = weatherdata["RealtimeWeatherStation"]["row"][i]["SAWS_TA_AVG"]
            x1 = weatherdata["RealtimeWeatherStation"]["row"][i]["SAWS_RN_SUM"]
            x2 = weatherdata["RealtimeWeatherStation"]["row"][i]["SAWS_HD"]

    #airconditon 모델

    airconditon_model = -20.681561 + 0.612228*x + 0.398742*x1 + 0.059454*x2

    airconditon_model_log = sigmoid(airconditon_model)

    print(x,x1,x2,airconditon_model_log)

    result = ""
    #모델 적용
    print(airconditon_model_log)
    if airconditon_model_log > 0.8:
        result="에어컨 사용을 강력 추천드립니다"
    elif airconditon_model_log >0.5:
        result="에이콘 사용을 추천 드립니다."
    elif airconditon_model_log > 0.25:
        result="에이콘 사용을 별로 추천하지 않습니다."
    else:
        result="에어콘 사용을 하지 말아주세요"

    return result

def weather_heater(content):
    #실시간 데이터 연동
    weatherURL = "http://openapi.seoul.go.kr:8088/4477637a6c6d756e3130384e616b6859/json/RealtimeWeatherStation/0/24"

    conf = requests.get(url=weatherURL)

    weatherdata = conf.json()


# 위치별 기온 강수 습도 순으로 indexing
    for i in range(0,23):
        if content == weatherdata["RealtimeWeatherStation"]["row"][i]["STN_NM"]:
            x1 = weatherdata["RealtimeWeatherStation"]["row"][i]["SAWS_TA_AVG"]
            x = weatherdata["RealtimeWeatherStation"]["row"][i]["SAWS_OBS_TM"]

    x= int(x[8:10]) #시간만 뽑아옴

#heater 모델

    heater_model = -0.73802 + 0.25783*x + -0.35194*x1

    heater_model_log = sigmoid(heater_model)

    print(x,x1,heater_model_log)

#모델 적용

    if heater_model_log > 0.8:
        result="히터 사용을 강력 추천드립니다"
    elif heater_model_log >0.5:
        result="히터 사용을 추천 드립니다."
    elif heater_model_log > 0.25:
        result="히터 사용을 별로 추천하지 않습니다."
    else:
        result="히터 사용을 하지 말아주세요"
    
    return result