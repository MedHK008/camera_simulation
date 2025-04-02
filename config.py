# Camera configurations
CAMERAS = [
    {
        "id": "camera-1",
        "video_path": "2697636-uhd_1920_1440_30fps.mp4",
        "coverage_area": [(33.999, -118.500), (34.050, -118.460)],
        "port": 8002
    },
    {
        "id": "camera-2",
        "video_path": "2697636-uhd_1920_1440_30fps.mp4",
        "coverage_area": [(34.051, -118.461), (34.100, -118.430)],
        "port": 8003
    },
    {
        "id": "camera-3",
        "video_path": "2697636-uhd_1920_1440_30fps.mp4",
        "coverage_area": [(34.000, -118.430), (34.050, -118.400)],
        "port": 8004
    }
]

# MQTT configuration
MQTT_BROKER = "localhost"  # Ensure this matches the aggregator's broker
MQTT_PORT = 1883           # Ensure this matches the aggregator's port
