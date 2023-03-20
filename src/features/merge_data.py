import pandas as pd
import os
import glob


path = os.getcwd()
src_folder = os.path.abspath(os.path.join(path, os.pardir))
project_folder = os.path.abspath(os.path.join(src_folder, os.pardir))
outside_folder = os.path.abspath(os.path.join(project_folder, os.pardir))
data_folder = outside_folder + '/sb-mirror'
csv_files = glob.glob(os.path.join(data_folder + '/processed_data', "*.csv"))

df_list = []
for f in csv_files:
    df = pd.read_csv(f)
    df_list.append(df)

processed_transcripts = pd.concat(df_list)


if __name__ == '__main__':
    # Concat processed transcripts
    processed_transcripts.to_csv(data_folder + '/processed_transcripts.csv')
    full_channel_df = pd.read_csv(data_folder + '/full_channel_df.csv')
    full_channel_df = full_channel_df.reset_index().rename(columns={'Unnamed: 0': 'channelID'})
    transcript_topic_statistic = processed_transcripts.merge(full_channel_df, how='left', on='channelID')

    df = transcript_topic_statistic[['videoID', 'Transcript', 'channelID', 'title', 'published',
                                     'sponsored', 'processed_transcript', 'total_views', 'subscribers',
                                     'hidden_subscribers', 'num_videos', 'topics']]
    df.to_csv(data_folder + '/transcript_topic_statistic.csv')


