import os
import tempfile
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from pydantic import BaseModel

from app.api.auth import get_current_user
from app.models.user import User
from app.models.drive import DriveFile

import cv2
import numpy as np
import fitz  # PyMuPDF
from svgpathtools import svg2paths, Path, Line, Arc, CubicBezier, QuadraticBezier
import math
import re
import potrace

router = APIRouter()

# ──────────────────────────────────────────────────────────────────────────── #
#  Subpath splitting helper                                                     #
# ──────────────────────────────────────────────────────────────────────────── #

GAP_TOL = 0.01   # SVG units; gap larger than this = new subpath

def _split_subpaths(path):
    """
    Split a (possibly compound) svgpathtools Path into a list of lists of
    continuous segments. A 'gap' occurs when the start of a segment does
    not coincide with the end of the previous segment within GAP_TOL.
    """
    if len(path) == 0:
        return []
    subpaths = []
    current  = []
    for seg in path:
        if current:
            prev = current[-1].end
            gap  = (abs(seg.start.real - prev.real) > GAP_TOL or
                    abs(seg.start.imag - prev.imag) > GAP_TOL)
            if gap:
                subpaths.append(current)
                current = []
        current.append(seg)
    if current:
        subpaths.append(current)
    return subpaths


# ──────────────────────────────────────────────────────────────────────────── #
#  Tracing Helpers                                                              #
# ──────────────────────────────────────────────────────────────────────────── #

def generate_hatch_lines(mask, spacing=5.0, angle=45.0, pad=0):
    """
    Casts parallel rays across the image and generates ONE-DIRECTIONAL line segments.
    Subtracts the 'pad' border to keep coordinates aligned with the original image.
    """
    h, w = mask.shape
    angle_rad = math.radians(angle)
    
    nx, ny = math.cos(angle_rad), math.sin(angle_rad)
    dx, dy = -math.sin(angle_rad), math.cos(angle_rad)
    
    corners = [(0,0), (w,0), (w,h), (0,h)]
    projs = [cx*nx + cy*ny for cx, cy in corners]
    min_p, max_p = min(projs), max(projs)
    
    hatch_d = ""
    node_count = 0
    
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
                            node_count += 2
                
                if in_segment:
                    seg_end = (x_coords[-1], y_coords[-1])
                    hatch_d += f"M {seg_start[0]-pad:.3f},{seg_start[1]-pad:.3f} L {seg_end[0]-pad:.3f},{seg_end[1]-pad:.3f} "
                    node_count += 2
                    
        p += spacing
        
    return hatch_d, node_count


def optimize_path_to_circle(pts_array, tolerance=0.05):
    """
    Analyzes a dense array of vector points. 
    If they mathematically form a perfect circle, returns (cx, cy, r).
    """
    if len(pts_array) < 10: 
        return None
        
    x_min, y_min = np.min(pts_array, axis=0)
    x_max, y_max = np.max(pts_array, axis=0)
    w, h = x_max - x_min, y_max - y_min
    
    if w == 0 or h == 0 or abs(w - h) / max(w, h) > 0.15:
        return None
        
    (cx, cy), radius = cv2.minEnclosingCircle(pts_array)
    if radius < 1.0: 
        return None
        
    distances = np.sqrt((pts_array[:, 0] - cx)**2 + (pts_array[:, 1] - cy)**2)
    mean_r = np.mean(distances)
    if mean_r == 0: 
        return None
        
    if (np.std(distances) / mean_r) < tolerance:
        return cx, cy, mean_r
        
    return None


