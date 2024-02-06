#!python3

import os
import sys
import csv
import argparse
import configparser
from appscript import app, k

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
utilPath = config.get("env", "UtilPath")
sys.path.append(utilPath)
from externapi.front.restapiv2 import getProductsById
from externapi.front.restapiv2 import getStockList

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=str, required=True)

recipientFile = config.get("email", "RecipientFile")

productIdHeader = config.get("personalization", "ProductIdHeader")
stockIdHeader = config.get("personalization", "StockIdHeader")
stockNameHeader = config.get("personalization", "StockNameHeader")
emailHeader = config.get("personalization", "EmailHeader")

outlook = app("Microsoft Outlook")

def send_email (recipient, title, message):
    msg = outlook.make(
		new=k.outgoing_message,
		with_properties={
			k.subject: title,
			k.content: message
		}
	)
    for r in recipient["epost"]:
        msg.make(new=k.recipient,
                with_properties={
                    k.email_address: {
                        k.address: r		
                    }	
                }
        )
    msg.open()
    msg.activate()

def getProductIdsFromCSVFile(filename, productIdHeader):
    file = None
    try:
        file = open(filename, "r", encoding="utf-8-sig")
    except FileNotFoundError:
        print(f"File {filename} does not exist!")
        return False
    csvfile = csv.DictReader(file, delimiter=";")
    if productIdHeader not in csvfile.fieldnames:
        print("Wrong format of product list CSV-file!")
        print(f"File should contain a column {productIdHeader}")
        return False
    productIds = []
    for row in csvfile:
        productIds.append(row[productIdHeader])
    return productIds

def getStockByProductId(productIds):
    stocks = getStockList()
    stockQtyDict = {}
    products = getProductsById(productIds, showStock=True)
    for product in products:
        sizes = product["productSizes"]
        stocklist = []
        for size in sizes:
            if size["stockQty"]:
                stocks = size["stockQty"]
                for stock in stocks:
                    stockId = stock["stockId"]
                    if stockId not in stocklist:
                        if not stockQtyDict.get(stockId):
                            stockQtyDict[stockId] = {
                                "products": []
                            }
                        stockQtyDict[stockId]["products"].append({
                                "name": product["name"],
                                "number": product["number"],
                                "brand": product["brand"],
                                "productId": product["productid"],
                                "price": product["price"],
                                "season": product["season"]
                            })
                        stocklist.append(stockId)
    return stockQtyDict

def getMailingDict(filename, stockIdHeader, stockNameHeader, emailHeader):
    file = None
    try:
        file = open(filename, "r", encoding="utf-8-sig")
    except FileNotFoundError:
        print(f"{filename} does not exist!")
        print(f"Please create a CSV-file with columns {stockIdHeader}, {stockNameHeader} and {emailHeader}")
        return False
    csvfile = csv.DictReader(file, delimiter=";")
    if stockIdHeader not in csvfile.fieldnames or stockNameHeader not in csvfile.fieldnames or emailHeader not in csvfile.fieldnames:
        print("Wrong format of mailing list CSV-file!")
        print(f"File should contain columns {stockIdHeader}, {stockNameHeader} and {emailHeader}")
        return False
    mailingDict = {}
    for row in csvfile:
        mailingDict[row[stockIdHeader]]= {
            "name": row[stockNameHeader],
            "emails": row[emailHeader].split(",")
        }
    return mailingDict

def sendPriceUpdateMessage(recipient, products):
    columns = ["Produkt ID", "Navn", "Merke", "Ny utpris"]
    message = f"Hei! <br>"
    message += f"Følgende styles som {recipient['name']} har på lager har fått nye utpriser<br><br>:"
    message += "<table><tr>"
    for column in columns:
        message += "<th style=\"text-align: center; height: 40px\">" + column + "</th>"
    message += "</tr>"
    for product in products:
        message += "<tr>"
        message += "<td style=\"text-align: center; height: 40px\">" + str(product["productId"]) + "</td>"
        message += "<td style=\"text-align: center; height: 40px\">" + product["name"] + "</td>"
        message += "<td style=\"text-align: center; height: 40px\">" + product["brand"] + "</td>"
        message += "<td style=\"text-align: center; height: 40px\">" + str(product["price"]) + "</td>"
        message += "</tr>"
    message += "</table>"
    message += "<br><br>"
    message += "Vennlig hilsen,"
    send_email({"epost":recipient["emails"]}, "Nye utpriser", message)

def main():
    args = parser.parse_args()
    filename = args.file
    productIds = getProductIdsFromCSVFile(filename, productIdHeader)
    if not productIds:
        sys.exit(1)
    stockQtyDict = getStockByProductId(productIds)
    mailingDict = getMailingDict(recipientFile, stockIdHeader, stockNameHeader, emailHeader)
    if not mailingDict:
        sys.exit(1)
    for stockId in stockQtyDict.keys():
        if not mailingDict.get(str(stockId)):
            print(f"Warning: Could not find recipient for stockID {str(stockId)}")
        else:
            sendPriceUpdateMessage(mailingDict[str(stockId)], stockQtyDict[stockId]["products"])

main()