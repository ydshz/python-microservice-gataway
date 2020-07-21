import asyncio
import json
import logging
from modules.endpoint import Microservice

microservices = {}


async def server(websocket, path):
    request = await websocket.recv()
    logging.debug("Handling request...")
    logging.debug("Request content: " + request)
    request_object = json.loads(request)
    if request_object["endpoint"] == "register":
        microservices[request_object["data"]["name"]] = Microservice(name=request_object["data"]["name"],
                                                                     description=request_object["data"]["description"],
                                                                     endpoints=request_object["data"]["endpoints"])
        await websocket.send(json.dumps({"code": 200}))
        logging.info("Registered new microservice " + request_object["data"]["name"])
        while True:
            if microservices[request_object["data"]["name"]].check_queue():
                await websocket.send(json.dumps(microservices[request_object["data"]["name"]].execute_queue()))
                response = json.loads(await websocket.recv())
                print(response["data"]["greeting"])
                microservices[request_object["data"]["name"]].enter_queue_response(response["data"]["greeting"])
            await asyncio.sleep(0.5)
    elif request_object["name"] == microservices[request_object["name"]].name and \
            microservices[request_object["name"]].endpoints[request_object["endpoint"]].name == request_object[
        "endpoint"]:
        logging.debug("New client got registered")
        microservices[request_object["name"]].append_queue(endpoint=request_object["endpoint"],
                                                           parameters=request_object["data"])
        while not microservices[request_object["name"]].check_queue_response():
            await asyncio.sleep(0.5)
        logging.debug("Sending client response")
        await websocket.send(microservices[request_object["name"]].show_queue_response())
        microservices[request_object["name"]].delete_queue_entry()
    else:
        await websocket.send(json.dumps({"code": 400}))
        logging.debug("Got bad request")