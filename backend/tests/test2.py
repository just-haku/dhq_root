import cv2
import numpy as np
import math

def test_proj():
    image_path = '/home/haku/projects/DHQ_Root/test_files/circle1.png'
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    cnt = max(contours, key=cv2.contourArea)
    approx = cv2.approxPolyDP(cnt, 0.5, True)
    points = [(float(pt[0][0]), float(pt[0][1])) for pt in approx]
    points.append(points[0])
    
    n = len(points)
    i = 0
    k = min(200, n - i) - 1
    
    segment = points[i : i+k+1]
    x = np.array([p[0] for p in segment])
    y = np.array([p[1] for p in segment])
    A = np.c_[x, y, np.ones(len(x))]
    b = x**2 + y**2
    
    c, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = c[0]/2, c[1]/2
    r = np.sqrt(c[2] + cx**2 + cy**2)
    
    print(f"Original: cx={cx:.3f}, cy={cy:.3f}, r={r:.3f}")
    
    mid_x = (segment[0][0] + segment[-1][0]) / 2.0
    mid_y = (segment[0][1] + segment[-1][1]) / 2.0
    nx, ny = -(segment[-1][1] - segment[0][1]), (segment[-1][0] - segment[0][0])
    length = math.hypot(nx, ny)
    print(f"Endpoints: start={segment[0]}, end={segment[-1]}, dist_span={length:.3f}")
    
    if length > 0:
        nx, ny = nx / length, ny / length
        dot = (cx - mid_x) * nx + (cy - mid_y) * ny
        new_cx, new_cy = mid_x + dot * nx, mid_y + dot * ny
        new_r = math.hypot(new_cx - segment[0][0], new_cy - segment[0][1])
        print(f"Projected: cx={new_cx:.3f}, cy={new_cy:.3f}, r={new_r:.3f}")

test_proj()
