from get_data import get_id_list, get_video_list, get_captions
from match import match_captions

def main():
    # prepare videos and captions data
    get_id_list()
    get_video_list()
    get_captions()

    # match video captions with words to memorize
    match_captions()


if __name__ == "__main__":
    main()