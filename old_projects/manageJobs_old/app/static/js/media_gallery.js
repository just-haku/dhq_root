/**
 * Media Gallery Logic
 * Requires window.GALLERY_CONFIG to be defined in the HTML.
 */

// Initialize Variables from Config
let allFileIds = window.GALLERY_CONFIG.allFileIds || [];
let currentIndex = -1;
let currentMediaId = null;
let currentVideoEl = null;
let pendingDeleteId = null;

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
    // Auto-clear upload form listener
    const uploadModal = document.getElementById('uploadModal');
    if (uploadModal) {
        uploadModal.addEventListener('hidden.bs.modal', function () {
            document.getElementById('fileInput').value = '';
            document.getElementById('uploadCaption').value = '';
            // Reset group selection
            const select = document.getElementById('uploadGroup');
            if (window.GALLERY_CONFIG.currentGroupId) {
                select.value = window.GALLERY_CONFIG.currentGroupId;
            } else {
                select.value = "";
            }
        });
    }

    // Keydown listeners
    document.addEventListener('keydown', (e) => {
        const lb = document.getElementById('lightbox');
        if (!lb || lb.style.display === 'none') return;
        
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft') navMedia(-1);
        if (e.key === 'ArrowRight') navMedia(1);
        if (e.key === 'Enter' && document.activeElement === document.getElementById('lb-comment-input')) postComment();
    });

    // Delete confirmation listener
    const btnConfirmDelete = document.getElementById('btnConfirmDelete');
    if (btnConfirmDelete) {
        btnConfirmDelete.addEventListener('click', async () => {
            if(!pendingDeleteId) return;
            btnConfirmDelete.disabled = true; 
            btnConfirmDelete.innerHTML = 'Deleting...';
            
            await fetch(`/media/delete_group/${pendingDeleteId}`, {
                method: 'POST',
                headers: getCommonHeaders()
            });
            location.reload();
        });
    }
});

// --- HELPER: GET CSRF TOKEN ---
function getCsrfToken() {
    // Check Meta Tags first (standard Flask-WTF)
    let token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
                document.querySelector('meta[name="csrf_token"]')?.getAttribute('content');
    
    if (token) return token;

    // Check Input Fields (fallback if meta missing but form rendered)
    const input = document.querySelector('input[name="csrf_token"]') || 
                  document.querySelector('input[name="csrf-token"]') ||
                  document.getElementById('csrf_token');
                  
    if (input) return input.value;
    
    console.warn("Could not find CSRF token in DOM");
    return null;
}

// --- HELPER: GET CSRF HEADERS ---
function getCommonHeaders(extras = {}) {
    const headers = { 'X-Requested-With': 'XMLHttpRequest', ...extras };
    const csrfToken = getCsrfToken();
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
    } else {
        console.warn("CSRF Token not found in DOM. Requests may fail.");
    }
    return headers;
}

// --- CUSTOM DELETE MODAL ---
function confirmDeleteGroup(id, name) {
    pendingDeleteId = id;
    document.getElementById('delConfirmMsg').textContent = `Delete "${name}"? Files inside will be removed.`;
    new bootstrap.Modal(document.getElementById('deleteConfirmModal')).show();
}

// --- LIGHTBOX LOGIC ---
async function openLightbox(id) {
    currentMediaId = id;
    currentIndex = allFileIds.indexOf(id);
    document.getElementById('lightbox').style.display = 'flex';
    await loadDetails(id);
}

function closeLightbox() {
    document.getElementById('lightbox').style.display = 'none';
    const container = document.getElementById('lightbox-media-container');
    container.innerHTML = '';
    currentVideoEl = null;
    refreshGridCard(currentMediaId);
}

function navMedia(dir) {
    let newIndex = currentIndex + dir;
    if(newIndex < 0) newIndex = allFileIds.length - 1;
    if(newIndex >= allFileIds.length) newIndex = 0;
    openLightbox(allFileIds[newIndex]);
}

