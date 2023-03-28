import requests
import telnyx
from flask import Flask, request
import threading
import time
import json

telnyx.api_key = "KEY0186A43D727B3C82CF23271FD872B49B_mNhtxkYxhyJaXRSRbExPXo"

# DATA
server_ip = "206.188.196.251"
to_number = "+17086978616"
audio_play = f"http://{server_ip}/annoying.mp3"


# STATS
interval_sec = 2
retry_count = 0
retry_limit = 2

def call_completed():
    print(f"Call completed, calling again in {interval_sec} seconds -> {to_number}")
    time.sleep(interval_sec)
    make_call()

def call_failed():
    global retry_count
    global retry_limit
    if retry_count < retry_limit:
        print(f"Call retried -> {to_number}")
        time.sleep(interval_sec)
        retry_count = retry_count + 1
        make_call()
    else:
        print(f"No retries left -> {to_number}")

def make_call():
    try:
        call = telnyx.Call.create(connection_id="2131188473946703165", to=to_number, from_="+12702489426", webhook_url=f"http://{server_ip}:5000/call/{to_number}")
        print(f"Call queued -> {to_number}")
    except:
        print(f"Retrying call to {to_number} in {interval_sec} seconds...")
        call_failed()

make_call()

app = Flask(__name__)

@app.route("/call/<number>", methods = ['POST', 'GET'])
async def call(number):
    data = request.json['data']
    call = telnyx.Call.retrieve(data['payload']['call_control_id'])

    event = data.get('event_type')

    if event == "call.initiated":
        print(f"Call initiated -> {number}")

    elif event == "call.answered":
        call.playback_start(audio_url=audio_play)
        print(f"Call answered -> {number}")

    elif event == "call.hangup":
        print(f"Call ended -> {number}")
        call_completed()

    return "done"

threading.Thread(target=lambda: app.run(port=5000, host='0.0.0.0', debug=True, use_reloader=False)).start()