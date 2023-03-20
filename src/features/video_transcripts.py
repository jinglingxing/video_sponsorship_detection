import pandas as pd
import numpy as np
import os
import glob
from typing import List
from youtube_transcript_api import YouTubeTranscriptApi
import json
from os import listdir


# Find data folder
path = os.getcwd()
print("Current Directory", path)
src_folder = os.path.abspath(os.path.join(path, os.pardir))
project_folder = os.path.abspath(os.path.join(src_folder, os.pardir))
outside_folder = os.path.abspath(os.path.join(project_folder, os.pardir))
data_folder = outside_folder + '/sb-mirror'

# Use glob to get all the csv files in the folder
csv_files = glob.glob(os.path.join(data_folder, "*.csv"))
file_mapper = list(map(lambda file: pd.read_csv(file), csv_files))
file_names = [file.rsplit('/')[-1] for file in csv_files]
df_names = [name.split('.')[0] for name in file_names]
print('Read all the csv files from SponsorBlocker')

# Find the video info: videoID, channelID, title, published
df_dict = {name: file for name, file in zip(df_names, file_mapper)}
video_info = df_dict['videoInfo']

# Add a new column: sponsored
video_info['sponsored'] = np.where(video_info['videoID'].isin(video_info['videoID']), True, False)
video_info.to_csv(data_folder + '/video_info_with_sponsor.csv')

video_list = video_info['videoID'].unique()
no_english_transcript = []
transcript_save_path = data_folder + '/new_transcript'


def get_transcript(videos: List[str]) -> None:
    """
    :param videos: input video list
    :return: Transcripts in a list
    """
    already_saved = set(os.listdir(transcript_save_path))

    for index, video_id in enumerate(videos):
        print(index, video_id)
        if f"{video_id}.json" in already_saved:
            continue
        try:
            complete_name = os.path.join(transcript_save_path, f"{video_id}.json")
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            with open(complete_name, "w") as outfile:
                outfile.write(json.dumps(transcript, indent=4))
        except:
            no_english_transcript.append(video_id)
            continue

    print('Task Completed: get transcripts!')


def labelling_data():
    label_data = {}
    for file_name in os.listdir(transcript_save_path):
        if '.json' not in file_name:
            continue
        video_id = file_name.split('.')[0]
        transcript_path = transcript_save_path + '/' + file_name
        with open(transcript_path, 'r') as f:
            data = json.load(f)
            sentences = [data[i]['text'] for i in range(len(data))]
            one_transcript = '. '.join(sentences)
            label_data[video_id] = one_transcript
    labelled_df = pd.DataFrame.from_dict(label_data, orient='index', columns=['Transcript']).reset_index().rename(
        columns={'index': 'videoID'})
    return labelled_df


if __name__ == '__main__':
    # Run get_transcript to get transcripts from Youtube API
    # get_transcript(video_list)
    labelled_df = labelling_data()
    print(len(labelled_df))
    video_trancript_info = labelled_df.merge(video_info, how='left', on='videoID')
    video_trancript_info.to_csv(data_folder + '/video_transcripts_dataframe.csv')

