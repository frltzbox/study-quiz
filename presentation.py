import fitz  # PyMuPDF
import os
from groq import Groq
import base64


def pdf_to_png_with_pymupdf(pdf_path, output_folder):
    # Erstellen des Ausgabeordners, falls er nicht existiert
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Öffnen der PDF-Datei
    pdf_document = fitz.open(pdf_path)
    
    # Jede Seite konvertieren und speichern
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        pix = page.get_pixmap(dpi=300)  # Render die Seite als Bild mit 300 DPI
        output_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
        pix.save(output_path)
        print(f"Seite {page_num + 1} als {output_path} gespeichert.")
    pdf_document.close()
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')



def pdfinfo(pdf):
    newpath = 'pdfimages' 
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    file = open('text.pdf', 'wb')
    file.write(pdf)
    file.close()
    dirname = os.path.dirname(__file__)
    pdf_path = os.path.join(dirname, 'text.pdf')
    image_directory_path = os.path.join(dirname, newpath)
    # Beispiel für die Verwendung des Programms
    pdf_to_png_with_pymupdf(pdf_path, image_directory_path)
    
    # Function to encode the image
    base64_images = []
    for filename in os.listdir(image_directory_path):
        file_path = os.path.join(image_directory_path, filename)
        # Check if it's a file (to avoid directories)
        if os.path.isfile(file_path):
            base64_image = encode_image(file_path)
            base64_images.append(base64_image)



    client = Groq(api_key='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')
    response = ""
    for i in base64_images:
        chat_completion = client.chat.completions.create(
        messages=[

            {

                "role": "user",

                "content": [

                    {"type": "text", "text": "Beschreibe den Inhalt dieser Seite in maximal 100 wörtern"},

                    {

                        "type": "image_url",

                        "image_url": {

                            "url": f"data:image/jpeg;base64,{i}",

                        },

                    },

                ],

            }

        ],

        model="llama-3.2-11b-vision-preview",

        )
        response = response + chat_completion.choices[0].message.content
    os.remove(pdf_path)
    return response
