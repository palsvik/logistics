#!python3

import sys
import csv
import time
import argparse
sys.path.append("/Users/pederhveemalsvik/dev/logistics/src/")
from externapi.front.restapiv2 import getProductsByGtin
from externapi.front.restapiv2 import updateProduct

def main():
    file = open("gtins.csv")
    gtins = {}
    csvfile = csv.reader(file)
    datenow = time.strftime("%Y-%m-%dT00:00:00Z")
    for row in csvfile:
        gtins[row[0]]=row[1]
    file.close()
    gtinlist = list(gtins.keys())
    products = getProductsByGtin(gtinlist)
    product_dict = {}
    for product in products:
        productid = product["productid"]
        sizes = product["productSizes"]
        for size in sizes:
            gtin = size["gtin"]
            if gtin in gtins.keys() and not product_dict.get(productid):
                product_dict[productid] = {
                    "price": gtins[gtin]
                }
    for productid in product_dict.keys():
        updateProduct(productid, product_dict[productid])
    outfile = open("update_list.csv", "w")
    csvfile = csv.writer(outfile)
    csvfile.writerow(["productId", "outPrice", "time"])
    for productid in product_dict.keys():
        csvfile.writerow([productid, product_dict[productid]["price"], datenow])
    outfile.close()
main()