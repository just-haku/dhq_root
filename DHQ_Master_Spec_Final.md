THE DIGITAL HEADQUARTERS (DHQ) - MASTER TECHNICAL SPECIFICATION

Codename: Project Haku
Version: 5.1 (Separated Architecture Edition)
Role: Operator (OP)

1. EXECUTIVE SUMMARY & PHILOSOPHY

Core Philosophy: "Radical Internal Transparency, Fort Knox External Privacy."
The DHQ is a centralized Enterprise Resource Planning (ERP) system designed for a multi-channel content creator. It unifies workflow management, secure asset storage, internal communication, gamified employee incentivization, and organic growth automation into a single Single Page Application (SPA).

The "Separated Concerns" Mandate:
The Frontend must utilize Vue.js 3, but explicitly rejects the standard Single File Component (SFC) compression. To maximize maintainability and strict separation of logic, styling, and structure, every UI component must be physically decomposed into three distinct files residing in a dedicated folder:

Structure: Component.html (The template)

Logic: Component.js (The reactive logic)

Presentation: Component.css (The scoped styling)
These are then aggregated via a lightweight .vue shell or build process. This ensures that a designer can work on HTML/CSS without touching the Logic, and the Developer can work on JS without breaking the Layout.

The "One Man Army" Mandate:
The system is built to be modular. While designed for a team, it includes automation (AI, "Bounty Boards," "Crooked Graph") to allow the Operator to function efficiently even without active staff.

2. TECHNOLOGY STACK

Frontend: Vue.js 3 (Vite Build Tool) using Distributed Component Architecture.

Styling: Tailwind CSS (Utility) + Custom CSS (Component specific).

Backend: Python FastAPI (Async support, Auto-docs, High Performance).

Database: MongoDB (Main Data Storage).

ODM: MongoEngine (Strict Python Schemas).

Cache/Queue: Redis (Session management, Celery Broker).

Background Tasks: Celery (Email, Transcoding, Nuke execution, Ordering).

Real-time: Socket.IO (Chat, Notifications, Order Updates).

Security: AES-256-GCM (File Encryption), Bcrypt (Passwords), TLS 1.3.

3. SECURITY MODULE: "THE GATEKEEPER"

3.1 Entry Point Obfuscation

