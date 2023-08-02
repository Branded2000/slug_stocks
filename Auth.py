import requests
from requests.structures import CaseInsensitiveDict
import urllib.parse
import json
url = "https://api.tdameritrade.com/v1/oauth2/token"



def GetTokens(code):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    #print("code before:")
    print(code)
    
    code = urllib.parse.quote_plus(code)
    #print("code After")
    #print(code)
    
    data = "grant_type=authorization_code&refresh_token=&access_type=offline&code={}&client_id=ITO7WGSBTYFIW6BQSVDZYFUYH3ECVGET&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2FProfile".format(code)
    
    resp = requests.post(url, headers = headers, data=data)
    tokenjson = json.loads(resp.content)
    
    return tokenjson

def GetNewAuthToken(RefreshToken):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    RefreshToken = urllib.parse.quote_plus(RefreshToken)
    data = "grant_type=refresh_token&refresh_token={}&access_type=&code=&client_id=ITO7WGSBTYFIW6BQSVDZYFUYH3ECVGET&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2FProfile".format(RefreshToken)
    
    resp = requests.post(url, headers = headers, data=data)
    tokenjson = json.loads(resp.content)
    return tokenjson