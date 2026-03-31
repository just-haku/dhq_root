import cv2
import numpy as np

def generate_hatching(img_path, gap_px=5, angle_deg=45):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None: return []
    _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours or hierarchy is None: return []

    # Filter out contours with no area to prevent crashes
    valid_indices = [i for i, cnt in enumerate(contours) if cv2.contourArea(cnt) > 2]
    
    h_y, w_x = thresh.shape
    diag_len = int(np.ceil(np.sqrt(w_x**2 + h_y**2)))
    # We want a set of lines covering the image
    # For 45 deg, m=1. y = x + c => x - y + c = 0
    # Let's just create an image with lines and bitwise_and it with the solid filled shapes
    
    # Actually, we can just draw lines on a white mask
    hatch_mask = np.zeros((h_y, w_x), dtype=np.uint8)
    
    # 45 degrees:
    for c in range(-diag_len, diag_len, gap_px):
        x1 = c
        y1 = 0
        x2 = c + h_y
        y2 = h_y
        cv2.line(hatch_mask, (x1, y1), (x2, y2), 255, 1)

    # What areas should be hatched?
    # In RETR_TREE:
    # Hierarchy: [Next, Previous, First_Child, Parent]
    # Root contours (Parent=-1) are outer boundaries of black shapes (since we inverted). 
    # Let's just use drawContours with a hierarchical rule to fill the black areas natively
    fill_mask = np.zeros((h_y, w_x), dtype=np.uint8)
    for i in range(len(contours)):
        # Check depth
        depth = 0
        parent = hierarchy[0][i][3]
        while parent != -1:
            depth += 1
            parent = hierarchy[0][parent][3]
            
        # Even depth -> Outer boundary of black, fill it with White
        # Odd depth -> Hole inside black (e.g., white paper), fill it with Black
        color = 255 if depth % 2 == 0 else 0
        cv2.drawContours(fill_mask, contours, i, color, -1)

    # Now bitwise AND the hatch and the fill
    final_hatch = cv2.bitwise_and(hatch_mask, fill_mask)
    
    # Now extract contours of the hatch lines
    # They should be straight line segments
    hatch_contours, _ = cv2.findContours(final_hatch, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    hatch_paths = []
    for cnt in hatch_contours:
        approx = cv2.approxPolyDP(cnt, 1.0, False)
        if len(approx) >= 2:
            # Connect the points
            d = f"M {approx[0][0][0]},{approx[0][0][1]} "
            for pt in approx[1:]:
                d += f"L {pt[0][0]},{pt[0][1]} "
            hatch_paths.append('<path d="' + d + '" fill="none" stroke="black" stroke-width="1"/>')
            
    return hatch_paths

paths = generate_hatching('/home/haku/projects/DHQ_Root/test_files/Yin-Yang-Logo.png')
print(f"Hatch lines generated: {len(paths)}")
with open('hatch_out.svg', 'w') as f:
    f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500">\n')
    for p in paths:
        f.write(p + '\n')
    f.write('</svg>')
