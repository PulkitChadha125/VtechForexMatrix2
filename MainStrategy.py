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
                'Belowprice':float(row['Belowprice']),
                'AbovePrice': float(row['AbovePrice']),
                'InitialTrade':None,
                'ssbupLevel':None,
                'ssbdownLevel': None,
                'bbsupLevel': None,
                'bbsdownLevel': None,
                'Orders': []
            }
            result_dict[row['Symbol']] = symbol_dict
        print(result_dict)
    except Exception as e:
        print("Error happened in fetching symbol", str(e))

level_list=[]
def remove_level(price):
    if price in level_list:
        level_list.remove(price)
        print(f"Level {price} removed from the list.")
    else:
        print(f"Level {price} not found in the list.")

def add_level(price):
    global level_list
    level_list.append(float(price))
def check_level(price):
    global level_list
    for level in level_list:
        if price == level:
            return True
    return False
get_user_settings()

def main_strategy():
    global result_dict,level_list
    try:
        for symbol, params in result_dict.items():
            symr = trade.get_data(symbol=symbol, timeframe="TIMEFRAME_M5")
            close = float(symr[0][4])
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            candletime = symr[0][0]

            if params['TradeMode']=="BBS":
                if (params['InitialTrade'] == None and close >= params['AbovePrice']):
                    add_level(params['AbovePrice'])
                    params['InitialTrade'] = "BBS"
                    params['bbsupLevel'] = params['AbovePrice'] - params['NextLevelDistance']
                    params['bbsdownLevel'] = params['AbovePrice'] + params['NextLevelDistance']
                    Oederog = f"{timestamp} One sell order and Two buy orderexecuted  @ {symbol} @ {params['Belowprice']}, next up level={params['bbsupLevel']}, next down level={params['bbsdownLevel']} "
                    print(Oederog)
                    write_to_order_logs(Oederog)
                    res = trade.mt_buy(symbol=symbol, lot=float(params['Lotsize']),
                                       MagicNumber=int(params['MagicNumber']))
                    order1_id=res


                    res = trade.mt_buy(symbol=symbol, lot=float(params['Lotsize']),
                                       MagicNumber=int(params['MagicNumber']))
                    order2_id = res

                    params['Orders'].append(trade_log)
                    res = trade.mt_short(symbol=symbol, lot=float(params['Lotsize']),
                                         MagicNumber=int(params['MagicNumber']))
                    order3_id = res
                    trade_log = {
                        "OrderID_1":order1_id,
                        "OrderType_1": "BUY",
                        "OrderID_2": order2_id,
                        "OrderType_2": "BUY",
                        "OrderID_3": order3_id,
                        "OrderType_3": "SELL",
                        "Triggrlevel":params['AbovePrice']
                    }
                    params['Orders'].append(trade_log)

                if (params['InitialTrade'] == None and close <= params['Belowprice']):
                    params['InitialTrade'] = "BBS"
                    add_level(params['Belowprice'])
                    params['bbsupLevel'] = params['Belowprice'] - params['NextLevelDistance']
                    params['bbsdownLevel'] = params['Belowprice'] + params['NextLevelDistance']
                    Oederog = f"{timestamp} One sell order and Two buy orderexecuted  @ {symbol} @ {params['Belowprice']}, next up level={params['bbsupLevel']}, next down level={params['bbsdownLevel']} "
                    print(Oederog)
                    write_to_order_logs(Oederog)
                    res = trade.mt_buy(symbol=symbol, lot=float(params['Lotsize']),
                                       MagicNumber=int(params['MagicNumber']))
                    order1_id=res


                    res = trade.mt_buy(symbol=symbol, lot=float(params['Lotsize']),
                                       MagicNumber=int(params['MagicNumber']))
                    order2_id = res
                    res = trade.mt_short(symbol=symbol, lot=float(params['Lotsize']),
                                         MagicNumber=int(params['MagicNumber']))
                    order3_id = res
                    trade_log = {
                        "OrderID_1": order1_id,
                        "OrderType_1": "BUY",
                        "OrderID_2": order2_id,
                        "OrderType_2": "BUY",
                        "OrderID_3": order3_id,
                        "OrderType_3": "SELL",
                        "Triggrlevel": params['Belowprice']
                    }
                    params['Orders'].append(trade_log)

                if (params['InitialTrade'] == "BBS" and close <= params['bbsdownLevel']):
                    if check_level(params['bbsdownLevel']) is False:
                        add_level(params['bbsdownLevel'])
                        previouslevel = params['bbsupLevel'] + params['NextLevelDistance']
                        orderlog = f"{timestamp} closing previous Sell Trade of level {previouslevel}"
                        write_to_order_logs(orderlog)
                        for order in params['Orders']:
                            if previouslevel == order['Triggrlevel']:
                                trade.mt_close_sell(symbol, params['Lotsize'],order['OrderID_3'], timestamp)

                        res = trade.mt_buy(symbol=symbol, lot=float(params['Lotsize']),
                                           MagicNumber=int(params['MagicNumber']))
                        order1_id = res

                        res = trade.mt_buy(symbol=symbol, lot=float(params['Lotsize']),
                                           MagicNumber=int(params['MagicNumber']))
                        order2_id = res
                        res = trade.mt_short(symbol=symbol, lot=float(params['Lotsize']),
                                             MagicNumber=int(params['MagicNumber']))
                        order3_id = res
                        trade_log = {
                            "OrderID_1": order1_id,
                            "OrderType_1": "BUY",
                            "OrderID_2": order2_id,
                            "OrderType_2": "BUY",
                            "OrderID_3": order3_id,
                            "OrderType_3": "SELL",
                            "Triggrlevel": params['bbsupLevel']
                        }
                        params['Orders'].append(trade_log)
                        params['bbsupLevel'] = params['bbsdownLevel'] - params['NextLevelDistance']
                        params['bbsdownLevel'] = params['bbsdownLevel'] + params['NextLevelDistance']
                        orderlog = f"{timestamp} Opening new BBS Trade this is new level next BBSup: {params['bbsupLevel']} and BBSdown:{params['bbsdownLevel']} "
                        write_to_order_logs(orderlog)

                    if check_level(params['bbsdownLevel']) is True:
                        previouslevel = params['bbsupLevel'] + params['NextLevelDistance']
                        orderlog = f"{timestamp} closing previous Sell Trade of level {previouslevel}"
                        write_to_order_logs(orderlog)
                        for order in params['Orders']:
                            if previouslevel == order['Triggrlevel']:
                                trade.mt_close_sell(symbol, params['Lotsize'], order['OrderID_3'], timestamp)

                        res = trade.mt_buy(symbol=symbol, lot=float(params['Lotsize']),
                                           MagicNumber=int(params['MagicNumber']))
                        order1_id = res

                        res = trade.mt_buy(symbol=symbol, lot=float(params['Lotsize']),
                                           MagicNumber=int(params['MagicNumber']))
                        order2_id = res
                        res = trade.mt_short(symbol=symbol, lot=float(params['Lotsize']),
                                             MagicNumber=int(params['MagicNumber']))
                        order3_id = res
                        trade_log = {
                            "OrderID_1": order1_id,
                            "OrderType_1": "BUY",
                            "OrderID_2": order2_id,
                            "OrderType_2": "BUY",
                            "OrderID_3": order3_id,
                            "OrderType_3": "SELL",
                            "Triggrlevel": params['bbsupLevel']
                        }
                        params['Orders'].append(trade_log)
                        params['bbsupLevel'] = params['bbsdownLevel'] - params['NextLevelDistance']
                        params['bbsdownLevel'] = params['bbsdownLevel'] + params['NextLevelDistance']
                        orderlog = f"{timestamp} Opening new BBS Trade this is new level next BBSup: {params['bbsupLevel']} and BBSdown:{params['bbsdownLevel']} "
                        write_to_order_logs(orderlog)

            if (params['InitialTrade'] == "BBS" and close >= params['bbsupLevel']):
                    if check_level(params['bbsupLevel']) is False:
                        add_level(params['bbsupLevel'])
                        previouslevel=params['bbsupLevel']-params['NextLevelDistance']
                        orderlog=f"{timestamp} closing previous BBS Trade of level {previouslevel}"
                        write_to_order_logs(orderlog)
                        for order in params['Orders']:
                            if previouslevel == order['Triggrlevel']:
                                trade.mt_close_buy(symbol, params['Lotsize'],order['OrderID_1'], timestamp)
                                trade.mt_close_buy(symbol, params['Lotsize'],order['OrderID_2'], timestamp)
                                trade.mt_close_sell(symbol, params['Lotsize'],order['OrderID_3'], timestamp)

                        res = trade.mt_buy(symbol=symbol, lot=float(params['Lotsize']),
                                           MagicNumber=int(params['MagicNumber']))
                        order1_id = res

                        res = trade.mt_buy(symbol=symbol, lot=float(params['Lotsize']),
                                           MagicNumber=int(params['MagicNumber']))
                        order2_id = res
                        res = trade.mt_short(symbol=symbol, lot=float(params['Lotsize']),
                                             MagicNumber=int(params['MagicNumber']))
                        order3_id = res
                        trade_log = {
                            "OrderID_1": order1_id,
                            "OrderType_1": "BUY",
                            "OrderID_2": order2_id,
                            "OrderType_2": "BUY",
                            "OrderID_3": order3_id,
                            "OrderType_3": "SELL",
                            "Triggrlevel": params['bbsupLevel']
                        }
                        params['Orders'].append(trade_log)
                        params['bbsdownLevel'] = params['bbsupLevel'] + params['NextLevelDistance']
                        params['bbsupLevel'] = params['bbsupLevel'] - params['NextLevelDistance']
                        orderlog = f"{timestamp} Opening new BBS Trade this is new level next BBSup: {params['bbsupLevel']} and BBSdown:{params['bbsdownLevel']} "
                        write_to_order_logs(orderlog)


                    if check_level(params['bbsupLevel']) is True:
                        previouslevel = params['bbsupLevel'] - params['NextLevelDistance']
                        orderlog = f"{timestamp} closing previous BBS Trade of level {previouslevel}"
                        write_to_order_logs(orderlog)
                        for order in params['Orders']:
                            if previouslevel == order['Triggrlevel']:
                                trade.mt_close_buy(symbol, params['Lotsize'], order['OrderID_1'], timestamp)
                                trade.mt_close_buy(symbol, params['Lotsize'], order['OrderID_2'], timestamp)
                                trade.mt_close_sell(symbol, params['Lotsize'], order['OrderID_3'], timestamp)

                        for order in params['Orders']:
                            if params['bbsupLevel'] == order['Triggrlevel']:
                                res = trade.mt_short(symbol=symbol, lot=float(params['Lotsize']),
                                             MagicNumber=int(params['MagicNumber']))
                                order3_id = res
                                order['OrderID_3'] =order3_id

                        params['bbsdownLevel'] = params['bbsupLevel'] + params['NextLevelDistance']
                        params['bbsupLevel'] = params['bbsupLevel'] - params['NextLevelDistance']

                        orderlog = f"{timestamp} Open 1 new sell order this level has 2 buy open, new bbsupLevel {params['bbsupLevel']},bbsdownLevel:{params['bbsdownLevel']}"
                        write_to_order_logs(orderlog)





    except Exception as e:
        print("Error happened in Main strategy loop: ", str(e))
        traceback.print_exc()


def write_to_order_logs(message):
    with open('OrderLogs.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')




# trade.mt_buy("XAUUSD",0.01,12345)
# end_date = datetime(2024, 4, 13)
# while True:
#     main_strategy()

