from flask import Flask, render_template, request, send_file
from PIL import Image
import pillow_heif
import zipfile
import os
import uuid
import tempfile

app = Flask(__name__)

# Habilita apertura de imágenes HEIC
pillow_heif.register_heif_opener()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    files = request.files.getlist("images")

    if not files or files[0].filename == "":
        return "No se subieron imágenes", 400

    # Carpeta temporal (se borra sola después)
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "imagenes_convertidas.zip")

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in files:
            # Guardar HEIC temporal
            heic_path = os.path.join(temp_dir, file.filename)
            file.save(heic_path)

            # Abrir y convertir
            img = Image.open(heic_path).convert("RGB")

            jpg_name = f"{uuid.uuid4()}.jpg"
            jpg_path = os.path.join(temp_dir, jpg_name)

            img.save(jpg_path, "JPEG", quality=90)

            # Agregar al ZIP
            zipf.write(jpg_path, jpg_name)

    return send_file(zip_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
