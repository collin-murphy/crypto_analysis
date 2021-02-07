from bs4 import BeautifulSoup
import requests as rq
import os
from PIL import Image
import pandas as pd
import urllib.request
import json

URL = "https://coinmarketcap.com/"

#getCurrencies() - find all top 100 cryptos on front page of coinmarketcat.com
def getCurrencies(URL):
    #open link
    r2 = rq.get(URL)
    soup = BeautifulSoup(r2.text, "html.parser")
    currencies = []
    for a in soup.find_all('a', href=True):
        if "/currencies/" in a['href']:
            currencies.append(a)
    return currencies

#assembleCurrencies() - create a working link for each cryptocurrency
def assembleCurrencies(currencies):
    #complete every link that isn't full
    for c in currencies:
        if "coinmarketcap.com" not in c['href']:
            c['href'] = "https://coinmarketcap.com" + str(c["href"])
    
    
    #remove terms that we don't want from list of currencies
    bannedTerms = ["volume", "markets", "wrapped"]
    for term in bannedTerms:
        for c in currencies:
            if term in c['href']:
                currencies.remove(c)
        for c in currencies:
            if term in c['href']:
                currencies.remove(c)

    #Organize currencies by name and link
    names = []
    for c in currencies:
        name = str(c['href']).split("https://coinmarketcap.com/currencies/")[1].split("/")[0].replace("-", " ")

        if name not in names:
            names.append((name, c['href']))

    #filter out any repeats (if any)
    noRepeats = list(set([i for i in names]))

    return noRepeats

#getData() - retrieve information from each link and store them in a tuple with a name and a price
def getData(currencies):
    prices = []
    for c in currencies:
        html_content = rq.get(c[1]+"historical-data/").text
        soup = BeautifulSoup(html_content, "lxml")
        mydivs = soup.select("div[class*=priceValue]")

        for div in mydivs:
            text = div.text.split("$")[1].split("/")[0].replace(",", "")
        prices.append((c[0],text))
        print("Processing " + c[0] + "...")
    
    print("Processing complete.")
    return prices

#sort() - put the cryptocurrencies in a pandas dataframe
def sort(prices):
    rows = []
    for n in prices:
        rows.append([n[0], (float(n[1]))])
    data = pd.DataFrame(rows, columns = ["Name", "Price"])
    return data

#topx() - Print the top x crytpocurrencies by value
def topx(data,x):
    data = data.sort_values(by=["Price"] ,ascending = False)
    print("Top " + str(x) +" Cryptocurrencies by price:")
    print(data.head(x))

def writeData(prices):
    f = open("prices.json", "w")
    f.write("{\n")
    for p in prices:
        f.write("\t\"" + p[0] +"\":" + p[1] + "")
        if p[0] != prices[len(prices)-1][0]:
            f.write(",\n")
        else:
            f.write("\n")
    f.write("}")
    f.close()

def readData():
    # Opening JSON file 
    f = open('prices.json') 
  
    # returns JSON object as  
    # a dictionary 
    data = json.load(f) 
    list = [(k, v) for k, v in data.items()] 
    
    return list
    
def main():
    choice = 0
    while choice != "u" and choice !="l":
        choice = input("Press \'u\' to update database or \'l\' to read previous data: ")
    if choice == "u":
        currencies = getCurrencies(URL)
        currencies = assembleCurrencies(currencies)
        prices = getData(currencies)
        writeData(prices)
        prices = sort(prices)
        print("\nDatabase has been updated.\n")
    else:
        prices = readData()
        prices = sort(prices)
        print("\nData loaded from prices.json successfully.\n")

    
    isValid = False
    while isValid == False:
        value = input("Enter number of currencies to show: ")
        if not value.isnumeric():
            print("Number must be numerical")
            isValid = False
        elif int(value) > 100:
            print("Number must be less than 100")
            isValid = False
        else: isValid = True

    topx(prices,int(value))
    print("\nInformation provided by coinmarketcap.com")

if __name__ == "__main__":
    main()