import os

import ffmpeg
from gtts import gTTS

from utils import get_config, get_database, print_error

__config = get_config()
__db = get_database()
__words_collection = __db[__config['database']['words_collection_name']]
__words_per_videos = __config['number']['words_per_videos']

def __gen_intro(word, translation):
    font_path = __config['path']['font']
    path = __config['path']['root']
    video_width = 1920
    video_height = 1080
    cover = (
        ffmpeg
        .input(__config['path']['cover'], framerate=1, r=60)
        .filter('scale', video_width, video_height, force_original_aspect_ratio='decrease')
        .filter('gblur', sigma=8)
        .filter('pad', video_width, video_height, '(ow-iw)/2', '(oh-ih)/2', 'White')
        .filter('setsar', sar='1/1')
        .drawtext(text=word, fontfile=font_path, fontsize=120, bordercolor='black', fontcolor='white', borderw=10, x='(w-tw)/2', y='(h-th)/2-100')
        .drawtext(text=f"{translation['type']}. {translation['chinese']}", fontfile=font_path, fontsize=96, bordercolor='black', fontcolor='white', borderw=10, x='(w-tw)/2', y='(h-th)/2+100')
    )

    # speak the target word and translation
    tts_en = gTTS(word)
    tts_zh = gTTS(translation['chinese'], lang='zh')
    with open(f"{path}/{word}/pronunciation.mp3", "wb") as audio_stream:
        tts_en.write_to_fp(audio_stream)
        tts_zh.write_to_fp(audio_stream)
        tts_en.write_to_fp(audio_stream)
    audio = ffmpeg.input(f'{path}/{word}/pronunciation.mp3').filter('aresample', __config['number']['audio_sample_rate']).filter('asetpts', 'N/SR/TB')

    (
        ffmpeg
        .output(cover, audio, f'{path}/{word}/intro.mp4', pix_fmt='yuv420p')
        .overwrite_output()
        .run()
    )

def concat_by_word():
    # concat videos of the word that has already matched captions and downloaded clips.
    for word_doc in __words_collection.find({ "downloaded": True, "generated": { "$exists": False }, "dirty": { "$exists": False } }).limit(__words_per_videos):
        word = word_doc['word']
        word_path = f"{__config['path']['root']}/{word}"
        try:
            __gen_intro(word, word_doc['translations'])
            # write txt for concat demuxer
            files = (file for file in os.listdir(word_path) if file.endswith('.mp4') and file != 'intro.mp4')
            with open(f'{word_path}/list.txt', 'w') as txt:
                txt.write(f"file 'intro.mp4'{os.linesep}")
                for file in files:
                    txt.write(f"file '{str(file)}'{os.linesep}")
            (
                ffmpeg
                .input(f'{word_path}/list.txt', format='concat', safe=0)
                .output(f'{word_path}/clips.mp4')
                .run()
            )
            __words_collection.update_one(
                { 'word': word },
                { '$set': { 'generated': True } }
            )
        except:
            print_error(f'generate video failed for [{word}]')
