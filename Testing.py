import requests
from pytz import timezone, utc
import datetime
from datetime import timedelta

KST=timezone('Asia/Seoul')

def Make_aDay():
    now = datetime.datetime.utcnow()
    after = now + timedelta(days = 7)
    snow = now.strftime('%Y%m%d')
    safter = after.strftime('%Y%m%d')
    return snow,safter

def load_event():
    event = {}
    now,after = Make_aDay()
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

@application.route('/eventcheck')
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