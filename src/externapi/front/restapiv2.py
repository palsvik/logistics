import os
import urllib3
import json
import configparser
import time

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "front.config.ini"))

apikey = config.get("auth", "ApiKey")
subscriptionkey = config.get("auth", "SubscriptionKey")
baseurl = config.get("url", "BaseUrl")
apiV2path = config.get("url", "ApiV2Path")

http = urllib3.PoolManager(headers={
	"x-api-key": apikey,
	"Ocp-Apim-Subscription-Key": subscriptionkey,
	"Content-Type":"application/json"
})

def getStockList():
    print("Fetching stock list...")
    endpoint = baseurl + apiV2path + "Stock/list"
    response = http.request(
        "GET",
        endpoint
    )
    if response.status >= 400:
        print(f"Request Error with status code {response.status}")
        print(response.reason)
        return False
    print(f"Status code {response.status}")
    data = json.loads(response.data.decode("utf-8"))
    return data

def getStores():
    endpoint = baseurl + apiV2path + "Stores"
    response = http.request(
        "GET",
        endpoint
    )
    if response.status >= 400:
        print(f"Request Error with status code {response.status}")
        print(response.reason)
        return False
    print(f"Status code {response.status}")
    data = json.loads(response.data.decode("utf-8"))
    return data

def getSizeSystems():
    endpoint = baseurl + apiV2path + "SizeSystems"
    response = http.request(
        "GET",
        endpoint
    )
    if response.status >= 400:
        print(f"Request Error with status code {response.status}")
        print(response.reason)
        return False
    print(f"Status code {response.status}")
    data = json.loads(response.data.decode("utf-8"))
    return data

def getSeasons():
    endpoint = baseurl + apiV2path + "SizeSystems"
    response = http.request(
        "GET",
        endpoint
    )
    if response.status >= 400:
        print(f"Request Error with status code {response.status}")
        print(response.reason)
        return False
    print(f"Status code {response.status}")
    data = json.loads(response.data.decode("utf-8"))
    return data

def product_products(query):
    endpoint = baseurl + apiV2path + "Product"
    response = http.request(
        "POST",
        endpoint,
        body=json.dumps(query)
    )
    if response.status >= 400:
        print(f"Request Error with status code {response.status}")
        print(response.reason)
        return []
    print(f"Status code {response.status}")
    data = json.loads(response.data.decode("utf-8"))
    return data

def updateProduct(productId, updatePayload):
    if type(productId) == int:
        productId = str(productId)
    elif type(productId) != str or not productId.isnumeric():
        print(f"Error: Invalid product ID: {productId}")
        return False
    endpoint = baseurl + apiV2path + "products/" + productId
    print(endpoint)
    response = http.request(
        "PUT",
        endpoint,
        body=json.dumps(updatePayload)
    )
    if response.status >= 400:
        print(f"Error: Response failed with error code {response.status}")
        print(response.reason)
        print("Payload:")
        print(updatePayload)
        return False
    print(f"Update successful! Response code {response.status}")
    print(f"Product with id {productId} updated.")
    return True

##
#@ productId : String (numeric)
#ret None
def deleteProduct (productId):
    if type(productId) == int:
        productId = str(productId)
    elif type(productId) != str or not productId.isnumeric():
        print(f"Error: Invalid product ID: {productId}")
        return False
    print(f"Deleting product with id {productId}...")
    endpoint = baseurl + apiV2path + "products/" + productId
    response = http.request(
        "DELETE",
        endpoint
    )
    if response.status >= 400:
        print(f"Error: Response failed with error code {response.status}")
        print(response.reason)
        print(f"Product ID {productId} doesn't exist?")
        return False
    print(f"Delete successful! Response code {response.status}")
    print(f"Product with id {productId} deleted.")
    return True

def createProductTransfer(productLines, storeId, stockId, toStockId, orderDate=False, expectedDeliveryDate=False, insertAsReceived=False):
    endpoint = baseurl + apiV2path + "ProductTransfer"
    if not orderDate:
        orderDate = time.strftime("%Y-%m-%dT00:00:00Z")
    if not expectedDeliveryDate:
        expectedDeliveryDate = orderDate
    payload = {
        "storeId": storeId,
        "stockId": stockId,
        "toStockId": toStockId,
        "orderDate": orderDate,
        "expectedDeliveryDate": expectedDeliveryDate,
        "comment": "Created by API call",
        "insertAsRecevied": insertAsReceived,
        "productLines": productLines
    }
    response = http.request(
        "PUT",
        endpoint,
        body=json.dumps(payload)
    )
    if response.status >= 400:
        print(f"Error: Response failed with error code {response.status}")
        print("Attempted payload:")
        print(payload)
        return False
    print(f"Product transfer successful! Response code {response.status}")
    return response.json()

# ids : list
# includeStock
def getProductsById(ids, showStock=False):
    if len(ids) == 0:
        return []
    print("Fetching products by ID...")
    query = {
        "includeStockQuantity": showStock,
        "productIds": ids
    }
    data = product_products(query)
    return data

def getProductsByGtin(gtins, showStock=False):
    query = {
        "includeStockQuantity": showStock,
        "gtins": gtins
    }
    data = product_products(query)
    return data

def updateProductsById(ids, payloads, showStock=False):
    for (id, payload) in zip(ids, payloads):
        updateProduct(id, payload)

# 
def deleteProductsById(ids):
    print("Deleting products...")
    if len(ids) == 0:
        print("No products to delete!")
        return
    for id in ids:
        print(id)
        deleteProduct(id)
    print("Delete completed!")            

# send list of gtins
# return list of ids             
def getProductIdsByGtins(gtins):
    styles = getProductsByGtin(gtins)
    ids = set()
    for style in styles:
        ids.add(style['productid'])
    return list(ids)

def getGtinsByProductIds(id_size_dict):
    styles = getProductsById(list(id_size_dict))
    output_dict = {}
    for style in styles:
        productId = str(style["productid"])
        output_dict[productId] = []
        sizes = id_size_dict[productId]
        for size in style["productSizes"]:
            if size["label"] in sizes:
                output_dict[productId].append((size["label"], size["gtin"]))
            elif size["label"] == "":
                output_dict[productId].append(("OneSize", size["gtin"]))                
    return output_dict