async function loadDetails(id) {
    const container = document.getElementById('lightbox-media-container');
    container.innerHTML = '<div class="spinner-border text-primary"></div>';
    document.getElementById('video-controls').classList.add('d-none');

    const res = await fetch(`/media/details/${id}`);
    const data = await res.json();
    const placeholder = window.GALLERY_CONFIG.placeholderUrl;

    // DYNAMIC LOAD
    // Use data.url provided by backend which now points to hashed file URL
    if(data.filename.match(/\.(mp4|avi|mov|mkv)$/i)) {
        // iOS FIX: Added playsinline and webkit-playsinline attributes
        container.innerHTML = `<video id="active-video" src="${data.url}" controls autoplay playsinline webkit-playsinline class="w-100 h-100" style="object-fit:contain"></video>`;
        const vid = document.getElementById('active-video');
        vid.volume = 0.2;
        currentVideoEl = vid;
        document.getElementById('video-controls').classList.remove('d-none');
    } else {
        container.innerHTML = `<img src="${data.url}" class="w-100 h-100" style="object-fit:contain" onerror="this.src='${placeholder}'">`;
    }

    document.getElementById('lb-filename').innerText = data.filename;
    document.getElementById('lb-uploader').innerText = data.uploader;
    document.getElementById('lb-date').innerText = data.upload_date;
    document.getElementById('lb-caption').innerText = data.caption;
    
    const avatarSrc = data.uploader_avatar || `https://ui-avatars.com/api/?name=${data.uploader}`;
    const avatarEl = document.getElementById('lb-avatar');
    avatarEl.src = avatarSrc;
    avatarEl.onerror = function() { this.src = placeholder; };

    document.getElementById('opt-delete').style.display = data.can_edit ? 'block' : 'none';
    document.getElementById('opt-hide').style.display = data.can_hide ? 'block' : 'none';
    document.getElementById('openInTabBtn').href = data.url;

    renderSocials(data);
}

function renderSocials(data) {
    const placeholder = window.GALLERY_CONFIG.placeholderUrl;
    const rBox = document.getElementById('lb-reactions-display');
    rBox.innerHTML = Object.entries(data.reactions).map(([type, count]) => {
        let content = type;
        if(type === 'heart') content = '<img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/2764.png" width="16">';
        else if(type === 'like') content = '<img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f44d.png" width="16">';
        else if(type === 'haha') content = '<img src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f602.png" width="16">';
        else {
            const customImg = document.querySelector(`img[title="${type}"]`);
            if(customImg) content = `<img src="${customImg.src}" width="16">`;
        }
        return `<span class="badge bg-body-secondary text-body border d-flex align-items-center gap-1">${content} ${count}</span>`;
    }).join('');

    const cBox = document.getElementById('lb-comments');
    cBox.innerHTML = data.comments.map(c => `
        <div class="d-flex gap-2 mb-3">
            <img src="${c.avatar || 'https://ui-avatars.com/api/?name='+c.user}" class="rounded-circle mt-1 border" width="28" height="28" onerror="this.src='${placeholder}'">
            <div class="bg-body-secondary rounded p-2 flex-grow-1">
                <div class="d-flex justify-content-between"><strong class="small text-body">${c.user}</strong><span class="x-small text-muted">${c.time}</span></div>
                <div class="small text-body text-break">${c.text}</div>
            </div>
        </div>
    `).join('');
    cBox.scrollTop = cBox.scrollHeight;
}

function mediaAction(type, val) {
    if(!currentVideoEl) return;
    if(type === 'speed') currentVideoEl.playbackRate = val;
    if(type === 'rewind') currentVideoEl.currentTime -= 10;
    if(type === 'forward') currentVideoEl.currentTime += 10;
}

