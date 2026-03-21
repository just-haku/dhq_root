import cv2
import numpy as np
import svgpathtools

img = cv2.imread('/home/haku/projects/DHQ_Root/test_files/circle1.png', cv2.IMREAD_GRAYSCALE)
_, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"Num contours: {len(contours)}")
if contours:
    print(f"Points in contour 0: {len(contours[0])}")
