import os
import time
import pyaudio
import numpy as np
from pushover import Client
import json

# Function to load configuration from a JSON file or generate default
def load_or_generate_config():
    config_file = "config.json"
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
    else:
        # Default configuration
        config = {
            "PUSHOVER_TOKEN": "",
            "PUSHOVER_USER_KEY": "",
            "DETECT_FREQUENCY": 440,
            "FREQUENCY_THRESHOLD": 10,
            "NOTIFICATION_DELAY": 60
        }

        # Generate a config.json file with default values
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)

    return config

# Initialize Pushover client
def init_pushover_client(config):
    pushover_user_key = config["PUSHOVER_USER_KEY"]
    pushover_api_token = config["PUSHOVER_TOKEN"]
    pushover_client = Client(pushover_user_key, api_token=pushover_api_token)
    return pushover_client

# Function to detect the frequency of the audio data
def detect_song_frequency(audio_data, sample_rate):
    # Apply FFT to the audio data
    fft_data = np.fft.fft(audio_data)

    # Find the index of the maximum amplitude in the FFT data
    max_index = np.argmax(np.abs(fft_data))

    # Calculate the corresponding frequency
    frequency = max_index * sample_rate / len(audio_data)

    return frequency

# Function to send a notification using Pushover
def send_notification(pushover_client):
    pushover_client.send_message("Data Terminal Has A New Message!", title="CAP Radio Message Alert")

# Rest of your code remains the same

def main():
    config = load_or_generate_config()
    pushover_client = init_pushover_client(config)

    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    print("Listening for song...")

    try:
        while True:
            data = stream.read(1024)
            audio_data = np.frombuffer(data, dtype=np.int16)
            detected_frequency = detect_song_frequency(audio_data, 44100)

            if abs(detected_frequency - config["DETECT_FREQUENCY"]) < config["FREQUENCY_THRESHOLD"]:
                send_notification(pushover_client)
                time.sleep(config["NOTIFICATION_DELAY"])
    except KeyboardInterrupt:
        pass

    stream.stop_stream()
    stream.close()
    audio.terminate()

if __name__ == "__main__":
    main()
