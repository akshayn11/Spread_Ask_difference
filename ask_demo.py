
import asyncio
import json
import pandas as pd
from datetime import datetime
from kiteconnect import KiteConnect
from kiteconnect import KiteTicker
import time
import configparser

current_instrument_token=None
current_instrument_token_CE = None
current_instrument_token_PE = None
selected_index=None
index_list_instrument_token=[]

config=configparser.ConfigParser()
config.read("user_data.ini")
entered_key=config['user']['key']
entered_secret=config['user']['secret']
entered_access=config['user']['access_token']

key=entered_key
secret=entered_secret
kite = KiteConnect(api_key=key)
access_token = entered_access
kite.set_access_token(access_token)
kws = KiteTicker(key,access_token)
df = pd.read_csv("https://api.kite.trade/instruments")
map_dict={"NIFTY 50":{'NAME':'NIFTY','SEGMENT':'NFO-OPT'},
          'NIFTY BANK':{'NAME':'BANKNIFTY','SEGMENT':'NFO-OPT'},
          'NIFTY FIN SERVICE':{'NAME':'FINNIFTY','SEGMENT':'NFO-OPT'},
          'NIFTY MID SELECT':{'NAME':'MIDCPNIFTY','SEGMENT':'NFO-OPT'},
          'SENSEX':{'NAME':'SENSEX','SEGMENT':'BFO-OPT'},
          'BANKEX':{'NAME':'BANKEX','SEGMENT':'BFO-OPT'},

          }



def get_recent_expiry(index_value):
    global df
    
    df['expiry'] = pd.to_datetime(df['expiry'],dayfirst="True")
    index_name=map_dict[index_value]['NAME']
    segment=map_dict[index_value]['SEGMENT']
    
    filtered_df_for_nifty = df[(df['name'] == index_name)  & (df['segment'] == segment)]
    unique_expiry_dates = {timestamp.date() for timestamp in filtered_df_for_nifty['expiry']}

    today = datetime.now().date()
    closest_date = min(unique_expiry_dates, key=lambda x: abs(x - today))

    return closest_date.strftime('%Y-%m-%d')


def get_expiry(index,expiry):
    # this function return the dict based on expiry and index
    global df   
    
    index_name=map_dict[index]['NAME']
    segment=map_dict[index]['SEGMENT']

    df['expiry'] = pd.to_datetime(df['expiry'],dayfirst="True")
    df['expiry_2'] = df['expiry'].astype(str)
    filtered_df_for_nifty = df[(df['name']== index_name) & (df['expiry_2']== expiry) & (df['segment'] == segment)]
    # print("filtered df",filtered_df_for_nifty)
    # output_dict = filtered_df_for_nifty.iloc[1:].set_index('instrument_token')['tradingsymbol'].to_dict()
    output_dict=filtered_df_for_nifty.set_index('instrument_token')['tradingsymbol'].to_dict()
    # print(output_dict)
    return output_dict

def get_expiry_ce_pe(index, expiry):
    global df
    
    index_name = map_dict[index]['NAME']
    segment = map_dict[index]['SEGMENT']

    df['expiry'] = pd.to_datetime(df['expiry'], dayfirst=True)
    df['expiry_2'] = df['expiry'].astype(str)
    
    filtered_df_for_nifty = df[(df['name'] == index_name) & 
                               (df['expiry_2'] == expiry) & 
                               (df['segment'] == segment)]
        
    ce_data = filtered_df_for_nifty[filtered_df_for_nifty['instrument_type'] == "CE"]
    pe_data = filtered_df_for_nifty[filtered_df_for_nifty['instrument_type'] == "PE"]

    ce_dict = ce_data.set_index('instrument_token')['tradingsymbol'].to_dict()
    # print(ce_dict)
    pe_dict = pe_data.set_index('instrument_token')['tradingsymbol'].to_dict()
    
    return {'CE': ce_dict, 'PE': pe_dict}


def find_the_trading_symbol(date,index,strike):
    global map_dict
    try:
        strike_part=''.join(filter(str.isalpha, strike))
        alphabetic_part_upper = strike_part.upper()
        result = ''.join(filter(str.isdigit, strike)) + alphabetic_part_upper
        year,month,date=date.split('-')
        year=year[-2:]
        new_month=month.lstrip('0')
        # print(new_month)
        ce_trading_symbol=''.join([map_dict[index]['NAME'],year,new_month,date,result,"CE"])
        pe_trading_symbol=''.join([map_dict[index]['NAME'],year,new_month,date,result,"PE"])
        return [ce_trading_symbol,pe_trading_symbol]

    except Exception as e:
        print("Error occured",e)
        return None

