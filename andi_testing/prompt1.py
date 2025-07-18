import openai
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# Your OpenAI API key
openai.api_key = "sk-..."

# Load local image or from URL
image_path = "photo_20250709_182857.jpg"
image = Image.open(image_path)

# Convert to bytes for API upload
with open(image_path, "rb") as f:
    img_bytes = f.read()

# 1. Send the image to OpenAI's Vision API with an appropriate prompt
prompt = (
    "Identify all plants in this image. "
    "Return a list of bounding boxes in the format [x_min, y_min, x_max, y_max], "
    "and the label for each plant. Use 'Thistle' if you can identify it, otherwise use 'Unknown'."
)

# OpenAI Vision API call (GPT-4o vision example)
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are an expert botanist and image annotator."},
        {"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": "attachment://input_image.jpg"},
        ]}
    ],
    files=[("input_image.jpg", img_bytes)]
)
result = response.choices[0].message.content

# Example of expected response (simulate parsing)
# result = '''
# [
#   {"label": "Thistle", "box": [25, 210, 590, 480]},
#   {"label": "Unknown", "box": [320, 40, 570, 210]},
#   {"label": "Unknown", "box": [10, 10, 250, 130]},
#   {"label": "Unknown", "box": [430, 110, 610, 250]}
# ]
# '''

import json
boxes = json.loads(result)

# 2. Draw the bounding boxes and labels
draw = ImageDraw.Draw(image)
try:
    font = ImageFont.truetype("arial.ttf", 28)
except:
    font = ImageFont.load_default()

for obj in boxes:
    box = obj["box"]
    label = obj["label"]
    color = "green" if label.lower() == "thistle" else "red"
    draw.rectangle(box, outline=color, width=4)
    draw.text((box[0]+5, box[1]-30), label, fill=color, font=font)

# 3. Save the result
output_path = "annotated_output.jpg"
image.save(output_path)
print(f"Saved: {output_path}")
