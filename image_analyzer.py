from PIL import Image
from feature_extraction import extract_image_features
from detection_methods import image_detection_methods

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