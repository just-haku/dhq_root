import cv2
import numpy as np
import potrace
import math
import os

def get_skeleton(img):
    skel = np.zeros(img.shape, np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    while True:
        eroded = cv2.erode(img, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(img, temp)
        skel = cv2.bitwise_or(skel, temp)
        img = eroded.copy()
        if cv2.countNonZero(img) == 0: break
    return skel

def generate_hatch_lines(mask, spacing=5.0, angle=45.0, pad=0):
    h, w = mask.shape
    angle_rad = math.radians(angle)
    nx, ny = math.cos(angle_rad), math.sin(angle_rad)
    dx, dy = -math.sin(angle_rad), math.cos(angle_rad)
    corners = [(0,0), (w,0), (w,h), (0,h)]
    projs = [cx*nx + cy*ny for cx, cy in corners]
    min_p, max_p = min(projs), max(projs)
    hatch_d = ""
    p = min_p
    while p <= max_p:
        pts = []
        if abs(ny) > 1e-5:
            y0 = (p - 0*nx)/ny
            if 0 <= y0 <= h: pts.append((0, y0))
            yw = (p - w*nx)/ny
            if 0 <= yw <= h: pts.append((w, yw))
        if abs(nx) > 1e-5:
            x0 = (p - 0*ny)/nx
            if 0 <= x0 <= w: pts.append((x0, 0))
            xh = (p - h*ny)/nx
            if 0 <= xh <= w: pts.append((xh, h))
        if len(pts) >= 2:
            pts = sorted(pts, key=lambda pt: pt[0] if abs(dx) > abs(dy) else pt[1])
            pt1, pt2 = pts[0], pts[-1]
            length = math.hypot(pt2[0]-pt1[0], pt2[1]-pt1[1])
            num_samples = int(length) + 1
            if num_samples > 1:
                x_coords = np.linspace(pt1[0], pt2[0], num_samples)
                y_coords = np.linspace(pt1[1], pt2[1], num_samples)
                xi = np.clip(np.round(x_coords).astype(int), 0, w-1)
                yi = np.clip(np.round(y_coords).astype(int), 0, h-1)
                mask_vals = mask[yi, xi]
                in_segment = False
                seg_start = None
                for i in range(num_samples):
                    if mask_vals[i] >= 127: 
                        if not in_segment:
                            in_segment = True
                            seg_start = (x_coords[i], y_coords[i])
                    else:
                        if in_segment:
                            in_segment = False
                            seg_end = (x_coords[i-1], y_coords[i-1])
                            hatch_d += f"M {seg_start[0]-pad:.3f},{seg_start[1]-pad:.3f} L {seg_end[0]-pad:.3f},{seg_end[1]-pad:.3f} "
                if in_segment:
                    seg_end = (x_coords[-1], y_coords[-1])
                    hatch_d += f"M {seg_start[0]-pad:.3f},{seg_start[1]-pad:.3f} L {seg_end[0]-pad:.3f},{seg_end[1]-pad:.3f} "
        p += spacing
    return hatch_d

def optimize_path_to_circle(pts_array, tolerance=0.05):
    if len(pts_array) < 10: return None
    (cx, cy), radius = cv2.minEnclosingCircle(pts_array)
    distances = np.sqrt((pts_array[:, 0] - cx)**2 + (pts_array[:, 1] - cy)**2)
    mean_r = np.mean(distances)
    if mean_r > 0 and (np.std(distances) / mean_r) < tolerance:
        return cx, cy, mean_r
    return None

def process_file(img_path, output_svg, hatch=False):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None: return
    h, w = img.shape
    pad = 20
    img_pad = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=255)
    _, mask = cv2.threshold(img_pad, 127, 255, cv2.THRESH_BINARY_INV)
    
    svg_paths = []
    bitmap = potrace.Bitmap(np.ascontiguousarray(mask > 0))
    path = bitmap.trace(turdsize=2, alphamax=1.0, opticurve=1, opttolerance=0.2)
    
    for curve in path:
        sampled_pts = []
        current_pt = curve.start_point
        sampled_pts.append(current_pt)
        for segment in curve:
            if segment.is_corner:
                sampled_pts.append(segment.c)
                sampled_pts.append(segment.end_point)
                current_pt = segment.end_point
            else:
                c1, c2, end = segment.c1, segment.c2, segment.end_point
                for i in range(1, 9):
                    t = i / 8.0
                    inv_t = 1.0 - t
                    x = (inv_t**3)*current_pt[0] + 3*(inv_t**2)*t*c1[0] + 3*inv_t*(t**2)*c2[0] + (t**3)*end[0]
                    y = (inv_t**3)*current_pt[1] + 3*(inv_t**2)*t*c1[1] + 3*inv_t*(t**2)*c2[1] + (t**3)*end[1]
                    sampled_pts.append((x, y))
                current_pt = end
        
        circle = optimize_path_to_circle(np.array(sampled_pts, dtype=np.float32))
        if circle:
            cx, cy, r = circle
            d = f"M {cx-pad-r:.3f},{cy-pad:.3f} A {r:.3f},{r:.3f} 0 0,0 {cx-pad+r:.3f},{cy-pad:.3f} A {r:.3f},{r:.3f} 0 0,0 {cx-pad-r:.3f},{cy-pad:.3f} Z"
            svg_paths.append(f'<path d="{d}" fill="none" stroke="black" stroke-width="1"/>')
        else:
            d = f"M {curve.start_point[0]-pad:.3f},{curve.start_point[1]-pad:.3f} "
            for segment in curve:
                if segment.is_corner:
                    d += f"L {segment.c[0]-pad:.3f},{segment.c[1]-pad:.3f} L {segment.end_point[0]-pad:.3f},{segment.end_point[1]-pad:.3f} "
                else:
                    d += f"C {segment.c1[0]-pad:.3f},{segment.c1[1]-pad:.3f} {segment.c2[0]-pad:.3f},{segment.c2[1]-pad:.3f} {segment.end_point[0]-pad:.3f},{segment.end_point[1]-pad:.3f} "
            d += "Z"
            svg_paths.append(f'<path d="{d}" fill="none" stroke="black" stroke-width="1"/>')
            
    if hatch:
        hd = generate_hatch_lines(mask, spacing=5, angle=45, pad=pad)
        if hd: svg_paths.append(f'<path d="{hd}" fill="none" stroke="blue" stroke-width="0.5"/>')
        
    with open(output_svg, "w") as f:
        f.write(f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">\n')
        f.write('<rect width="100%" height="100%" fill="white"/>\n')
        f.write("\n".join(svg_paths))
        f.write("\n</svg>")

os.makedirs("output_test", exist_ok=True)
process_file("test_files/circle1.png", "output_test/circle1_potrace.svg", hatch=False)
process_file("test_files/Yin-Yang-Logo.png", "output_test/Yin-Yang_potrace_hatch.svg", hatch=True)
process_file("test_files/GI.png", "output_test/GI_potrace.svg", hatch=False)
