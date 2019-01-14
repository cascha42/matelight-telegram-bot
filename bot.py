import requests
import datetime
import time
import config

telegram_token = config.telegram_token 
telegram_api_url = "https://api.telegram.org/bot{}/".format(telegram_token)
matelight_api_url = "http://matelight.cbrp3.c-base.org:80/api/"
#matelight_api_url = "http://localhost:1337/api/"

def telegram_send_message(chat_id, text):
    params = {'chat_id': chat_id, 'text': text}
    method = 'sendMessage'
    resp = requests.post(telegram_api_url + method, params)
    return resp

def get_updates(offset=None, timeout=30):
    method = 'getUpdates'
    params = {'timeout': timeout, 'offset': offset}
    resp = requests.get(telegram_api_url + method, params)
    result_json = resp.json()['result']
    return result_json

def bot_help( chatid, args ):
    msg = """
Available Commands:
    /list - list videos
    /play [video_id] - play a video
    /help - print this help screen
    """
    if args[0].lower() != "/help":
        msg = "Unknown command: '{}'\n".format( args[0] ) + msg
    telegram_send_message( chatid, msg )

def bot_play( chatid, args ):
    if len (args) < 2:
        return bot_help(chatid, args)
    msg = "playing {}".format( args[1] )
    resp = requests.get(matelight_api_url + "getvideos").json()
    videos = [vid['title'] for vid in resp]
    if args[1] not in videos:
        telegram_send_message( chatid, "Video not Found. Use /list to list videos." )
        return
    telegram_send_message( chatid, msg )
    resp = requests.get(matelight_api_url + "play/" + args[1])

def bot_list( chatid, args ):
    resp = requests.get(matelight_api_url + "getvideos").json()
    videos=[]
    for item in resp:
        videos.append(item["title"])
    msg = "available videos:\n  " + ",\n  ".join(videos)
    telegram_send_message( chatid, msg )

def bot_start( chatid, args ):
    msg = """

#########################
######## WELCOME ########
#########################

This is the Telegram-Bot, which controls the Matelight @ c-base berlin.

check out https://c-base.org/ for more information.

Available Commands:
    /list - list videos
    /play [video_id] - play a video
    /help - print this help screen
    """
    telegram_send_message( chatid, msg )


bot_toplevel = {
    "/help": bot_help,
    "/play": bot_play,
    "/list": bot_list,
    "/start": bot_start,
    "/default": bot_help
}

def docmd( funcs, chatid, request ):
    try:
        f = funcs[request[0].lower()]
    except KeyError:
        f = funcs["/default"]
    return f( chatid, request )

if __name__ == "__main__":

    curr_offset = -1
    while True:
        results = get_updates(offset=curr_offset+1)
        for result in results:
            curr_offset = result['update_id']
            msg = result['message']
            chatid = result["message"]["chat"]["id"]
            text = msg.get('text')
            if text is not None:
                print( "got {}".format( msg ) )
                docmd( bot_toplevel, chatid, text.split() )
    time.sleep(5.0)
