from mongoengine import Document, StringField, IntField, DateTimeField, BooleanField, ReferenceField, ListField, DictField, FloatField
from datetime import datetime, timedelta
from .user import User

class DailyKPIBonus(Document):
    """Model for daily KPI bonus system"""
    
    # User reference
    user = ReferenceField(User, required=True)
    
    # Bonus details
    date = DateTimeField(required=True)  # The date for this bonus
    base_amount = IntField(required=True)  # Base amount for the day
    bonus_multiplier = FloatField(default=1.0)  # Multiplier for special days
    final_amount = IntField(required=True)  # Final amount after multiplier
    day_number = IntField(required=True)  # Day number in the 30-day cycle (1-30)
    
    # Status
    is_claimed = BooleanField(default=False)
    claimed_at = DateTimeField()
    is_expired = BooleanField(default=False)
    
    # Special day indicators
    is_wednesday = BooleanField(default=False)  # Wednesday bonus
    is_special_day = BooleanField(default=False)  # Other special days
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'daily_kpi_bonuses',
        'indexes': [
            'user',
            'date',
            'day_number',
            'is_claimed',
            {'fields': ['user', 'date'], 'unique': True}
        ]
    }
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user': {
                'id': str(self.user.id),
                'username': self.user.username,
                'display_name': self.user.display_name
            },
            'date': self.date,
            'base_amount': self.base_amount,
            'bonus_multiplier': self.bonus_multiplier,
            'final_amount': self.final_amount,
            'day_number': self.day_number,
            'is_claimed': self.is_claimed,
            'claimed_at': self.claimed_at,
            'is_expired': self.is_expired,
            'is_wednesday': self.is_wednesday,
            'is_special_day': self.is_special_day,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class KPIBonusCycle(Document):
    """Model for tracking 30-day KPI bonus cycles"""
    
    # User reference
    user = ReferenceField(User, required=True, unique=True)
    
    # Cycle tracking
    current_cycle_start = DateTimeField(required=True)
    current_day = IntField(default=1)  # Current day in cycle (1-30)
    total_claimed_this_cycle = IntField(default=0)
    total_available_this_cycle = IntField(default=0)
    
    # Statistics
    total_cycles_completed = IntField(default=0)
    total_lifetime_claimed = IntField(default=0)
    best_cycle_amount = IntField(default=0)
    current_streak = IntField(default=0)  # Consecutive days claimed
    longest_streak = IntField(default=0)
    
    # Metadata
    last_claim_date = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'kpi_bonus_cycles',
        'indexes': [
            'user',
            'current_cycle_start',
            'current_day'
        ]
    }
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user': {
                'id': str(self.user.id),
                'username': self.user.username,
                'display_name': self.user.display_name
            },
            'current_cycle_start': self.current_cycle_start,
            'current_day': self.current_day,
            'total_claimed_this_cycle': self.total_claimed_this_cycle,
            'total_available_this_cycle': self.total_available_this_cycle,
            'total_cycles_completed': self.total_cycles_completed,
            'total_lifetime_claimed': self.total_lifetime_claimed,
            'best_cycle_amount': self.best_cycle_amount,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_claim_date': self.last_claim_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class KPIBonusConfig(Document):
    """Configuration for KPI bonus system"""
    
    # Base configuration
    base_daily_amount = IntField(default=30)  # Starting amount for day 1
    daily_increment = IntField(default=2)  # Daily increment amount
    
    # Wednesday bonus
    wednesday_multiplier = FloatField(default=1.5)  # 1.5x bonus on Wednesday
    
    # Special day bonuses
    special_days = ListField(DictField())  # List of special day configurations
    
    # Cycle settings
    cycle_length_days = IntField(default=30)
    expiry_hours = IntField(default=24)  # Hours after which bonus expires
    
    # Global settings
    is_system_active = BooleanField(default=True)
    max_daily_amount = IntField(default=1000)  # Maximum daily bonus
    
    meta = {
        'collection': 'kpi_bonus_config',
        'indexes': [
            'is_system_active'
        ]
    }
    
    @classmethod
    def get_config(cls):
        """Get or create default configuration"""
        config = cls.objects().first()
        if not config:
            config = cls(
                special_days=[
                    {
                        'day_number': 7,  # Day 7 of cycle
                        'multiplier': 2.0,  # 2x bonus
                        'name': 'Weekly Bonus',
                        'description': 'Double bonus for completing first week'
                    },
                    {
                        'day_number': 15,  # Day 15 of cycle
                        'multiplier': 2.5,  # 2.5x bonus
                        'name': 'Mid-Cycle Bonus',
                        'description': 'Extra bonus at halfway point'
                    },
                    {
                        'day_number': 30,  # Day 30 of cycle
                        'multiplier': 3.0,  # 3x bonus
                        'name': 'Cycle Completion',
                        'description': 'Triple bonus for completing full cycle'
                    }
                ]
            )
            config.save()
        return config
    
    def calculate_daily_amount(self, day_number, is_wednesday=False):
        """Calculate the bonus amount for a specific day"""
        # Base calculation
        base_amount = self.base_daily_amount + (day_number - 1) * self.daily_increment
        
        # Apply Wednesday bonus
        multiplier = 1.0
        if is_wednesday:
            multiplier = self.wednesday_multiplier
        
        # Check for special day bonus
        for special_day in self.special_days:
            if special_day['day_number'] == day_number:
                multiplier = max(multiplier, special_day['multiplier'])
                break
        
        # Calculate final amount
        final_amount = int(base_amount * multiplier)
        
        # Cap at maximum
        final_amount = min(final_amount, self.max_daily_amount)
        
        return {
            'base_amount': base_amount,
            'multiplier': multiplier,
            'final_amount': final_amount,
            'is_wednesday': is_wednesday,
            'is_special_day': any(s['day_number'] == day_number for s in self.special_days)
        }