def get_skeleton(img):
    """
    Morphological thinning (skeletonization) to extract the 1-pixel centerline of strokes.
    """
    skel = np.zeros(img.shape, np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    img_work = img.copy()
    while True:
        eroded = cv2.erode(img_work, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(img_work, temp)
        skel = cv2.bitwise_or(skel, temp)
        img_work = eroded.copy()
        if cv2.countNonZero(img_work) == 0:
            break
    return skel


def validate_and_clean_gcode(gcode_lines):
    """
    Validate and clean G-code to prevent malformed output for pen plotting.
    Removes duplicate consecutive points and ensures proper Z movements.
    """
    cleaned_lines = []
    last_pos = None
    last_z = None
    
    for line in gcode_lines:
        line = line.strip()
        if not line or line.startswith(';'):
            cleaned_lines.append(line)
            continue
            
        # Parse coordinates
        x_match = re.search(r'X([-\d.]+)', line)
        y_match = re.search(r'Y([-\d.]+)', line)
        z_match = re.search(r'Z([-\d.]+)', line)
        
        current_pos = None
        if x_match and y_match:
            current_pos = (float(x_match.group(1)), float(y_match.group(1)))
            
        current_z = None
        if z_match:
            current_z = float(z_match.group(1))
        
        # Skip duplicate movements (except Z changes)
        if current_pos and last_pos and current_pos == last_pos:
            if not current_z or current_z == last_z:
                continue
                
        cleaned_lines.append(line)
        
        if current_pos:
            last_pos = current_pos
        if current_z is not None:
            last_z = current_z
            
    return cleaned_lines

# ──────────────────────────────────────────────────────────────────────────── #
#  Completion Time Estimation                                                   #
# ──────────────────────────────────────────────────────────────────────────── #

def estimate_plotting_time(gcode_lines, feed_rate=2000, travel_rate=4000):
    """
    Estimate completion time of plotting process in seconds.
    Returns total_time_seconds, drawing_time_seconds, travel_time_seconds
    """
    drawing_time = 0.0
    travel_time = 0.0
    current_pos = [0.0, 0.0]
    z_up = True
    total_distance = 0.0
    
    # Convert feed rates from mm/min to mm/sec for calculation
    feed_rate_sec = feed_rate / 60.0
    travel_rate_sec = travel_rate / 60.0
    
    for line in gcode_lines:
        line = line.strip()
        if not line or line.startswith(';'):
            continue
            
        # Extract coordinates from G-code commands
        if line.startswith('G1') or line.startswith('G0'):
            # Parse X and Y coordinates (they might be on separate lines)
            x_match = re.search(r'X([-\d.]+)', line)
            y_match = re.search(r'Y([-\d.]+)', line)
            z_match = re.search(r'Z([-\d.]+)', line)
            
            new_x = current_pos[0]
            new_y = current_pos[1]
            moved = False
            
            if x_match:
                new_x = float(x_match.group(1))
                moved = True
            if y_match:
                new_y = float(y_match.group(1))
                moved = True
                
            # Check for Z coordinate on this line OR if we have a Z state from previous lines
            if z_match:
                z_val = float(z_match.group(1))
                z_up = z_val > 0
                print(f"DEBUG: Z found: {z_val}, z_up: {z_up}")  # Debug Z state
                
            if moved:
                # Calculate distance from previous position
                distance = math.hypot(new_x - current_pos[0], new_y - current_pos[1])
                total_distance += distance
                
                # Determine if this is a drawing move or travel move
                # Default to drawing for G1 moves unless we know pen is up
                is_drawing = line.startswith('G1') and not z_up
                
                if is_drawing:
                    # Drawing move
                    drawing_time += distance / feed_rate_sec if feed_rate_sec > 0 else 0
                    print(f"DEBUG: Drawing move: distance={distance:.3f}, time={distance/feed_rate_sec:.3f}")  # Debug
                else:
                    # Travel move
                    travel_time += distance / travel_rate_sec if travel_rate_sec > 0 else 0
                    print(f"DEBUG: Travel move: distance={distance:.3f}, time={distance/travel_rate_sec:.3f}")  # Debug
                    
                current_pos = [new_x, new_y]
    
    total_time = drawing_time + travel_time
    
    # Add some overhead time for pen up/down movements and acceleration
    overhead_time = len(gcode_lines) * 0.01  # 0.01 seconds per line for overhead
    total_time += overhead_time
    
    return total_time, drawing_time, travel_time

# ──────────────────────────────────────────────────────────────────────────── #
#  Request models                                                               #
# ──────────────────────────────────────────────────────────────────────────── #

class PageData(BaseModel):
    svg: str
    width_mm: Optional[float] = None
    height_mm: Optional[float] = None

class GenerateRequest(BaseModel):
    pages: List[PageData]
    output_mode: str = "Lines"     # "Lines" (G1 only) or "Curves" (G2/G3 future)
    feed_rate: int = 2000
    travel_rate: int = 4000
    x_max: float = 300.0
    y_max: float = 300.0
    units: str = "mm"
    origin: str = "bottom-left"   # "bottom-left" | "top-left"
    scaling: str = "fit"           # "fit" | "actual"
    z_up: float = 5.0
    z_down: float = -1.0
    dwell_time: int = 0
    optimize_paths: bool = True
    simplify_tolerance: float = 0.5   # mm, segment density
    curve_resolution: int = 10        # minimum steps per bezier
    use_arcs: bool = False            # Convert G1 sequences to G2/G3 where possible

class SaveGcodeRequest(BaseModel):
    filename: str
    gcode_data: str


@router.post("/gcode/preview")
async def preview_gcode(
    file: UploadFile = File(...),
    threshold: int = Form(127),
    blur: int = Form(0),
    despeckle: int = Form(2),
    detail_level: int = Form(5),
    smoothing: int = Form(1),
    epsilon_val: float = Form(0.1), # Explicit epsilon override from frontend UI
    color_mode: str = Form("bw"),
    invert_colors: bool = Form(False),
    trace_mode: str = Form("Outline Only"),
    output_mode: str = Form("Lines"),
    hatch: bool = Form(False),
    hatch_spacing: float = Form(5.0),
    hatch_angle: float = Form(45.0),
    current_user: User = Depends(get_current_user)
):
    """
    Accept an image/pdf, apply CV2 filters, trace to SVG, return JSON list of pages.
    """
    content = await file.read()
    ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    def _process_image(img_raw, width_mm=None, height_mm=None, small_text_bboxes=None):
        if img_raw.ndim == 2:
            img = cv2.cvtColor(img_raw, cv2.COLOR_GRAY2BGR)
        elif img_raw.shape[2] == 4:
            bgr = img_raw[:, :, :3].astype(np.float32)
            alpha = img_raw[:, :, 3:4].astype(np.float32) / 255.0
            white_bg = np.ones_like(bgr, dtype=np.float32) * 255.0
            img = (bgr * alpha + white_bg * (1.0 - alpha)).astype(np.uint8)
        else:
            img = img_raw
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        orig_h, orig_w = gray.shape
        
        pad = 20
        gray = cv2.copyMakeBorder(gray, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=255)
        
        if threshold == 127:
            _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        else:
            _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
            
        if invert_colors:
            mask = cv2.bitwise_not(mask)

        if trace_mode == "Outline Only":
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            mask = np.zeros_like(mask)
            cv2.drawContours(mask, contours, -1, 255, thickness=cv2.FILLED)

        svg_paths = []
        node_count_total = 0

        thick_mask = mask.copy()
        thin_mask = None

        if small_text_bboxes and len(small_text_bboxes) > 0:
            small_mask = np.zeros_like(mask)
            for (x0, y0, x1, y1) in small_text_bboxes:
                ix0, iy0 = int(x0) + pad - 2, int(y0) + pad - 2
                ix1, iy1 = int(x1) + pad + 2, int(y1) + pad + 2
                cv2.rectangle(small_mask, (ix0, iy0), (ix1, iy1), 255, -1)
                
            thin_mask = cv2.bitwise_and(mask, small_mask)
            thick_mask = cv2.bitwise_and(mask, cv2.bitwise_not(small_mask))
            
            contours, _ = cv2.findContours(thin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w <= 10 and h <= 10:
                    cx, cy = x + w/2.0, y + h/2.0
                    r = 0.8
                    d = f"M {cx-pad-r:.3f},{cy-pad:.3f} A {r:.3f},{r:.3f} 0 0,0 {cx-pad+r:.3f},{cy-pad:.3f} A {r:.3f},{r:.3f} 0 0,0 {cx-pad-r:.3f},{cy-pad:.3f} Z"
                    svg_paths.append(f'<path d="{d}" fill="none" stroke="black" stroke-width="1"/>')
                    node_count_total += 2
                    cv2.drawContours(thin_mask, [cnt], -1, 0, -1)
                    
            thin_mask = get_skeleton(thin_mask)
            thin_mask = cv2.dilate(thin_mask, cv2.getStructuringElement(cv2.MORPH_CROSS, (2,2)))
            thin_mask = cv2.GaussianBlur(thin_mask, (3, 3), 0)
            _, thin_mask = cv2.threshold(thin_mask, 50, 255, cv2.THRESH_BINARY)

        def append_paths_from_mask(current_mask, is_centerline=False):
            nonlocal node_count_total, svg_paths
            if current_mask is None or cv2.countNonZero(current_mask) == 0:
                return
                
            bitmap = potrace.Bitmap(np.ascontiguousarray(current_mask > 0))
            
            t_size = 0 if is_centerline else 2
            a_max = 1.34 if is_centerline else 1.0 # alphamax defaults to 1.0
            path = bitmap.trace(turdsize=t_size, alphamax=a_max, opticurve=1, opttolerance=0.2)
            
            for curve in path:
                sampled_pts = []
                current_pt = curve.start_point
                sampled_pts.append((current_pt[0], current_pt[1]))
                
                for segment in curve:
                    if segment.is_corner:
                        sampled_pts.append((segment.c[0], segment.c[1]))
                        sampled_pts.append((segment.end_point[0], segment.end_point[1]))
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
                        
                circle_params = None
                if not is_centerline:
                    pts_array = np.array(sampled_pts, dtype=np.float32)
                    circle_params = optimize_path_to_circle(pts_array, tolerance=0.05)
                
                if circle_params:
                    cx, cy, r = circle_params
                    d = f"M {cx-pad-r:.3f},{cy-pad:.3f} A {r:.3f},{r:.3f} 0 0,0 {cx-pad+r:.3f},{cy-pad:.3f} A {r:.3f},{r:.3f} 0 0,0 {cx-pad-r:.3f},{cy-pad:.3f} Z"
                    node_count_total += 2
                    svg_paths.append(f'<path d="{d}" fill="none" stroke="black" stroke-width="1"/>')
                else:
                    start = curve.start_point
                    d = f"M {start[0]-pad:.3f},{start[1]-pad:.3f} "
                    for segment in curve:
                        if segment.is_corner:
                            c = segment.c
                            end = segment.end_point
                            d += f"L {c[0]-pad:.3f},{c[1]-pad:.3f} L {end[0]-pad:.3f},{end[1]-pad:.3f} "
                            node_count_total += 2
                        else:
                            c1 = segment.c1
                            c2 = segment.c2
                            end = segment.end_point
                            d += f"C {c1[0]-pad:.3f},{c1[1]-pad:.3f} {c2[0]-pad:.3f},{c2[1]-pad:.3f} {end[0]-pad:.3f},{end[1]-pad:.3f} "
                            node_count_total += 1
                    d += "Z"
                    color = "blue" if is_centerline else "black"
                    svg_paths.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1"/>')

        append_paths_from_mask(thick_mask, is_centerline=False)
        if thin_mask is not None:
            append_paths_from_mask(thin_mask, is_centerline=True)

        if hatch:
            hatch_d, h_nodes = generate_hatch_lines(thick_mask, spacing=hatch_spacing, angle=hatch_angle, pad=pad)
            if hatch_d:
                svg_paths.append(f'<path d="{hatch_d}" fill="none" stroke="#3b82f6" stroke-width="0.5"/>')
                node_count_total += h_nodes

        svg_out = f'<svg viewBox="0 0 {orig_w} {orig_h}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">\n'
        svg_out += f'  <rect width="{orig_w}" height="{orig_h}" fill="white"/>\n'
        svg_out += "\n".join(svg_paths)
        svg_out += '\n</svg>'
        
        path_count = len(svg_paths)
        file_size = len(svg_out.encode('utf-8'))
        
        stats = {
            "paths": path_count,
            "nodes": node_count_total,
            "size_kb": round(file_size / 1024, 1),
            "width": orig_w,
            "height": orig_h
        }
        if width_mm and height_mm:
            stats["width_mm"] = round(width_mm, 2)
            stats["height_mm"] = round(height_mm, 2)
            
        return {"svg": svg_out, "stats": stats}

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, f"input.{ext}")
        with open(input_path, "wb") as f:
            f.write(content)
            
        pages_out = []
        if ext == 'svg':
            with open(input_path, "r", encoding="utf-8") as f:
                pages_out.append({"svg": f.read(), "stats": {}})
        elif ext == 'pdf':
            doc = fitz.open(input_path)
            if len(doc) == 0:
                raise HTTPException(status_code=400, detail="Empty PDF")
            for page in doc:
                # PDF FONT DATA EXTRACTION for skeletonization
                small_text_bboxes = []
                try:
                    text_data = page.get_text("dict")
                    scale_factor = 150.0 / 72.0 
                    for block in text_data.get("blocks", []):
                        if block.get("type") == 0:
                            for line in block.get("lines", []):
                                for span in line.get("spans", []):
                                    if span.get("size", 100) < 16.0:
                                        bbox = span.get("bbox")
                                        scaled_bbox = (
                                            bbox[0] * scale_factor,
                                            bbox[1] * scale_factor,
                                            bbox[2] * scale_factor,
                                            bbox[3] * scale_factor
                                        )
                                        small_text_bboxes.append(scaled_bbox)
                except:
                    pass

                processed_path = os.path.join(tmpdir, f"processed_{page.number}.png")
                pix = page.get_pixmap(dpi=150)
                pix.save(processed_path)
                img_raw = cv2.imread(processed_path, cv2.IMREAD_UNCHANGED)
                
                rect = page.rect
                width_mm = rect.width * 25.4 / 72.0
                height_mm = rect.height * 25.4 / 72.0
                
                pages_out.append(_process_image(img_raw, width_mm, height_mm, small_text_bboxes=small_text_bboxes))
        else:
            img_raw = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
            if img_raw is None:
                raise HTTPException(status_code=400, detail="Invalid image format")
            pages_out.append(_process_image(img_raw))
            
        return {"pages": pages_out}

# ──────────────────────────────────────────────────────────────────────────── #
#  Optimization Helpers                                                         #
# ──────────────────────────────────────────────────────────────────────────── #

def _optimize_subpaths(subpaths, get_xy_func, start_pos=(0, 0), merge_tol=0.1):
    """
    Greedy Nearest Neighbor optimization for subpaths with merging logic.
    Considers both start and end points to allow path reversal.
    Merges subpaths if the distance between them is less than merge_tol.
    """
    if not subpaths:
        return []
        
    # Pre-calculate start and end points for all subpaths
    path_data = []
    for sp in subpaths:
        p_start = get_xy_func(sp[0].start)
        p_end = get_xy_func(sp[-1].end)
        path_data.append({
            'sp': sp,
            'start': p_start,
            'end': p_end
        })
        
    optimized = []
    remaining = path_data
    curr = start_pos
    
    merge_tol_sq = merge_tol ** 2
    
    while remaining:
        best_d = float('inf')
        best_idx = -1
        should_reverse = False
        
        for i, data in enumerate(remaining):
            # Dist to start
            d_s = (data['start'][0]-curr[0])**2 + (data['start'][1]-curr[1])**2
            if d_s < best_d:
                best_d = d_s
                best_idx = i
                should_reverse = False
                
            # Dist to end (reverse)
            d_e = (data['end'][0]-curr[0])**2 + (data['end'][1]-curr[1])**2
            if d_e < best_d:
                best_d = d_e
                best_idx = i
                should_reverse = True
        
        selected = remaining.pop(best_idx)
        
        # Check if we should merge with previous path
        if best_d < merge_tol_sq and optimized:
            # Merge: just append points to the previous path
            prev_path, prev_reversed = optimized[-1]
            # Since we can't easily merge raw svgpathtools segments without re-calculating,
            # we'll return a structure that tells the generator to keep the pen down.
            optimized.append((selected['sp'], should_reverse, True)) # True = is_merged
        else:
            optimized.append((selected['sp'], should_reverse, False))
            
        curr = selected['start'] if should_reverse else selected['end']
        
    return optimized

@router.post("/gcode/generate")
async def generate_gcode(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Parse SVG pages → subpaths → compress to Arcs → generate G-code list.
    """
    
    def _arc_direction(p1, p2, p3):
        """Use cross product to find turning direction in machine cartesian space. >0 is CCW (G3), <0 is CW (G2)"""
        cross = (p2[0] - p1[0]) * (p3[1] - p2[1]) - (p2[1] - p1[1]) * (p3[0] - p2[0])
        return "G3" if cross > 0 else "G2"

    def contour_to_gcode_commands(approx_contour, use_arcs, origin_mode):
        points = [(float(pt[0]), float(pt[1])) for pt in approx_contour]
        if not points: 
            return []
        
        commands = []
        i = 0
        n = len(points)
        tol = 0.1  # Tighter tolerance for pen plotting accuracy
        
        while i < n - 1:
            if not use_arcs:
                commands.append(f"G1 X{points[i+1][0]:.3f} Y{points[i+1][1]:.3f}")
                i += 1
                continue
                
            best_arc = None
            best_k = 0
            
            # More conservative lookahead for pen plotting
            max_lookahead = min(20, n - i)
            for k in range(max_lookahead - 1, 2, -1):
                segment = points[i : i+k+1]
                
                dist_span = math.hypot(segment[-1][0] - segment[0][0], segment[-1][1] - segment[0][1])
                if dist_span < 0.3:  # Smaller minimum for pen plotters
                    continue
                    
                x = np.array([p[0] for p in segment])
                y = np.array([p[1] for p in segment])
                A = np.c_[x, y, np.ones(len(x))]
                b = x**2 + y**2
                
                try:
                    c, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
                    cx, cy = c[0]/2, c[1]/2
                    r = np.sqrt(c[2] + cx**2 + cy**2)
                except Exception:
                    continue
                    
                if r > 1000.0 or r < 0.05:  # More conservative radius limits
                    continue
                    
                distances = np.sqrt((x - cx)**2 + (y - cy)**2)
                max_err = np.max(np.abs(distances - r))
                
                if max_err <= tol:
                    best_arc = (segment[0], segment[len(segment)//2], segment[-1], cx, cy, r)
                    best_k = k
                    break
                    
            if best_k >= 3 and best_arc:
                p_start, p_mid, p_end, cx, cy, r = best_arc
                ix = cx - p_start[0]
                iy = cy - p_start[1] 

                cmd = _arc_direction(p_start, p_mid, p_end)
                commands.append(f"{cmd} X{p_end[0]:.3f} Y{p_end[1]:.3f} I{ix:.3f} J{iy:.3f}")
                i += best_k
            else:
                commands.append(f"G1 X{points[i+1][0]:.3f} Y{points[i+1][1]:.3f}")
                i += 1
                
        return commands

    def process_page(page: PageData):
        with tempfile.NamedTemporaryFile("w+", suffix=".svg") as f:
            f.write(page.svg)
            f.flush()
            paths, attributes = svg2paths(f.name)
            
        import xml.etree.ElementTree as ET
        root = ET.fromstring(page.svg)
        vb = root.attrib.get('viewBox', '').split()
        if len(vb) == 4:
            svg_w, svg_h = float(vb[2]), float(vb[3])
        else:
            w_str = root.attrib.get('width', '100').replace('px', '')
            h_str = root.attrib.get('height', '100').replace('px', '')
            svg_w = float(re.sub(r'[^0-9.]', '', w_str))
            svg_h = float(re.sub(r'[^0-9.]', '', h_str))
            
        scale_mode = request.scaling
        x_max = request.x_max
        y_max = request.y_max
        
        if page.width_mm and page.height_mm:
            scale_mode = "actual"
            x_max = page.width_mm
            y_max = page.height_mm
            
        if scale_mode == "fit":
            scale = min(x_max / max(svg_w, 1.0), y_max / max(svg_h, 1.0))
        else:
            if page.width_mm:
                scale = page.width_mm / max(svg_w, 1.0)
            else:
                scale = 25.4 / 96.0

        def _raw(c: complex):
            x = c.real * scale
            # Respect origin request: bottom-left (CNC standard) or top-left (SVG standard)
            if request.origin == "top-left":
                y = c.imag * scale
            else:
                y = (svg_h - c.imag) * scale
            return x, y

        step_mm = max(request.simplify_tolerance, 0.1)
        min_steps = max(request.curve_resolution, 2)

        def _seg_points(seg, transform_func=None):
            if transform_func is None:
                transform_func = _raw
            # IMPROVED: Handle different segment types appropriately for pen plotting
            if isinstance(seg, Line):
                x, y = transform_func(seg.end)
                return [(x, y)]
            
            # For curves, use adaptive sampling based on segment length and curvature
            seg_len_mm = abs(seg.length()) * scale
            
            # Adaptive resolution: shorter segments need fewer points
            if seg_len_mm < 0.2:
                n = 1 # Just the end point is enough for micro-segments
            elif seg_len_mm < 1.0:
                n = max(2, min_steps // 2) 
            elif seg_len_mm < 5.0:
                n = max(5, int(seg_len_mm / (step_mm * 0.5)))
            else:
                n = max(min_steps, int(seg_len_mm / step_mm))
            
            # Cap maximum points to prevent over-sampling
            n = min(n, 50)
            
            pts = []
            for k in range(1, n + 1):
                x, y = transform_func(seg.point(k / n))
                pts.append((x, y))
            return pts

        all_subpaths = []
        all_x, all_y = [], []
        
        valid_paths = []
        for p, attr in zip(paths, attributes):
            if not p: continue
            fill = attr.get('fill', 'none').lower()
            if fill in ['white', '#ffffff', '#fff']: continue
            
            if len(p) == 4:
                xs = [s.start.real for s in p] + [s.end.real for s in p]
                ys = [s.start.imag for s in p] + [s.end.imag for s in p]
                if (max(xs)-min(xs)) >= svg_w - 5 and (max(ys)-min(ys)) >= svg_h - 5:
                    continue
            valid_paths.append(p)
            
        for path in valid_paths:
            sps = _split_subpaths(path)
            for sp in sps:
                if not sp: continue
                x0, y0 = _raw(sp[0].start)
                all_x.append(x0); all_y.append(y0)
                for seg in sp:
                    for px, py in _seg_points(seg):
                        all_x.append(px); all_y.append(py)
                all_subpaths.append(sp)
                
        if not all_x:
            return "" 
            
        off_x = min(all_x)
        off_y = min(all_y)
        
        def _xy(c: complex):
            x, y = _raw(c)
            return x - off_x, y - off_y

        gc = []
        gc.append(f"; Generated by DHQ G-code Generator")
        gc.append(f"; Scale:{scale:.4f}  Offset:({off_x:.3f},{off_y:.3f})  Subpaths:{len(all_subpaths)}")
        gc.append("G21" if request.units == "mm" else "G20")
        gc.append("G90")
        gc.append(f"G0 Z{request.z_up:.3f}")
        gc.append("G0 X0.000 Y0.000")
        gc.append(f"G0 F{request.travel_rate}")
        
        merge_mm = max(request.simplify_tolerance, 0.05)
        
        if request.optimize_paths:
            optimized_subpaths = _optimize_subpaths(all_subpaths, _xy, merge_tol=merge_mm)
        else:
            optimized_subpaths = [(sp, False, False) for sp in all_subpaths]

        for sp, is_reversed, is_merged in optimized_subpaths:
            # 1. Collect all points for the subpath
            full_sp_pts = []
            full_sp_pts.append(_xy(sp[0].start))
            for seg in sp:
                full_sp_pts.extend(_seg_points(seg, transform_func=_xy))
            
            # 2. Reverse if needed
            if is_reversed:
                full_sp_pts.reverse()
            
            # 3. Perform lead-in (travel to start, pen down) IF NOT MERGED
            sx, sy = full_sp_pts[0]
            if not is_merged:
                gc.append(f"G0 Z{request.z_up:.3f}")
                gc.append(f"G0 X{sx:.3f} Y{sy:.3f}")
                
                if request.dwell_time > 0:
                    gc.append(f"G4 P{request.dwell_time}")
                gc.append(f"G1 Z{request.z_down:.3f}")
                gc.append(f"G1 F{request.feed_rate}")
            else:
                # If merged, we are already at Z_down, but we might need a small move to the EXACT start
                # Usually best to just draw a line to the start of the next segment
                gc.append(f"G1 X{sx:.3f} Y{sy:.3f} F{request.feed_rate}")
            
            # 4. Generate drawing commands for the rest of the points
            cv2_approx = [[x, y] for x, y in full_sp_pts]
            gc.extend(contour_to_gcode_commands(cv2_approx, request.use_arcs, request.origin))
            
        gc.append(f"G0 Z{request.z_up:.3f}")
        gc.append("G0 X0.000 Y0.000")
        
        # Validate and clean G-code to prevent malformed output
        gcode_lines = gc
        cleaned_lines = validate_and_clean_gcode(gcode_lines)
        
        return "\n".join(cleaned_lines)

    results = []
    time_estimates = []
    
    for p in request.pages:
        if not p.svg:
            continue
        gcode = process_page(p)
        if gcode:
            # Estimate completion time
            gcode_lines = gcode.split('\n')
            total_time, drawing_time, travel_time = estimate_plotting_time(
                gcode_lines, request.feed_rate, request.travel_rate
            )
            
            # Debug logging
            print(f"DEBUG: G-code lines: {len(gcode_lines)}")
            print(f"DEBUG: Feed rate: {request.feed_rate} mm/min, Travel rate: {request.travel_rate} mm/min")
            print(f"DEBUG: Calculated times - Total: {total_time:.2f}s, Drawing: {drawing_time:.2f}s, Travel: {travel_time:.2f}s")
            
            results.append(gcode)
            time_estimates.append({
                "total_time_seconds": round(total_time, 2),
                "drawing_time_seconds": round(drawing_time, 2),
                "travel_time_seconds": round(travel_time, 2),
                "estimated_completion": f"{int(total_time//60)}m {int(total_time%60)}s"
            })
            
    if not results:
        raise HTTPException(status_code=400, detail="No printable paths found in any page.")
        
    return {"gcodes": results, "time_estimates": time_estimates}

@router.post("/gcode/save")
async def save_gcode(
    request: SaveGcodeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Save the generated G-code to Drive under "Generated Gcodes/".
    """
    folder = DriveFile.objects(owner=current_user, filename="Generated Gcodes", is_folder=True, folder_path="/", is_deleted=False).first()
    if not folder:
        folder = DriveFile(
            owner=current_user,
            filename="Generated Gcodes",
            stored_filename="Generated Gcodes",
            file_path="/Generated Gcodes",
            mime_type="inode/directory",
            file_size=0,
            folder_path="/",
            is_folder=True
        )
        folder.save()
        
    filename = request.filename.strip()
    if not filename.lower().endswith(('.nc', '.gcode')):
        filename += '.nc'
        
    storage_path = os.path.join(os.path.expanduser("~/storage/uploads"), f"{uuid.uuid4()}_{filename}")
    os.makedirs(os.path.dirname(storage_path), exist_ok=True)
    
    with open(storage_path, "w", encoding="utf-8") as f:
        f.write(request.gcode_data)
        
    file_size = os.path.getsize(storage_path)
    
    existing_file = DriveFile.objects(
        owner=current_user,
        folder_path="/Generated Gcodes",
        filename=filename,
        is_deleted=False
    ).first()
    
    if existing_file:
        raise HTTPException(status_code=409, detail="File with this name already exists in Generated Gcodes")
        
    new_file = DriveFile(
        owner=current_user,
        filename=filename,
        stored_filename=os.path.basename(storage_path),
        file_path=storage_path,
        mime_type="text/plain",
        file_size=file_size,
        folder_path="/Generated Gcodes"
    )
    new_file.save()
    
    return {"message": "G-code saved successfully", "file_id": str(new_file.id)}