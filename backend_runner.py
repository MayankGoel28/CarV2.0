from asyncio import locks
from kafka import KafkaConsumer, KafkaProducer
from threading import Lock
import json
import requests
from car import Car 
from geopy import distance
import time
import threading
from threading import Lock
import time

def traverser():
    for i in range(len(path)-1):
        current_coords = path[i]
        target = path[i+1]
        while(True):
            # print(current_coords)
            time.sleep(0.05)
            dist = distance.geodesic(current_coords, target).km
            # print(dist)
            if speed > dist:
                current_coords = target 
            else:
                current_coords[0] = (current_coords[0]*(dist-speed) + target[0]*speed)/dist
                current_coords[1] = (current_coords[1]*(dist-speed) + target[1]*speed)/dist
            
            new_pin = vehicle.update_lat_long(current_coords[0], current_coords[1])
            # print(new_pin)
            if new_pin != vehicle.location:
                vehicle.location_update(new_pin)
            
            event = {"x": current_coords[0], "y": current_coords[1], "ID": vehicle.carID, "speed": speed}
            vehicle.produce(json.dumps(event).encode('utf-8'))

            if target[0]==current_coords[0] and target[1]==current_coords[1]:
                break

def consumer():
    while(True):
        ret = vehicle.consume()
        if ret == []:
            continue
        batch_lock.acquire()
        # my_surroundings.append(ret)
        batch_lock.release()
        print("---------------------")


if __name__ == "__main__":
    with open("vehicle2.json") as json_file:
        config = json.load(json_file)
    print(config)
    path = config["PATH"]
    speed = config["SPEED"]
    vehicle = Car(config)
    ego_id = config["ID"]

    batch_lock = Lock()

    t1 = threading.Thread(target=traverser)
    t2 = threading.Thread(target=consumer)
    
    t1.start()
    t2.start()


    # vehicle.update_lat_long(config["PATH"][0][0], config["PATH"][0][1])
