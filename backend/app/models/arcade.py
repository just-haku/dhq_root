from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField, IntField, BooleanField, FloatField, EmbeddedDocumentField, EmbeddedDocument
from datetime import datetime, timedelta
from .user import User

class DailyBonusConfig(Document):
    """Configuration for daily login bonuses"""
    name = StringField(default="Default Bonus Config")
    is_active = BooleanField(default=True)
    base_bonus = IntField(default=30)
    # List of 30 percentages (e.g., 0.3 for 30%)
    percentages = ListField(FloatField(), default=[0.0]*30)
    
    meta = {
        'collection': 'arcade_bonus_config'
    }

class Achievement(EmbeddedDocument):
    """User achievement record"""
    achievement_id = StringField(required=True)
    name = StringField(required=True)
    description = StringField()
    points_awarded = IntField(default=0)
    unlocked_at = DateTimeField(default=datetime.utcnow)
    icon = StringField()

class ShopItem(EmbeddedDocument):
    """Purchased shop item"""
    item_id = StringField(required=True)
    name = StringField(required=True)
    description = StringField()
    cost_kpi = IntField(required=True)
    purchased_at = DateTimeField(default=datetime.utcnow)
    is_active = BooleanField(default=True)
    item_type = StringField(choices=['AVATAR', 'BADGE', 'TITLE', 'EFFECT', 'POWERUP'])

class GameSession(Document):
    """Gaming session record"""
    user = ReferenceField(User, required=True)
    game_type = StringField(choices=['PUZZLE', 'QUIZ', 'CHALLENGE', 'TOURNAMENT'], required=True)
    score = IntField(default=0)
    kpi_earned = IntField(default=0)
    duration_seconds = IntField(default=0)
    completed_at = DateTimeField(default=datetime.utcnow)
    difficulty = StringField(choices=['EASY', 'MEDIUM', 'HARD', 'EXTREME'], default='MEDIUM')
    
    meta = {
        'collection': 'arcade_sessions',
        'indexes': [
            'user',
            'game_type',
            'completed_at',
            ('user', 'game_type')
        ]
    }

class LeaderboardEntry(Document):
    """Leaderboard entries"""
    user = ReferenceField(User, required=True)
    game_type = StringField(required=True)
    score = IntField(required=True)
    kpi_earned = IntField(default=0)
    achieved_at = DateTimeField(default=datetime.utcnow)
    period_type = StringField(choices=['DAILY', 'WEEKLY', 'MONTHLY', 'ALL_TIME'], default='ALL_TIME')
    
    meta = {
        'collection': 'arcade_leaderboards',
        'indexes': [
            'game_type',
            'period_type',
            'score',
            'achieved_at',
            ('game_type', 'period_type', 'score')
        ]
    }

class ShopItemDefinition(Document):
    """Shop items available for purchase"""
    name = StringField(required=True, max_length=100)
    description = StringField()
    cost_kpi = IntField(required=True)
    item_type = StringField(choices=['AVATAR', 'BADGE', 'TITLE', 'EFFECT', 'POWERUP'], required=True)
    icon = StringField()
    rarity = StringField(choices=['COMMON', 'RARE', 'EPIC', 'LEGENDARY'], default='COMMON')
    is_active = BooleanField(default=True)
    is_limited = BooleanField(default=False)
    stock_limit = IntField()
    current_stock = IntField()
    
    # Item effects
    effect_type = StringField()  # e.g., 'KPI_BOOST', 'XP_MULTIPLIER'
    effect_value = FloatField(default=1.0)
    effect_duration_hours = IntField(default=24)
    
    meta = {
        'collection': 'arcade_shop_items',
        'indexes': [
            'item_type',
            'rarity',
            'is_active',
            'cost_kpi'
        ]
    }

