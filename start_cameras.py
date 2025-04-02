import subprocess
import sys
from config import CAMERAS, MQTT_BROKER, MQTT_PORT
import os

def start_all_cameras():
    """Start all camera processes using subprocess"""
    processes = []
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"Starting {len(CAMERAS)} cameras...")

    for camera in CAMERAS:
        cmd = [
            sys.executable,
            "-c",
            (
                f"from camera import CameraModule; "
                f"import uvicorn; "
                f"camera = CameraModule("
                f"'{camera['id']}', "
                f"'{camera['video_path']}', "
                f"{str(camera['coverage_area'])}, "  # Use str() to serialize the list
                f"model_path='yolo11m.pt', "  # Explicitly pass model_path if needed
                f"mqtt_broker='{MQTT_BROKER}', "  # Use config's MQTT_BROKER
                f"mqtt_port={MQTT_PORT}); "
                f"uvicorn.run(camera.app, host='0.0.0.0', port={camera['port']})"
            )
        ]

        print(f"Starting {camera['id']} on port {camera['port']}...")

        # Start the process and add it to our list
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        processes.append({
            'camera': camera['id'],
            'process': process,
            'port': camera['port']
        })

    print("All cameras started!")
    print("Press Ctrl+C to stop all cameras")

    try:
        # Keep the main process running
        while True:
            for p in processes:
                stdout = p['process'].stdout.readline()
                if stdout:
                    print(f"[{p['camera']}] {stdout.strip()}")

                stderr = p['process'].stderr.readline()
                if stderr:
                    print(f"[{p['camera']} ERROR] {stderr.strip()}")

                # Check if process is still running
                if p['process'].poll() is not None:
                    print(f"Camera {p['camera']} process exited with code {p['process'].returncode}")
                    processes.remove(p)

            # Debug: Check if processes are running
            for p in processes:
                if p['process'].poll() is not None:
                    print(f"Camera {p['camera']} process exited unexpectedly with code {p['process'].returncode}")

            if not processes:
                print("All camera processes have exited")
                break
    except KeyboardInterrupt:
        print("Stopping all camera processes...")
        for p in processes:
            p['process'].terminate()

        print("All cameras stopped!")

if __name__ == "__main__":
    start_all_cameras()
