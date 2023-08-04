import re

from utils import get_config, get_database, vtubers

# match captions that include the specific word
def match_captions():
    config = get_config()
    db = get_database()
    caption_collection = db['caption_list']
    words_collection = db[config['database']['words_collecion_name']]
    captions = []
    channels = []
    count = 0

    for word_doc in words_collection.find():
        word = word_doc['word']
        print('looking for word:', word)
        while count < len(vtubers):
            caption_doc = caption_collection.find_one_and_update(
                {
                    # '$text': { '$search': word },
                    'text': { '$regex': r'\b%s\b' % re.escape(word), '$options': 'i' },
                    'used_word': { '$exists': False },
                    'channel_name': { '$nin': channels } # each vtuber only once
                },
                { '$set': { 'used_word': word } }
            )
            if caption_doc is None:
                break
            count += 1
            channels.append(caption_doc.get('channel_name'))
            captions.append(caption_doc)
        print('captions found:', count)
        if count > 0:
            words_collection.update_one(
                { '_id': word_doc.get('_id') },
                { '$set': { 'captions': captions } }
            )
        count = 0
        captions = []
        channels = []
  