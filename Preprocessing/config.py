MONGODB = dict(
    hostname = "localhost",
    port = 27017,
    db = 'zhuanti',
    collection_sarcasm_es = 'sarcasm_es_3',
    collection_sarcasm_en = 'sarcasm_en_1',
    collection_sarcasm_fr = 'sarcasm_fr_1',
    collection_abusive_es = 'abusive_es_4',
    collection_abusive_en = 'abusive_en_1',
    collection_abusive_fr = 'abusive_fr_1',
    collection_news_es= 'news_es_1',
    collection_news_en= 'news_en_1',
    collection_news_fr= 'news_en_1',
    collection_normal_es='normal_es_1',
    collection_normal_en='normal_en_1',
    collection_normal_fr='normal_fr_1',
    news_sarcasm_abusive_normal='news_sarcasm_abusive_normal',
    sarcasm_abusive_normal='sarcasm_abusive_normal',
    abusive_normal='abusive_normal',
    sarcasm_normal='sarcasm_normal',
    news_abusive='news_abusive',
    news_and_sarcasm='news_and_sarcasm'


)

# create twitter app to access Twitter Streaming API (https://apps.twitter.com)

TWITTER = dict(
    consumer_key = 'oPuLdZnU91aUBfpYTNSnSwKjn',
    consumer_secret = 'j5MnqSaHT3wg4n6ZitNPPUFfciuBjlceTd2mwNBWuZlMPSJd5H',
    access_token = '782482888180641792-sXN4pW3IJQYcLz32SAcAcWkQAkKyoAS',
    access_secret = '9lpu0qvMrjKC08AQrBeeQBquCzof852w1kMrS91F5yTJu'
)
