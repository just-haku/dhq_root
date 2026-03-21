import os
import hashlib
import vt
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import get_vt_client
from app.models import ScanResult
from datetime import datetime

scan_bp = Blueprint('scan', __name__, url_prefix='/scan')

def calculate_file_hash(filepath):
    """Calculates SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@scan_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            # Save temporarily
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'temp')
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            # 1. Calculate Hash
            file_hash = calculate_file_hash(filepath)

            # 2. Check VirusTotal
            client = get_vt_client()
            if not client:
                flash("VirusTotal API Key not configured.", "warning")
                # Remove temp file
                if os.path.exists(filepath): os.remove(filepath)
                return render_template('scan/index.html')

            try:
                # Try to get file report by hash
                file_obj = client.get_object(f"/files/{file_hash}")
                stats = file_obj.last_analysis_stats
                
                # Store result in MongoDB using MongoEngine
                scan = ScanResult(
                    resource_type='file',
                    resource_key=file_hash,
                    status='completed',
                    malicious_count=stats.get('malicious', 0),
                    total_engines=sum(stats.values()),
                    permalink=f"https://www.virustotal.com/gui/file/{file_hash}",
                    requested_by=current_user
                )
                scan.save()

                if stats.get('malicious', 0) > 0:
                    flash(f"DANGER: {stats['malicious']} engines detected this file as malicious!", "danger")
                else:
                    flash(f"File appears clean. Scanned by {sum(stats.values())} engines.", "success")

            except vt.APIError as e:
                # If error is NotFoundError, the file hasn't been seen by VT yet
                if "NotFoundError" in str(e):
                    flash("File hash not found in VirusTotal database. Please upload it manually to VT for analysis.", "warning")
                else:
                    flash(f"VirusTotal Error: {e}", "danger")
            except Exception as e:
                flash(f"An error occurred: {e}", "danger")
            finally:
                client.close()
                # Clean up temp file
                if os.path.exists(filepath):
                    os.remove(filepath)

            return redirect(url_for('scan.history'))

    return render_template('scan/index.html')

@scan_bp.route('/history')
@login_required
def history():
    # Fetch user's scan history using MongoEngine syntax
    scans = ScanResult.objects(requested_by=current_user).order_by('-scanned_at')
    return render_template('scan/history.html', scans=scans)