from googleapiclient.discovery import build
import pandas as pd
from time import sleep
import traceback
import os
import getpass
from dotenv import load_dotenv

load_dotenv()

def get_comments(api_key, video_id, max_pages=5):
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
        textFormat="plainText",
        maxResults=100,
        order="relevance"

    )

    df = pd.DataFrame(columns=['comment', 'replies', 'date', 'user_name', 'likes'])

    curr_page = 0

    while request and curr_page < max_pages:
        curr_page += 1
        try:
            response = request.execute()

            comments, replies, dates, users, likes = [], [], [], [], []

            for item in response['items']:
                snippet = item['snippet']['topLevelComment']['snippet']

                comment = snippet['textDisplay']
                user = snippet['authorDisplayName']
                date = snippet['publishedAt']
                like_count = snippet['likeCount']

                comments.append(comment)
                users.append(user)
                dates.append(date)
                likes.append(like_count)

                # replies
                reply_list = []
                if 'replies' in item:
                    for reply in item['replies']['comments']:
                        reply_list.append(reply['snippet']['textDisplay'])
                replies.append(reply_list)

            # add to dataframe
            df2 = pd.DataFrame({
                "comment": comments,
                "replies": replies,
                "date": dates,
                "user_name": users,
                "likes": likes
            })

            df = pd.concat([df, df2], ignore_index=True)

            # sleep(1)  # be nice to API
            request = youtube.commentThreads().list_next(request, response)
            print(f"Page {curr_page} fetched...")

        except Exception:
            traceback.print_exc()
            break

    df.to_csv(f"{video_id}_user_comments.csv", index=False, encoding='utf-8')
    print(f"Saved {len(df)} comments to {video_id}_user_comments.csv")


def main():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    print(api_key)
    video_id = input("Enter YouTube video ID: ")
    get_comments(api_key, video_id)


if __name__ == "__main__":
    main()
