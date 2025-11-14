import os
import imghdr  # Import here
from image_analyzer import analyze_image
from file_analyzer import analyze_file
from reporting import generate_report
from config import load_config

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