// ACTIONS
async function react(type) { 
    await fetch(`/media/react/${currentMediaId}`, { 
        method: 'POST', 
        headers: getCommonHeaders({'Content-Type': 'application/x-www-form-urlencoded'}), 
        body: `type=${type}` 
    }); 
    const res = await fetch(`/media/details/${currentMediaId}`); 
    renderSocials(await res.json()); 
}

async function removeMyReactions() { 
    await fetch(`/media/clear_reactions/${currentMediaId}`, {
        method: 'POST',
        headers: getCommonHeaders()
    }); 
    const res = await fetch(`/media/details/${currentMediaId}`); 
    renderSocials(await res.json()); 
}

async function postComment() { 
    const val = document.getElementById('lb-comment-input').value; 
    if(!val) return; 
    await fetch(`/media/comment/${currentMediaId}`, { 
        method: 'POST', 
        headers: getCommonHeaders({'Content-Type': 'application/x-www-form-urlencoded'}), 
        body: `content=${encodeURIComponent(val)}` 
    }); 
    document.getElementById('lb-comment-input').value = ''; 
    const res = await fetch(`/media/details/${currentMediaId}`); 
    renderSocials(await res.json()); 
}

async function refreshGridCard(id) { const res = await fetch(`/media/details/${id}`); const data = await res.json(); const total = Object.values(data.reactions).reduce((a,b)=>a+b,0); document.getElementById(`card-react-${id}`).innerHTML = `<i class="fas fa-heart text-danger"></i> ${total}`; document.getElementById(`card-comment-${id}`).innerHTML = `<i class="fas fa-comment"></i> ${data.comments.length}`; }

// --- STALL GUARD UPLOAD LOGIC ---
async function startUpload() {
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    const g = document.getElementById('uploadGroup').value;
    const c = document.getElementById('uploadCaption').value;
    
    if(files.length === 0) return;

    bootstrap.Modal.getInstance(document.getElementById('uploadModal')).hide();
    const widget = document.getElementById('upload-progress-widget');
    const bar = document.getElementById('uploadBar');
    const percent = document.getElementById('uploadPercent');
    const label = document.getElementById('uploadStatusText'); 
    widget.style.display = 'block';

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        let fName = file.name;
        if (fName.length > 25) {
            fName = fName.substring(0, 12) + "..." + fName.substring(fName.length - 8);
        }
        
        label.innerText = `Uploading ${i + 1}/${files.length}: ${fName}`;
        bar.style.width = '0%'; percent.innerText = '0%';
        bar.className = 'progress-bar bg-primary progress-bar-striped progress-bar-animated';
        
        try {
            await uploadSingleFile(file, g, c, (p) => {
                bar.style.width = p + '%';
                percent.innerText = p + '%';
            });
        } catch (err) {
            console.error(err);
            bar.className = 'progress-bar bg-danger';
            label.innerText = "Stalled/Failed";
            await fetch('/dashboard/add_notification', {
                method: 'POST',
                headers: getCommonHeaders({'Content-Type': 'application/json'}),
                body: JSON.stringify({
                    type: 'danger', 
                    title: 'Upload Failed', 
                    content: `Upload stalled/failed for ${file.name}. Aborted.`
                })
            });
        }
    }
    
    setTimeout(() => location.reload(), 1000);
}

function uploadSingleFile(file, group, caption, onProgress) {
    return new Promise((resolve, reject) => {
        const fd = new FormData();
        fd.append('file', file);
        fd.append('group_id', group);
        fd.append('caption', caption);
        
        // Add CSRF to body as well for robustness
        const csrfToken = getCsrfToken();
        if(csrfToken) fd.append('csrf_token', csrfToken);

        const xhr = new XMLHttpRequest();
        let lastLoaded = 0;
        let lastTime = Date.now();
        
        const stallCheck = setInterval(() => {
            const now = Date.now();
            if (now - lastTime > 15000 && lastLoaded > 0 && lastLoaded < file.size) {
                xhr.abort();
                clearInterval(stallCheck);
                reject("Stall detected");
            }
        }, 5000);

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                if (e.loaded > lastLoaded) {
                    lastLoaded = e.loaded;
                    lastTime = Date.now();
                }
                onProgress(Math.round((e.loaded / e.total) * 100));
            }
        });

        xhr.onload = () => {
            clearInterval(stallCheck);
            if (xhr.status === 200) resolve();
            else reject("HTTP Error");
        };

        xhr.onerror = () => {
            clearInterval(stallCheck);
            reject("Network Error");
        };
        
        xhr.onabort = () => {
            clearInterval(stallCheck);
            reject("Aborted");
        }

        xhr.open('POST', '/media/upload');
        // Add CSRF Header
        if (csrfToken) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        }
        xhr.send(fd);
    });
}

