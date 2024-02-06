#!python3

import os
import sys
import csv
import argparse
import configparser

sys.path.append("/Users/pederhveemalsvik/dev/logistics/src/")

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))
utilPath = config.get("env", "UtilPath")
sys.path.append(utilPath)
from externapi.front.restapiv2 import createProductTransfer
from externapi.front.restapiv2 import getStockList
from externapi.front.restapiv2 import getStores

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=str, required=True)
parser.add_argument("--to", type=str, required=True)
parser.add_argument("--stock", type=str, required=False)

def getStoreId(stockId):
    stockId = int(stockId)
    stores = getStores()
    for store in stores:
        if store["StockId"] == stockId:
            return store["StoreId"]
    return None

def createProductLines(filename):
    file = open(filename, "r", encoding="utf-8-sig")
    productLines = []
    csvfile = csv.DictReader(file, delimiter=";")
    for row in csvfile:
        productLines.append(
            {
                "gtin": row["gtin"],
                "qty": int(row["qty"])
            }
        )
    return productLines

def main():
    args = parser.parse_args()
    filename = args.file
    toStockId = args.to
    fromStockId = args.stock
    stockList = getStockList()
    if not stockList.get(toStockId):
        print(f"To-stock ID {toStockId} is invalid!")
        sys.exit(1)
    toStockName = stockList[toStockId]
    if not fromStockId:
        fromStockId = "4023"
    elif not stockList.get(fromStockId):
        print(f"From-stock ID {fromStockId} is invalid!")
        sys.exit(1)
    fromStockName = stockList[fromStockId]
    fromStoreId = getStoreId(fromStockId)
    if not fromStoreId:
        print(f"From-stock ID {fromStockId} is valid, but cannot find store ID for the stock!")
        sys.exit(1)
    confirm = input(f"Transfering products from {fromStockName} to {toStockName}? [Y/n]: ")
    if (confirm != "Y"):
        print("Products not transfered.")
        sys.exit(1)
    productLines = createProductLines(filename)
    print(f"Transfering products to {toStockName}...")
    transferId = createProductTransfer(productLines, storeId=fromStoreId, stockId=fromStockId, toStockId=toStockId)
    print(transferId)

main()