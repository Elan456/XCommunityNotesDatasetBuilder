from io import BytesIO
import os
import cv2
import pytesseract
import numpy as np
from PIL import Image
import argparse

import requests

def remove_meme_text(pil_image):
    # Convert PIL image to OpenCV format
    image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape

    # Use PSM 6 (Assume a uniform block of text) for better meme text detection
    custom_oem_psm_config = r'--oem 3 --psm 6'
    data = pytesseract.image_to_data(gray, config=custom_oem_psm_config, output_type=pytesseract.Output.DICT)

    bounding_boxes = []
    cropped_text = []

    for i in range(len(data["text"])):
        text = data["text"][i].strip()
        conf = int(data["conf"][i])
        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]

        # Only consider text with high confidence and reasonable size
        if conf > 60 and len(text) > 2:
            bounding_boxes.append((x, y, w, h))

    def merge_boxes(boxes, threshold=75):
        """Merge overlapping bounding boxes into larger text regions."""
        if not boxes:
            return []

        boxes.sort(key=lambda b: b[1])  # Sort by y-coordinate
        merged_boxes = [boxes[0]]

        for x, y, w, h in boxes[1:]:
            prev_x, prev_y, prev_w, prev_h = merged_boxes[-1]

            # Merge if close in y-direction considering the height of the previous box
            if y <= prev_y + prev_h + threshold:
                new_x = min(prev_x, x)
                new_y = min(prev_y, y)
                new_w = max(prev_x + prev_w, x + w) - new_x
                new_h = max(prev_y + prev_h, y + h) - new_y

                merged_boxes[-1] = (new_x, new_y, new_w, new_h)
            else:
                merged_boxes.append((x, y, w, h))

        return merged_boxes

    bounding_boxes = merge_boxes(bounding_boxes)

    if not bounding_boxes:
        return pil_image, None
    
    filtered_width_boxes = []
    min_width = width * 0.80
    top_threshold = height * 0.10
    bottom_threshold = height * 0.90

    for box in bounding_boxes:
        #can you print the text in the boxes
        x, y, w, h = box
        if w >= min_width:
            filtered_width_boxes.append(box)

    if not filtered_width_boxes:
        return pil_image, None


    # Determine cropping boundaries
    min_y = min(box[1] for box in filtered_width_boxes)
    max_y = max(box[1] + box[3] for box in filtered_width_boxes)

    # Check if the min or max is in the top or bottom 10% of the image


    if min_y < top_threshold or max_y > bottom_threshold:
        # Ensure we are cropping a significant portion but not more than 50% of the image height
        max_crop_height = height * 0.50

        if min_y < height/2:
            crop_height = max_y
        else:
            crop_height = height-min_y

        if height * 0.10 < crop_height <= max_crop_height:
            for i in range(len(data["text"])):
                text = data["text"][i].strip()
                x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                if min_y <= y <= max_y or min_y <= y + h <= max_y:
                    if text:
                        cropped_text.append(text)

            if min_y < height / 2:
                # Meme text is at the top
                cropped_image = image[max_y:height, :, :]
            else:
                # Meme text is at the bottom
                cropped_image = image[:min_y, :, :]

            cropped_pil_image = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
            return cropped_pil_image if cropped_pil_image.size[1] > 0 else pil_image, " ".join(
                cropped_text)  # Avoid empty images
    return pil_image, None

def main():
    parser = argparse.ArgumentParser(description="Remove meme text from an image by cropping.")
    parser.add_argument("media_url", type=str, help="Path to the input image")
    parser.add_argument("output_path", type=str, help="Path to save the output image")

    args = parser.parse_args()

    output_dir = os.path.dirname(args.output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Create the directory if it doesn't exist

    response = requests.get(args.media_url)
    my_img = Image.open(BytesIO(response.content))
    cleaned_image, cropped_text = remove_meme_text(my_img)
    cleaned_image.save(args.output_path)
    #check to see if output path exists
    print(f"Processed image saved at {args.output_path}")
    if cropped_text:
        print("Cropped Text:", cropped_text)
    else:
        print("No significant meme text detected.")

if __name__ == "__main__":
    main()