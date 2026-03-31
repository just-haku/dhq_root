from mongoengine import Document, StringField, DateTimeField, BooleanField
from datetime import datetime

class SystemConfig(Document):
    """Global system configuration and state (Singleton pattern)"""
    power_mode = StringField(choices=["normal", "power_saver"], default="normal")
    last_updated = DateTimeField(default=datetime.utcnow)
    ps_disable_ai = BooleanField(default=True)
    ps_disable_uploads = BooleanField(default=True)
    ps_disable_gcode = BooleanField(default=True)
    
    meta = {
        'collection': 'system_config'
    }

    @classmethod
    def get_config(cls):
        config = cls.objects.first()
        if not config:
            config = cls(power_mode="normal").save()
        return config
