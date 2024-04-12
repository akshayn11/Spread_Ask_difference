# import logging
# # from kiteconnect import KiteTicker
# from kiteconnect import KiteConnect

# logging.basicConfig(level=logging.DEBUG)
# key="b81f5ldjwoudy02l"
# secret_key="1pjssjqheymzkhkjmaifbgn6v18og84b"
# kite=KiteConnect(api_key=key)
# print(f"Follow this link to generate request token {kite.login_url()}")
# request_token = input("Enter request token ")
# # kws = KiteTicker(key, access_token)
# data=kite.generate_session(request_token,api_secret=secret_key)
# access_token=(data["access_token"])

# print("Access token is : ",access_token)
# print("\n")

# from datetime import datetime

# ctime=datetime.now()
# print(ctime.strftime("%I:%M:%S"))









import logging
from kiteconnect import KiteTicker
from kiteconnect import KiteConnect

logging.basicConfig(level=logging.DEBUG)
key="b81f5ldjwoudy02l"
secret_key="1pjssjqheymzkhkjmaifbgn6v18og84b"
kite=KiteConnect(api_key=key)
print(f"Follow this link to generate request token {kite.login_url()}")
request_token = input("Enter request token ")
# kws = KiteTicker(key, access_token)
data=kite.generate_session(request_token,api_secret=secret_key)
access_token=(data["access_token"])

print("Access token is : ",access_token)
print("\n")




# for multiple trading symbol
# def find_the_trading_symbol(date, index, strikes):
#     try:
#         new_data_list = []
#         year, month, day = date.split('-')  # Split date outside the loop
        
#         for strike in strikes:
#             strike_part = ''.join(filter(str.isalpha, strike))
#             alphabetic_part_upper = strike_part.upper()
#             numeric_part = ''.join(filter(str.isdigit, strike))
#             year_short = year[-2:]  # Use a different variable name to avoid overwriting 'year'
#             new_month = month.lstrip('0')
#             new_data = ''.join([map_dict[index]['NAME'], year_short, new_month, day, numeric_part, alphabetic_part_upper])
#             new_data_list.append(new_data)
#         return new_data_list
#     except Exception as e:
#         print("Error occurred:", e)
#         return None