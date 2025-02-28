import requests
from PIL import Image

import os
import io
import base64
import requests

SUPPORTED_SERVICES = ['0x0.st', 'imgbb']

def host_image(image: Image, service: str) -> str:
    """
    Will upload the given image to the internet and then return the URL

    Services Supported:
    - '0x0.st'
    """

    if service not in SUPPORTED_SERVICES:
        raise ValueError(f"Service '{service}' is not supported. Supported services: {SUPPORTED_SERVICES}")

    if service == '0x0.st':
        return host_image_on_0x0st(image)
    
    if service == 'imgbb':
        return host_image_on_imgbb(image)
    

def host_image_on_0x0st(image: Image) -> str:
    """
    Will upload the given image to 0x0.st and then return the URL
    """

    # Temporarily write the image to a file
    image.save('temp_image.png')

    """
    Curl example
    Uploading a file:
        curl -F'file=@yourfile.png' https://0x0.st

         Uploading a file:
        curl -F'file=@yourfile.png' https://0x0.st
    Copy a file from a remote URL:
        curl -F'url=http://example.com/image.jpg' https://0x0.st
    Same, but with hard-to-guess URLs:
        curl -F'file=@yourfile.png' -Fsecret= https://0x0.st
        curl -F'url=http://example.com/image.jpg' -Fsecret= https://0x0.st

    """

    # Upload the image to 0x0.st with hard-to-guess URLs
    response = requests.post('https://0x0.st', files={'file': open('temp_image.png', 'rb')})
    return response.text

def host_image_on_imgbb(image: Image) -> str:
    """
    Uploads the given image to imgbb.com using the imgbb API and returns the image URL.
    
    The image is converted to a Base64 encoded string before sending.
    The image will auto-expire after the specified number of seconds (e.g., 60 seconds).
    
    Requirements:
    - Set your imgbb API key in the environment variable 'IMGBB_API_KEY'.
    """
    imgbb_api_key = open("imgbb.key", "r").read().strip()

    # Convert image to Base64 string
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    encoded_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

    payload = {
        'key': imgbb_api_key,
        'image': encoded_image,
        'expiration': 60  # Image will auto-delete after 60 seconds
    }
    
    response = requests.post("https://api.imgbb.com/1/upload", data=payload)
    response_json = response.json()
    
    if not response_json.get("success"):
        error_message = response_json.get("error", {}).get("message", "Unknown error")
        raise Exception(f"Image upload failed: {error_message}")
    
    return response_json["data"]["url"]


if __name__ == "__main__":
    image = Image.open('misleading_image/imgs/mcdonald.png')
    print(host_image(image, 'imgbb'))

    for image_url in os.listdir('misleading_image/imgs'):
        image = Image.open(f'misleading_image/imgs/{image_url}')
        print(host_image(image, 'imgbb'))