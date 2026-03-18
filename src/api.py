import requests
import pandas as pd
from datetime import datetime
import time

def get_token_accounts(helius_key, mint_address, decimals=9):
    """
    使用 Helius DAS API 獲取所有代幣持有者。
    如果能取得 decimals，就直接轉換成人類可讀餘額。
    """
    url = f"https://mainnet.helius-rpc.com/?api-key={helius_key}"
    all_holders = []
    page = 1
    
    while True:
        payload = {
            "jsonrpc": "2.0",
            "id": "my-id",
            "method": "getTokenAccounts",
            "params": {
                "page": page,
                "limit": 1000,
                "displayOptions": {},
                "mint": mint_address
            }
        }
        
        response = requests.post(url, json=payload).json()
        if 'result' not in response or not response['result']['token_accounts']:
            break
            
        accounts = response['result']['token_accounts']
        for acc in accounts:
            all_holders.append({
                "owner": acc['owner'],
                "amount": acc['amount'] / (10 ** decimals),
                "address": acc['address']
            })
        
        if len(accounts) < 1000:
            break
        page += 1
        
    return pd.DataFrame(all_holders)

def get_token_metadata(birdeye_key, mint_address):
    """
    獲取代幣的基本資訊與當前價格
    """
    url = f"https://public-api.birdeye.so/defi/token_overview?address={mint_address}"
    headers = {"X-API-KEY": birdeye_key, "accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers).json()
        if response.get('success'):
            return response['data']
    except Exception as e:
        print(f"Error fetching metadata: {e}")
    return None

def get_wallet_history(helius_key, wallet_address, mint_address):
    """
    (預留擴充) 獲取單個錢包針對某個代幣的交易歷史，用來精算成本。
    """
    url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions?api-key={helius_key}"
    pass

def fetch_historical_price(birdeye_key, mint_address, unix_time):
    """
    (進場偵探功能) 獲取該代幣在特定 Unix Timestamp 的價格
    """
    url = f"https://public-api.birdeye.so/defi/history_price?address={mint_address}&address_type=token&type=1H&time_from={unix_time}&time_to={unix_time + 3600}"
    headers = {"X-API-KEY": birdeye_key, "accept": "application/json"}
    try:
        response = requests.get(url, headers=headers).json()
        if response.get('success') and response['data']['items']:
            return response['data']['items'][0]['value']
    except Exception:
        pass
    return None
