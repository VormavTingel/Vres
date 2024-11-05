from flask import Flask, request, send_file, render_template_string
import qrcode
import io

app = Flask(__name__)

@app.route("/")
def index():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Code Generator</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; flex-direction: column; align-items: center; padding-top: 50px; }
        input, select { padding: 10px; width: 300px; margin-bottom: 10px; }
        button { padding: 10px 20px; margin-top: 10px; }
        img { margin-top: 20px; }
    </style>
</head>
<body>
    <h1>QR Code Generator</h1>
    <input type="text" id="data" placeholder="Enter your link or text here" />
    <select id="fileFormat">
        <option value="png">PNG</option>
        <option value="jpg">JPG</option>
    </select>
    <button onclick="generateQRCode()">Generate QR Code</button>
    <div id="qrcode"></div>
    <a id="downloadLink" style="display: none;" download="qrcode">Download QR Code</a>

    <script>
        async function generateQRCode() {
            const data = document.getElementById("data").value;
            const fileFormat = document.getElementById("fileFormat").value;
            if (!data) {
                alert("Please enter some data to generate a QR code.");
                return;
            }

            const response = await fetch("/generate_qrcode", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ data: data, format: fileFormat })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                document.getElementById("qrcode").innerHTML = `<img src="${url}" alt="QR Code" />`;

                // Configurar o link de download
                const downloadLink = document.getElementById("downloadLink");
                downloadLink.href = url;
                downloadLink.download = `qrcode.${fileFormat}`;
                downloadLink.style.display = "inline";
                downloadLink.textContent = "Download QR Code";
            } else {
                alert("Failed to generate QR code.");
            }
        }
    </script>
</body>
</html>
    """
    return render_template_string(html_content)

@app.route('/generate_qrcode', methods=['POST'])
def generate_qrcode():
    try:
        data = request.json.get("data")
        file_format = request.json.get("format", "png").lower()

        if not data:
            return {"error": "No data provided"}, 400

        # Criar QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")

        # Salvar a imagem no formato especificado
        buffer = io.BytesIO()
        if file_format == "jpg":
            img = img.convert("RGB")  # Converte para RGB, pois JPG não suporta transparência
            img.save(buffer, format="JPEG")
        else:
            img.save(buffer, format="PNG")
        buffer.seek(0)

        return send_file(buffer, mimetype=f"image/{file_format}")
    except Exception as e:
        print(f"Erro ao gerar QR Code: {e}")
        return {"error": "Failed to generate QR code"}, 500

if __name__ == "__main__":
    app.run(debug=True)
