from datetime import datetime
import os
import random
import time

import colorama
import googleapiclient.discovery
from youtube_transcript_api import YouTubeTranscriptApi

from utils import get_config, vtubers, MongoManager

def get_youtube():
    config = get_config()

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps tab of https://cloud.google.com/console
    # ensure that you have enabled the YouTube Data API
    developer_key = config['youtube']['api_key']

    youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=developer_key)
    return youtube

# get channel id and stream video playlist id of vtuber
def get_id_list():
    db = MongoManager.get_database()
    vtubers_collection = db['vtuber_list']
    youtube = get_youtube()
    for name in vtubers:
        # get the id of channel
        response = youtube.search().list(
            q=name,
            type='channel',
            part='id'
        ).execute()
        channel_id = response['items'][0]['id']['channelId']

        # get the id of uploads playlist
        response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()
        playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        vtubers_collection.insert_one({
            '_id': channel_id,
            'name': name,
            'playlist_id': playlist_id
        })

# get all of the stream videos by playlist id
def get_video_list():
    db = MongoManager.get_database()
    video_collection = db['video_list']
    vtubers_collection = db['vtuber_list']
    youtube = get_youtube()

    for vtuber in vtubers_collection.find():
        name = vtuber['name']
        id = vtuber['playlist_id']
        amount = total = 0
        page_token = '' # page_token is needed when results are more than 50

        print(f'get videos for {name} now')

        while amount == 0 or amount < total:
            response = youtube.playlistItems().list(
                part='snippet',
                maxResults=50,
                playlistId=id,
                pageToken=page_token
            ).execute()
            total = response['pageInfo']['totalResults']
            amount += 50
            page_token = response.get('nextPageToken')

            video_collection.insert_many([
                {
                    '_id': item['snippet']['resourceId']['videoId'],
                    'video_id': item['snippet']['resourceId']['videoId'],
                    'time': item['snippet']['publishedAt'],
                    'title': item['snippet']['title'],
                    'channel_name': item['snippet']['channelTitle']
                } for item in response['items']
            ])

        video_collection.create_index('channel_name')
    print('all done!', datetime.now())

# get captions of each video by video id
def get_captions():
    db = MongoManager.get_database()
    caption_collection = db['caption_list']
    video_collection = db['video_list']
    video_list = video_collection.find()
    success_count = 0
    
    for video in video_list:
        video_id = video['video_id']
        channel_name = video['channel_name']

        try:
            caption = YouTubeTranscriptApi.get_transcript(video_id)
            format_caption = [dict(item, channel_name=channel_name, video_id=video_id) for item in caption]
            caption_collection.insert_many(format_caption)
            success_count += 1
            time.sleep(random.randrange(0, 2)) # wait for a while, avoid anti-crawler
        except:
            continue # ignore the video without captions

    caption_collection.create_index('channel_name')
    caption_collection.create_index('text')
