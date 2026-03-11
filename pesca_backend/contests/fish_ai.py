from google.cloud import vision
from google.oauth2 import service_account
import os

# ruta a tu credencial
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

credentials = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR, "credentials/service_account.json")
)

client = vision.ImageAnnotatorClient(credentials=credentials)


def detect_species(image_url):

    try:

        image = vision.Image()
        image.source.image_uri = image_url

        response = client.label_detection(image=image)

        labels = [label.description.lower() for label in response.label_annotations]

        print("LABELS DETECTADAS:", labels)

        if "catfish" in labels:
            return "Bagre"

        if "pike" in labels:
            return "Tararira"

        if "carp" in labels:
            return "Boga"

        if "fish" in labels:
            return "Pez"

        return "Desconocido"

    except Exception as e:

        print("ERROR IA:", e)

        return "Pez"