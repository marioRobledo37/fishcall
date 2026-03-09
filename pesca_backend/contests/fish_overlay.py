import cv2
import numpy as np
import requests
from io import BytesIO
from PIL import Image


def draw_measurement(image_url, length_cm):

    response = requests.get(image_url)

    img = Image.open(BytesIO(response.content))

    img = np.array(img)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray,(5,5),0)

    edges = cv2.Canny(blur,50,150)

    contours,_ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return img

    fish = max(contours, key=cv2.contourArea)

    x,y,w,h = cv2.boundingRect(fish)

    start = (x, y+h//2)

    end = (x+w, y+h//2)

    # dibujar línea
    cv2.line(img, start, end, (0,255,0), 4)

    # dibujar extremos
    cv2.circle(img, start, 8, (0,255,0), -1)
    cv2.circle(img, end, 8, (0,255,0), -1)

    text = f"{length_cm} cm"

    cv2.putText(
        img,
        text,
        (x, y-20),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        3
    )

    return img