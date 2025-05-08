import streamlit as st
import pandas as pd
import ast  # We may need this to safely parse e.g. lists of image URLs from CSV
import os 

def show_matchup(index, total):
    """
    Displays the matchup for the current row from st.session_state.df,
    and shows feedback buttons to record if the user is happy with the judge's decision.
    """
    row = st.session_state.df.iloc[index]
    
    st.subheader(f"Matchup {index + 1} of {total}")
    st.write(f"**Matchup Description:** {row['Matchup']}")

    # Show original CN
    with st.expander("Original Community Note"):
        st.write(row["Original_CN"])

    # Layout for the two generated notes side by side
    colA, colB = st.columns(2)

    # Figure out which note was chosen as winner for highlighting
    comp = row["Matchup"].split(" vs ")

    st.markdown(f"**Winner:** {row['Winner']}")


    a_cn = row["A's CN"]
    b_cn = row["B's CN"]

    print(row.keys())

    a_accurate = int(row["A's Accuracy"]) == 1
    b_accurate = int(row["B's Accuracy"]) == 1

    # --- A's side ---
    with colA:
        st.markdown(f"### {comp[0]}")
        # If the left side won:
        if a_accurate:
            st.markdown("A was labelled as **accurate**", unsafe_allow_html=True)
        else:
            st.markdown("A was labelled as **inaccurate**", unsafe_allow_html=True)
        st.markdown(f"**A's Note**<br>{a_cn}", unsafe_allow_html=True)


    # --- B's side ---
    with colB:
        st.markdown(f"### {comp[1]}")
        if b_accurate:
            st.markdown("B was labelled as **accurate**", unsafe_allow_html=True)
        else:
            st.markdown("B was labelled as **inaccurate**", unsafe_allow_html=True)
        st.markdown(f"**B's Note**<br>{b_cn}", unsafe_allow_html=True)

    # LLM explanation and ELO details
    with st.expander("LLM Reason for Choosing Winner"):
        st.write(row["Reason"])

    st.write(f"A's Elo After: {row['A_New_ELO']:.2f}")
    st.write(f"B's Elo After: {row['B_New_ELO']:.2f}")

    # Display current feedback status
    feedback = row.get("user-agree", None)
    if pd.isna(feedback) or feedback is None:
        st.write("No feedback given yet.")
    elif feedback == True:
        st.write("Feedback: Agree with the decision.")
    elif feedback == False:
        st.write("Feedback: Disagree with the decision.")

    # Add feedback buttons side by side
    col_feedback1, col_feedback2 = st.columns(2)
    if col_feedback1.button("Agree", key=f"happy_{index}"):
        st.session_state.df.loc[index, "user-agree"] = True
        st.success("Feedback saved: Happy with the decision.")
    if col_feedback2.button("Disagree", key=f"not_happy_{index}"):
        st.session_state.df.loc[index, "user-agree"] = False
        st.success("Feedback saved: Not happy with the decision.")
    if st.button("Reset Feedback", key=f"reset_feedback_{index}"):
        st.session_state.df.loc[index, "user-agree"] = None
        st.success("Feedback reset.")
    st.text_input("Feedback Reason", key=f"feedback_reason_{index}", value=row.get("user-agree-reason", ""))
    if st.button("Save Feedback", key=f"save_feedback_{index}"):
        # Collect the feedback reason
        feedback_reason = st.session_state[f"feedback_reason_{index}"]
        # Save the feedback reason to the DataFrame
        st.session_state.df.loc[index, "user-agree-reason"] = feedback_reason
        # Save the DataFrame to a CSV file
        st.session_state.df.to_csv("feedback_results.csv", index=False)
        path = os.path.join(os.getcwd(), "feedback_results.csv")
        st.success(f"Feedback saved to {path}")

    # --- Show matching test set data, if loaded and found ---
    if "df_test" in st.session_state:
        test_data = st.session_state.df_test
        # Adjust to your actual column name in matchups CSV that references the ID:
        match_id = row["Id"]  

        # Attempt to match on test_data["id"] == row["ID"]
        matched_rows = test_data[test_data["id"] == match_id]

        if not matched_rows.empty:
            # If there's more than one match, we handle the first; adjust as you see fit
            test_row = matched_rows.iloc[0]

            with st.expander("Test Set Data for This Matchup"):
                # Show the text
                st.write("**Tweet text:**")
                st.write(test_row["text"])

                # If the CSV stores a list-string of URLs (e.g. "['url1', 'url2']"), parse it
                # If it's already a string or a single URL, adjust accordingly.
                if pd.notna(test_row["image_urls"]):
                    try:
                        # Safely parse if it looks like a Python list
                        urls = ast.literal_eval(test_row["image_urls"])
                        # If it’s actually just a string or something else, wrap in a list
                        if isinstance(urls, str):
                            urls = [urls]
                    except:
                        # If parsing fails, fallback to a single string
                        urls = [test_row["image_urls"]]

                    st.write("**Images:**")
                    st.write(urls)
                    for url in urls[0]:
                        st.write(url)
                        # If you want to show as an actual image inline:
                        st.image(url)

                # Show tweet URL
                if "tweet_url" in test_row:
                    st.write("**Tweet URL:**")
                    st.write(test_row["tweet_url"])

                # Optionally show other columns from the test set
                # (like reverse_image_search_results, dememe_reverse_image_search_results, etc.)
                # st.write(test_row["reverse_image_search_results"])
                # st.write(test_row["dememe_reverse_image_search_results"])
        else:
            st.info("No matching row found in the test set for this ID:  " + str(match_id))

def main():
    st.set_page_config(layout="wide")
    st.title("Community Note Matchup Explorer")

    # Track the current index of the matchup
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    # Primary CSV for matchups
    uploaded_matchups_file = st.file_uploader("Upload the matchups _results.csv file", type=["csv"])
    # Secondary CSV for test data
    uploaded_test_file = st.file_uploader("Upload the Test Set parquet file", type=["parquet"])

    if uploaded_test_file is not None:
        test_df = pd.read_parquet(uploaded_test_file)
        st.session_state.df_test = test_df
        st.success("Test set data loaded!")

    if uploaded_matchups_file is not None:
        df = pd.read_csv(uploaded_matchups_file)

        # Add a "user-agree" column if it doesn't exist
        if "user-agree" not in df.columns:
            df["user-agree"] = None
        if "user-agree-reason" not in df.columns:
            df["user-agree-reason"] = None

        # Ensure the "Matchup" column exists
        if "Matchup" not in df.columns:
            st.error("The uploaded matchups CSV does not contain a 'Matchup' column. Make sure you upload a '<datasetname>_results.csv' file produced by `ranking.py`. Do not upload the ranking csv.")
            return
        
        # Store the DataFrame in session_state if not already stored
        if "df" not in st.session_state:
            st.session_state.df = df
        
        total_rows = len(st.session_state.df)
        st.write(f"Loaded {total_rows} matchups.")
        
        # Navigation buttons for previous/next matchup
        col_left, col_right = st.columns([1, 1])
        if col_left.button("⬅ Previous"):
            st.session_state.current_index = max(st.session_state.current_index - 1, 0)
        if col_right.button("Next ➡"):
            st.session_state.current_index = min(st.session_state.current_index + 1, total_rows - 1)
        
        # Show the current matchup along with feedback buttons
        show_matchup(st.session_state.current_index, total_rows)
    else:
        st.info("Please upload a CSV file for the matchups to continue.")

if __name__ == "__main__":
    main()
