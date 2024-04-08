import time
import traceback
import pandas as pd
from pathlib import Path
import MT5Integration as trade
from datetime import datetime, timedelta, timezone
import pytz
# timezone = pytz.timezone("Etc/UTC")
result_dict = {}
current_date = datetime.today()
last_run_date=current_date - timedelta(days=1)
vantage_timezone ="GMT"
exceness="Etc/UTC"
timezoneused=exceness

def get_mt5_credentials():
    credentials = {}
    try:
        df = pd.read_csv('MT5Credentials.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials


credentials_dict = get_mt5_credentials()
Login = credentials_dict.get('Login')
Password = credentials_dict.get('Password')
Server = credentials_dict.get('Server')

print("LoginId:",Login)
print("Server:",Server)
trade.login(Login, Password, Server)
def get_user_settings():
    # Symbol	TradeMode	NextLevelDistance	Lotsize	MagicNumber
    global result_dict
    try:
        csv_path = 'TradeSettings.csv'
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        result_dict = {}

        for index, row in df.iterrows():
            # Create a nested dictionary for each symbol
            symbol_dict = {
                'TradeMode': float(row['TradeMode']),
                'NextLevelDistance': float(row['NextLevelDistance']),
                'Lotsize': float(row['Lotsize']),
                'MagicNumber': float(row['MagicNumber']),
                'TradePrice':float(row['TradePrice']),
                'InitialTrade':None,
                'CurrTradeBuyLevel':None,
                'CurrTradeSellLevel': None,
                'Orders': []
            }
            result_dict[row['Symbol']] = symbol_dict
        print(result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))


get_user_settings()

def main_strategy():
    global result_dict
    try:
        for symbol, params in result_dict.items():
            symr = trade.get_data(symbol=symbol, timeframe="TIMEFRAME_M5")
            close = float(symr[0][4])
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            candletime = symr[0][0]


    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()


def write_to_order_logs(message):
    with open('OrderLogs.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')


end_date = datetime(2024, 4, 13)
while True:
    main_strategy()

