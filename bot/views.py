from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json, datetime
# Create your views here.

def keyboard(reuquest):
    first_response={
    "type" : "buttons",
    "buttons" : ["기상정보확인", "에너지사용추천" ]
}
    return JsonResponse(first_response)

@csrf_exempt
def message(request):
    user = (request.body).decode("utf-8")
    user = json.loads(user)
    user_content = user["content"]
    reply = message_maker(user_content)
    
    response={
        "message":{
            "text" : reply
        }
        
        

        }
    return JsonResponse(response)

def message_maker(content):
    today_date = datetime.date.today().strftime("%m월 %d일")
    if content in ["기상정보확인"]:
        answer = today_date + '의 기상정보입니다' 
    elif content in ["에너지사용추천"]:
        answer = today_date + '추천 에너지 사용입니다.'
    else:
        answer = "잘모르겠습니다."
    return answer