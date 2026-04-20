import requests

API_KEY = "K87314508188957"  # https://ocr.space/ocrapi

def leer_texto_api(archivo):
    url = "https://api.ocr.space/parse/image"

    response = requests.post(
        url,
        files={"file": archivo},
        data={
            "apikey": API_KEY,
            "language": "spa",
            "isOverlayRequired": False
        }
    )

    resultado = response.json()

    try:
        return resultado["ParsedResults"][0]["ParsedText"].upper()
    except:
        return ""