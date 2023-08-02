from flask_login import current_user
from datetime import datetime
import requests
from Auth import *
import pandas as pd
from datetime import datetime
import time
from Refresh import RefreshT


def GetAccountDataUser(User):
    url = "https://api.tdameritrade.com/v1/accounts?fields=positions"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer "+User.access_token
    request = requests.get(url,headers=headers)
    Accountdata = request.json()
    return Accountdata

def GetAccountData():
    url = "https://api.tdameritrade.com/v1/accounts?fields=positions"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer "+current_user.access_token
    request = requests.get(url,headers=headers)
    Accountdata = request.json()
    return Accountdata

def GetMaxQuantity(StockName):
    Positions = GetPositions()
    for Pos in Positions:
        if  Pos[3].upper() == StockName.upper():
            return Pos[0]
    return 0
def GetPositions():
    RefreshT()
    if current_user.access_token =="":
        return([])
    data = list()
    Assets = list()
    try: #catch the KeyError when an account does not have positions
        data = GetAccountData()[0]['securitiesAccount']['positions']
        for position in data:
            if  position['instrument'] and  position['instrument']['symbol'] == "MMDA1":
                CashPosition = position
    except KeyError:
        data = None
        pass

    if data != None:
        #print(data)
        Assets.append((CashPosition["longQuantity"],1,1,"Cash"))
        for pos in data:
            if  pos['instrument']['symbol'] != "MMDA1":
                Assets.append((pos["longQuantity"],pos["averagePrice"],pos["marketValue"]/pos['longQuantity'],pos['instrument']['symbol']))
    else:
        Assets.append(-1)
    #print(Assets)
    return Assets
def AdjustStringTime(Time):
    index = Time.find("T")
    return Time[:index]
def GetOrders():
    RefreshT()
    url = "https://api.tdameritrade.com/v1/orders"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer "+current_user.access_token
    headers["Content-Type"] = "application/json"
    request = requests.get(url,headers=headers)
    Orders = request.json()
    OrderList = [(Order["accountId"],Order['orderId'],
                  Order["orderLegCollection"][0]["instrument"]["symbol"],
                  Order["orderLegCollection"][0]["instruction"],Order["filledQuantity"],
                  Order["quantity"],AdjustStringTime(Order["enteredTime"])) for Order in Orders if Order["status"]!= "CANCELED" and Order["remainingQuantity"]>0]
    return OrderList

def GetTotalInvestment(avg_price,quantity): #gets total investmet on all assets
    total_investments = 0
    for i in range(len(quantity)):
        total_investments += int(quantity[i]) * int(avg_price[i])
    return total_investments

def getPercentage(avg_price, quantity): #gets the percentage the user owns for each asset
    percentage = []
    total_investments = GetTotalInvestment(avg_price,quantity)
    for i in range(len(quantity)):
        percentage.append(int(quantity[i]) * int(avg_price[i]))
    for i in range(len(quantity)):
        percentage[i] = round(percentage[i]/total_investments,2) * 100
    return percentage

def get_time(unix_time): #transform unix time to readable date time
    time = datetime.fromtimestamp(unix_time).strftime('%b %d %Y %H:%M')
    return time

def same_length_lists(lengths, values, times):
    to_return = []
    min_length = min(lengths)
    for (list, index) in zip(values,range(len(values))):
        difference = lengths[index] - min_length
        for i in range(difference):
            values[list].pop(0)
    difference = lengths[0] - min_length
    for i in range(difference):
        times.pop(0)
    to_return.append(values)
    to_return.append(times)
    return to_return

def get_1days_time_values(asset_name, quantity): #gets the times and closing values of all assets the user owns and sums its quantity*closing value to provide the user an estimate of his investment performance 
    time_val = []
    times = []
    values = []
    time_val_list = {}
    lengths = []
    quantity_index = 0
    current_unix_time = str(round(time.time() * 1000))
    RefreshT()
    for ticker in asset_name:
        url = "https://api.tdameritrade.com/v1/marketdata/"+ticker.upper()+"/pricehistory?frequencyType=minute&frequency=10&periodType=day&period=1" #changed date range
        headers = CaseInsensitiveDict()
        headers["Authorization"] = "Bearer "+current_user.access_token
        headers["Content-Type"] = "application/json"
        request = requests.get(url,headers=headers)
        #print(headers,url)
        data = request.json()
        time_val = data['candles']
        temp_val =[]
        for i in time_val:
            if quantity_index == 0: 
                times.append(get_time((i['datetime'])/1000))
            temp_val.append(i['close'] * quantity[quantity_index]) #multiply closing price of stock and the quantity that user owns of that stock 
        time_val_list[ticker] = temp_val
        #print('Length of ' + ticker + ': ' + str(len(temp_val)) + '\n')
        lengths.append(len(temp_val) - 1)
        quantity_index += 1
    
    time_val = []
    table_of_values = same_length_lists(lengths,time_val_list,times)
    df = pd.DataFrame(table_of_values[0])
    sum_val = df.sum(axis=1)
    for i in sum_val:
        values.append(i)
    time_val.append(table_of_values[1])
    time_val.append(values)
    return time_val  