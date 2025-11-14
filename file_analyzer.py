from feature_extraction import extract_file_features
from detection_methods import file_detection_methods

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