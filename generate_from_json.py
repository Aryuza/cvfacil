import json
import os
import sys
from cv_dividers_only import generate_divider, generate_divider_smaller, generate_divider_larger, create_circular_image_with_border

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_from_json.py <json_file> [image_path]")
        return

    json_file = sys.argv[1]
    image_path = sys.argv[2] if len(sys.argv) > 2 else None

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Image Processing
    processed_image_path = None
    if image_path:
        if os.path.exists(image_path):
            print(f"Processing image: {image_path}")
            temp_img_path = "processed_profile_manual.png"
            processed_image_path = create_circular_image_with_border(image_path, temp_img_path)
        else:
            print(f"Warning: Image path does not exist: {image_path}")

    output_dir = "output_cvs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Generating PDFs from JSON...")
    path_normal = generate_divider(data, out_dir=output_dir, image_path=processed_image_path)
    path_small = generate_divider_smaller(data, out_dir=output_dir, image_path=processed_image_path)
    path_large = generate_divider_larger(data, out_dir=output_dir, image_path=processed_image_path)

    print(f"Generated:\n{path_normal}\n{path_small}\n{path_large}")

if __name__ == "__main__":
    main()
