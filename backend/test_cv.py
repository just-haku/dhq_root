import cv2
import numpy as np

img = np.ones((100, 100), dtype=np.uint8) * 255
img[25:75, 25:75] = 0

_, thresh1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
contours1, _ = cv2.findContours(thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

_, thresh2 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
contours2, _ = cv2.findContours(thresh2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"THRESH_BINARY (current code) contours: {len(contours1)}")
if len(contours1) > 0: print(f"  Shape 1: {contours1[0].shape}")
print(f"THRESH_BINARY_INV (proposed fix) contours: {len(contours2)}")
if len(contours2) > 0: print(f"  Shape 2: {contours2[0].shape}")
