# Community Note Generation

The package contains scripts for generating Twitter community notes using a variety of methods. It also contains scripts for ranking, evaluating, and comparing the generated notes against each other and the original notes. 

## Generate a community note 

To generate a community note, look in the `gemini` and `llama` folders. Then contain modules with functions for generating community notes using the respective models.
These functions can be passed into the `generate` function in the `generator.py` module. 

## Ranking

### Running an ELO Tournament

To compare community notes, we have a judge LLM pick between two generated community notes at a time, picking which one matches the orignal community note the best or has better sources. See `gcn_scorer.py` for the scoring function and judge prompt. 

`ranking.py` is a script to generate a bunch of community notes and then pass them into a ELO tournament to see which ones perform the best. 
The `rank` function in `gcn_scorer.py` is used to conduct the ELO tournament.

`ranking.py` produces pair of csv files, describing the ELO tournament and the final rankings. The `<datasetname>_ranking.csv` shows the final rankings of the generation methods.
THe `<datasetname>_results.csv` shows the results of each matchup in the ELO tournament. These results can be visualized to go through each matchup and see if the correct community note was chosen as the winner and the system is working correctly.

### Visualizing the ELO Tournament

We created a Streamlit app to visualize each matchup in the ELO tournament. 

#### 1. Install Dependencies

Download all the dependencies in the project root using pip. 
```bash
pip install -r requirements.txt
```

#### 2. Run the Streamlit App

The app at: `misleading_image\community_note_generation\app.py`
```bash
streamlit run app.py
```

#### 3. Upload the results.csv from running `ranking.py` 

The app will ask you to upload the results.csv file. This file contains the results of each matchup in the ELO tournament.
Once this is uploaded, you'll be able to start going through each matchup. 

#### 4. Upload the test set parquet file (optional, but recommended)

Prior to running the ELO tournament, a test set of tweets + community notes was created. This test set contains all the additional information about the 
tweets. The extra context makes it much easier to understand the context of the community notes and the tweets.

The Streamlit App will ask you to upload the test set parquet file. Upload this will add the extra context to the app, including the tweet's text, image, and link.

On the app, simply scroll down to the "Test data for this matchup" expansion panel. This will show the tweet text, image, and link.

#### 5. Give feedback on the matchups

On each matchup, the app gives you the options of "Agree" or "Disagree" with the judge's choice. You can also write the reasoning for your choice.
After selecting the feedback option, click "Save Feedback" to write a new CSV file with the feedback.