class AchievementDefinition(Document):
    """Achievement definitions"""
    name = StringField(required=True, max_length=100)
    description = StringField()
    icon = StringField()
    points_awarded = IntField(required=True)
    achievement_type = StringField(choices=['TASKS', 'LOGIN', 'COLLABORATION', 'VAULT', 'SOCIAL', 'GAMING'], required=True)
    
    # Achievement criteria
    criteria_field = StringField()  # e.g., 'tasks_completed', 'login_streak'
    criteria_value = IntField(required=True)
    
    # Achievement state
    is_active = BooleanField(default=True)
    is_hidden = BooleanField(default=False)
    
    meta = {
        'collection': 'arcade_achievements',
        'indexes': [
            'achievement_type',
            'is_active',
            'points_awarded'
        ]
    }

class UserKPIHistory(Document):
    """KPI earning history"""
    user = ReferenceField(User, required=True)
    kpi_amount = IntField(required=True)
    source_type = StringField(choices=['TASK', 'ACHIEVEMENT', 'GAME', 'BONUS', 'PURCHASE_REFUND', 'LOGIN'], required=True)
    source_id = StringField()  # Reference to task, achievement, etc.
    description = StringField()
    timestamp = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'arcade_kpi_history',
        'indexes': [
            'user',
            'source_type',
            'timestamp',
            ('user', 'timestamp')
        ]
    }

