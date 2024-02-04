import math
import requests
import time

def deg2rad(deg):
    return deg * (math.pi/180)

class User:

    API_KEY = "65bec36441f29041192514iald6bc81"

    def __init__(self, name, bloodType, age, weight, height, medicalConditions, rating, address):
        self.name = name
        self.bloodType = bloodType
        self.age = age
        self.weight = weight
        self.height = height
        self.medicalConditions = medicalConditions
        self.rating = rating
        # address format: streetNumber streetName city State postalCode Country

    def lngLat(address, API_KEY):
        geocode = "https://geocode.maps.co/search?q='" + address + "'&api_key=" + API_KEY
        data = []
        tries = 3
        while data == [] and tries > 0:
            tries -= 1
            data = requests.get(geocode)
            time.sleep(1)
            try:
                data = data.json()
            except Exception:
                data = []
        try:
            lat = data[0]['lat']
            lng = data[0]['lon']
        except Exception:
            lat = 0
            lng = 0
            
        return lng, lat

    def getDistanceKm(lng1, lat1, lng2, lat2):
        radius = 6371
        degLat = deg2rad(lat2-lat1)
        degLng = deg2rad(lng2-lng1)
        a = math.sin(degLat/2) * math.sin(degLat/2) + math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.sin(degLng/2) * math.sin(degLng/2)
        b = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = radius * b
        distance_miles = distance * 0.621371 
        return distance_miles
    
print(User.lngLat("703 Windfall, IL", User.API_KEY))