The Decoy: The root URL (https://domain.com/) serves a static, innocent "Lifestyle Blog" or "Under Construction" page to fool casual browsers/web crawlers.

The Real Gate: Login is only accessible via a specific route defined in .env (e.g., REAL_LOGIN_ROUTE=/staff/portal).

Hidden Registration: Registration is accessible only via REAL_REGISTER_ROUTE.

Flow: User Registers -> Account Status PENDING -> OP receives notification -> OP Accepts/Declines.

Decline Logic: If declined, the user receives a specific "Reason for Rejection" message upon their next login attempt.

3.2 Authentication & 2FA

Credentials: Username + Password (Bcrypt Hashed).

SMTP 2FA (The Bouncer):

Upon valid password entry, System generates a cryptographically secure 6-digit integer.

Code is stored in Redis (TTL: 300s).

System uses smtplib (Gmail App Password) to email the code to the user.

User inputs code -> System issues JWT (JSON Web Token).

3.3 The "Panic Button" (Lockdown Protocol)

Location: Prominent Red Button in OP Dashboard Top Bar.

Function: Emergency containment of compromise.

Actions:

Kill Sessions: Invalidates ALL active JWT signatures immediately (Forces logout for everyone).

Maintenance Mode: Sets a global Redis flag MAINTENANCE=True. Only OP credentials can bypass this.

Link Sever: Disables all public/shared file links immediately.

3.4 The "Nuke" Protocol (Total Sanitization)

Location: Exclusive OP Dashboard (Bottom Right, Guarded UI).

Purpose: Rapid, irreversible clearing of data for dev-testing or emergency server sanitization.

Constraint: ONLY OP can trigger this.

Verification:

Stage 1: Click Button -> Modal Warning "TOTAL DATA WIPE".

Stage 2: Re-enter OP Password.

Stage 3 (Prod): 8-Digit Email OTP (60s validity).

Execution Logic:

Database: Iterates through all MongoDB Collections. Drops Collaboration, ChatMessage, ShopItem, SystemLog. EXCLUDES: User collection where role == 'OP' (Preserves Operator).

File System: Executes rm -rf on:

/home/haku/storage/uploads/*

/home/haku/storage/safe/*

/home/haku/storage/temp_chat/*

Rebuild: Immediately re-instantiates the empty directory tree to prevent app crash.

4. WORKFLOW MODULE: "THE FACTORY"

4.1 Hierarchy

OP (Operator): Superuser.

AD (Admin): Channel Manager. Assigns tasks.

User: Content Creator/Editor. Receives tasks.

4.2 Collaboration Data Structure

Meta: Name, Time Created (Immutable), Collaborator Name, Collaborator Email (for future AI), Scope (App/Product), Channel, Platform.

Type Logic: Dropdown 

$$`Paid`, `Product Exchange`, `Paid+Product`$$

.

If Paid: Show Agreed Price (USD).

If Product: Show Tracking Number, Package Received (Checkbox).

Logistics: Term (Long/Short), Duration, Contract Link, Posting Date, Deadline.

Productivity: "Other Notes" (Paragraph).

4.3 The VideoUnit (Embedded List)

Each Collaboration contains multiple VideoUnits.

Status: Video Completed? (Checkbox).

Subtitles: Subtitles Needed? (Checkbox).

UI: Blur-box interface. Click timeline to add timestamp. Button to copy text at specific timestamp.

Metadata: Title (Copy Button), Caption+Hashtags (Copy Button), Tags.

QA: Edits Needed? (Checkbox + Notes field), Video Updated? (Checkbox), Approved? (Checkbox).

Posting: Platform Link (e.g., TikTok URL), Paid Proof (Image Upload).

4.4 Efficiency Features

Clipboard History Sidebar: Stores last 10 copied strings (Titles, hashtags, links) for rapid access.

Bounty Board:

OP posts urgent, unassigned tasks with high KPI rewards.

First User to click "Claim" locks the task.

Contract Generator: PDF Template mapper. Maps Agreed Price + Name to a standard PDF contract.

5. FILE SYSTEM MODULE: "THE VAULT"

5.1 Storage Architecture & Quotas

Mount Point: /home/haku/storage/

User Storage: .../uploads/{user_id}/ (Quota: 30GB - Counts toward User Cap).

Collab Storage: .../uploads/Collaboration/{Client}/{Video}/ (Counts toward Server Cap).

Secret Safe: .../safe/ (Encrypted).

Temp Chat: .../temp_chat/ (Auto-delete > 60 days, Max 500MB/file).

5.2 The Secret Safe (Encryption)

Ingest: File Stream -> AES-256-GCM Encryption -> Disk Write.

Thumbnails (The Critical Path):

Images: Decrypt to RAM -> Generate low-res thumb -> Encrypt Thumb -> Save to Disk.

Videos: Decrypt first 5MB to RAM -> FFmpeg extracts frame -> Encrypt Thumb -> Save.

Security Guarantee: Unencrypted content never touches the persistent storage (HDD/SSD).

Access:

Browser request -> Server validates ACL -> Decrypts chunk-by-chunk -> Streams to Client.

5.3 File Manager UI (Nautilus/Drive Hybrid)

Permissions: Me Only, Specific User (Searchable), Company (All logged in), Public (Hashed Link).

Versioning (Time Machine): Overwriting a file named demo.mp4 moves the old file to _archive/demo_v1.mp4.

Transcoding: 4K Uploads trigger background Celery task to generate 720p Proxy for web preview.

5.4 The "Leaker Trap" (Forensic Watermarking)

When a user views sensitive content in the browser:

Overlay: A CSS layer sits on top of the <video> or <img> tag.

Content: User's Display Name + User ID + IP Address.

Style: Repeating diagonal pattern, opacity: 0.04, pointer-events: none.

Purpose: If screen-recorded and leaked, OP can increase contrast in Photoshop to identify the leaker.

6. COMMUNICATIONS MODULE: "THE HUB"

6.1 Chat Architecture

Protocol: Socket.IO (Messages), WebRTC (Voice/Video P2P).

Structure: Discord-style Sidebar (Rooms/Channels) + Messenger-style Chat Area.

Encryption: All messages stored encrypted in MongoDB.

6.2 Features

Emotes: Custom parser :<alias>: -> Replaces with <img> from /assets/emotes/.

Ghost Mode (OP Exclusive): OP can view any channel or join any voice call without appearing in the "Online/Member" list.

Audit Logging: All "Read" actions are logged. OP knows who saw what message.

Search: Global Cmd+K search bar indexes decrypted message cache.

7. GAMIFICATION MODULE: "THE ARCADE"

7.1 The KPI Economy

Currency: KPI Points.

Sources: Completing VideoUnits, "Bounty" Tasks, Perfect Attendance.

Sinks: The Shop, The Gacha.

7.2 The Shop

Inventory:

Frames: Animated SVGs around Avatar.

Banners: Profile headers (Default is plain Blue).

Roles: Custom chat name colors.

Effects: CSS particle effects on profile.

OP Control: OP creates items, sets prices, creates "Flash Sales" (Start/End Date).

7.3 Minigames

"AFK Tycoon": Sidebar Idle game. Buy "Virtual Editors" to generate "Fake Coins" (Leaderboard score). Keeps users logged in.

"The Gacha": Slot machine using KPI. Chance to win rare Banners or "Double KPI" items.

8. AUTOMATION MODULE: "THE BOT"

8.1 "Crooked Graph" Algorithm

Objective: Simulate organic viral growth for ordered views/likes.

Formula: Order_Qty(t) = (Linear_Slope * t) + (Amplitude * sin(Frequency * t)) + (Random_Noise * Tolerance).

Logic:

User inputs Target (e.g., 5000) and Duration (e.g., 6h).

System generates a schedule map: [{time: 10:00, qty: 12}, {time: 10:10, qty: 45}...].

Celery Workers wake up at timestamps to execute API calls.

8.2 API Management

Storage: User API Keys are AES Encrypted.

Controls:

Check Balance: Real-time fetch.

Run Now: Force execution of next batch.

Skip: Bypass next batch.

9. USER PROFILE & SETTINGS

Immutable: Username.

Mutable: Display Name, Bio, Avatar (Base), Phone, Email.

Unlockable: Banner, Frames, Name Color.

Stats: KPI Wallet, KPI Lifetime, Inventory.

API: Encrypted Key input, Balance Cache.

10. DATABASE SCHEMA (MONGOENGINE)

# Detailed Schema Reference

class ShopItem(Document):
    name = StringField()
    type = StringField(choices=('Frame', 'Banner', 'Effect', 'Role'))
    price = IntField()
    asset_url = StringField()
    sale_price = IntField()
    sale_end = DateTimeField()

class User(Document):
    username = StringField(primary_key=True)
    password_hash = StringField()
    role = StringField(choices=('OP', 'AD', 'USER'))
    status = StringField(choices=('PENDING', 'ACTIVE', 'DECLINED'))
    decline_reason = StringField()
    
    # Security
    api_key_encrypted = BinaryField()
    
    # Gamification
    kpi_current = IntField(default=0)
    inventory = ListField(ReferenceField(ShopItem))
    equipped_items = DictField() # {'frame': ID, 'banner': ID}

class VideoUnit(EmbeddedDocument):
    completed = BooleanField()
    media_path = StringField()
    subtitles = ListField(DictField()) # [{'time': '00:01', 'text': 'Hi'}]
    title = StringField()
    caption = StringField()
    approved = BooleanField()
    proof_link = StringField()

class Collaboration(Document):
    name = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    collaborator_name = StringField()
    collaborator_email = StringField()
    type = StringField(choices=('Paid', 'Product', 'Mixed'))
    agreed_price = FloatField()
    tracking_number = StringField()
    package_received = BooleanField()
    
    videos = ListField(EmbeddedDocumentField(VideoUnit))
    
    meta = {'indexes': ['created_at', 'collaborator_name']}

class ChatMessage(Document):
    room = StringField()
    sender = ReferenceField(User)
    content = StringField() # Encrypted
    timestamp = DateTimeField()
    attachments = ListField(StringField()) # Paths to temp storage


11. DEPLOYMENT & ENVIRONMENT

11.1 Folder Structure

/DHQ_Root
├── backend/
│   ├── app/
│   │   ├── api/ (Routes for Auth, Files, Chat, Bot)
│   │   ├── core/ (Security, Config, Email)
│   │   ├── models/ (MongoEngine Schemas)
│   │   ├── services/ (AES, FFmpeg, Celery Tasks)
│   │   └── main.py
│   ├── .env
│   └── requirements.txt
├── frontend/ (Vue.js Distributed Architecture)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth/
│   │   │   │   └── LoginBox/            <-- Component Folder
│   │   │   │       ├── LoginBox.html    <-- Structure
│   │   │   │       ├── LoginBox.js      <-- Logic
│   │   │   │       ├── LoginBox.css     <-- Style
│   │   │   │       └── index.vue        <-- Aggregator
│   │   │   ├── Vault/
│   │   │   │   └── FileGrid/
│   │   │   │       ├── FileGrid.html
│   │   │   │       ├── FileGrid.js
│   │   │   │       └── FileGrid.css
│   │   │   └── ... (All components follow this structure)
│   │   ├── stores/ (Pinia State)
│   │   ├── views/
│   │   └── App.vue
│   └── vite.config.js
└── scripts/
    └── nuke_server.sh


11.2 The .env File

# SECURITY
SECRET_KEY=super_complex_random_string
ALGORITHM=HS256
AES_KEY=32_byte_hex_key_for_file_encryption

# ROUTES (Obfuscation)
REAL_LOGIN_ROUTE=/shadow-garden/login
REAL_REGISTER_ROUTE=/shadow-garden/apply

# DB
MONGODB_URI=mongodb://localhost:27017/dhq_main

# SMTP (Gmail)
SMTP_USER=haku.servegame.com@gmail.com
SMTP_PASS=vovmjborlkokcehd

# OP CREDENTIALS (Bootstrap)
OP_INIT_USER=haku
OP_INIT_PASS=00491E4C
