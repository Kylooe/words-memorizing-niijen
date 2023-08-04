import configparser
import datetime
import os
import random
import time

import pymongo
import colorama
import googleapiclient
import youtube_transcript_api

from get_data import get_id_list, get_video_list,get_captions

def main():
    # prepare videos and captions data
    get_id_list()
    get_video_list()
    get_captions()
    

if __name__ == "__main__":
    main()