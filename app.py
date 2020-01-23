#!/usr/bin/env python3


import os
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Flask, request

app = Flask(__name__)

ZIPCODE   = {
    '#redwood':  94062, # Redwood, CA
    '#nd':   46556, # Notre Dame, IN
    '#menlo': 94025, # Menlo, CA NOT RIGHT
    '#at&t': 94025 # NOT RIGHT
}
DEFAULT_ZIPCODE = 94025

# get bot_id and api keys
with open(".secret", "r") as f:
    f = f.readlines()
    bot_id = f[0].strip()
    OWM_APPID = f[1].strip()


@app.route('/', methods=['POST'])
def shortstop():
    sender = request.get_json()['name']
    message = request.get_json()['text']
    print(message)

    # bot logic
    noise_complaint(message)
    sign_in(message)
    detain(message)
    weather_handler(message)


    return "ok", 200


def detain(msg):
    """Detain a user"""
    msg = msg.split()
    if msg[0].lower().startswith("!detain") and len(msg) < 4:
        reply(' '.join(msg[1:]) + " has been detained")


def reply(msg):
    """Reply to a message in the chat"""
    url = 'https://api.groupme.com/v3/bots/post'
    data = {
        'bot_id'		: bot_id,
        'text'			: msg
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()


def sender_is_bot(message):
    """Check if sender is bot to not reply to own msgs"""
    return message['sender_type'] == "bot"


def noise_complaint(msg):
    """If you're being too loud, register a noise complaint"""
    if msg == msg.upper():
        reply("Noise complaint registered with Redwood room 202")


def sign_in(msg):
    """Return attendance google form"""
    if '!attendance' in msg:
        reply("https://docs.google.com/forms/u/0/d/e/1FAIpQLScYQDbMuOAH4EVpUlCAPxRhmPMJGXoYnR0Loo3fIrDzp6ZgTg/formResponse")

def weather_handler(s):
    if '!weather' in s:
        args = s.strip().split()
        if len(args) > 1:
            weather(args[1])
        else:
            weather()

def weather(location=None):
    weather_url = 'http://api.openweathermap.org/data/2.5/weather?zip={},us'

    if not location:
        location = DEFAULT_ZIPCODE 
    elif location in ZIPCODE:
        location = ZIPCODE[location]
    else:
        location = DEFAULT_ZIPCODE

    weather_url = weather_url.format(location)
    
    parm  = {
        'appid': OWM_APPID,
        'units': 'imperial',
    }

    resp = requests.get(weather_url, params=parm)
    resp = json.loads(resp.text)
    pprint.pprint(resp)
    temp = resp['main']['temp']
    try:
        desc = resp['weather'][0]['description']
    except:
        desc = None
    message = 'Current weather is {}°F, {}'.format(temp,desc)
    reply(message)

if __name__ == '__main__':
    app.run(host='167.172.204.173')
