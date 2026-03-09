import cv2
import numpy as np
import requests
from io import BytesIO
from PIL import Image


def measure_fish(image_url):

    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img = np.array(img)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # detectar bordes
    edges = cv2.Canny(gray, 50, 150)

    # detectar líneas de la regla
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi/180,
        threshold=100,
        minLineLength=200,
        maxLineGap=10
    )

    if lines is None:
        return None

    # buscar la línea más larga (probablemente la regla)
    longest = 0

    for line in lines:
        x1, y1, x2, y2 = line[0]
        length = np.hypot(x2-x1, y2-y1)

        if length > longest:
            longest = length

    ruler_pixels = longest

    # asumimos regla visible de 30 cm
    px_per_cm = ruler_pixels / 30

    # detectar pez
    blur = cv2.GaussianBlur(gray,(5,5),0)
    thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]

    contours,_ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    fish = max(contours, key=cv2.contourArea)

    x,y,w,h = cv2.boundingRect(fish)

    fish_pixels = max(w,h)

    length_cm = fish_pixels / px_per_cm

    return round(length_cm,1)