import random


BASE_SENSORS = [
    {
        "sensor_id": "S001",
        "location": {
            "latitude": 11.4102,
            "longitude": 76.6950
        }
    },
    {
        "sensor_id": "S002",
        "location": {
            "latitude": 11.3850,
            "longitude": 76.7200
        }
    },
    {
        "sensor_id": "S003",
        "location": {
            "latitude": 11.4500,
            "longitude": 76.6800
        }
    }
]


def generate_sensor_data():

    sensors = []

    for sensor in BASE_SENSORS:

        readings = {
            "rainfall": round(random.uniform(40, 130), 1),

            "soil_moisture": round(
                random.uniform(50, 90), 1
            ),

            "temperature": round(
                random.uniform(20, 28), 1
            ),

            "humidity": round(
                random.uniform(70, 98), 1
            ),

            "pressure": round(
                random.uniform(995, 1010), 1
            ),

            "tilt": round(
                random.uniform(1, 8), 1
            )
        }

        sensors.append({
            "sensor_id": sensor["sensor_id"],
            "location": sensor["location"],
            "readings": readings
        })

    return sensors