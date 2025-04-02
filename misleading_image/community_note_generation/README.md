# Community Note Generation

This package contains scripts for generating Twitter community notes using various methods. It also includes tools for ranking, evaluating, and comparing generated notes against each other and the original notes.

## Generating a Community Note

To generate a community note, look in the `gemini` and `llama` folders. These contain modules with functions for generating community notes using their respective models.  
These functions can be passed into the `generate` function in the `generator.py` module.

## Ranking

### Running an ELO Tournament

To compare community notes, we use a judge LLM that selects the better of two generated notes based on how well they match the original community note or how strong their sources are.  
See `gcn_scorer.py` for the scoring function and judge prompt.

The script `ranking.py` generates a batch of community notes and conducts an ELO tournament to determine the best-performing methods.  
The `rank` function in `gcn_scorer.py` executes the tournament.

`ranking.py` produces two CSV files summarizing the tournament:

- `<datasetname>_ranking.csv` — Contains the final rankings of the generation methods.
- `<datasetname>_results.csv` — Details each matchup in the ELO tournament. These results can be reviewed to verify whether the correct community note was selected as the winner.

### Visualizing the ELO Tournament

We provide a Streamlit app to visualize each matchup in the ELO tournament.

#### 1. Install Dependencies

Install all required dependencies in the project root using pip:

```bash
pip install -r requirements.txt
```

#### 2. Run the Streamlit App

Run the app from the `misleading_image/community_note_generation/` directory:

```bash
streamlit run app.py
```

#### 3. Upload the Results CSV from `ranking.py`

The app will prompt you to upload the `results.csv` file, which contains the outcomes of each matchup in the ELO tournament.  
Once uploaded, you'll be able to review each matchup.

#### 4. Upload the Test Set Parquet File (Optional but Recommended)

Before running the ELO tournament, a test set of tweets and their corresponding community notes is created. This test set includes additional information about the tweets, which provides context for evaluating the notes.

The Streamlit app will prompt you to upload this test set parquet file. Doing so will add extra details to the interface, including the tweet's text, image, and link.

To view this additional context, scroll down to the **"Test Data for This Matchup"** expansion panel in the app.

#### 5. Provide Feedback on the Matchups

For each matchup, the app allows you to select **"Agree"** or **"Disagree"** with the judge's choice. You can also provide a written explanation for your decision.  
After selecting your response, click **"Save Feedback"** to generate a new CSV file containing your feedback.