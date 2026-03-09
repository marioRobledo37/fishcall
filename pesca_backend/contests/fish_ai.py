import requests
from PIL import Image
from io import BytesIO


def detect_species(image_url):

    try:

        response = requests.get(image_url)

        img = Image.open(BytesIO(response.content))

        width, height = img.size

        # lógica simple temporal
        # solo verificar que sea una imagen válida

        if width > 0 and height > 0:
            return "Pez"

    except Exception:
        pass

    return "Desconocido"