import requests
import urllib.parse
import os
from dotenv import load_dotenv

import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

import re
import emoji

from langdetect import detect

import pandas as pd
# Load variables from .env
load_dotenv()

# Get the API key
API_KEY = os.getenv("YOUTUBE_API_KEY")

def search_videos(query, max_results=5):
    """Search YouTube for videos matching the query"""
    query_encoded = urllib.parse.quote(query)
    url = (
        f"https://youtube.googleapis.com/youtube/v3/search?"
        f"part=snippet&maxResults={max_results}&order=relevance&q={query_encoded}"
        f"&type=video&videoDuration=medium&key={API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    videos = []
    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        videos.append((video_id, title))
    return videos

def fetch_comments(video_id, max_results=20):
    """Fetch top comments for a given video"""
    url = (
        f"https://youtube.googleapis.com/youtube/v3/commentThreads?"
        f"part=snippet&videoId={video_id}&maxResults={max_results}&textFormat=plainText"
        f"&key={API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    comments = []
    for item in data.get("items", []):
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)
    return comments


def preprocess_comment(comment):
    if not is_english(comment):
        return None
    comment = clean_text(comment)
    # comment = expand_slang(comment)
    comment = remove_stopwords(comment)
    return comment

def remove_stopwords(text):
    return " ".join([w for w in text.split() if w not in stop_words])

def clean_text(text):
    # Remove emojis
    text = emoji.replace_emoji(text, replace='')
    # Remove special characters, numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Lowercase
    text = text.lower()
    return text

def is_english(text):
    try:
        return detect(text) == "en"
    except:
        return False


if __name__ == "__main__":
    user_query = input("Enter a topic: ")
    print(f"\n🔍 Searching YouTube for: {user_query}\n")

    videos = search_videos(user_query, max_results=5)

    for video_id, title in videos:
        print(f"\n📺 {title} (ID: {video_id})")
        comments = fetch_comments(video_id, max_results=10)  # change limit if needed
        for idx, comment in enumerate(comments, start=1):
            print(f"   {idx}. {comment}")

    all_comments = []

    for video_id, title in videos:
        comments = fetch_comments(video_id, max_results=50)
        for c in comments:
            processed = preprocess_comment(c)
            if processed:  # keep only English + non-empty
                all_comments.append({"video_id": video_id, "title": title, "comment": processed})

    df = pd.DataFrame(all_comments)
    print(df.head())
