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
from image_handler import update_image, update_locs
import time
import streamlit as st
import sys

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
        my_surroundings.append(ret)
        batch_lock.release()
        print("---------------------")

def get_batch():
    ret = []
    batch_lock.acquire()
    for x in my_surroundings:
        ret.append(x)
    batch_lock.release()
    return ret

locs = {}

def get_display_data(ego_id):
    global locs
    batch = get_batch()
    locs = update_locs(locs, batch)
    return update_image(locs, ego_id)

if __name__ == "__main__":

    if len(sys) < 2 or sys.argv[1] == 0:
        run = 0
    else:
        run = 1

    with open("vehicle1.json") as json_file:
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

    my_surroundings = []

    if run:
        st.title("Dashboard")

        display = st.empty()

        while True:
            image = get_display_data(ego_id)
            display.image(image)
            time.sleep(0.05)

    # vehicle.update_lat_long(config["PATH"][0][0], config["PATH"][0][1])
