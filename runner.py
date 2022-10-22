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
    for i in range(len(path) - 1):
        current_coords = path[i]
        target = path[i + 1]
        while True:
            # print(current_coords)
            time.sleep(0.05)
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
                "SOS": SOS,
                "t1_x": target[0],
                "t1_y": target[1],
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


SOS = False
locs = {}


def get_display_data(ego_id):
    global locs
    batch = get_batch()
    locs = update_locs(locs, batch)
    return update_image(locs, ego_id)


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("error")
        exit()

    run = int(sys.argv[1])
    config_json_file = sys.argv[2]

    with open(config_json_file) as json_file:
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
        button = st.sidebar.button("SOS", key="1")
        button2 = st.sidebar.button("end SOS", key="2")
        while True:
            image = get_display_data(ego_id)
            display.image(image)
            print(ego_id, SOS)
            time.sleep(0.1)
            # with display.sidebar:
            if button:
                SOS = True
                # if st.button("End Distress", key=2):
                #     SOS = False
            elif button2:
                SOS = False
    # vehicle.update_lat_long(config["PATH"][0][0], config["PATH"][0][1])
