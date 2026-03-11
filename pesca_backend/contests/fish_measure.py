import cv2
import numpy as np
import requests
from io import BytesIO
from PIL import Image
import pytesseract


def measure_fish(image_url):

    try:

        # ==========================
        # descargar imagen
        # ==========================

        response = requests.get(image_url)

        img = Image.open(BytesIO(response.content))

        img = np.array(img)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        height, width = gray.shape


        # ==========================
        # detectar bordes
        # ==========================

        edges = cv2.Canny(gray, 50, 150)


        # ==========================
        # detectar regla
        # ==========================

        lines = cv2.HoughLinesP(
            edges,
            1,
            np.pi/180,
            threshold=120,
            minLineLength=200,
            maxLineGap=20
        )

        if lines is None:
            return None


        longest = 0

        for line in lines:

            x1, y1, x2, y2 = line[0]

            length = np.hypot(x2-x1, y2-y1)

            if length > longest:

                longest = length


        ruler_pixels = longest

        if ruler_pixels == 0:
            return None


        # ==========================
        # intentar OCR de números
        # ==========================

        px_per_cm = None

        try:

            roi = gray[int(height*0.5):height, :]

            text = pytesseract.image_to_string(roi)

            numbers = []

            for t in text.split():

                try:
                    numbers.append(int(t))
                except:
                    pass


            numbers = sorted(numbers)

            if len(numbers) >= 2:

                span_cm = numbers[-1] - numbers[0]

                if span_cm > 0:

                    px_per_cm = ruler_pixels / span_cm

        except:
            pass


        # ==========================
        # fallback si OCR falla
        # ==========================

        if px_per_cm is None:

            # asumimos que la regla visible ≈ 20 cm
            px_per_cm = ruler_pixels / 20


        # ==========================
        # detectar pez
        # ==========================

        blur = cv2.GaussianBlur(gray,(7,7),0)

        _, thresh = cv2.threshold(
            blur,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )


        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )


        if not contours:
            return None


        fish = max(contours, key=cv2.contourArea)


        # ==========================
        # medir pez (distancia máxima)
        # ==========================

        pts = fish.reshape(-1,2)

        max_dist = 0

        for i in range(len(pts)):

            for j in range(i+1, len(pts)):

                d = np.linalg.norm(pts[i] - pts[j])

                if d > max_dist:

                    max_dist = d


        fish_pixels = max_dist


        # ==========================
        # convertir a cm
        # ==========================

        length_cm = fish_pixels / px_per_cm


        # ==========================
        # torneo usa enteros
        # ==========================

        return int(length_cm)


    except Exception as e:

        print("ERROR MEDICION:", e)

        return None