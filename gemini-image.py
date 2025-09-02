from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

# Initialize the client with API key
client = genai.Client(api_key="AIzaSyDZIpa8sya6wPRlNuzh1TJx07-k-rXPDY8")  # Replace with your actual API key

# Generate an image from text description using Gemini
def generate_image_from_text():
    contents = ('Hi, can you create a 3d rendered image of a pig '
                'with wings and a top hat flying over a happy '
                'futuristic scifi city with lots of greenery?')

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO((part.inline_data.data)))
            image.save('gemini-native-image.png')
            image.show()

# Modify an existing image by adding elements using Gemini
def modify_existing_image():
    image = Image.open('Screenshot 2025-05-05 115555.png')
    text_input = ('Hi, can you add another character to this image?',)

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=[text_input, image],
        config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
        )
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.show()

# Generate multiple images using Imagen model
def generate_multiple_images():
    response = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt='A picture of a cat',
        config=types.GenerateImagesConfig(
            number_of_images=2,
        )
    )
    for generated_image in response.generated_images:
        image = Image.open(BytesIO(generated_image.image.image_bytes))
        image.show()

# Example usage - uncomment the function you want to test
if __name__ == "__main__":
    # generate_image_from_text()
    # modify_existing_image()
    # generate_multiple_images()
    pass

# Reference: https://ai.google.dev/gemini-api/docs/image-generation
# Consider the above link for more information on perfect prompts
