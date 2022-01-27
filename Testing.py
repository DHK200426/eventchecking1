from flask import Flask, request, jsonify, render_template, send_file
import requests
from pytz import timezone, utc
import datetime
from datetime import timedelta

application=Flask(__name__)

KST=timezone('Asia/Seoul')
Msg = [["[오늘 아침]","[오늘 점심]","[오늘 저녁]"],["[내일 아침]","[내일 점심]","[내일 저녁]"]]
Menu = [["","",""],["","",""]] # 오늘, 내일 급식
Menu_saved_date = "" # 급식 불러온 날짜

def Make_aDay(L):
    now = datetime.datetime.now()
    after = now + timedelta(days = L)
    snow = now.strftime('%Y%m%d')
    safter = after.strftime('%Y%m%d')
    return snow,safter

def what_is_menu():  # made by 1316, 1301 advanced by 2106
    global Menu, Menu_saved_date
    now, after = Make_aDay(1)
    if Menu_saved_date == "" or Menu_saved_date != now:
        Menu = [["", "", ""], ["", "", ""]]
        Menu_saved_date = now
        url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
        params = {'KEY': 'b9558a909eb84bc68f5dd7add35f34a0',
                  'ATPT_OFCDC_SC_CODE': 'D10',
                  'SD_SCHUL_CODE': '7240331',
                  'MLSV_FROM_YMD': now,
                  'MLSV_TO_YMD': after,
                  'Type': 'json',
                  'pIndex': 1,
                  'pSize': 100}
        response = requests.get(url, params=params)
        res = response.json()
        for i in range(res['mealServiceDietInfo'][0]['head'][0]['list_total_count']):
            if res['mealServiceDietInfo'][1]['row'][i]['MLSV_YMD'] == now:
                tempmenu = res['mealServiceDietInfo'][1]['row'][i]['DDISH_NM']
                tempmenu = tempmenu.split('<br/>')
                final_menu = "\n".join(tempmenu)
                Menu[0][int(res['mealServiceDietInfo'][1]['row'][i]['MMEAL_SC_CODE']) - 1] = final_menu
            else:
                tempmenu = res['mealServiceDietInfo'][1]['row'][i]['DDISH_NM']
                tempmenu = tempmenu.split('<br/>')
                final_menu = "\n".join(tempmenu)
                Menu[1][int(res['mealServiceDietInfo'][1]['row'][i]['MMEAL_SC_CODE']) - 1] = final_menu

    req = request.get_json()  # 파라미터 값 불러오기
    askmenu = req["action"]["detailParams"]["ask_menu"]["value"]

    
    now = datetime.datetime.utcnow()  # 몇 번째 주인지 계산
    date = int(utc.localize(now).astimezone(KST).strftime("%d"))
    month = int(utc.localize(now).astimezone(KST).strftime("%m"))
    year = int(utc.localize(now).astimezone(KST).strftime("%Y"))
    
    '''
    cday = (year - 1) * 365 + (year - 1) // 4 - (year - 1) // 100 + (year - 1) // 400
    if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0: cday += 1
    for i in range(month - 1): cday += mday[i]
    cday += date
    if askmenu == "내일 급식": cday += 1
    cweek = (cday - 1) // 7
    cweek -= 105407  # 2021-03-02 = 105407번째 주
    classn = ["1반", "2반", "3반", "4반"]
    boborder = "급식 순서 : " + classn[cweek % 4] 급식 순서 퇴화
    for i in range(1, 4): boborder += ' - ' + classn[(i + cweek) % 4]
    '''

    hour = int(utc.localize(now).astimezone(KST).strftime("%H"))  # Meal 계산
    minu = int(utc.localize(now).astimezone(KST).strftime("%M"))
    if (hour == 7 and minu >= 30) or (hour >= 8 and hour <= 12) or (hour == 13 and minu < 30):
        Meal = "아침"  # 가장 최근 식사가 언제인지 자동 계산
    elif (hour == 13 and minu >= 30) or (hour >= 14 and hour < 19) or (hour == 19 and minu < 30):
        Meal = "점심"
    else:
        Meal = "저녁"
    i = 0
    if Meal == "아침":
        fi = 1; si = 2; ti = 0  # 아침 점심 저녁 정보 불러오기 및 배열
    elif Meal == "점심":
        fi = 2; si = 0; ti = 1
    elif Meal == "저녁":
        fi = 0; si = 1; ti = 2
    if askmenu == "내일 급식": fi = 0; si = 1; ti = 2; i = 1
    first = Menu[i][fi]
    second = Menu[i][si]
    third = Menu[i][ti]
    if Menu[i][fi] == "": first = "등록된 급식이 없습니다."
    if Menu[i][si] == "": second = "등록된 급식이 없습니다."
    if Menu[i][ti] == "": third = "등록된 급식이 없습니다."
    return Msg[i][fi], Msg[i][si], Msg[i][ti], first, second, third


@application.route('/menu', methods=['POST'])
def response_menu():  # 메뉴 대답 함수
    msg1, msg2, msg3, menu1, menu2, menu3 = what_is_menu()
    if menu1 == "등록된 급식이 없습니다." and menu2 == "등록된 급식이 없습니다." and menu3 == "등록된 급식이 없습니다.":
        res = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": "급식이 없는 날입니다."
                        }
                    }
                ]
            }
        }
    else:
        res = {  # 답변
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "carousel": {
                            "type": "basicCard",
                            "items": [
                                {"title": msg1, "description": menu1},
                                {"title": msg2, "description": menu2},
                                {"title": msg3, "description": menu3}
                            ]
                        }
                    }  # ,
                    # {
                    # "simpleText": {
                    # "text": boborder
                    # }
                    # }
                ]
            }
        }
    return jsonify(res)


def load_event(): #made by 2106
    event = {}
    now,after = Make_aDay(15)
    url = "https://open.neis.go.kr/hub/SchoolSchedule"
    params = {'KEY' : 'b9558a909eb84bc68f5dd7add35f34a0',
              'ATPT_OFCDC_SC_CODE':'D10',
              'SD_SCHUL_CODE' : '7240331',
              'AA_FROM_YMD':now,
              'AA_TO_YMD':after,
              'Type': 'json',
              'pIndex': 1,
              'pSize':100}
    response = requests.get(url,params = params)
    res = response.json()
    for i in range(res['SchoolSchedule'][0]['head'][0]['list_total_count']):
        if res['SchoolSchedule'][1]['row'][i]['AA_YMD'] not in event:
            event[res['SchoolSchedule'][1]['row'][i]['AA_YMD']] = res['SchoolSchedule'][1]['row'][i]['EVENT_NM']
        else:
            temp = event[res['SchoolSchedule'][1]['row'][i]['AA_YMD']]
            temp = temp + '\n' + res['SchoolSchedule'][1]['row'][i]['EVENT_NM']
            event[res['SchoolSchedule'][1]['row'][i]['AA_YMD']] = temp
    return event

@application.route('/eventcheck', methods=['POST'])
def Evecheck():
    events = load_event()
    final_events = [{"title": date , "description" : event} for date,event in zip(events.keys(),events.values())]
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "carousel": {
                        "type": "basicCard",
                        "items": final_events
                    }
                }
            ]
        }
    }
    return jsonify(res)

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)
