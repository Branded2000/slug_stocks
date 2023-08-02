import requests
from Auth import *
from Positions import GetAccountData ,GetAccountDataUser
#from MainFile import RefreshT
from flask import session

def FormatDataToTickerDict(data):
    return {'symbol':data['Global Quote']['01. symbol'],\
            'open':data['Global Quote']['02. open'],\
            'high':data['Global Quote']['03. high'],\
            'low':data['Global Quote']['04. low'],\
            'price':data['Global Quote']['05. price'],\
            'volume':data['Global Quote']['06. volume'],\
            'latest trading day':data['Global Quote']['07. latest trading day'],\
            'previous close':data['Global Quote']['08. previous close'],\
            'change':data['Global Quote']['09. change'],\
            'change percent':data['Global Quote']['10. change percent']}


def CancelOrder(AccountNumber,OrderId,current_user):
  url = "https://api.tdameritrade.com/v1/accounts/{}/orders/{}".format(AccountNumber,OrderId)
  headers = CaseInsensitiveDict()
  headers["Authorization"] = "Bearer "+current_user.access_token
  headers["Content-Type"] = "application/json"
  responce = requests.delete(url,headers=headers)
  print( "is this response code" +  str(responce.status_code))

def Buy(Stock,Quanitiy,current_user):
    requestData = """
{
  "orderType": "MARKET",
  "session": "NORMAL",
  "duration": "DAY",
  "orderStrategyType": "SINGLE",
  "orderLegCollection": [
    {
      "instruction": "Buy",
      "quantity": AMOUNTOFSTOCK,
      "instrument": {
        "symbol": "STOCKSYMBOL",
        "assetType": "EQUITY"
      }
    }
  ]
}
"""
    requestData = requestData.replace('STOCKSYMBOL', Stock)
    requestData = requestData.replace('AMOUNTOFSTOCK', Quanitiy)
    
    Accountdata = GetAccountData()
    AccountNumber = Accountdata[0]['securitiesAccount']['accountId']
    
    url = "https://api.tdameritrade.com/v1/accounts/{}/orders".format(AccountNumber)
    
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer "+current_user.access_token
    headers["Content-Type"] = "application/json"
    request = requests.post(url,headers=headers,data=requestData)
    print(request.status_code)
    
def Sell(Stock,Quanitiy,User):
    requestData = """
{
  "orderType": "MARKET",
  "session": "NORMAL",
  "duration": "DAY",
  "orderStrategyType": "SINGLE",
  "orderLegCollection": [
    {
      "instruction": "SELL",
      "quantity": AMOUNTOFSTOCK,
      "instrument": {
        "symbol": "STOCKSYMBOL",
        "assetType": "EQUITY"
      }
    }
  ]
}
"""
    requestData = requestData.replace('STOCKSYMBOL', Stock)
    requestData = requestData.replace('AMOUNTOFSTOCK', Quanitiy)
    
    Accountdata = GetAccountDataUser(User)
    AccountNumber = Accountdata[0]['securitiesAccount']['accountId']
    
    url = "https://api.tdameritrade.com/v1/accounts/{}/orders".format(AccountNumber)
    
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer "+User.access_token
    headers["Content-Type"] = "application/json"
    request = requests.post(url,headers=headers,data=requestData)
    print(request.headers)
    print(request.status_code)
    
    
def GetQuoteNoAcc(StockName):
        key = 'ZC1007CF615L7DAV'
        #Get data from API
        if(session.get(StockName+"quote",None) != None and session.get(StockName+"quote",None).get("Note",None) == None):
            print("getting cached quotes")
            return session[StockName+"quote"]
        request = requests.get('https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol='+StockName+'&apikey='+key)
        if request.json().get("Note",None) != None:
          return None
        # Convert the data to a dictionary
        session[StockName+"quote"] = request.json()
        Quote = request.json()
        return Quote
      
def GetNews(StockName):
        key = 'ZC1007CF615L7DAV'
        if(session.get(StockName+"News",None) != None):
            print("getting cached news")
            return session[StockName+"News"]
          
        
        request = requests.get('https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers='+StockName+'&apikey='+key)
        news = request.json()
        if ("Note" in news or ('Information' in news and news['Information'] == 'Invalid inputs. Please refer to the API documentation https://www.alphavantage.co/documentation#newsapi and try again.')):
            feed = None
        else:
            feed = [{"url": new["url"], "banner_image": new["banner_image"],"title": new["title"],"source": new["source"]} for new in news['feed'][:8]] #getting first 8 news
        session[StockName+"News"] = feed
        return feed
        
def getFeedMultiStock(Stocks):
  Feed = []
  for StockName in Stocks:
      news = GetNews(StockName)
      if news == None:
        continue
      Feed = Feed + news
  return Feed