class UserArcadeProfile(Document):
    """User's arcade profile and stats"""
    user = ReferenceField(User, required=True, unique=True)
    
    # KPI and currency
    kpi_balance = IntField(default=0)
    chip_balance = IntField(default=0)
    api_dollar_balance = FloatField(default=0.0)
    total_kpi_earned = IntField(default=0)
    kpi_spent = IntField(default=0)
    
    # Gaming stats
    games_played = IntField(default=0)
    total_game_time = IntField(default=0)  # in seconds
    high_scores = ListField(StringField())  # JSON strings of game-specific high scores
    
    def add_chips(self, amount: int):
        """Add or subtract chips from user's arcade balance"""
        self.chip_balance += amount
        return self.save()

    def spend_chips(self, amount: int):
        """Spend chips from user's arcade balance"""
        if amount > 0 and self.chip_balance >= amount:
            self.chip_balance -= amount
            return self.save()
        return None
    
    def add_api_dollars(self, amount: float):
        """Add API$ to user's balance"""
        self.api_dollar_balance += amount
        # Sync with main User model
        user = self.user
        user.api_dollar_balance = self.api_dollar_balance
        user.save()
        return self.save()

    def spend_api_dollars(self, amount: float):
        """Spend API$ from user's balance"""
        if self.api_dollar_balance >= amount:
            self.api_dollar_balance -= amount
            # Sync with main User model
            user = self.user
            user.api_dollar_balance = self.api_dollar_balance
            user.save()
            return self.save()
        return None
    
    # Achievements and items
    achievements = ListField(EmbeddedDocumentField(Achievement))
    owned_items = ListField(EmbeddedDocumentField(ShopItem))
    
    # Active effects
    active_effects = ListField(StringField())  # JSON strings of active power-ups
    effect_expirations = ListField(DateTimeField())
    
    # Preferences
    selected_avatar = StringField()
    selected_badge = StringField()
    selected_title = StringField()
    
    # Appearance settings
    unlocked_themes = ListField(StringField(), default=['dark', 'light'])
    side_menu_layout = StringField(choices=['list', 'grid'], default='list')
    active_theme = StringField(default='dark')
    is_single_click_open = BooleanField(default=False)
    
    # Streaks and counters
    login_streak = IntField(default=0)
    last_login = DateTimeField()
    tasks_completed = IntField(default=0)
    collaborations_created = IntField(default=0)
    files_uploaded = IntField(default=0)
    
    # Level and experience
    level = IntField(default=1)
    experience_points = IntField(default=0)
    
    meta = {
        'collection': 'arcade_profiles',
        'indexes': [
            'user',
            'kpi_balance',
            'level',
            'login_streak'
        ]
    }
    
    def add_kpi(self, amount: int, source_type: str, source_id: str = None, description: str = ""):
        """Add KPI to user balance and sync with main User model"""
        self.kpi_balance += amount
        self.total_kpi_earned += amount
        
        # Sync with main User model
        user = self.user
        user.kpi_current += amount
        if amount > 0:
            user.kpi_lifetime += amount
        user.save()
        
        # Create history record
        history = UserKPIHistory(
            user=self.user,
            kpi_amount=amount,
            source_type=source_type,
            source_id=source_id,
            description=description
        )
        history.save()
        
        # Check for level up
        self.check_level_up()
        
    def spend_kpi(self, amount: int, description: str = ""):
        """Spend KPI from user balance"""
        if self.kpi_balance >= amount:
            self.kpi_balance -= amount
            self.kpi_spent += amount
            
            # Create history record
            history = UserKPIHistory(
                user=self.user,
                kpi_amount=-amount,
                source_type='PURCHASE_REFUND',
                description=description
            )
            history.save()
            return True
        return False
    
    def check_level_up(self):
        """Check if user should level up"""
        # Level thresholds (can be made configurable)
        level_thresholds = [0, 100, 250, 500, 1000, 2000, 3500, 5000, 7500, 10000]
        
        for i, threshold in enumerate(level_thresholds):
            if self.experience_points >= threshold and self.level <= i:
                self.level = i + 1
                # Award level up bonus KPI
                self.add_kpi(50 * self.level, 'ACHIEVEMENT', description=f"Level {self.level} reached!")
    
    def update_login_streak(self):
        """Update login streak"""
        now = datetime.utcnow()
        
        if self.last_login:
            # Check if logged in yesterday
            yesterday = now - timedelta(days=1)
            if self.last_login.date() == yesterday.date():
                self.login_streak += 1
            # Check if missed a day
            elif self.last_login.date() < yesterday.date():
                self.login_streak = 1
        else:
            self.login_streak = 1
        
        self.last_login = now
        
        # Calculate bonus based on config
        from .arcade import DailyBonusConfig
        config = DailyBonusConfig.objects(is_active=True).first()
        base = config.base_bonus if config else 30
        
        # Use 30-day cycle for percentages
        streak_idx = (self.login_streak - 1) % 30
        percentage = 0.0
        if config and streak_idx < len(config.percentages):
            percentage = config.percentages[streak_idx]
            
        bonus = int(base * (1 + percentage))
        self.add_kpi(bonus, 'LOGIN', description=f"Daily login (streak: {self.login_streak}, bonus: {bonus})")
        
        # Check for theme unlocks
        from app.services.achievements import check_theme_unlocks
        check_theme_unlocks(self.user, self)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user.id),
            'kpi_balance': self.user.kpi_current,
            'total_kpi_earned': self.total_kpi_earned,
            'kpi_spent': self.kpi_spent,
            'games_played': self.games_played,
            'total_game_time': self.total_game_time,
            'achievements_count': len(self.achievements),
            'owned_items_count': len(self.owned_items),
            'selected_avatar': self.selected_avatar,
            'selected_badge': self.selected_badge,
            'selected_title': self.selected_title,
            'active_theme': self.active_theme,
            'unlocked_themes': self.unlocked_themes,
            'side_menu_layout': self.side_menu_layout,
            'is_single_click_open': self.is_single_click_open,
            'login_streak': self.login_streak,
            'tasks_completed': self.tasks_completed,
            'collaborations_created': self.collaborations_created,
            'files_uploaded': self.files_uploaded,
            'level': self.level,
            'experience_points': self.experience_points,
            'chip_balance': self.chip_balance,
            'api_dollar_balance': self.api_dollar_balance,
            'achievements': [
                {
                    'id': achievement.achievement_id,
                    'name': achievement.name,
                    'description': achievement.description,
                    'points_awarded': achievement.points_awarded,
                    'unlocked_at': achievement.unlocked_at.isoformat(),
                    'icon': achievement.icon
                }
                for achievement in self.achievements
            ],
            'owned_items': [
                {
                    'id': item.item_id,
                    'name': item.name,
                    'description': item.description,
                    'cost_kpi': item.cost_kpi,
                    'item_type': item.item_type,
                    'is_active': item.is_active
                }
                for item in self.owned_items
            ]
        }
