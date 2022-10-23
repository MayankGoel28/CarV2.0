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
import random
import global_vars

def traverser():
    stopped = False
    for i in range(len(path) - 1):
        current_coords = path[i]
            
        target = path[i + 1]
        target2 = path[i+1]
        if i < len(path)-2:
            target2 = path[i+2]
        while True:
            time.sleep(0.5)
            if global_vars.collided and not stopped:
                stopped = True
                event = {
                    "x": current_coords[0],
                    "y": current_coords[1],
                    "ID": vehicle.carID,
                    "speed": speed,
                    "t1_x": target[0],
                    "t1_y": target[1],
                    "t2_x": current_coords[0],
                    "t2_y": current_coords[1],
                    "msg": "SOS"
                }
                vehicle.produce(json.dumps(event).encode("utf-8"))
                break
            if global_vars.collided:
                break
            # print(current_coords)
            
            dist = distance.geodesic(current_coords, target).km
            # print(dist)
            if speed > dist:
                current_coords = target
                
            else:
                current_coords[0] = (
                    current_coords[0] * (dist - speed) + target[0] * speed
                ) / dist
                current_coords[1] = (
                    current_coords[1] * (dist - speed) + target[1] * speed
                ) / dist

            new_pin = vehicle.update_lat_long(current_coords[0], current_coords[1])
            # print(new_pin)
            if new_pin != vehicle.location:
                vehicle.location_update(new_pin)

            event = {
                "x": current_coords[0],
                "y": current_coords[1],
                "ID": vehicle.carID,
                "speed": speed,
                "t1_x": target[0],
                "t1_y": target[1],
                "t2_x": target2[0],
                "t2_y": target2[1],
                "msg": ""
            }
            vehicle.produce(json.dumps(event).encode("utf-8"))

            # tree creation
            if random.uniform(0, 1) < 0.05:
                event = {
                    "x": current_coords[0]+random.uniform(-0.001,0.001),
                    "y": current_coords[1]+random.uniform(-0.001,0.001),
                    "ID": 0,
                    "speed": 0,
                    "t1_x": 0,
                    "t1_y": 0,
                    "t2_x": 0,
                    "t2_y": 0,
                    "msg": ""
                }
                vehicle.produce(json.dumps(event).encode("utf-8"))

            if target[0] == current_coords[0] and target[1] == current_coords[1]:
                break


def consumer():
    while True:
        ret = vehicle.consume()
        if ret == []:
            continue
        batch_lock.acquire()
        my_surroundings.append(ret)
        batch_lock.release()
        


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
    global_vars.init()
    if len(sys.argv) != 3:
        print("error")
        exit()

    run = int(sys.argv[1])
    config_json_file = sys.argv[2]

    with open(config_json_file) as json_file:
        config = json.load(json_file)
    print(config)
    global path
    global speed
    global ego_id
    global vehicle
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
            time.sleep(0.01)
            # with display.sidebar:
    # vehicle.update_lat_long(config["PATH"][0][0], config["PATH"][0][1])
