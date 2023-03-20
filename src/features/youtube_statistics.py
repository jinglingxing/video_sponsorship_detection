import os
import requests
import pandas as pd
from typing import List, Dict, Tuple
import csv


def create_url(channel_id: str, resource: str):
    """
    :param channel_id: name of the channel (ie: rachelsenglish)
    :param resource: name of the resource you want (ie: topicDetails, statistics, ...)
    :return: the URL of one channel
    """
    key = os.getenv("API_KEY")
    return f'https://www.googleapis.com/youtube/v3/channels?key={key}&id={channel_id}&part={resource}'


def make_api_call(channel_id: str, resource: str):
    """
    :param channel_id: name of the channel (ie: rachelsenglish)
    :param resource: name of the resource you want (ie: topicDetails, statistics, ...)
    :return: a JSON file
    """
    try:
        r = requests.get(create_url(channel_id, resource))
        if r.status_code != 200:
            print(f"status code not ok: {r.status_code}")
        return r.json()
    except requests.RequestException as e:
        print(f"an error occurred {e}")


def get_statistics(channel_id: str):
    """
    :param channel_id: name of the channel (ie: rachelsenglish)
    :return: get the statistic of channels
    """
    return make_api_call(channel_id, "statistics")


def get_topics(channel_id: str):
    """
    :param channel_id: name of the channel (ie: rachelsenglish)
    :return: get the topic details of channels
    """
    return make_api_call(channel_id, "topicDetails")


def get_video_url(video_id: str, resource: str) -> str:
    """
    :param video_id: video ID
    :param resource: name of the resource you want (ie: topicDetails, statistics, ...)
    :return: the URL of one channel
    """
    key = os.getenv('API_KEY')
    return f"https://www.googleapis.com/youtube/v3/videos?key={key}&id={video_id}&part={resource}"


def get_video_statistics(video_id: str):
    """
    :param video_id: video ID
    :return: a JSON file of statistics
    """
    try:
        r = requests.get(get_video_url(video_id, "statistics"))
        return r.json()
    except:
        print(f"error when requesting statistics for video_id: '{video_id}'")


def get_video_topics(video_id: str):
    try:
        r = requests.get(get_video_url(video_id, "topicDetails"))
        return r.json()
    except:
        print(f"error when requesting topics for video_id: '{video_id}'")


def get_video_topic_statistics(video_id: str):
    """
    :param video_id: video ID
    :return: topics, views, likes, favorites, comments of each video
    """
    try:
        topic_links = get_video_topics(video_id)['items'][0]['topicDetails']['topicCategories']
        topics = [v.split('/')[-1] for v in topic_links]
    except (KeyError, IndexError):
        topics = []
    try:
        statistics = get_video_statistics(video_id)['items'][0]['statistics']
        views, likes, favorites, comments = statistics['viewCount'], statistics['likeCount'], statistics[
            'favoriteCount'], statistics['commentCount']
    except (KeyError, IndexError):
        views, likes, favorites, comments = 0, 0, 0, 0
    return [topics, views, likes, favorites, comments]


def get_channel_statistics(channel_id: str):
    """

    :param channel_id: channel ID
    :return: topic_categories, total_views, subscribers, hidden_subscribers, videos of each channel
    """
    try:
        topic_categories_links = get_topics(channel_id)['items'][0]['topicDetails']['topicCategories']
        topic_categories = [v.split('/')[-1] for v in topic_categories_links]
    except (KeyError, IndexError):
        print('channel_id', channel_id)
        topic_categories = []
    try:
        c_statistics = get_statistics(channel_id)['items'][0]['statistics']
        total_views, subscribers, hidden_subscribers, videos = c_statistics['viewCount'], c_statistics[
            'subscriberCount'], c_statistics['hiddenSubscriberCount'], c_statistics['videoCount']
    except (KeyError, IndexError):
        total_views, subscribers, hidden_subscribers, videos = 0, 0, 0, 0
    return [topic_categories, total_views, subscribers, hidden_subscribers, videos]


def get_channels_topics_statistics(channel_ids: List[str]):
    """
    :param channel_ids: ids of channels
    :return: a json of information
    """
    return make_api_call(','.join(channel_ids), "topicDetails,statistics")  # id1,id2,id3


def extract_topics_from_response(response: Dict) -> List[str]:
    try:
        topic_categories_links = response['topicDetails']['topicCategories']
        topic_categories = [v.split('/')[-1] for v in topic_categories_links]
    except (KeyError, IndexError):
        topic_categories = []

    return topic_categories


def extract_statistics_from_response(response: Dict) -> Tuple[float, float, float, float]:
    try:
        c_statistics = response['statistics']
        total_views, subscribers, hidden_subscribers, num_videos = c_statistics['viewCount'], c_statistics[
            'subscriberCount'], c_statistics['hiddenSubscriberCount'], c_statistics['videoCount']
    except (KeyError, IndexError):
        total_views, subscribers, hidden_subscribers, num_videos = 0, 0, 0, 0
    return [total_views, subscribers, hidden_subscribers, num_videos]


def add_channel_topics_statistics(channel_ids: List[str]) -> Dict[str, List[str]]:
    """
    :param channel_ids:
    :return:
    """
    res = dict()
    batch = len(channel_ids) // 10
    for i in range(batch+1):
        print("i", i, "batch", batch)
        try:
            batch_channel_ids = channel_ids[i * 10: (i+1) * 10]
            batch_json = get_channels_topics_statistics(batch_channel_ids)
            items = batch_json['items']
            for item in items:
                try:
                    total_views, subscribers, hidden_subscribers, num_videos = extract_statistics_from_response(item)
                    topics = extract_topics_from_response(item)
                    res[item['id']] = [total_views, subscribers, hidden_subscribers, num_videos, topics]
                    w.writerow([item['id'], total_views, subscribers, hidden_subscribers, num_videos, topics])
                except KeyError:
                    continue
        except IndexError:
            continue

    # check if there's any diff:
    leftovers = list(set(channel_ids) - set(list(res.keys())))
    if leftovers:
        print("The following channel_ids were not extracted in the result: ", leftovers)

    return res


if __name__ == '__main__':

    path = os.getcwd()
    src_folder = os.path.abspath(os.path.join(path, os.pardir))
    project_folder = os.path.abspath(os.path.join(src_folder, os.pardir))
    outside_folder = os.path.abspath(os.path.join(project_folder, os.pardir))
    data_folder = outside_folder + '/sb-mirror'
    transcript_save_path = data_folder + '/video_transcripts_dataframe.csv'
    df = pd.read_csv(transcript_save_path)

    # Write info from API call in the output
    w = csv.writer(open("api_call_output.csv", "w"))

    channel_id_list = list(set(df['channelID']))[1:]
    channel_dict = add_channel_topics_statistics(channel_id_list)
    channel_df = pd.DataFrame.from_dict(channel_dict, orient='index', columns=['total_views',
                                                                               'subscribers',
                                                                               'hidden_subscribers',
                                                                               'num_videos',
                                                                               'topics'])
    channel_df.to_csv(data_folder + '/full_channel_df.csv')


