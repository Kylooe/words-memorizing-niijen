import configparser
import math
import os
import re
import shutil
from textwrap import wrap

import colorama
import ffmpeg
from pymongo import MongoClient
from yt_dlp.postprocessor.common import PostProcessor

colors = {
    'SelenTatsuki': '#7E4EAC',
    'PomuRainpuff': '#258E70',
    'EliraPendora': '#95C8D8',
    'FinanaRyugu': '#79CFB8',
    'Rosemi_Lovelock': '#DC3753',
    'petragurin': '#FFAE42',
    'MillieParfait': '#FEBC87',
    'EnnaAlouette': '#858ED1',
    'ReimuEndou': '#B90B4A',
    'NinaKosaka': '#660000',
    'LucaKaneshiro': '#D4AF37',
    'ShuYamino': '#A660A7',
    'IkeEveland': '#348EC7',
    'MystaRias': '#C3552B',
    'VoxAkuma': '#960018',
    'AlbanKnox': '#FF5F00',
    'FulgurOvid': '#FF0000',
    'UkiVioleta': '#B600FF',
    'SonnyBrisko': '#FFF321',
    'MariaMarionette': '#E55A9B',
    'RenZotto': '#429B76',
    'KyoKaneko': '#00AFCC',
    'ScarleYonaguni': '#E60012',
    'AsterArcadia': '#6662A4',
    'AiaAmare': '#FFFEF7',
    'VerVermillion': '#D5345E',
    'HexHaywire': '#007199',
    'DoppioDropscythe': '#A50082',
    # 'MelocoKyoran': '#A09BD8',
    # 'KotokaTorahime': ''
}

vtubers = [vtuber for vtuber in colors]

# ffmpeg post processor for embedding captions
class AddCaptionsPostProcessor(PostProcessor):
    def __init__(self, downloader=None, word='', caption=''):
        super().__init__(downloader)
        self.word = word
        self.caption = caption

    # convert hex RGB color to ASS V4+ Styles color
    def convert_color(self, uploader_id):
        key = uploader_id[1:]
        R, G, B = wrap(colors[key][1:], 2)
        return f'&H00{B}{G}{R}&'
        
    def run(self, info):
        config = get_config()
        path = config['path']['videos_path']
        video_name = os.path.splitext(os.path.basename(info['filepath']))[0]
        ass_path = f'{path}/{self.word}/ass/{video_name}.ass'
        shutil.copyfile(f'{path}/ass_template.txt', ass_path)
        fore, back = re.split(re.compile(self.word, re.I), self.caption, 1)
        color = self.convert_color(info['uploader_id'])
        with open(ass_path, 'a') as ass:
            ass.write(f'{fore}{{\\3a&H00&\\3c{color}}}{self.word}{{\\3c\\3a}}{back}') # render caption with outline target word

        ffmpeg_input = ffmpeg.input(info['filepath'])
        audio = ffmpeg_input.audio
        video = ffmpeg_input.video.filter('subtitles', ass_path)
        ffmpeg.output(video, audio, f'{path}/{self.word}/{video_name}.mp4').run()

        return [], info

def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def get_database():
    config = get_config()
    client = MongoClient(config['database']['host'])
    return client[config['database']['db_name']]

def print_error(message):
    colorama.init(autoreset=True)
    error_message = f'{colorama.Fore.RED}{message}{colorama.Style.RESET_ALL}'
    print(error_message)
