import re
import requests
import random
from bs4 import BeautifulSoup

nasdaq = "^IXIC"
dow = "^DJI"
nyse = "^NYA"
userAgents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
              'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
              'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.3179.73',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/117.0.0.0',
              'Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/119.0.0.0',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Vivaldi/7.3.3635.9',
              'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0']



def request_and_parse(url):
    headers = {'User-Agent' : random.choice(userAgents)}

    search = f"https://finance.yahoo.com/quote/{url}"

    page = requests.get(search, headers=headers)

    soup = BeautifulSoup(page.content, "html.parser")

    #main body we're looking at
    results = soup.find("main")

    #get numerical info
    price_block = results.find("section", {"data-testid": "quote-price"})

    #get name and ticket
    #creates python generator
    name_block = results.find("h1", string=True).strings

    return price_block, name_block


def get_name_and_ticker(result):
    #converts generator to list
    names = list(result)
    #splits and gets rid of parenthesis
    names = re.split(r'[(|)]',names[0])
    stock_name, ticker = names[0], names[1]
    return [stock_name, ticker]

def get_stock_price(result):
    quote = result.find("span", {"data-testid": "qsp-price"}).get_text()
    quote = quote.strip()
    quote = quote.replace(',','')
    quote = float(quote)
    return quote

def get_stock_change(result):
    quote_change = result.find("span", {"data-testid": "qsp-price-change"}).get_text()
    quote_change = quote_change
    return quote_change

def get_stock_change_percent(result):
    quote_change_per = result.find("span", {"data-testid": "qsp-price-change-percent"}).get_text()
    return quote_change_per

def do_everything(var):
    price_page, name_page = request_and_parse(var)
    name, ticker = get_name_and_ticker(name_page)
    stock_price = get_stock_price(price_page)
    price_change = get_stock_change(price_page)
    price_change_percent = get_stock_change_percent(price_page)
    return name, ticker, stock_price, price_change, price_change_percent

def search_for_stocks(url):
    search = f"https://finance.yahoo.com/lookup/equity/?s={url}"
    headers = {'User-Agent' : random.choice(userAgents)}
    page = requests.get(search, headers=headers)

    soup = BeautifulSoup(page.content, "html.parser")

    #main body we're looking at
    results = soup.find("tbody")

    rows = list(results.find_all("tr"))
    tds = rows[0].find_all("td")
    empty = []
    search_total = []

    for row in range(len(rows)):
        td = rows[row].find_all("td")
        search_total.append(empty)
        for cell in td:
            text = cell.get_text()
            empty.append(text)

    print(search_total[0][5])



#search_for_stocks("apple")

