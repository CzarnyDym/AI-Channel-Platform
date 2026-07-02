import os
from datetime import datetime

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
UPLOADS_PLAYLIST_ID = "UUqUyE0GB1heTwJL7jKRhffQ"
print("API_KEY:", "OK" if API_KEY else "BRAK")


def get_latest_videos(limit=10):
    url = "https://www.googleapis.com/youtube/v3/playlistItems"

    params = {
        "part": "snippet",
        "playlistId": UPLOADS_PLAYLIST_ID,
        "maxResults": limit,
        "key": API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=15)
    except requests.exceptions.RequestException:
        return []
    data = response.json()

    videos = []

    for item in data.get("items", []):
        snippet = item["snippet"]
        published_at = snippet["publishedAt"]

        video_date = datetime.fromisoformat(
            published_at.replace("Z", "+00:00")
        ).date()

        videos.append({
            "title": snippet["title"],
            "video_id": snippet["resourceId"]["videoId"],
            "published_at": published_at,
            "date": video_date
        })

    return videos


def get_comments(video_id):
    url = "https://www.googleapis.com/youtube/v3/commentThreads"

    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": 30,
        "textFormat": "plainText",
        "key": API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=15)
    except requests.exceptions.RequestException:
        return []
    data = response.json()

    comments = []

    for item in data.get("items", []):
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)

    return comments
