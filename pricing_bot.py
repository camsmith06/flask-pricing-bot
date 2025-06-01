
from dataclasses import dataclass
from typing import Optional
import requests

@dataclass
class UserProfile:
    followers: int
    avg_engagements: int
    avg_views: int
    engagement_rate: float
    subscribers: Optional[int] = None
    avg_youtube_views: Optional[int] = None
    content_type: str = 'non-sector'
    page_type: str = 'personal'
    brand_size: str = 'startup'
    niche_multiplier: float = 1.0
    base_deliverable_price: Optional[float] = None
    ugc_score: Optional[int] = None

CONTENT_TYPE_FACTORS = {
    'non-sector': 1.0,
    'sector': 1.2,
    'personal': 1.5,
    'meme': 0.7
}

BRAND_SIZE_FACTORS = {
    'startup': 1.0,
    'small': 1.1,
    'mid': 1.3,
    'big': 1.5
}

ENGAGEMENT_RATE_MULTIPLIERS = {
    'low': 0.8,
    'medium': 1.0,
    'high': 1.2
}

PAGE_TYPE_MULTIPLIERS = {
    'personal': 1.0,
    'creator': 1.1,
    'business': 1.2
}

IG_CONTENT_TYPE_MULTIPLIERS = {
    'image': 1.0,
    'video': 1.2,
    'carousel': 1.1
}

CPM_TABLE_INSTAGRAM = {
    'reel': 7.50,
    'post': 8.00,
    'story': 6.00
}

BASE_CPM_YOUTUBE = 12.00

FORMAT_MULTIPLIERS = {
    'integration': 0.6,
    'shorts': 0.3,
    'dedicated': 1.0
}

UGC_SCORE_MULTIPLIERS = {
    range(1, 5): 0.85,
    range(5, 8): 1.0,
    range(8, 11): 1.1,
    range(11, 14): 1.2,
    range(14, 100): 1.3
}

def get_ugc_multiplier(score: int) -> float:
    for score_range, multiplier in UGC_SCORE_MULTIPLIERS.items():
        if score in score_range:
            return multiplier
    return 1.0

def calculate_engaged_views(avg_views: int, engagement_rate: float) -> float:
    return avg_views * (engagement_rate / 100)

def calculate_tiktok_price(user: UserProfile, integrated: bool = False) -> float:
    engaged_views = calculate_engaged_views(user.avg_views, user.engagement_rate)
    base_price = (engaged_views * 0.0275) + ((user.followers / 1000) * 1.50)
    price = base_price * CONTENT_TYPE_FACTORS[user.content_type] * BRAND_SIZE_FACTORS[user.brand_size]
    return price * 0.4 if integrated else price

def get_engagement_rate_multiplier(rate: float) -> float:
    if rate < 1.0:
        return ENGAGEMENT_RATE_MULTIPLIERS['low']
    elif 1.0 <= rate <= 3.0:
        return ENGAGEMENT_RATE_MULTIPLIERS['medium']
    else:
        return ENGAGEMENT_RATE_MULTIPLIERS['high']

def calculate_instagram_price(user: UserProfile, deliverable: str, content_format: str, integrated: bool = False) -> float:
    cpm = CPM_TABLE_INSTAGRAM[deliverable]
    engagement_multiplier = get_engagement_rate_multiplier(user.engagement_rate)
    page_type_multiplier = PAGE_TYPE_MULTIPLIERS[user.page_type]
    content_type_multiplier = IG_CONTENT_TYPE_MULTIPLIERS[content_format]
    price = (user.followers / 1000) * cpm * engagement_multiplier * page_type_multiplier * content_type_multiplier
    return price * 0.4 if integrated else price

def calculate_youtube_price(user: UserProfile, format_type: str) -> float:
    if not user.subscribers or not user.avg_youtube_views:
        return 0.0
    engagement_multiplier = user.avg_youtube_views / user.subscribers
    price = (user.subscribers / 1000) * BASE_CPM_YOUTUBE * engagement_multiplier * FORMAT_MULTIPLIERS[format_type] * user.niche_multiplier
    return price

def calculate_ugc_price(user: UserProfile) -> float:
    if not user.base_deliverable_price or not user.ugc_score:
        return 0.0
    score_multiplier = get_ugc_multiplier(user.ugc_score)
    return user.base_deliverable_price * score_multiplier * user.niche_multiplier * BRAND_SIZE_FACTORS[user.brand_size]

def apply_discount(price: float, discount_rate: float = 0.3) -> float:
    return price * (1 - discount_rate)

def get_price_recommendation_range(price: float) -> tuple:
    return round(price * 0.7, 2), round(price * 1.3, 2)

def score_ugc_questionnaire(skill_level: str, editing: str, complexity: str, content_type: str, equipment: str) -> int:
    score_map = {
        'skill_level': {
            'Beginner': 1,
            'Intermediate': 2,
            'Advanced': 3,
            'Expert': 4
        },
        'editing': {
            'No Editing': 0,
            'Basic Editing': 1,
            'Advanced Editing': 2
        },
        'complexity': {
            'Light': 1,
            'Intermediate': 2,
            'Heavy': 3
        },
        'content_type': {
            'Talking Head': 1,
            'Lifestyle / Demo': 2,
            'Tutorial / How-To': 3,
            'Unboxing / Review': 4,
            'Voiceover Only': 1
        },
        'equipment': {
            'Smartphone': 1,
            'Camera + Natural Light': 2,
            'Camera + Lighting + Microphone': 3
        }
    }
    return (
        score_map['skill_level'].get(skill_level, 0) +
        score_map['editing'].get(editing, 0) +
        score_map['complexity'].get(complexity, 0) +
        score_map['content_type'].get(content_type, 0) +
        score_map['equipment'].get(equipment, 0)
    )

def estimate_brand_details(brand_name: str) -> tuple:
    brand_size_map = {
        'startup': ['indie', 'small batch', 'new brand'],
        'small': ['niche', 'boutique'],
        'mid': ['established', 'retail'],
        'big': ['global', 'mass market', 'fortune']
    }
    niche_keywords = ['beauty', 'fashion', 'tech', 'fitness', 'food', 'travel', 'gaming']
    size = 'startup'
    niche = 'general'
    try:
        response = requests.get(f'https://www.google.com/search?q={brand_name}+brand+overview', timeout=5)
        text = response.text.lower()
        for key, keywords in brand_size_map.items():
            if any(k in text for k in keywords):
                size = key
        for keyword in niche_keywords:
            if keyword in text:
                niche = keyword
    except:
        pass
    return size, niche
