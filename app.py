from flask import Flask, request, jsonify
import requests
import io
import os
import fitz

# Asegúrate de que las variables de entorno estén configuradas en Heroku
SUPABASE_API_KEY = os.environ.get('SUPABASE_API_KEY')
SUPABASE_BEARER_TOKEN = os.environ.get('SUPABASE_BEARER_TOKEN')

app = Flask(__name__)


@app.route('/test-crop', methods=['POST'])
def test_crop():
    data = request.get_json()
    """record = data.get('record') """  # Accede al diccionario 'record' dentro del JSON

    # if not record:
    #   return jsonify({"error": "El cuerpo de la solicitud no contiene 'record'."}), 400

    pdf_url = data.get('URL_PDF')
    row_id = data.get('id')
    prompt = data.get('prompt')
    print(f"URL del PDF: {pdf_url}, ID de la fila: {row_id}")

    if not row_id or not pdf_url:
        return jsonify({"error": "Falta el 'id' de la fila o la URL del PDF."}), 400

    try:
        # Descargar el PDF
        response = requests.get(pdf_url)
        response.raise_for_status()

        # Usar PyMuPDF para leer el PDF desde la respuesta
        doc = fitz.open(stream=io.BytesIO(response.content), filetype="pdf")

        extracted_text = ""
        extracted_text += prompt
        doc_txt = ""
        altura_footer = 80  # Ajusta este valor según tus documentos

        for page in doc:
            blocks = page.get_text("dict", sort=True)["blocks"]
            for block in blocks:
                rect = fitz.Rect(block["bbox"])
                if rect.y1 < (page.rect.height - altura_footer):
                    for line in block["lines"]:
                        for span in line["spans"]:
                            extracted_text += span["text"] + " "
                            doc_txt += span["text"] + " "
                    extracted_text += "\n"
                    doc_txt += "/n"

        # Cerrar documento
        doc.close()

        # Ahora que tienes el texto, puedes enviarlo a fastgen


        fastgen_url = 'https://juiciator.fastgenapp.com/txtSupabase'

        # Supongamos que quieres actualizar la columna 'document_text' del documento que cumple cierta condición
        data_to_post = {
            "id": row_id,
            "Doc_TXT": doc_txt,  
            "chatGpt_txt": extracted_txt
        }

        # Realiza la petición POST para actualizar el registro en Supabase
        response = requests.post(fastgen_url, data=data_to_post)
        response.raise_for_status()
        print("PDF procesado y texto actualizado en Supabase con éxito.")

        return jsonify({"message": "PDF procesado y texto mandado a fastgen con éxito."})

    except requests.HTTPError as e:
        print(f"HTTPError al procesar la solicitud: {e}")
        return jsonify({"error": f"Error al procesar la solicitud: {e}"}), 500
    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": f"Error al procesar el archivo PDF: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
