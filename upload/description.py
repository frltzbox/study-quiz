import fitz  # PyMuPDF
import os
from groq import Groq
import base64
import logging
import io
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
import tempfile
from pathlib import Path

allowed_paths = [".pptx", ".pdf"]


def api_setup():
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    if GROQ_API_KEY is None:
        raise ValueError("The GROQ_API_KEY environment variable is not set.")
    # Initialize the Groq client
    client = Groq(api_key=GROQ_API_KEY)
    return client



def encode_image(image_stream):
    return base64.b64encode(image_stream.read()).decode('utf-8')



def save_text(text_to_save):
    print("save function running")
    full_text_path = Path(__file__).parent / "full_text.txt"
    if not full_text_path.exists():
        full_text_path.touch()
    with open(full_text_path, "a") as file:
        file.write(text_to_save)
    return None

def describe_image(image_stream, prompt):
    client = api_setup()
    base64_image = encode_image(image_stream)
    try:
        chat_completion = client.chat.completions.create(
                        messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                            },},],}],
                    model="llama-3.2-90b-vision-preview",)
        return chat_completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Error during summary API request: {e}")
        return None



def summarize(long_text, prompt):
    client = api_setup()
    try:
        chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": long_text,
                    },
                ],
                model="llama3-8b-8192",
            )
        response = chat_completion.choices[0].message.content
        return response
    except Exception as e:
        logging.error(f"Error during summary API request: {e}")
        return None



def describe_pdf(pdf, short_response=False, max_length=3000, store_content=False):
    pdf_stream = io.BytesIO(pdf.read())
    image_prompt = "Das folgende Bild ist Teil einer Presentation, fasse zentrale Inhalte des Bildes in maximal 100 Worten zusammen, ohne Information hinzuzufügen"
    summary_prompt = "du fasst die wichtigsten informationen eines Textes auf deutsch in ganzen sätzen zusammen. Füge keine Informationen hinzu. gebe nur die Zusammenfassung zurück. Füge keine Textformatierung hinzu."
    pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
    response = ""
    for page_num in range(pdf_document.page_count):
        text = ""
        page = pdf_document[page_num]
        text += page.get_text()
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_stream = io.BytesIO(image_bytes)
            text += describe_image(image_stream, image_prompt)
        response += summarize(text, summary_prompt)
        if store_content:
            save_text(text)
    pdf_document.close()
    summary = response
    if len(response) > max_length and short_response:
            logging.warning("Die Länge der Zusammenfassung könnte zu Problemen führen, daher wird diese in Abschnitten erneut zusammengefasst")
            summary = summarize(response, summary_prompt)
    return summary



def describe_pptx(pptx, short_response=False, max_length=3000, store_content=False):
    pptx_bytes = pptx.read()
    pptx_stream = io.BytesIO(pptx_bytes)
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as temp_file:
        temp_file.write(pptx_stream.read())
        temp_file_path = temp_file.name  # Get the path of the temporary file
    # Load the PowerPoint presentation
    prs = Presentation(temp_file_path)
    response = ""
    image_prompt = "Das folgende Bild ist Teil einer Presentation, fasse zentrale Inhalte des Bildes in maximal 100 Worten zusammen, ohne Information hinzuzufügen"
    # Instruction for summarizing the content of a presentation slide in German
    summary_prompt = "du fasst die Inhalte einer presentationsfolie kurz auf deutsch zusammen. Füge keine Informationen hinzu. Vermeide Geplappere und gebe nur die Zusammenfassung zurück. Füge keine Textformatierung hinzu."
    if len(prs.slides) > 20:
        logging.warning("The length of this presentation might cause issues with the token limit.")

    for slide_number,slide in enumerate(prs.slides):
        slide_content = ""
        # Position elements
        for shape in slide.shapes:
            # If the shape has text, draw the text
            if hasattr(shape, "text") and shape.text and shape.text != "<#>":
                slide_content += shape.text

            # If the shape is a picture, add the image
            elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                image_stream = io.BytesIO(shape.image.blob)  # Read image data from shape
                slide_content += describe_image(image_stream, image_prompt)

        response += summarize(slide_content, summary_prompt)
        if store_content:
            save_text(slide_content)
    summary = response
    if len(response) > max_length and short_response:
            logging.warning("Die Länge der Zusammenfassung könnte zu Problemen führen, daher wird diese in Abschnitten erneut zusammengefasst")
            summary = summarize(response, summary_prompt)
    return summary

pdf_path = r'C:\Users\Jonas\Downloads\2023.03.02_BROSCH_NEU_NUR_WEB_gym_Oberstufe_v12_WEB.pdf'
pptx_path = r"C:\Users\Jonas\Downloads\schlacht-bei-tannenberg(1).pptx"
#with open(pptx_path, 'rb') as source:
#    document = source.read()
#    print(describe_pptx(document))

