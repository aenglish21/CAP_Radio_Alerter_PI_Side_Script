import os
import pyaudio
import numpy as np
import pushover
import time
import json

# Default configuration
DEFAULT_CONFIG = {
    "PUSHOVER_TOKEN": "",
    "PUSHOVER_USER_KEY": "",
    "DETECT_FREQUENCY": 440,
    "FREQUENCY_THRESHOLD": 10,
    "NOTIFICATION_DELAY": 60
}

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def setup_config():
    config = load_config()
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = input(f"Enter {key.replace('_', ' ').title()} [{value}]: ") or value
    save_config(config)
    return config

def detect_song_frequency(data):
    # ... (same as previous code)

def send_notification(pushover_client):
    pushover_client.send_message("Detected the specified song!", title="Song Detection")

def main():
    config = setup_config()

    # Initialize Pushover client
    pushover_client = pushover.Client(config["PUSHOVER_USER_KEY"], api_token=config["PUSHOVER_TOKEN"])

    # Initialize audio stream
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    print("Listening for song...")

    try:
        while True:
            data = stream.read(1024)
            detected_frequency = detect_song_frequency(data)

            if abs(detected_frequency - config["DETECT_FREQUENCY"]) < config["FREQUENCY_THRESHOLD"]:
                send_notification(pushover_client)
                time.sleep(config["NOTIFICATION_DELAY"])
    except KeyboardInterrupt:
        pass

    stream.stop_stream()
    stream.close()
    audio.terminate()

if __name__ == "__main__":
    if not os.path.exists(CONFIG_FILE):
        print("Config file not found. Creating a new one...")
        setup_config()
    main()
