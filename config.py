import json
import os

DEFAULT_CONFIG = {
    "default_image_methods": ["lsb_analysis"],
    "default_file_methods": [],
    "report_output_dir": "reports",
    "suspicious_threshold": 0.7  # Example threshold
}

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**DEFAULT_CONFIG, **config}
        except json.JSONDecodeError:
            print("Error decoding config.json. Using default configuration.")
            return DEFAULT_CONFIG
    else:
        print("config.json not found. Using default configuration.")
        return DEFAULT_CONFIG

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print("Configuration saved to config.json")
    except Exception as e:
        print(f"Error saving configuration: {e}")

if __name__ == "__main__":
    config = load_config()
    print("Current Configuration:")
    print(json.dumps(config, indent=4))

    # Example of modifying and saving the config
    config['default_file_methods'] = ["byte_frequency_analysis"]
    save_config(config)