from kafka import KafkaConsumer, KafkaProducer
from threading import Lock
import requests
from pymmi.mmi import MapMyIndia
import json
import time

class Car:
    def __init__(self, config):
        # use a config file to define demo behaviour
        self.consumer = KafkaConsumer(bootstrap_servers='164.52.208.158:9092') # Consumer to listen to local messages
        self.producer = KafkaProducer(bootstrap_servers='164.52.208.158:9092') # producer to send events to local topic
        
        time.sleep(5)
        
        self.locationAPI = MapMyIndia("18b08477725b6446165d1f1b23b8a4f6")

        self.location = "" # PINCODE | location is also the topic this car is subscribed to
        self.lat = config["PATH"][0][0]
        self.long = config["PATH"][0][1]
        self.carID = config["ID"]
        self.speed = config["SPEED"]
        self.consumer_lock = Lock()
        self.producer_lock = Lock()

    
    def consume(self):
        # this function will read values from the consumer
        ret = []
        if self.location=="":
            return []
        self.consumer_lock.acquire()
        msg = next(self.consumer)
        decoded = json.loads(msg.value.decode('utf-8'))
        # self.consumer.commit()
        self.consumer_lock.release()
        return decoded
    
    def location_update(self, location):
        self.location = location
        self.consumer_lock.acquire()
        self.consumer.unsubscribe()
        self.consumer.subscribe(self.location)
        self.consumer_lock.release()

    def produce(self, event):
        self.producer.send(self.location, event)

    def update_lat_long(self, lat, long):
        self.lat = lat
        self.long = long

        # parameters = {"lat": lat, "lng": long, "REST_KEY":"18b08477725b6446165d1f1b23b8a4f6"}

        # result = requests.get(self.locationAPI.reverse_geocoding_api, params=parameters)
        # return result.json()["results"][0]["pincode"]
        return "500031"