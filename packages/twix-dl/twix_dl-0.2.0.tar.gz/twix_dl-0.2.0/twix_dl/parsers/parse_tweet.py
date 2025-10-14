from ..models import TweetInfo, AuthorData, TweetMedia
from typing import Dict, Any

def parse_tweet_info(tweet_info: Dict[str, Any]) -> TweetInfo:
    tweet_data = tweet_info["data"]["tweetResult"]["result"]
    user_data = tweet_data["core"]["user_results"]["result"]
    legacy_data = tweet_data["legacy"]
    user_legacy = user_data["legacy"]

    # Parse author data
    author = AuthorData(
        id=user_data["id"],
        rest_id=user_data["rest_id"],
        name=user_data["core"]["name"],
        screen_name=user_data["core"]["screen_name"],
        url=f"https://x.com/{user_data['core']['screen_name']}",
        avatar_url=user_data["avatar"]["image_url"],
        profile_banner_url=user_legacy.get("profile_banner_url", ""),
        description=user_legacy.get("description", ""),
        is_blue_verified=user_data.get("is_blue_verified", False),
        favourites_count=user_legacy.get("favourites_count", 0),
        followers_count=user_legacy.get("followers_count", 0)
    )

    # Parse media
    media = []
    for media_data in legacy_data.get("extended_entities", {}).get("media", []):
        media.append(TweetMedia(
            type=media_data["type"],
            url=media_data["media_url_https"],
            width=media_data.get("original_info", {}).get("width"),
            height=media_data.get("original_info", {}).get("height"),
            duration=media_data.get("video_info", {}).get("duration_millis")
        ))

    return TweetInfo(
        tweet_id=tweet_data["rest_id"],
        url=f"https://x.com/{user_data['core']['screen_name']}/status/{tweet_data['rest_id']}",
        full_text=legacy_data["full_text"],
        author=author,
        media=media,
        favorite_count=legacy_data.get("favorite_count"),
        retweet_count=legacy_data.get("retweet_count"),
        reply_count=legacy_data.get("reply_count"),
        quote_count=legacy_data.get("quote_count"),
        lang=legacy_data.get("lang")
    )
