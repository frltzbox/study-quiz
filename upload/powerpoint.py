from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from PIL import Image
import os
import io
import base64
from groq import Groq

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def describe_pptx(pptx_path):
    # Load the PowerPoint presentation
    prs = Presentation(pptx_path)
    
    newpath = r'export-images' 
    dirname = os.path.dirname(os.path.realpath(__file__))
    image_directory_path = os.path.join(dirname, newpath)
    if not os.path.exists(image_directory_path):
        os.makedirs(image_directory_path)

    slide_content = []
    response = []
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')

    # Initialize the Groq client
    client = Groq(api_key=GROQ_API_KEY)
    summary_instruction = "fasse die folgenden informationen auf deutsch zusammen ohne informationen hinzuzufügen"

    # Loop through each slide in the presentation
    for slide_num, slide in enumerate(prs.slides):
        # Position elements
        for shape in slide.shapes:
            # If the shape has text, draw the text
            if hasattr(shape, "text") and shape.text:
                slide_content.append(shape.text)
            
            # If the shape is a picture, add the image
            elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                #TODO: store images on one slide into an array and do the request after finishing process all text on the same slide
                image_stream = io.BytesIO(shape.image.blob)  # Read image data from shape
                slide_image = Image.open(image_stream)
                slide_image.save(os.path.join(image_directory_path,'slide.png'))
                base64_image = encode_image(os.path.join(image_directory_path,'slide.png'))

                #API request
                chat_completion = client.chat.completions.create(
                    messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", "text": "fasse wichtige inhalte aus dem Bild kurz zusammen Füge keine neuen informationen hinzu. Wenn keine Informationen da sind, gebe nichts zurück"
                            },
                            {
                        "type": "image_url",
                        "image_url": {

                            "url": f"data:image/png;base64,{base64_image}",
                        },},
                           ],
                    }
                    ],
                model="llama-3.2-90b-vision-preview",
                    
                )
                slide_content.append(chat_completion.choices[0].message.content)


        #Summarize the descriptions
        summary_input = [
                {

                    "role": "user",

                    "content": summary_instruction,

                },
            ]
        
        for co in slide_content:
            if co != '‹#›':
                summary_input.append(
                    {

                        "role": "user",

                        "content": co,
                    }
                    )
        print(summary_input, '\n\n')

        chat_completion = client.chat.completions.create(
            messages=summary_input,

            model="llama3-8b-8192",
        )
        response.append(chat_completion.choices[0].message.content)
        summary_input.clear()
        slide_content.clear()
    print(response)
    return response


