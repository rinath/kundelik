import requests
from pprint import pprint
import json
while True:
	x = input('s - setWebhook\ng - getWebhookInfo\nr - removeWebhook\nq - quit\n')
	if x == 's':
		r = requests.get('https://api.telegram.org/bot710802627:AAFBMxqgKU_lWHua_La8xAu-IVrSWKC2qDk/setWebHook?url=https%3A%2F%2Fhu87w38xe1.execute-api.ap-southeast-2.amazonaws.com%2Fv0')
	elif x == 'g':
		r = requests.get('https://api.telegram.org/bot710802627:AAFBMxqgKU_lWHua_La8xAu-IVrSWKC2qDk/getWebhookInfo')
	elif x == 'r':
		r = requests.get('https://api.telegram.org/bot710802627:AAFBMxqgKU_lWHua_La8xAu-IVrSWKC2qDk/setWebhook')
	else:
		break;
	pprint(json.loads(r.text))