import configparser
import math
import os

import colorama
import ffmpeg
import yt_dlp
from pymongo import MongoClient

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