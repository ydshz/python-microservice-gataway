import datetime
import json
import time
import _thread as thread
import websocket
import uuid

isConnected = False


def on_open(ws):
    register = json.dumps({
        "uuid": uuid.uuid4().hex,
        "name": "internal",
        "endpoint": "register",
        "type": "request",
        "data": {
            "name": "test",
            "description": "A test microservice",
            "endpoints": [
                {
                    "name": "hello",
                    "description": "says hello",
                    "parameters": [
                        {
                            "name": "user",
                            "description": "The user to say hello",
                            "optional": False,
                            "type": "string"
                        }
                    ]
                }
            ]
        }})
    ws.send(register)


def on_message(ws, message):
    global isConnected
    request = json.loads(message)
    print(request)
    if not isConnected and request["code"] == 200 and request["connected"] == True:
        isConnected = True
    elif request["endpoint"] == "hello":
        def run():
            while True:
                response = json.dumps({
                    "code": 200,
                    "name": "test",
                    "endpoint": "hello",
                    "type": "response",
                    "uuid": request["uuid"],
                    "data": {
                        "response": "Hello " + request["data"]["user"] + "!" + str(datetime.datetime.now())
                    }
                })
                print(response)
                ws.send(response)
                time.sleep(1)
        thread.start_new_thread(run, ())


ws = websocket.WebSocketApp("ws://localhost:8000", on_message=on_message)
ws.on_open = on_open
ws.run_forever()