def find_instrument_token(data_dict, trading_symbols):
    tokens = []
    for segment, symbols in data_dict.items():
        for instrument_token, symbol in symbols.items():
            if symbol in trading_symbols:
                tokens.append(instrument_token)
    return tokens
    # return None

def flatten_list(nested_list):
    flattened_list = []
    for element in nested_list:
        if isinstance(element, list):
            flattened_list.extend(flatten_list(element))
        else:
            flattened_list.append(element)
    return flattened_list
# filtering_the_data(df,'SENSEX')
# current_expiry=get_recent_expiry('SENSEX')
# print("Nearest expiry is",current_expiry)
# instrument_data=get_expiry('SENSEX',current_expiry)
# instrument_tokens=instrument_data.keys()
# list_instrument_token=list(instrument_tokens)
# print(list_instrument_token)


def get_chart_data(instrument_token=current_instrument_token):
    try:
        return data_dict[instrument_token]
    except :
        return {}



data_dict = {}

def on_ticks(ws, ticks):
    global list_instument_token
    global instu_map, data_dict

    # ctime = int(time.time())

    ctime = datetime.now()

# Format the current time into a string in the format '%I:%M:%S'
    formatted_time = ctime.strftime('%I:%M:%S')

    # Remove colons from the formatted time string
    formatted_time_without_colons = formatted_time.replace(':', '')

    # Convert the formatted time string to an integers
    new_time_int = int(formatted_time_without_colons)

    for tick in ticks:      
        # print(tick)
        try:
            diff= tick['depth']['sell'][0]['price'] -  tick['depth']['buy'][0]['price']
            data_dict[tick["instrument_token"]][new_time_int] = diff
        except KeyError:
            data_dict[tick["instrument_token"]] = {}
        finally:
            pass

    # print("Data dict",data_dict)
# ON_CONNECT  get called only once 
def on_connect(ws, response):
    global map_dict, index_list_instrument_token

    unique_lists = set()
    for i in map_dict: 
        current_expiry = get_recent_expiry(i)
        instrument_data = get_expiry(i, current_expiry)
        instrument_tokens = list(instrument_data.keys())
        unique_lists.add(tuple(instrument_tokens))  # Convert list to tuple for set uniqueness

    index_list_instrument_token = [list(tokens) for tokens in unique_lists]

    combine_index_list_instrument_token=flatten_list(index_list_instrument_token)
    # print("combine list",combine_index_list_instrument_token)

    ws.subscribe(combine_index_list_instrument_token)
    ws.set_mode(ws.MODE_FULL, combine_index_list_instrument_token)


def on_close(ws, code, reason):

  
    pass

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close
kws.connect(threaded=True)

##---------------------------------------- CHART LOGIC ---------------------------------------------------##

from fastapi import FastAPI, Request,HTTPException, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")     

templates = Jinja2Templates(directory="templates")



@app.post("/process_input")
async def process_input(request: Request):
    global current_instrument_token_CE, current_instrument_token_PE
    global selected_index
    try:
        
        
        data = await request.json()
        user_input = data.get("input")
        selected_index = data.get("selection")
        if user_input is None or selected_index is None:
            raise HTTPException(status_code=400, detail="Input data is missing or empty")
        


        
        output_dict={'trading_symbol': user_input,'index':selected_index}
        # print("Received user input:", user_input)
        # print("Selected index:", selected_index)
        print(output_dict)
        recent_expiry=get_recent_expiry(selected_index)
        selected_index=selected_index
        instrument_data=get_expiry_ce_pe(selected_index,recent_expiry)
        # print('Instrument data',instrument_data)
        trading_symbol=find_the_trading_symbol(recent_expiry,selected_index,user_input)
        # print("Trading symbol is ",trading_symbol)

        aacurrent_instrument_token=find_instrument_token(instrument_data,trading_symbol)
        # print("Current instrument token is",aacurrent_instrument_token)
        current_instrument_token_CE, current_instrument_token_PE=aacurrent_instrument_token
        return {"message": "Data received successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing input: {str(e)}")
    

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    data = []
    return templates.TemplateResponse(request=request, name="index.html", context={"data": data})


##---------------------------------------- WEBSOCKET LOGIC --------------------------------------##
async def send_data(websocket):
    global current_instrument_token_CE, current_instrument_token_PE 
    while True:
        ce_data = get_chart_data(instrument_token=current_instrument_token_CE)
        pe_data = get_chart_data(instrument_token=current_instrument_token_PE)
        data = {"CE" : ce_data, "PE" : pe_data}
        # print(data)
        await websocket.send_text(json.dumps(data))
        await asyncio.sleep(0.5)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await send_data(websocket)





import uvicorn
if __name__ == "__main__":
    print("running FastAPI")
    uvicorn.run(app, host="127.0.0.1", port=8005)
    
