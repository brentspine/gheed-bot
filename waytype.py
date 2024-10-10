from enum import Enum

class WayType(Enum):

    LIKE_FACEBOOK = 25
    VISIT_YOUTUBE = 26
    FOLLOW_TWITTER_OR_TWITCH = 28 # Follow Twitter/Twitch, Retweet, Visit Link
    VISIT_LINK = 33 # Or Follow Insta/Twitter/Twitch Steam TikTok
    VISIT_NEWSLETTER = 34
    JOIN_OTHER = 35
    COMPLETE_ALL = 37
    STEAM_LINK = 38
    QUESTION = 42
    JOIN_DISCORD = 45
    VIEW_INSTA_POST = 49
    VISIT_OTHER_LINK = 51
    VISIT_FACEBOOK = 52
    VISIT_INSTAGRAM = 53
    VISIT_TIKTOK = 55
    VIEW_TIKTOK = 56
    
class RequestType(Enum):

    GET = 0
    POST = 1
