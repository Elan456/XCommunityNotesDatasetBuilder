import streamlit as st
import pandas as pd

def show_matchup(row, index, total):
    """
    Displays the matchup for a single row from the DataFrame.
    Highlights the winner and shows reason, original CN, etc.
    """
    
    st.subheader(f"Matchup {index + 1} of {total}")
    st.write(f"**Matchup Description:** {row['Matchup']}")
    
    # Show original CN
    with st.expander("Original Community Note"):
        st.write(row["Original_CN"])
    
    # Layout for the two generated notes side by side
    colA, colB = st.columns(2)
    
    # Winner logic
    winner = row["Winner"].strip()  # e.g. 'gemini_multishot_cng'
    
    # Decide which note is highlighted
    if "A:" in row["Matchup"]:
        # By convention, we can assume "A's CN" is always the "A" note, "B's CN" is the "B" note
        # But ensure logic matches your CSV naming
        a_title = "A's CN"
        b_title = "B's CN"
    else:
        # If the CSV is structured differently, adjust accordingly
        # For this example, we’ll just assume "A's CN" and "B's CN" are the columns.
        a_title = "A's CN"
        b_title = "B's CN"
    
    # Styling for winner vs loser
    highlight_style = """
        background-color: #d8f0da; 
        padding: 10px; 
        border-radius: 5px;
    """
    normal_style = """
        background-color: #f9f9f9; 
        padding: 10px; 
        border-radius: 5px;
    """
    
    # If the row's "Winner" is "gemini_multishot_cng", highlight A's CN
    # If it's "gemini_ris_cng", highlight B's CN, etc.
    
    # You could also incorporate logic if your row["Winner"] specifically says "A" or "B".
    # But for now, let's just match strings: if row['Winner'] in the matchup's A side, highlight A. Otherwise highlight B.
    
    # For a quick approach, check if the row['Winner'] is in "A:" portion of the matchup string:
    # (e.g. "A: gemini_multishot_cng vs B: gemini_multishot_cng_gg")
    # But if you have a stable naming convention, just match exactly:
    is_a_winner = (row['Winner'] in row['Matchup'].split(" vs ")[0])
    
    comp = row["Matchup"].split(" vs ")

    # Show A side
    with colA:
        st.markdown(f"# {comp[0]}")
        # Winner highlight if is_a_winner
        if is_a_winner:
            st.markdown(f"**A's Note (Chosen Winner)**<br>{row[a_title]}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"**A's Note**<br>{row[a_title]}</div>", unsafe_allow_html=True)
    
    # Show B side
    with colB:
        st.markdown(f"# {comp[1]}")
        if not is_a_winner:
            st.markdown(f"**B's Note (Chosen Winner)**<br>{row[b_title]}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"**B's Note**<br>{row[b_title]}</div>", unsafe_allow_html=True)
    
    # Show the reason the LLM chose the winner
    with st.expander("LLM Reason for Choosing Winner"):
        st.write(row["Reason"])
    
    # Show updated ELO or any other fields you want:
    st.write(f"**ELO After Winner:** {row['ELO_After_Winner']}")
    st.write(f"**ELO After Loser:** {row['ELO_After_Loser']}")

def main():
    st.set_page_config(layout="wide")
    st.title("Community Note Matchup Explorer")

    # Have a place in session_state to track the current index
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    
    uploaded_file = st.file_uploader("Upload the CSV file here", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        # Sanity check: show how many rows
        st.write(f"Loaded {len(df)} matchups.")

        # Buttons to navigate
        col_left, col_right = st.columns([1,1])

        # "Back" button
        if col_left.button("⬅ Previous", disabled=(st.session_state.current_index == 0)):
            st.session_state.current_index -= 1

        # "Next" button
        if col_right.button("Next ➡", disabled=(st.session_state.current_index == len(df) - 1)):
            st.session_state.current_index += 1
        
        # Show the current matchup
        current_row = df.iloc[st.session_state.current_index]
        show_matchup(current_row, st.session_state.current_index, len(df))
    
    else:
        st.info("Please upload a CSV file to continue.")

if __name__ == "__main__":
    main()
