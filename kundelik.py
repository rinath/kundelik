import lxml.html
import requests

class Kundelik:
	def __init__(self):
		self.signed_in = False
		self.login = ''
		self.password = ''
		self.login_url = 'https://login.kundelik.kz/login'
		self.marks_url = 'kundelik.kz/marks.aspx?tab=period'
		self.homework_url = 'kundelik.kz/homework.aspx'
		self.account_type = 0 # 0 - parent, 1 - child
		self.url_begins = ['http://children.', 'http://schools.']
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language':'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
			'Accept-Encoding':'gzip, deflate',
			'Connection':'keep-alive',
			'DNT':'1'
		}
		self.session = requests.session()
	def sign_in(self):
		payload = {
			'exceededAttempts':'False',
			'ReturnUrl':'',
			'login': self.login,
			'password': self.password,
			'Captcha.Input':'',
			'Captcha.Id':'16debe27-5dcc-4471-8c6e-943701797e17'
		}
		response = self.session.post(self.login_url, data=payload, headers=self.headers)
		page = lxml.html.fromstring(response.content)
		self.account_type = 0 # this is parent's account
		if len(page.xpath('//li[@id="School"]')) > 0:
			self.account_type = 1 # this is child's account
		print('account type:', self.account_type)
		success = page.xpath('//body[@class="page-body"]')
		unsuccess = page.xpath('//body[@class="page_adaptive"]')
		if len(success) > 0:
			print('log in successful')
			self.signed_in = True
			return True
		else:
			print('log in unsuccessful')
			self.signed_in = False
			return False
	def sign_out(self):
		self.signed_in = False
		self.session = requests.session()
	def set_signed_in(self, value):
		self.signed_in = value
		if self.signed_in:
			self.sign_in()
	def is_signed_in(self):			return self.signed_in
	def set_login(self, login):		self.login = login
	def set_password(self, password):	self.password = password
	def get_login(self):			return self.login
	def get_password(self):			return self.password
	def retrieve_grades(self):
		url = self.url_begins[self.account_type] + self.marks_url
		response = self.session.post(url, headers=self.headers)
		if self.account_type == 1:
			url = change_url(response.url, 'tab', 'period')
			print('kundelik child, changed url:', url)
			response = self.session.post(url, headers=self.headers)
		page = lxml.html.fromstring(response.content)
		with open('gr2.html', 'wb') as f:
			f.write(response.content)
			f.close()
		table = page.xpath('//table[@id="journal"]/tr')
		print('account_type:', self.account_type, 'url:', url)
		print('retrieve_grades: len:', len(table))
		marks_type = 0
		if len(table[0].xpath('./th')) > 7:
			marks_type = 1
		string = ''
		if marks_type == 0:
			for i in range(2, len(table)):
				title = table[i].xpath('./td[@class="s2"]')[0].text_content()
				marks = table[i].xpath('./td[@class="tac"]')[1].text_content()
				string += title + ': <code>' + marks + '</code>\n'
		else:
			for i in range(2, len(table)):
				title = table[i].xpath('./td[@class="s2 breakword"]')[0].text_content()
				arr = table[i].xpath('./td[@class="tac"]')
				marks = '<code>'
				for j in range(1, len(arr) - 2):
					txt = arr[j].text_content()
					if len(txt) > 0:
						marks += txt + ', '
				marks += '</code>'
				string += title + ': ' + arr[-1].text_content() + '\n'
				#marks += arr[-2].text_content()
		return string
	def retrieve_homework(self, page_number):
		response = self.session.post(self.url_begins[self.account_type] + self.homework_url + '?page=' + str(page_number), headers=self.headers)
		page = lxml.html.fromstring(response.content)
		with open('hw.html', 'wb') as f:
			f.write(response.content)
			f.close()
		table = page.xpath('//table/tbody')
		if len(table) == 0:
			return {'text':'No homework', 'buttons':[]}
		table = table[0]
		homework_list = []
		string = ''
		prev_date = ''
		for row in table:
			hw = row.xpath('./td[@class="breakword"]')[0].text_content().strip()
			subject = row.xpath('./td[@class="tac light"]')[0].text_content().strip()
			date = row.xpath('./td[@class="tac nowrap"]')[0].text_content()
			date = ' '.join(date.split())
			if date != prev_date:
				string += '<b>' + date + '</b>\n'
			prev_date = date
			string += subject + ': <code>' + hw + '</code>\n'
		page_numbers = page.xpath('//div[@class="pager"]/ul/li')
		pages = len(page_numbers)
		index = -1
		for i in range(pages):
			if len(page_numbers[i].xpath('./b')) > 0:
				index = i
				break
		reply_markup = []
		if index > 0:
			reply_markup.append(str(index))
		if pages - index > 1 and index != -1:
			reply_markup.append(str(index + 2))
		return {'text':string, 'buttons':reply_markup}
	def serialize(self):
		return {
			'login' : self.login,
			'password' : self.password,
			'signed_in' : self.signed_in,
			'account_type' : self.account_type
		}
	def deserialize(self, dic):
		self.set_login(dic['login'])
		self.set_password(dic['password'])
		self.set_signed_in(dic['signed_in'])
		self.account_type = dic['account_type']
		return self

def change_url(url, variable, value):
	arr = url.split('?')
	if len(arr) == 1:
		return url + '?' + variable + '=' + value
	elif len(arr) > 2:
		print('change_url: could not change url:', url)
		return url
	variables = arr[1].split('&')
	for i in range(len(variables)):
		arr2 = variables[i].split('=')
		if len(arr2) != 2:
			print('change_url: error')
			return url
		if arr2[0] == variable:
			arr2[1] = value
			variables[i] = '='.join(arr2)
	arr[1] = '&'.join(variables)
	return '?'.join(arr)

print(change_url('https://schools.kundelik.kz/marks.aspx?school=1000001219250&tab=week', 'school', 'huy'))
























