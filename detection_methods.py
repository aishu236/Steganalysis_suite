from PIL import Image
import numpy as np
from statistical_analysis import calculate_histogram, calculate_chi_square

# Image Steganalysis Methods
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