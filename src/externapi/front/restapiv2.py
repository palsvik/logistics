import urllib3
import json
import configparser

config = configparser.ConfigParser()
config.read('front.config.ini')

apikey = config.get("FrontApiCredentials", "ApiKey")
subscriptionkey = config.get("FrontApiCredentials", "SubscriptionKey")
baseurl = config.get("https://frontsystemsapis.frontsystems.no")
apiV2path = config.get("/restapi/V2/api/")

http = urllib3.PoolManager(headers={
	"x-api-key": apikey,
	"Ocp-Apim-Subscription-Key": subscriptionkey,
	"Content-Type":"application/json"
})

##
#@ productId : String (numeric)
def deleteProduct (productId):
    if type(productId) == int:
        productId = str(productId)
    elif type(productId) != str or not productId.isnumeric():
        return None
    endpoint = baseurl + apiV2path + productId
    response = http.request(
        "DELETE",
        endpoint
    )
    return json.loads(response.data.decode('utf-8'))
