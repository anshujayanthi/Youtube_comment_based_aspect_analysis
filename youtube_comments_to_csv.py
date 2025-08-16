from googleapiclient.discovery import build
import pandas as pd
from time import sleep
import traceback
import os
import argparse
from dotenv import load_dotenv


load_dotenv()

MAX_PAGES = 5 

def get_comments(api_key, video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
        textFormat="plainText"
    )

    df = pd.DataFrame(columns=['comment', 'replies', 'date', 'user_name'])

    curr_page = 0

    while request and curr_page < MAX_PAGES:
        curr_page += 1
        replies = []
        comments = []
        try:
            response = request.execute()

            for item in response['items']:
               
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)

                replycount = item['snippet']['totalReplyCount']


                replies.append([])
                
                if replycount > 0:
                    for reply in item['replies']['comments']:
                        reply = reply['snippet']['textDisplay']
                        replies[-1].append(reply)
                    
            # create new dataframe
            df2 = pd.DataFrame({"comment": comments, "replies": replies})
            df = pd.concat([df, df2], ignore_index=True)
            df.to_csv(f"{video_id}_user_comments.csv", index=False, encoding='utf-8')
            sleep(2)
            request = youtube.commentThreads().list_next(request, response)
            print("Iterating through next page")
        except Exception as e:
            print(str(e))
            print(traceback.format_exc())
            print("Sleeping for 10 seconds")
            sleep(10)
            df.to_csv(f"{video_id}_user_comments.csv", index=False, encoding='utf-8')
            break

def main():
    api_key = os.getenv("API_KEY")
    parser = argparse.ArgumentParser(description="YouTube Comment Scraper")
    parser.add_argument("video_id", help="YouTube video ID")
    args = parser.parse_args()

    get_comments(api_key, args.video_id)

if __name__ == "__main__":
    main()


# Do we need features like data, user_name etc? for now leaving it out.