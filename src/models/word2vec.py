import os
import pandas as pd
from gensim.models import Word2Vec
import multiprocessing
import ast
from gensim.models.phrases import Phrases, Phraser


path = os.getcwd()
src_folder = os.path.abspath(os.path.join(path, os.pardir))
project_folder = os.path.abspath(os.path.join(src_folder, os.pardir))
outside_folder = os.path.abspath(os.path.join(project_folder, os.pardir))
data_folder = outside_folder + '/sb-mirror'
processed_sponsor_df = pd.read_csv(data_folder + '/transcript_topic_statistic.csv')

print('Word to vector starting: ')
# Iterate rows for processed transcripts
transcripts = [ast.literal_eval(row) for row in processed_sponsor_df['processed_transcript']]

# create bi-gram subtitles
phrases = Phrases(transcripts, min_count=1, progress_per=5000)
bigram = Phraser(phrases)
subtitles = bigram[transcripts]


w2v_model = Word2Vec(min_count=3,
                     window=4,
                     vector_size=300,
                     sample=1e-5,
                     alpha=0.03,
                     min_alpha=0.0007,
                     negative=20,
                     workers=multiprocessing.cpu_count()-1)

w2v_model.build_vocab(subtitles, progress_per=50000)

# Train and save a Word2Vec model for subtitles
w2v_model.train(subtitles, total_examples=w2v_model.corpus_count, epochs=30, report_delay=1)
w2v_model.save("full_word2vec.model")
print('Word to vector finished! ')


