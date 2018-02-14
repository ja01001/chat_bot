import requests
import websocket
import json
import socket
import os 
from bs4 import BeautifulSoup 
""" 
	on_message(websocket, message)

	parameter :
		websocket : create socket in main to send msg 
		message : dictionary
	variance : 
		ch_msg : change_message's return value 
		retrun_msg : to send, identify return type 
	inner function, etc; 
		json.loads() : loads's parameter change type to json
		keys() : dictionary's key 
		send() : to send data though the websocket 
		dumps() : to encode for json  
"""
def on_message(ws, message):
    message = json.loads(message) # 전달받은 message는 무조건 JSON 형태이므로, 이를 사용하기 쉽게 Python Dict 형식으로 변환  -> diction aray 의 
    if 'type' not in message.keys() or message['type'] != 'message': # 입력받은 메세지가 텍스트가 아닐 경우
        return # 여기서 다룰 필요가 없으므로 그냥 끝내기
    ch_msg = change_message(message['text'])
    if ch_msg != None:
        return_msg = { 
            'channel': message['channel'], # 메세지를 입력한 채널에 다시 전송해야 하니까 그대로 가져다 쓰기
            'type': 'message', # 메세지를 전송하니까 message 형태
            'text': ch_msg # 전달할 메세지, echo 봇이니까 들어온 메세지를 그대로 다시 전달 
        }
        ws.send(json.dumps(return_msg)) # 서버에 메세지를 전송 

"""
	change_message(message)
	parameter
		message : type is str, etc
	variance 
		msg : message change to string 
		res : to post webpage of pusan univ 
		soup : 
		replace :
	inner function, etc
		str : to change str type 
		post : post msg  in webpage context area
		status_code : http response code 200 is ok 
		BeautifulSoup : html parsing lib
		res.text : find response text part
		find : to find 'td' para in html include {'class': 'tdReplace'} dictionary 
"""
def change_message(message):
    msg = str(message)
    res = requests.post('http://speller.cs.pusan.ac.kr/PnuWebSpeller/lib/check.asp',{'text1':msg})
    if res.status_code != 200:
        return None

    soup = BeautifulSoup(res.text)
    replace = soup.find('td',{'class':'tdReplace'})
    return replace.text
"""
	main 
	variance 
		token : you register slack bot integration and you get token like xoxb-...  here token heroku's change 
		get_url :to connect  slack RTM though websocket and api call 
		ws : websocket object 
"""
if __name__ == '__main__':
    token = os.environ.get('SLACK_BOT_TOKEN') 
    get_url = requests.get('https://slack.com/api/rtm.connect?token=' + token) # Slack RTM에 WebSocket 통신 URL을 가져오는 API 요청 보냄
    socket_endpoint = get_url.json()['url'] # get_url.json()은 위의 JSON 객체 형태를 지니니까, 여기서 ULR 부분만 뽑아와서 socket_endpoint에 저장
    websocket.enableTrace(True) # 디버깅을 위해 통신 정보를 모두 콘솔에 프린트 
    ws = websocket.WebSocketApp(socket_endpoint, on_message=on_message) # 가져온 URL, 콜백 함수를 이용하여 WebSocket 객체 생성
    ws.run_forever() # WebSocket 서버와 통신