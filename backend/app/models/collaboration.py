from mongoengine import Document, EmbeddedDocument, StringField, ListField, EmbeddedDocumentField, BooleanField, FloatField, DateTimeField, DictField
from datetime import datetime

class VideoUnit(EmbeddedDocument):
    completed = BooleanField(default=False)
    media_path = StringField(max_length=500)
    subtitles_needed = BooleanField(default=False)
    subtitles = ListField()  # [{'time': '00:01', 'text': 'Hi'}]
    title = StringField(max_length=200)
    caption = StringField(max_length=2000)
    tags = ListField(StringField(max_length=50))
    
    # Missing Video properties
    script = StringField(max_length=4000)
    invitation = BooleanField(default=False)
    subtitles_text = StringField(max_length=4000)
    post_links = DictField()
    
    # QA & Payment
    paid = BooleanField(default=False)
    done = BooleanField(default=False)
    edits_needed = BooleanField(default=False)
    edits_notes = StringField(max_length=1000)
    video_updated = BooleanField(default=False)
    approved = BooleanField(default=False)
    
    # Posting
    platform_link = StringField(max_length=500)
    proof_link = StringField(max_length=500)

class Collaboration(Document):
    status = StringField(choices=('On Going', 'Halted', 'Declined', 'Done'), default='On Going')
    name = StringField(max_length=200, required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    collaborator_name = StringField(max_length=100, required=True)
    collaborator_email = StringField(max_length=100)
    
    # Type Logic
    type = StringField(choices=('Paid', 'Product', 'Paid Product'), required=True)
    agreed_price = FloatField(min_value=0)
    tracking_number = StringField(max_length=100)
    package_received = BooleanField(default=False)
    
    # Logistics
    term = StringField(choices=('Long', 'Short'))
    duration = StringField(max_length=100)
    contract_link = StringField(max_length=500)
    posting_date = DateTimeField()
    deadline = DateTimeField()
    
    # Productivity
    other_notes = StringField(max_length=2000)
    
    # Videos
    videos = ListField(EmbeddedDocumentField(VideoUnit))
    
    # Meta
    scope = StringField(max_length=100)  # App/Product
    channel = StringField(max_length=100)
    platform = ListField(StringField(max_length=100))
    
    meta = {
        'collection': 'collaborations', 
        'indexes': ['created_at', 'collaborator_name', 'type', 'deadline']
    }
