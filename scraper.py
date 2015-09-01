from bs4 import BeautifulSoup
import urllib.request
import csv
import unidecode
import datetime

import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

def get_sheet():
	json_key = json.load(open('funda-194b901c0134.json'))
	scope = ['https://spreadsheets.google.com/feeds']
	credentials = SignedJwtAssertionCredentials(json_key['client_email'], bytes(json_key['private_key'], 'utf-8'), scope)
	gc = gspread.authorize(credentials)

	return gc.open_by_key("1JZ7XDauDJzOxyaoTaOvJ0fPfm7D_OduR6AJT8AiF1IY").sheet1

fundaURL = 'http://www.funda.nl'

city = 'Utrecht'

kind = 'koop'

page = '1-dag'

startURL = '/'.join([fundaURL, kind, city, page])

sheet = get_sheet()

req = urllib.request.Request(startURL)
req.add_header('User-Agent', 'prive crawler (Python3, urllib), harm@mindshards.com')
with urllib.request.urlopen(req) as response:
	html = response.read()
	soup = BeautifulSoup(html,'html.parser')
	
	houses = soup.find('table', class_='layout listing').find('ul', class_='object-list').find_all('li', recursive=False, class_='nvm')
	for house in houses:
		price = int(unidecode.unidecode(house.find('span', class_='price').text).replace("EUR ", "").replace(".", ""))
		street = house.find('a', class_='object-street')
		deep_link = fundaURL + street.get('href')
		surface = int(house.find('span', title="Woonoppervlakte").text.replace(" m²",""))

		with urllib.request.urlopen(deep_link) as response:
			html = response.read()
			soup = BeautifulSoup(html,'html.parser')
			area = "onbekend"
			possible_area = soup.find('span', class_='specs-hdr-overflow')
			if possible_area != None:
				area = possible_area.text.replace(" in Utrecht","")
		
		sheet.append_row([price/surface, price, surface, street.text.strip(), area, deep_link,datetime.strptime(datetime.datetime.now(), "%d/%m/%Y %H:%M")])

