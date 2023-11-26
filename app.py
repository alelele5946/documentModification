from flask import Flask, request, jsonify
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import RectangleObject
import requests
import io
import os

# Asegúrate de que las variables de entorno estén configuradas en Heroku
SUPABASE_API_KEY = os.environ.get('SUPABASE_API_KEY')
Git = os.environ.get('SUPABASE_BEARER_TOKEN')


app = Flask(__name__)


@app.route('/test-crop', methods=['POST'])
def test_crop():
    data = request.get_json()
    record = data.get('record')  # Accede al diccionario 'record' dentro del JSON

    if not record:
        return jsonify({"error": "El cuerpo de la solicitud no contiene 'record'."}), 400

    pdf_url = record.get('URL_PDF')
    row_id = record.get('id')
    print(f"URL del PDF: {pdf_url}, ID de la fila: {row_id}")

    if not row_id or not pdf_url:
        return jsonify({"error": "Falta el 'id' de la fila o la URL del PDF."}), 400

    try:
        # Descargar el PDF
        response = requests.get(pdf_url)
        response.raise_for_status()

        # Leer el PDF desde la respuesta
        reader = PdfReader(io.BytesIO(response.content))
        writer = PdfWriter()

        # Recortar cada página y extraer texto
        extracted_text = ""
        for page in reader.pages:
            page.cropbox = RectangleObject((100.3, 0, 612, 792))  # Recortar la página
            writer.add_page(page)
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

        # Ahora que tienes el texto, puedes enviarlo a Supabase
        supabase_url = 'https://mgfdhvmvuthxvfyriacu.supabase.co/rest/v1/Documentos'
        headers = {
            "apikey": SUPABASE_API_KEY,
            "Authorization": SUPABASE_BEARER_TOKEN,
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        # Supongamos que quieres actualizar la columna 'document_text' del documento que cumple cierta condición
        data_to_patch = {
            "Doc_TXT": extracted_text  # Asegúrate de que esta columna exista en tu tabla de Supabase
        }
        # Aquí necesitas especificar cómo identificar el registro a actualizar, por ejemplo:
        params = {
            "id": f"eq.{row_id}"  # Reemplaza con la condición apropiada
        }
        # Realiza la petición PATCH para actualizar el registro en Supabase
        response = requests.patch(supabase_url, headers=headers, json=data_to_patch, params=params)
        response.raise_for_status()
        print("PDF procesado y texto actualizado en Supabase con éxito.")


        return jsonify({"message": "PDF procesado y texto actualizado en Supabase con éxito."})

    except requests.HTTPError as e:
        print(f"HTTPError al procesar la solicitud: {e}")
        return jsonify({"error": f"Error al procesar la solicitud: {e}"}), 500
    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"error": f"Error al procesar el archivo PDF: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
