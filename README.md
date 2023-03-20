# Sponsoring  Recommendation

## Summary of the project

The purpose of the project is to work in close collaboration with companies that wants to sponsor content creators in exchange of an advertisement of some sort.

### Project organization
```bash                    
├── images                  # Images to display features on Readme
├── src
│   ├── exploration         # Jupyter notebooks to explore data
│   │   ├──  1.0-data_first_look.ipynb
│   │   ├──  1.1-preprocess_transcript.ipynb
│   │   ├──  1.2-sentiment_dictinary.ipynb
│   │   ├──  1.3-transcript_topic_modelling.ipynb
│   │   ├──  1.4-unsupervised_sentiment_analysis.ipynb
│   │   ├──  1.5-unsupervised_learning.ipynb
│   ├── features            # Used to generate the data necessary to train our model
│   │   ├── video_transcripts.py  # Get around 110K transcripts of videos:
│   │   ├── process_transcript.py  # Process transcripts from video_transcripts.py and save it as: processed_transcript_videos_df.csv 
│   │   ├── youtube_statistics.py  # Get the channel statistics for Youtuber with more than 20 videos
│   │   ├── merge_data.py   # Merge Channel statistics and processed transcripts
│   │   ├── api_call_output.csv   # Output of youtube_statistics.py
│   │   ├── sample.json     # Un-processed Channel statistics 
├── model                   # Train and save models and the corresponding scalers 
│   │   ├── word2vec.py  # Main function: Apply word2vec to our processed transcript: processed_transcript_videos_df.csv 
│   │   ├── app.py  # A CLI app to group videos together based on user's search
│   │   ├── DocSim.py  # Calculates similarity scores between given source document & all the target documents
│   │   ├── full_word2vec.model  # word2vec model(need to run word2vec.py to generate it locally, it's more than 1G)
├── .gitignore            
├── requirements.txt
└── README.md               # The top-level README for developers using this project.
```

### How to run code?
First, you need to create your virtual environment using `requirements.txt`. <br/>
you need to generate `word2vec.model` locally since it's more than 1G. <br/>
Then, using the below code to run app. <br/>
- cd src/models
- python app.py -h
- python app.py -p 'video_game' -k 'csgo' -s 10000 -v 20 -t 1000000
- copy and paste the channel ID to Command line
- Click the link

### Finding the right content creator
The first feature of our project is to categorise content creators. In fact, the most important concern for sponsors is to have an audience that will relate to the product and potentially buy it. Then, once in a category, content creators will be rated and searched based on the statistics of their channels and the cosine similarity of keywords.

![page 1](images/page1_kaggle.PNG)

![page 2](images/page2_kaggle.PNG)