async function createGroup() { 
    const nameInput = document.getElementById('groupName');
    const name = nameInput.value.trim(); 
    if(!name) { alert("Please enter a name."); return; }
    
    const avatarInput = document.getElementById('groupAvatar');
    const hasFile = avatarInput.files && avatarInput.files.length > 0;

    let options = {
        method: 'POST',
        headers: getCommonHeaders()
    };

    if (hasFile) {
        // Use FormData for file upload
        const fd = new FormData(); 
        fd.append('name', name);
        fd.append('avatar', avatarInput.files[0]);
        
        // Add CSRF to body as well for robustness
        const csrfToken = getCsrfToken();
        if(csrfToken) fd.append('csrf_token', csrfToken);
        
        options.body = fd;
        // NOTE: Content-Type is set automatically for FormData
    } else {
        // Use JSON for text-only (often more reliable with CSRF headers)
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify({ name: name });
    }
    
    const res = await fetch('/media/create_group', options); 
    
    if (res.ok) {
        location.reload(); 
    } else {
        let errMsg = "Failed to create group";
        try {
            const data = await res.json();
            if(data.error) errMsg = data.error;
        } catch(e) {
            errMsg = "Server Error (400). Likely missing CSRF Token.";
            console.error("Non-JSON error response", res);
        }
        alert(errMsg);
    }
}

async function uploadCustomReact() { 
    const f = document.getElementById('crFile').files[0]; 
    const n = document.getElementById('crName').value; 
    if(!f || !n) return; 
    const fd = new FormData(); 
    fd.append('file', f); 
    fd.append('name', n); 

    // Add CSRF to body
    const csrfToken = getCsrfToken();
    if(csrfToken) fd.append('csrf_token', csrfToken);

    await fetch('/media/add_custom_reaction', {
        method:'POST', 
        body:fd,
        headers: getCommonHeaders()
    }); 
    location.reload(); 
}

async function manageFile(action) { 
    if(action === 'delete' && !confirm("Delete?")) return; 
    let val = null; 
    if(action === 'rename') val = prompt("New Name:"); 
    if(action === 'caption') val = prompt("New Caption:"); 
    
    const res = await fetch('/media/manage_file', { 
        method: 'POST', 
        headers: getCommonHeaders({'Content-Type': 'application/json'}), 
        body: JSON.stringify({action, media_id: currentMediaId, value: val}) 
    }); 
    if(res.ok) { 
        if(action==='delete') { closeLightbox(); location.reload(); } 
        else { loadDetails(currentMediaId); } 
    } 
}

async function savePost() { 
    await fetch('/media/save_post', { 
        method: 'POST', 
        headers: getCommonHeaders({'Content-Type': 'application/json'}), 
        body: JSON.stringify({media_id: currentMediaId}) 
    }); 
    alert("Saved!"); 
}

async function reportPost() { 
    if(!confirm("Report this post?")) return; 
    await fetch('/media/manage_file', { 
        method: 'POST', 
        headers: getCommonHeaders({'Content-Type': 'application/json'}), 
        body: JSON.stringify({action: 'report', media_id: currentMediaId}) 
    }); 
    alert("Reported to Admins."); 
}