
MONITORING_LOCATIONS = [
    {
        "location_id": "LOC001",
        "name": "Ooty (Udhagamandalam)",
        "latitude": 11.4102,
        "longitude": 76.6950,
        "monitoring_type": "sensor",
        "sensor_id": "S001"
    },
    {
        "location_id": "LOC002",
        "name": "Coonoor",
        "latitude": 11.3498,
        "longitude": 76.7937,
        "monitoring_type": "weather_api",
        "sensor_id": None
    },
    {
        "location_id": "LOC003",
        "name": "Kotagiri",
        "latitude": 11.4200,
        "longitude": 76.8600,
        "monitoring_type": "weather_api",
        "sensor_id": None
    },
    {
        "location_id": "LOC004",
        "name": "Kundah",
        "latitude": 11.3200,
        "longitude": 76.6200,
        "monitoring_type": "weather_api",
        "sensor_id": None
    },
    {
        "location_id": "LOC005",
        "name": "Gudalur",
        "latitude": 11.5207,
        "longitude": 76.4814,
        "monitoring_type": "weather_api",
        "sensor_id": None
    },
    {
        "location_id": "LOC006",
        "name": "Pandalur",
        "latitude": 11.4800,
        "longitude": 76.3600,
        "monitoring_type": "weather_api",
        "sensor_id": None
    }
]


def get_monitoring_locations():
    return MONITORING_LOCATIONS