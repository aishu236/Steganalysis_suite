import json
import os
from datetime import datetime
import imghdr
from PIL import Image
import numpy as np
from collections import Counter

# --- config.py content ---
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

# --- detection_methods.py content ---
def lsb_analysis(image, features):
    """Basic LSB analysis by examining the distribution of LSBs."""
    print("Performing basic LSB statistical analysis on image.")
    img_array = np.array(image)

    # Analyze each color channel independently
    lsb_anomalies = {}
    for channel in range(img_array.shape[-1]):  # Iterate through color channels
        lsb_plane = img_array[:, :, channel] & 1
        unique_bits, counts = np.unique(lsb_plane, return_counts=True)
        probabilities = counts / np.sum(counts)

        expected_probability = 0.5
        expected_counts = np.array([len(lsb_plane) * expected_probability] * len(unique_bits))

        # Ensure both 0 and 1 are present for chi-square test
        observed_counts = np.zeros(2)
        observed_map = {bit: count for bit, count in zip(unique_bits, counts)}
        observed_counts[0] = observed_map.get(0, 0)
        observed_counts[1] = observed_map.get(1, 0)
        expected_counts_adjusted = np.array([len(lsb_plane) * expected_probability] * 2)

        # Perform chi-square test
        if np.all(expected_counts_adjusted > 0):
            chi2_value = calculate_chi_square(observed_counts, expected_counts_adjusted)
            # A high chi-square value might indicate a deviation from randomness
            lsb_anomalies[f"channel_{channel}"] = {"chi2_value": chi2_value}
        else:
            lsb_anomalies[f"channel_{channel}"] = {"error": "Insufficient data for chi-square test"}

    return {"lsb_statistical_anomalies": lsb_anomalies}

def visual_lsb_analysis(image, features):
    """Creates and returns the bit planes for visual inspection."""
    print("Generating bit planes for visual LSB analysis.")
    img_array = np.array(image)
    bit_planes = []
    for i in range(8):  # Iterate through all 8 bit planes
        bit_plane = ((img_array >> i) & 1) * 255  # Extract and scale to 0-255
        bit_planes.append(Image.fromarray(bit_plane.astype(np.uint8)))
    return {"bit_planes": "Generated (can't be directly shown in report)"} # Indicate generation

def histogram_analysis(image, features):
    """Analyzes the color histograms for unusual patterns."""
    print("Performing histogram analysis on image.")
    histograms = {}
    img_array = np.array(image)
    for i in range(img_array.shape[-1]):  # For each color channel
        histogram = calculate_histogram(img_array[:, :, i].flatten())
        histograms[f"channel_{i}"] = histogram
        # You would typically look for sharp drops, unexpected spikes, or uneven distributions
        # More sophisticated analysis would be needed here.
    return {"color_histograms": "Analysis performed (histograms in report)"}

# File Steganalysis Methods
def metadata_analysis(file_content, features):
    """Analyzes file metadata (if available in features)."""
    print("Performing metadata analysis on file.")
    metadata_anomalies = {}
    if 'file_size' in features:
        # Compare file size with expected size or related files
        metadata_anomalies['file_size'] = f"Size: {features['file_size']} bytes (further analysis needed)"
    # Add checks for other metadata if you extract them
    return {"metadata_anomalies": metadata_anomalies}

def byte_frequency_analysis(file_content, features):
    """Analyzes the frequency distribution of bytes."""
    print("Performing byte frequency analysis on file.")
    histogram = calculate_histogram(file_content)
    total_bytes = len(file_content)
    expected_frequency = total_bytes / 256.0  # Assuming a roughly uniform distribution
    deviations = {}
    for byte_val, count in histogram.items():
        deviation = count - expected_frequency
        if abs(deviation) > (0.05 * expected_frequency): # Example threshold: 5% deviation
            deviations[byte_val] = deviation
    return {"byte_frequency_deviations": deviations}

