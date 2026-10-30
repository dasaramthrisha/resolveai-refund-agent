import json
import time
from google import genai
from google.genai import types, errors

client = genai.Client()
MODELS = ["gemini-3.1-flash-lite", "gemini-3.8-flash", "gemini-3-flash-preview"]

COMPLAINT_PROMPT = """Read this customer refund message. Reply ONLY with JSON in exactly this format:
{"reason": "damaged | defective | wrong_item | changed_mind | unclear",
 "severity": "low | medium | high",
 "summary": "one short sentence"}
Use "unclear" if the customer does not say why they want a refund."""

PHOTO_PROMPT = """Look at this photo of a product. Reply ONLY with JSON in exactly this format:
{"damage_visible": true or false, "description": "one short sentence"}"""


def _ask(contents, fallback):
    config = types.GenerateContentConfig(response_mime_type="application/json")
    for model in MODELS:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model, contents=contents, config=config
                )
                return json.loads(response.text)
            except errors.APIError as e:
                if e.code == 404:  # model not available: try the next one
                    break
                time.sleep(5)
            except (json.JSONDecodeError, TypeError):
                continue
            except Exception:  # dropped connection, timeout, etc.
                time.sleep(5)
    return fallback


def analyze_complaint(message):
    fallback = {"reason": "unclear", "severity": "low", "summary": "Could not analyze"}
    return _ask([COMPLAINT_PROMPT, "Customer message: " + message], fallback)


def analyze_photo(image_path):
    mime = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
    with open(image_path, "rb") as f:
        image = types.Part.from_bytes(data=f.read(), mime_type=mime)
    fallback = {"damage_visible": None, "description": "Could not analyze photo"}
    return _ask([image, PHOTO_PROMPT], fallback)