import requests
import datetime

import config

class BotHandler:

    def __init__(self):
        self.token = config.token 
        self.api_url = "https://api.telegram.org/bot{}/".format(self.token)

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 1:
            last_update = get_result[-1]
        else:
            last_update = get_result[len(get_result)]

        return last_update

bot = BotHandler( )

def bot_help( chatid, args ):
    msg = """
Commands:
    play [video_id] - play a video
    help - print this help screen
    """
    if args[0] != "help":
        msg = "Unknown command: '{}'\n".format( args[0] ) + msg
    bot.send_message( chatid, msg )

def bot_play( chatid, args ):
    msg = "playing {}".format( args[1] )
    bot.send_message( chatid, msg )

bot_toplevel = {
    "help": bot_help,
    "play": bot_play,
    "default": bot_help
}

def docmd( funcs, chatid, request ):
    try:
        f = funcs[request[0].lower()]
    except KeyError:
        f = funcs["default"]
    return f( chatid, request )

if __name__ == "__main__":
    bot = BotHandler()
    chatid = bot.get_last_update()["message"]["chat"]["id"]
    msg = bot.get_last_update()["message"]["text"]
    print( "got {}".format( msg ) )
    docmd( bot_toplevel, chatid, msg.split() )
