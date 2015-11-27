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
	
	houses = soup.find('ul', class_='search-results').find_all('div', class_="search-result")#, recursive=False, class_='nvm')
	for house in houses:
		print("XXXXXXXXXX")
		print(house)
		price = int(unidecode.unidecode(house.find('span', class_='search-result-price').text).replace("EUR ", "").replace(".", "").replace("kk",""))
		street = house.find('h3', class_='search-result-title')
		deep_link = fundaURL + house.find('div', class_='search-result-header').find('a').get('href')
		surface = int(house.find('span', title="Woonoppervlakte").text.replace(" m²",""))

		with urllib.request.urlopen(deep_link) as response:
			html = response.read()
			soup = BeautifulSoup(html,'html.parser')
			#area = "onbekend"
			area = soup.find('ol', class_='breadcrumb-list').find_all('li')[2].find('a').get('title')
			#if possible_area != None:
			#	area = possible_area.text.replace(" in Utrecht","")

		jetst = datetime.datetime.now()
		sheet.append_row([price/surface, price, surface, street.text.strip(), area, deep_link,jetst.strftime("%d/%m/%Y %H:%M")])

