from flask import Flask, render_template, request
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

import cv2
import numpy as np
from PIL import Image
import re

app = Flask(__name__)

# State-wise carbon emission factors
state_factors = {
    "Kerala": 0.55,
    "Tamil Nadu": 0.75,
    "Karnataka": 0.72,
    "Maharashtra": 0.90,
    "Gujarat": 0.82,
    "Delhi": 0.85,
    "West Bengal": 0.95,
    "Jharkhand": 1.05,
    "Himachal Pradesh": 0.30
}

def extract_units(text):
    patterns = [
        r"(\d+\.?\d*)\s*(kwh|units)",
        r"(kwh|units)\s*(\d+\.?\d*)"
    ]

    text = text.lower()

    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            for match in matches:
                for item in match:
                    try:
                        value = float(item)
                        if 10 <= value <= 10000:
                            return value
                    except:
                        pass
    return None


@app.route("/", methods=["GET", "POST"])
def index():

    carbon = None
    units = None
    filename = None
    ocr_text = None
    state = None
    factor = None   # <-- add this

    if request.method == "POST":

        file = request.files["bill"]
        filename = file.filename

        state = request.form.get("state", "Kerala")
        factor = state_factors.get(state, 0.82)

        print("Selected state:", state)
        print("Emission factor:", factor)

        img = Image.open(file).convert("RGB")
        img = np.array(img)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5,5), 0)

        ocr_text = pytesseract.image_to_string(gray)

        units = extract_units(ocr_text)

        # fallback if OCR fails
        if units is None:
            units = 250

        carbon = round(units * factor, 2)

    return render_template(
        "index.html",
        units=units,
        carbon=carbon,
        filename=filename,
        ocr_text=ocr_text,
        states=state_factors.keys(),
        selected_state=state,
        factor=factor
    )

if __name__ == "__main__":
    app.run(debug=True)