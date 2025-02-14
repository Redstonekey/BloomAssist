from google import genai
from google.genai import types
import PIL.Image


def gemini_image(img_path, message, context):
    image = PIL.Image.open('image.jpg')
    if img_path == 'none':
        gemini(message, context)
        return "No image provided"

    client = genai.Client(api_key="AIzaSyDUGz1MODta7hkPBwLFLYembTb0xTtSv74")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=["What is this image?", image])

    print(response.text)