"""
This script uses vectorized transcripts to analyze and group the similar videos together.
- Apply K-means to separate video category
- Find the video category from Youtube API
- For each video category, we recommend several channels based on users requirements:
- Channel information: 'topic_categories', 'total_views', 'subscribers', 'hidden_subscribers', 'videos'

"""
from gensim.models import Word2Vec
import sys
import os
import pandas as pd
from DocSim import DocSim
import getopt


if __name__ == '__main__':
    # User Interface
    commands_input = '''
    Command (separator for points coordinates is a comma):
    - Product category: -p --product-category
    - Product key words: -k --keywords
    - Minimum subscribers: -s --subscribers
    - Minimum number of videos: -v --num-videos
    - Minimum number of total views: -t --num-total-views
    - exit
    example: python app.py -p 'video_game' -k 'csgo' -s 10000 -v 20 -t 1000000
    '''

    print('Program started! ')
    keywords = ''
    product_category = ''
    subscribers = 0
    num_videos = 0
    num_total_views = 0
    opts, args = getopt.getopt(sys.argv[1:], "hp:k:s:v:t:", ["product-category=", "keywords=", "subscribers=", "num-videos=", "num-total-views="])
    for opt, arg in opts:
        if opt == '-h':
            print(commands_input)
            sys.exit()
        elif opt in ("-p", "--product-category"):
            product_category = arg
        elif opt in ("-k", "--keyword"):
            keywords = arg
        elif opt in ("-s", "--subscribers"):
            subscribers = int(arg)
        elif opt in ("-v", "--num-videos"):
            num_videos = int(arg)
        elif opt in ("-t", "--num-total-views"):
            num_total_views = int(arg)

    if not keywords or not product_category:
        print("You need to enter a value of keywords you wish to search for, see helper (-h)")
        sys.exit(1)
    model = Word2Vec.load('full_word2vec.model')
    word_vectors = model.wv

    path = os.getcwd()
    src_folder = os.path.abspath(os.path.join(path, os.pardir))
    project_folder = os.path.abspath(os.path.join(src_folder, os.pardir))
    outside_folder = os.path.abspath(os.path.join(project_folder, os.pardir))
    data_folder = outside_folder + '/sb-mirror'
    processed_sponsor_df = pd.read_csv(data_folder + '/transcript_topic_statistic.csv', index_col=[0])

    processed_sponsor_df['transcript_list'] = processed_sponsor_df['processed_transcript'].apply(
        lambda elem: elem.strip('][').replace('\'', '').replace(',', ''))

    topics = []
    for i in range(len(processed_sponsor_df)):
        try:
            topic_list = processed_sponsor_df['topics'][i].strip("[]").replace("'", '').split(',')
        except AttributeError:
            topic_list = ['no topics']
        topics.append(topic_list)

    processed_sponsor_df['topic_list'] = pd.Series(topics)

    topic_df = pd.DataFrame(processed_sponsor_df['topic_list'].tolist())
    topic_df = topic_df.add_prefix('topic_')
    final_df = pd.concat([processed_sponsor_df, topic_df], axis=1)

    filter_topics_df = final_df[final_df['topic_0'].str.contains(product_category) |
                                final_df['topic_1'].str.contains(product_category) |
                                final_df['topic_2'].str.contains(product_category) |
                                final_df['topic_3'].str.contains(product_category) |
                                final_df['topic_4'].str.contains(product_category) |
                                final_df['topic_5'].str.contains(product_category) |
                                final_df['topic_6'].str.contains(product_category) |
                                final_df['topic_7'].str.contains(product_category) |
                                final_df['topic_8'].str.contains(product_category)]

    filter_topics_df = filter_topics_df.drop_duplicates(subset=['channelID'])
    filter_subscribers_df = filter_topics_df[(filter_topics_df['subscribers'] >= subscribers) &
                                             (filter_topics_df['num_videos'] >= num_videos) &
                                             (filter_topics_df['total_views'] >= num_total_views)]

    ds = DocSim(model.wv)

    source_doc = keywords
    target_docs = list(filter_subscribers_df['transcript_list'])
    channel_ids = list(filter_subscribers_df['channelID'])
    sim_scores = ds.calculate_similarity(source_doc, target_docs, channel_ids, 0.35)

    print(pd.DataFrame(sim_scores))

    try:
        while True:
            channel_id = input("Enter channel id > ")
            print(f"You can copy paste the following link in your browser: 'https://www.youtube.com/channel/{channel_id}'")
    except [KeyboardInterrupt, SystemError, SystemExit]:
        sys.exit()

