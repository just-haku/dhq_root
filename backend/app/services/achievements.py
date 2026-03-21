from app.models.user import User
from typing import List

def check_theme_unlocks(user: User, profile) -> List[str]:
    """
    Check and unlock themes based on achievements.
    Profile is passed as a generic object to avoid circular imports in some cases,
    but it's expected to be a UserArcadeProfile instance.
    """
    new_themes = []
    current_themes = profile.unlocked_themes or ['dark', 'light']
    
    # helper to add theme if not already unlocked
    def unlock(theme_name):
        if theme_name not in current_themes:
            current_themes.append(theme_name)
            new_themes.append(theme_name)

    # 1. Gold: Win 5000 KPI or reach level 20
    if profile.total_kpi_earned >= 5000 or profile.level >= 20:
        unlock('gold')
        
    # 2. Silver: Play 50 games
    if profile.games_played >= 50:
        unlock('silver')
        
    # 3. Red: 7 day login streak
    if profile.login_streak >= 7:
        unlock('red')
        
    # 4. Blue: KPI Lifetime > 2000
    if user.kpi_lifetime >= 2000:
        unlock('blue')
        
    # 5. Purple: Reach Level 10
    if profile.level >= 10:
        unlock('purple')
        
    # 6. Pink: Bought any item from shop
    if hasattr(profile, 'owned_items') and len(profile.owned_items) >= 1:
        unlock('pink')
        
    # 7. Glass: Reach Level 5 or Play 10 games
    if profile.level >= 5 or profile.games_played >= 10:
        unlock('glass')

    if new_themes:
        profile.unlocked_themes = current_themes
        profile.save()
    
    return new_themes
