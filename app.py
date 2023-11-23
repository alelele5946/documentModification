from PyPDF2.generic import RectangleObject
from flask import Flask, request, send_from_directory, jsonify
from PyPDF2 import PdfReader, PdfWriter
import os
import requests
import io

app = Flask(__name__)


@app.route('/test-crop', methods=['POST'])  # Aceptar solicitudes POST
def test_crop():
    # Obtener el JSON del cuerpo de la solicitud
    data = request.get_json()

    # Obtener la URL del PDF del JSON
    pdf_url = data.get('URL_PDF')

    if not pdf_url:
        return jsonify({"error": "No se proporcionó la URL del PDF."}), 400

    try:
        # Hacer una solicitud GET para descargar el PDF
        response = requests.get(pdf_url)
        response.raise_for_status()  # Asegurarse de que la solicitud fue exitosa

        # Leer el PDF desde la respuesta de la solicitud
        reader = PdfReader(io.BytesIO(response.content))
        writer = PdfWriter()

        # Ruta al archivo PDF recortado
        output_pdf_path = os.path.join('static', 'pdfs', 'test_cropped.pdf')

        # Ruta al archivo de texto donde se guardará el texto extraído
        output_txt_path = os.path.join('static', 'txt', 'test_extracted.txt')

        # Abre el archivo de texto en modo de escritura
        with open(output_txt_path, 'w') as txt_outstream:
            # Recortar cada página y extraer texto
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    txt_outstream.write(text + "\n")  # Escribe el texto en el archivo de texto
                page.cropbox = RectangleObject((0, 0, 500, 792))
                writer.add_page(page)

        # Escribir el archivo PDF recortado
        with open(output_pdf_path, 'wb') as outstream:
            writer.write(outstream)

    except requests.HTTPError as e:
        print(f"Ocurrió un error al descargar el PDF: {e}")
        return jsonify({"error": f"Error al descargar el PDF: {e}"}), 500
    except Exception as e:
        print(f"Ocurrió un error al procesar el PDF: {e}")
        return jsonify({"error": f"Error al procesar el archivo PDF: {e}"}), 500

    # Devuelve el archivo PDF recortado
    return send_from_directory('static/pdfs', 'test_cropped.pdf', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
