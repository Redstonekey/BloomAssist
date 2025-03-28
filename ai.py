from google import genai
from google.genai import types
import PIL.Image
import base64
import os


# def gemini_image(img_path, message, context):
#     image = PIL.Image.open('image.jpg')
#     if img_path == 'none':
#         gemini(message, context)  #type: ignore
#         return "No image provided"

#     client = genai.Client(api_key="AIzaSyDUGz1MODta7hkPBwLFLYembTb0xTtSv74")
#     response = client.models.generate_content(
#         model="gemini-2.0-flash",
#         contents=["What is this image?", image])

#     print(response.text)
#     return response.text

class gemini:
    # @staticmethod
    # def text(message, context):
    #     print('----------------')
    #     print("message: ", message)
    #     print("context: ", context)
    #     print('----------------')

    #     client = genai.Client(
    #         api_key='AIzaSyDUGz1MODta7hkPBwLFLYembTb0xTtSv74',
    #     )

    #     model = "gemini-2.0-flash"
    #     contents = [
    #         types.Content(
    #             role="user",
    #             parts=[
    #                 types.Part.from_text(text=message),
    #             ],
    #         ),
    #     ]
    #     generate_content_config = types.GenerateContentConfig(
    #         temperature=1,
    #         top_p=0.95,
    #         top_k=40,
    #         max_output_tokens=8192,
    #         response_mime_type="text/plain",
    #         system_instruction=[
    #             types.Part.from_text(text=context),
    #         ],
    #     )

    #     for chunk in client.models.generate_content_stream(
    #         model=model,
    #         contents=contents, # type: ignore
    #         config=generate_content_config,
    #     ):
    #         print(chunk.text)
    #         return chunk.text
    @staticmethod
    def picture(message: str, img_path: str, context: str):
        image = PIL.Image.open(img_path)
        if img_path == 'none':
            return gemini.text(message, context)

        client = genai.Client(api_key="AIzaSyDUGz1MODta7hkPBwLFLYembTb0xTtSv74")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[ 'context\n' + context + '\n Message\n' + message, image])

        print(response.text)
        return response.text
    

    @staticmethod
    def text(input_content: str, context: str):
        client = genai.Client(
            api_key='AIzaSyDUGz1MODta7hkPBwLFLYembTb0xTtSv74',
        )

        model = "gemini-2.0-flash"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="""content"""),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text=context),
            ],
        )

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=[input_content],
            config=generate_content_config,
        ):
            print(chunk.text, end="")

#----------------
# example usage
#----------------
# gemini.text('erzähle mir eine 30 sekunden geschichte', 'context')
# gemini.generate('erzähle mir eine 30 sekunden geschichte', 'sei eine katzte')
# gemini.picture('message', 'image.jpg', 'context')