# Dictionary to hold the detection methods for easy calling
image_detection_methods = {
    "lsb_analysis": lsb_analysis,
    "visual_lsb_analysis": visual_lsb_analysis,
    "histogram_analysis": histogram_analysis,
    # Add more image analysis methods here
}

file_detection_methods = {
    "metadata_analysis": metadata_analysis,
    "byte_frequency_analysis": byte_frequency_analysis,
    # Add more file analysis methods here
}

# --- feature_extraction.py content ---
def extract_image_features(image):
    features = {}
    pixels = np.array(image)
    features['pixel_mean'] = np.mean(pixels)
    features['pixel_std'] = np.std(pixels)
    # Add more image-specific feature extraction here (e.g., histograms)
    return features

def extract_file_features(file_content):
    features = {}
    features['file_size'] = len(file_content)
    # Add more file-specific feature extraction here (e.g., byte frequencies)
    return features

# --- file_analyzer.py content ---
def analyze_file(file_path, config):
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
        print(f"Loaded file: {file_path} ({len(file_content)} bytes)")
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return {}
    except Exception as e:
        print(f"Error reading file: {e}")
        return {}

    features = extract_file_features(file_content)
    detection_results = {}
    for method_name, method_func in file_detection_methods.items():
        if method_name in config.get('default_file_methods', []):
            print(f"Applying file analysis method: {method_name}")
            result = method_func(file_content, features)
            detection_results[method_name] = result

    return {"file_type": "file", "features": features, "detection_results": detection_results}

# --- image_analyzer.py content ---
def analyze_image(image_path, config):
    try:
        img = Image.open(image_path)
        print(f"Loaded image: {image_path} ({img.format}, {img.size})")
    except FileNotFoundError:
        print(f"Error: Image file not found: {image_path}")
        return {}
    except Exception as e:
        print(f"Error opening image: {e}")
        return {}

    features = extract_image_features(img)
    detection_results = {}
    for method_name, method_func in image_detection_methods.items():
        if method_name in config.get('default_image_methods', []):
            print(f"Applying image analysis method: {method_name}")
            result = method_func(img, features)
            detection_results[method_name] = result

    return {"file_type": "image", "features": features, "detection_results": detection_results}

# --- reporting.py content ---
def generate_report(input_file, analysis_results):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"steganalysis_report_{os.path.basename(input_file)}_{timestamp}.json"

    report_data = {
        "input_file": input_file,
        "timestamp": timestamp,
        "analysis_results": analysis_results
    }

    try:
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=4)
        print(f"Report saved to: {report_filename}")
    except Exception as e:
        print(f"Error saving report: {e}")

    print("\n--- Analysis Report ---")
    print(f"Input File: {input_file}")
    print(f"Timestamp: {timestamp}")
    print("\nAnalysis Results:")
    print(json.dumps(analysis_results, indent=4))

# --- statistical_analysis.py content ---
def calculate_histogram(data):
    """Calculates the histogram of the given data."""
    return Counter(data)

def calculate_chi_square(observed, expected):
    """Calculates the chi-square statistic."""
    if len(observed) != len(expected) or any(v == 0 for v in expected):
        return float('inf')  # Or handle division by zero appropriately
    return np.sum([(o - e)**2 / e for o, e in zip(observed, expected)])

# Add more statistical analysis functions as needed (e.g., entropy calculation)

# --- steganalysis_suite.py content (main entry point) ---
def main():
    config = load_config()

    input_file = input("Enter the path to the file you want to analyze: ")

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        return

    print(f"Analyzing: {input_file}")

    if imghdr.what(input_file):
        analysis_results = analyze_image(input_file, config)
    else:
        analysis_results = analyze_file(input_file, config)

    generate_report(input_file, analysis_results)
    print("Analysis complete. Report generated.")

if __name__ == "__main__":
    main()

# --- utils.py content ---
def byte_to_bits(byte):
    """Converts a byte to its 8-bit binary string representation."""
    return format(byte, '08b')

# Example of a potential utility function