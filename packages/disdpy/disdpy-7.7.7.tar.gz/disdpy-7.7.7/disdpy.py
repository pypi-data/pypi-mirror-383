import requests
import time
import threading

ft = None
ftc = None
fta = None
authtoken = None
channelid = None
v_cd = ''

def auth(token: str):
    global authtoken
    authtoken = token

def channel(id: str):
    global channelid
    global worked
    worked = {}
    worked[1] = []
    channelid = id
    lastmsgs = get_messages(limit=100)
    for msg in lastmsgs:
        worked[1].append(msg['id'])

def cd(path):
    global Cd
    Cd = path

def get_messages(limit=100, FromNewToOld=True, Banned: list = None, custom_channel_id=None, custom_auth_token=None, before=None):
    """
    Fetch up to 'limit' messages from the channel, handling Discord's 100-message per request limit.
    """
    all_msgs = []
    remaining = limit
    last_message_id = None
    channel = custom_channel_id if custom_channel_id else channelid
    auth = str(custom_auth_token if custom_auth_token else authtoken)

    while remaining > 0:
        fetch_limit = min(100, remaining)
        url = f'https://discord.com/api/v9/channels/{channel}/messages?limit={fetch_limit}'
        if last_message_id:
            url += f"&before={last_message_id}"
        res = requests.get(url=url, headers={'Authorization': auth})
        if res.status_code != 200:
            print(f'API/messages ERROR {res.status_code}')
            break
        try:
            msgs = res.json()
        except Exception:
            break
        if not msgs:
            break
        if Banned:
            msgs = [msg for msg in msgs if msg['author']['id'] not in Banned]
        all_msgs.extend(msgs)
        last_message_id = msgs[-1]['id']
        remaining -= len(msgs)
        if len(msgs) < fetch_limit:
            break  # No more messages to fetch

    if not FromNewToOld:
        return list(reversed(all_msgs))
    else:
        return all_msgs

def post(content = None, message_reference_id = None, files:list = None, custom_channel_id = None, custom_auth_token = None, custom_json = None, custom_url = None):
    global authtoken
    postjson = {"content":str(content)}
    if custom_json:
        postjson = custom_json
    if message_reference_id:
        postjson["message_reference"]={"channel_id": custom_channel_id if custom_channel_id else channelid, "message_id": message_reference_id}
    urel = f'https://discord.com/api/v9/channels/{custom_channel_id if custom_channel_id else channelid}/messages?'
    if custom_url:
        urel = custom_url
    res = requests.post(url=urel,headers={'Authorization': str(custom_auth_token if custom_auth_token else authtoken)},json=postjson,files={f"files[{i}]": (file.name, file) for i, file in enumerate(files)} if files else None)
    return res

def delete(message_id: str, custom_channel_id=None, custom_auth_token=None):
    res = requests.delete(url=f'https://discord.com/api/v9/channels/{custom_channel_id if custom_channel_id else channelid}/messages/'+str(message_id),headers={'Authorization': str(custom_auth_token if custom_auth_token else authtoken)})
    return res

def edit(content: str, message_id: str, custom_channel_id=None, custom_auth_token=None):
    res = requests.patch(url=f'https://discord.com/api/v9/channels/{custom_channel_id if custom_channel_id else channelid}/messages/'+str(message_id),headers={'Authorization': str(custom_auth_token if custom_auth_token else authtoken)},json={"content":str(content)})
    return res

def get_NEWmessages(limit=100, NoneAsZero=False, FromNewToOld=True, Banned: list=None, Sessions=[1], custom_channel_id=None, custom_auth_token=None):
    global worked
    lastmsgs = get_messages(limit, custom_channel_id=custom_channel_id, custom_auth_token=custom_auth_token)
    results = []
    for session in Sessions:
        if session not in worked:
            worked[session] = []
            for msg in lastmsgs:
                worked[session].append(msg['id'])
            results.append(None if NoneAsZero else [])
        else:
            news = []
            for msg in lastmsgs:
                if msg['id'] not in worked[session]:
                    worked[session].append(msg['id'])
                    if not Banned or (Banned and msg['author']['id'] not in Banned):
                        news.append(msg)
            if FromNewToOld:
                news = list(reversed(news))
            results.append(None if (NoneAsZero and len(news) == 0) else news)
    return results

def typing(seconds: int = 3, custom_channel_id=None, custom_auth_token=None):
    def f_typing(seconds, custom_channel_id, custom_auth_token):
        channel = custom_channel_id if custom_channel_id else channelid
        autht = custom_auth_token if custom_auth_token else authtoken
        full_intervals = seconds // 3
        remainder = seconds % 3
        for _ in range(full_intervals):
            requests.post(
                url=f'https://discord.com/api/v9/channels/{channel}/typing',
                headers={'Authorization': autht}
            )
            time.sleep(3)
        if remainder:
            requests.post(
                url=f'https://discord.com/api/v9/channels/{channel}/typing',
                headers={'Authorization': autht}
            )
    # Start the thread
    threading.Thread(target=f_typing, args=[seconds, custom_channel_id, custom_auth_token]).start()

def typing_force(state:bool = True, custom_channel_id=None, custom_auth_token=None):
    global ft,fta,ftc
    ft = state
    fta = custom_auth_token
    ftc = custom_channel_id

def msg_from_id(message_id: str, custom_channel_id=None, custom_auth_token=None):
    msgs = get_messages(custom_auth_token=custom_auth_token, custom_channel_id=custom_channel_id,FromNewToOld=True)
    for msg in msgs:
        if str(msg['id']) == str(message_id):
            return msg
    return None

def main():
    def _mainf():
        global ft, ftc, fta, authtoken, channelid
        while True:
            if ft:
                if (authtoken or fta) and (channelid or ftc):
                    # Correct the Authorization header: remove extra braces.
                    requests.post(
                        url=f'https://discord.com/api/v9/channels/{ftc if ftc else channelid}/typing',
                        headers={'Authorization': (fta if fta else authtoken)}
                    )
            time.sleep(3)
    threading.Thread(target=_mainf).start()