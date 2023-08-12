import math
import os

import ffmpeg
import yt_dlp

from utils import print_error, AddCaptionsPostProcessor

def manual_download(link, start, duration, word, caption, path):
    ydl_opts = {
        'outtmpl': '%(uploader_id)s[%(id)s].%(ext)s',
        'paths': { 'home': os.path.join(path, word, 'raw') },
        'download_ranges': yt_dlp.utils.download_range_func(None, [(math.floor(start), math.ceil(10 * (start + duration) / 10))]),
        'force_keyframes_at_cuts': True, # force re-encoding at cut points
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.add_post_processor(AddCaptionsPostProcessor(word=word, caption=caption)) # embed caption after download
        ydl.download([link])

def manual_embed_ass(video_path, ass_path, output_path, start, end):
    ffmpeg_input = ffmpeg.input(video_path, ss=start, t=end)
    audio = ffmpeg_input.audio
    video = ffmpeg_input.video.filter("subtitles", ass_path)
    ffmpeg.output(video, audio, output_path).overwrite_output().run()

def manual_clip(in_path, out_path, start, end):
    (
        ffmpeg
        .input(in_path, ss=start, t=end)
        .output(out_path, vcodec="copy", acodec="copy")
        .overwrite_output()
        .run()
    )