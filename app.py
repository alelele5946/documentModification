from PyPDF2.generic import RectangleObject
from flask import Flask, send_from_directory
from PyPDF2 import PdfReader, PdfWriter
import os

app = Flask(__name__)


@app.route('/test-crop')
def test_crop():
    # Ruta al archivo PDF original dentro de la carpeta 'static/pdfs'
    input_pdf_path = os.path.join('static', 'pdfs', 'test.pdf')

    # Ruta donde se guardará el archivo PDF recortado
    output_pdf_path = os.path.join('static', 'pdfs', 'test_cropped.pdf')

    # Ruta al archivo de texto donde se guardará el texto extraído
    output_txt_path = os.path.join('static', 'txt', 'test_extracted.txt')

    try:
        reader = PdfReader(input_pdf_path, 'rb')
        writer = PdfWriter()

        # Abre el archivo de texto en modo de escritura
        with open(output_txt_path, 'w') as txt_outstream:
            # Recortar cada página y extraer texto
            for i in range(len(reader.pages)):
                page = reader.pages[i]
                text = page.extract_text()
                if text:
                    txt_outstream.write(text + "\n")  # Escribe el texto en el archivo de texto
                page.cropbox = RectangleObject((0, 0, 500, 792))
                writer.add_page(page)

        # Escribir el archivo PDF recortado
        with open(output_pdf_path, 'wb') as outstream:
            writer.write(outstream)

    except Exception as e:
        print(f"Ocurrió un error al recortar el PDF: {e}")
        return f"Error al procesar el archivo PDF: {e}", 500

    # Devuelve el archivo PDF recortado
    return send_from_directory(os.path.join('static', 'pdfs'), 'test_cropped.pdf', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
