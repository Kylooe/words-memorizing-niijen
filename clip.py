import math
import os
import random

from yt_dlp import YoutubeDL
from yt_dlp.utils import download_range_func

from utils import get_config, get_database, print_error, AddCaptionsPostProcessor

# clip video by caption and save the clips in terms of word
def get_clips():
    config = get_config()
    db = get_database()
    words_collection = db[config['database']['words_collecion_name']]
    clips_limit = 8 # clip up to 8 videos for each word
    for word_doc in words_collection.find({ 'captions': { '$exists': True }, 'downloaded': { '$exists': False } }).limit(config['number']['words_per_videos']):
        path = config['path']['root']
        word = word_doc['word']
        captions = word_doc['captions']
        os.mkdir(os.path.join(path, word, 'raw')) # create folder for clips downloaded from youtube
        downloaded_videos = []
        selected_captions = random.sample(captions, clips_limit) if len(captions) > clips_limit else captions
        for item in selected_captions:
            video_id = item['video_id']
            channel_name = item['channel_name']
            start = item['start']
            duration = item['duration']
            caption = item['text']
            try:
                ydl_opts = {
                    'outtmpl': '%(uploader_id)s[%(id)s].%(ext)s',
                    'paths': { 'home': f'{path}/{word}/raw' },
                    'download_ranges': download_range_func(None, [(math.floor(start), math.ceil(10 * (start + duration)) / 10)]),
                    'force_keyframes_at_cuts': True, # force re-encoding at cut points, otherwise the downloaded video will freeze
                }
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.add_post_processor(AddCaptionsPostProcessor(word=word, caption=caption)) # embed caption after download
                    ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
                downloaded_videos.append(video_id)
            except:
                print_error(f'download failed for [{word}]: {channel_name}')
                continue
        if len(downloaded_videos) > 0:
            words_collection.update_one(
                { 'word': word },
                { '$set': { 'downloaded': True, 'captions.$[element].downloaded': True } },
                array_filters=[{ 'element.video_id': { '$in': downloaded_videos } }]
            )