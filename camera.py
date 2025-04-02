from fastapi import FastAPI, WebSocket
import cv2
import asyncio
import json
from ultralytics import YOLO
import paho.mqtt.client as mqtt

class CameraModule:
    def __init__(
        self, 
        camera_id, 
        video_path, 
        coverage_area, 
        model_path='yolo11m.pt',
        mqtt_broker="localhost", 
        mqtt_port=1883
    ):
        self.camera_id = camera_id
        self.video_path = video_path
        self.coverage_area = coverage_area
        self.model = YOLO(model_path)
        
        # All cameras publish on the same topic
        self.mqtt_topic = "cameras/detections"

        # MQTT setup
        self.mqtt_client = mqtt.Client(f"{camera_id}Publisher")
        try:
            self.mqtt_client.connect(mqtt_broker, mqtt_port, 60)
            self.mqtt_client.loop_start()
            print(f"MQTT client for {camera_id} connected successfully")
        except Exception as e:
            print(f"Failed to connect to MQTT broker for {camera_id}: {e}")

        # Create FastAPI app for this camera
        self.app = FastAPI(title=f"{camera_id} API")

        # OPTIONAL: If you want to have a WebSocket endpoint for this camera,
        # you can still enable it. It will call the same processing function,
        # but since we now run the processing loop on startup, it might result in duplicate processing.
        # For now, we disable this endpoint.
        # @self.app.websocket(f"/ws/{camera_id}")
        # async def websocket_endpoint(websocket: WebSocket):
        #     await websocket.accept()
        #     await self.process_video(websocket)

        # Launch the camera processing loop as a background task when the app starts
        @self.app.on_event("startup")
        async def start_camera_processing():
            # Run the process_video in a background task.
            asyncio.create_task(self.process_video())
        
    async def process_video(self, websocket: WebSocket = None):
        try:
            cap = cv2.VideoCapture(self.video_path)
            while True:
                # If video capture is closed or ended, reinitialize
                if not cap.isOpened():
                    cap = cv2.VideoCapture(self.video_path)

                ret, frame = cap.read()
                if not ret:
                    # Reset the video to the beginning if we reached the end
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

                # Run inference on the current frame
                results = self.model(frame)[0]
                
                # Count detected objects (adjust keys as needed)
                vehicle_counts = {"car": 0, "truck": 0, "bus": 0, "motorcycle": 0, "person": 0}
                for box in results.boxes:
                    class_id = int(box.cls[0].item())
                    class_name = self.model.names[class_id]
                    if class_name in vehicle_counts:
                        vehicle_counts[class_name] += 1

                data = {
                    "camera": self.camera_id,
                    "coverage_area": self.coverage_area,
                    "vehicle_counts": vehicle_counts
                }
                payload = json.dumps(data)

                # Publish the detection data to the shared MQTT topic
                self.mqtt_client.publish(self.mqtt_topic, payload)

                # If a websocket is provided (optional use-case), send the payload through it
                if websocket:
                    await websocket.send_text(payload)

                # Wait for next frame (simulate ~30 FPS)
                await asyncio.sleep(1 / 30)
        except Exception as e:
            print(f"Error in camera {self.camera_id}: {e}")
        finally:
            cap.release()
