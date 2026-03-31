import cv2
import numpy as np
import math
import os

def trace_to_svg(image_path, epsilon_val=0.5, tol=1.0):
    img_raw = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img_raw.ndim == 3 and img_raw.shape[2] == 4:
        bgr = img_raw[:, :, :3].astype(np.float32)
        alpha = img_raw[:, :, 3:4].astype(np.float32) / 255.0
        white_bg = np.ones_like(bgr, dtype=np.float32) * 255.0
        img = (bgr * alpha + white_bg * (1.0 - alpha)).astype(np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        if img_raw.ndim == 3: img = cv2.cvtColor(img_raw, cv2.COLOR_BGR2GRAY)
        else: img = img_raw
        
    h, w = img.shape
    _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    svg_paths = []
    
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, epsilon_val, True)
        if len(approx) < 3: continue
            
        points = [(float(pt[0][0]), float(pt[0][1])) for pt in approx]
        points.append(points[0]) # close loop
        
        path_d = f"M {points[0][0]:.3f},{points[0][1]:.3f} "
        
        i = 0
        n = len(points)
        
        while i < n - 1:
            best_arc = None
            best_k = 0
            
            # GROW GREEDY approach to naturally bound the segments
            for k in range(3, min(200, n - i)):
                segment = points[i : i+k+1]
                
                dist_span = math.hypot(segment[-1][0] - segment[0][0], segment[-1][1] - segment[0][1])
                if dist_span < 0.5: continue
                    
                x = np.array([p[0] for p in segment])
                y = np.array([p[1] for p in segment])
                
                A = np.c_[x, y, np.ones(len(x))]
                b = x**2 + y**2
                
                try:
                    c, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
                    cx, cy = c[0]/2, c[1]/2
                    r = np.sqrt(c[2] + cx**2 + cy**2)
                except Exception: continue
                    
                if r > 2000.0 or r < 0.1: continue
                    
                curve_length = np.sum(np.sqrt(np.diff(x)**2 + np.diff(y)**2))
                if curve_length > r * 2.0:
                    break 
                    
                distances = np.sqrt((x - cx)**2 + (y - cy)**2)
                max_err = np.max(np.abs(distances - r))
                
                if max_err <= tol:
                    # Enforce stable bisectors: removed dist_span < r * 0.5
                    
                    # PROJECT
                    mid_x = (segment[0][0] + segment[-1][0]) / 2.0
                    mid_y = (segment[0][1] + segment[-1][1]) / 2.0
                    nx, ny = -(segment[-1][1] - segment[0][1]), (segment[-1][0] - segment[0][0])
                    length = math.hypot(nx, ny)
                    if length > 0:
                        nx, ny = nx / length, ny / length
                        dot = (cx - mid_x) * nx + (cy - mid_y) * ny
                        cx, cy = mid_x + dot * nx, mid_y + dot * ny
                        # Recompute r based on projected center! Very important
                        r = math.hypot(cx - segment[0][0], cy - segment[0][1])

                    best_arc = (segment[0], segment[len(segment)//2], segment[-1], cx, cy, r)
                    best_k = k
                else:
                    break # error exceeded, stop growing
                    
            if best_k >= 3 and best_arc:
                p_start, p_mid, p_end, cx, cy, r = best_arc
                cross = (p_mid[0] - p_start[0]) * (p_end[1] - p_mid[1]) - (p_mid[1] - p_start[1]) * (p_end[0] - p_mid[0])
                sweep = 1 if cross > 0 else 0
                
                large_arc = 0
                
                path_d += f"A {r:.3f} {r:.3f} 0 {large_arc} {sweep} {p_end[0]:.3f} {p_end[1]:.3f} "
                i += best_k
            else:
                path_d += f"L {points[i+1][0]:.3f},{points[i+1][1]:.3f} "
                i += 1
                
        svg_paths.append(path_d)
        
    return svg_paths, w, h
    
paths, w, h = trace_to_svg('/home/haku/projects/DHQ_Root/test_files/GI.png')
with open('debug_gi.svg', 'w') as f:
    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">\n')
    f.write(f'<rect width="{w}" height="{h}" fill="white"/>\n')
    for p in paths: f.write(f'<path d="{p}" fill="none" stroke="black"/>\n')
    f.write('</svg>\n')
