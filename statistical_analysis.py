import numpy as np
from collections import Counter

def calculate_histogram(data):
    """Calculates the histogram of the given data."""
    return Counter(data)

def calculate_chi_square(observed, expected):
    """Calculates the chi-square statistic."""
    if len(observed) != len(expected) or any(v == 0 for v in expected):
        return float('inf')  # Or handle division by zero appropriately
    return np.sum([(o - e)**2 / e for o, e in zip(observed, expected)])

# Add more statistical analysis functions as needed (e.g., entropy calculation)