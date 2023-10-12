import pyaudio
import pushover
import numpy as np
import json
import click
import time
import logging
import sys

# Configure logging
logging.basicConfig(filename='audio_detection.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add a stream handler to display log messages in the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger('').addHandler(console_handler)

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

# Extract Pushover API token and user key from the config
PUSHOVER_API_TOKEN = config.get('PUSHOVER_TOKEN', 'YOUR_DEFAULT_API_TOKEN')
PUSHOVER_USER_KEY = config.get('PUSHOVER_USER_KEY', 'YOUR_DEFAULT_USER_KEY')

# Extract and set the selected input device from the config or None
selected_device = config.get('selected_input_device', None)

# Define sound detection parameters
SOUND_THRESHOLD = 60.01  # Adjust this threshold as needed
ALERT_MESSAGE = "CAP Radio Alert!"
ALERT_TITLE = "Alert Detected"

# Initialize the Pushover client
pushover_client = pushover.Client(PUSHOVER_USER_KEY, api_token=PUSHOVER_API_TOKEN)

# Initialize PyAudio
audio = pyaudio.PyAudio()


# Function to list available audio input devices
def list_input_devices():
    input_devices = {}
    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            input_devices[i] = device_info['name']
    return input_devices


# Function to select the audio input device interactively or use a default device
def select_input_device():
    input_devices = list_input_devices()

    if not input_devices:
        logging.error("No input devices found. Using the default input device.")
        print("No input devices found. Using the default input device.")
        return None

    logging.info("Available input devices:")
    for index, name in input_devices.items():
        logging.info(f"{index}: {name}")

    # Initialize selected_device to None
    selected_device = None

    if config.get('selected_input_device'):
        logging.info(f"Using previously selected device: {config['selected_input_device']}")
        selected_device = config['selected_input_device']

    if selected_device is None:
        selected_device = click.prompt(
            "Select an input device (enter the corresponding index) or press Enter for the default: ", type=int,
            default=None)

    if selected_device not in input_devices:
        logging.error("Invalid selection. Using the default input device.")
        print("Invalid selection. Using the default input device.")
        return None

    # Save the selected device to the config file for future use
    config['selected_input_device'] = selected_device
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file)

    return selected_device


selected_device = select_input_device()

# Initialize a variable to keep track of the last alert time
last_alert_time = 0

# Open the audio input stream using the selected input device or the default device
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True,
                    input_device_index=selected_device, frames_per_buffer=1024)

logging.info("Listening for sound...")

while True:
    try:
        data = stream.read(1024, exception_on_overflow=False)  # Set exception_on_overflow to False
        audio_data = np.frombuffer(data, dtype=np.int16)

        # Check if the audio data contains NaN or out-of-range values
        if not np.isnan(audio_data).any() and (np.abs(audio_data) < 32768).all():
            try:
                # Calculate the root mean square (RMS) value
                rms = np.sqrt(np.mean(audio_data ** 2))
            except RuntimeWarning as rw:
                logging.warning(f"RuntimeWarning: {rw}")
                rms = 0  # Set to 0 to avoid invalid value in case of warnings

            # Check if enough time has passed since the last alert
            current_time = time.time()
            if current_time - last_alert_time >= 60:  # 60 seconds (1 minute)
                if rms > SOUND_THRESHOLD:
                    logging.info("Alert detected!")
                    pushover_client.send_message(ALERT_MESSAGE, title=ALERT_TITLE)
                    last_alert_time = current_time  # Update the last alert time
    except KeyboardInterrupt:
        break

# Cleanup
stream.stop_stream()
stream.close()
audio.terminate()
sys.exit(0)
