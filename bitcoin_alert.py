import requests as r
from requests import Request, Session
import json,_thread,time
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects


alert_book = {}
current_price = 0

class TelegramConnect:
    def __init__(self):
        self.api_url = "https://api.telegram.org/bot1151046918:AAGJCJc5q7Sw3NrUFMm0FnVHhsoUyp-hj4U/"

    def getUpdates(self,offset=0):
        resp = r.get(self.api_url+'getUpdates',{'offset':offset})   
        return resp.json()['result']

    def send_message(self,chat_id,text):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        resp = r.post(self.api_url + 'sendMessage', params)
        return resp

bot = TelegramConnect()

def get_latest_bitcoin_price():

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': '5f577480-614b-4e59-879d-f61c518795ff',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url)
        data = json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    print("BTC Price", float(data['data'][0]['quote']['USD']['price']))
    return float(data['data'][0]['quote']['USD']['price'])

def send_trigger():
    while True:
        current_price = get_latest_bitcoin_price()
        for id,prices in alert_book.items():
            for price in prices.keys():
                if (float(current_price)>=float(price)) and not alert_book[id][price]:
                    alert_book[id][price] = True
                    bot.send_message(id, 'Bitcoin alert => Current Price: $'+str(current_price))
                    bot.send_message(id, 'Bitcoin alert => Trigger Price: $'+str(float(price)))
        time.sleep(30)

def main():
    new_offset = 0
    print("Bot Alive!!!")

    while True:
        messages = bot.getUpdates(new_offset)

        if len(messages) > 0:
            for message in messages:
                print(message)
                first_update_id = message['update_id']
                if 'text' not in message['message']:
                    first_chat_text='New member'
                else:
                    first_chat_text = message['message']['text']
                first_chat_id = message['message']['chat']['id']
                if 'first_name' in message['message']:
                    first_chat_name = message['message']['chat']['first_name']
                elif 'new_chat_member' in message['message']:
                    first_chat_name = message['message']['new_chat_member']['username']
                elif 'from' in message['message']:
                    first_chat_name = message['message']['from']['first_name']
                else:
                    first_chat_name = "unknown"

                try:
                    if first_chat_text.split()[0] in ['set','Set']:
                        alert_book[first_chat_id] = {first_chat_text.split()[1]:False}  
                        print(alert_book)
                        bot.send_message(first_chat_id, 'Bitcoin alert set at $'+first_chat_text.split()[1]+'.' )
                        new_offset = first_update_id + 1
                    elif first_chat_text in  ['check','Check']:
                        bot.send_message(first_chat_id, 'Bitcoin price: $'+current_price)
                    else:
                        bot.send_message(first_chat_id, 'send \'set XXX\' replacing quotes and price instead of XXX.')
                        new_offset = first_update_id + 1
                except:
                    print("Some error occured, please try again later.")


if __name__ == '__main__':
    try:
        try:
           _thread.start_new_thread( send_trigger,() )
        except ValueError:
           print ("Error: unable to start thread", ValueError)
        main()
    except KeyboardInterrupt:
        exit()
