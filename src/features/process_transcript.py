import nltk
import os
import pandas as pd
import spacy
from nltk.corpus import stopwords
from tqdm import tqdm


path = os.getcwd()
src_folder = os.path.abspath(os.path.join(path, os.pardir))
project_folder = os.path.abspath(os.path.join(src_folder, os.pardir))
outside_folder = os.path.abspath(os.path.join(project_folder, os.pardir))
data_folder = outside_folder + '/sb-mirror'
df_save_path = data_folder + '/video_transcripts_dataframe.csv'

# Initialize tqdm for pandas
tqdm.pandas()


def preprocess(one_transcript: str):
    # Lemmatisation
    try:
        tokenized_transcript = nltk.word_tokenize(one_transcript)
        sponsor_lemma = nltk.WordNetLemmatizer()
        lemmatized_transcript = ' '.join([sponsor_lemma.lemmatize(t) for t in tokenized_transcript])
        lemmatized_transcript = lemmatized_transcript.lower()

        # Using spacy to lemmatize words to distinguish words with multiple meanings
        spacy_nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
        spacy_parse_transcript = spacy_nlp(lemmatized_transcript)
        spacy_transcript_list = [token.lemma_ for token in spacy_parse_transcript]

        # Remove stopwords
        stop_words_nltk = list(stopwords.words('english'))
        stop_words_spacy = spacy_nlp.Defaults.stop_words
        stop_words = stop_words_nltk + list(stop_words_spacy)
        without_stopwords = [word for word in spacy_transcript_list if word not in stop_words and len(word) > 3]
        return without_stopwords
    except ValueError:
        return []


processed_transcript_save_path = data_folder + '/processed_transcript_videos_df.csv'


def process_transcript():
    # Read data
    sponsor_df = pd.read_csv(df_save_path)
    # Using progress apply to function preprocess
    div = 10000
    num_loops = len(sponsor_df)//div+1
    for l in range(num_loops):
        sub_df = sponsor_df[l*div: (l+1)*div]
        sub_df['processed_transcript'] = sub_df['Transcript'].progress_apply(lambda x: preprocess(x))
        sub_df.to_csv(data_folder + '/processed_data' + f'/processed_transcript_{l}.csv')
        print(f'Saved processed_transcript_{l}')


if __name__ == '__main__':
    process_transcript()
    print('Finished processing transcripts ! ')
