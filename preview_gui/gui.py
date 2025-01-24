import streamlit as st
import json
from PIL import Image
import requests
from io import BytesIO

# make the app wider
st.set_page_config(layout="wide")

def display_tweet(tweet):

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.subheader(f"Tweet by {tweet['author_name']} (@{tweet['author_username']})")
        st.write(f"Date: {tweet['date']}")
        st.write(f"Retweets: {tweet['retweet_count']}")
        st.write(f"[View Tweet]({tweet['tweet_url']})")

    with col2:
        st.markdown("### Text")
        st.write(tweet['text'])

        st.markdown("### Images")
        for image_url in tweet['image_urls']:
            response = requests.get(image_url)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                st.image(img, caption=image_url, use_container_width=True)

    with col3:
        st.markdown("### LLM Classification")
        st.write(tweet['llm_image_classification'])

        st.markdown("### LLM Reasoning")
        st.write(tweet['full_llm_image_response'])

    st.markdown("### Community Note Summary")
    st.write(tweet['community_note']['summary'])

    if st.button("Show Full Community Note", key=f"expand_{tweet['id']}"):
        st.json(tweet['community_note'])

        
# Streamlit App
st.title("Twitter Community Notes Dataset Viewer")



# Load dataset
uploaded_file = st.file_uploader("Upload JSON File", type="json")
if uploaded_file:
    # uploaded_file.read() returns a bytes object, so we need to decode it to a string
    tweets = json.loads(uploaded_file.read().decode("utf-8"))

    if "index" not in st.session_state:
        st.session_state.index = 0

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("Previous"):
            st.session_state.index = max(0, st.session_state.index - 1)

    with col3:
        if st.button("Next"):
            st.session_state.index = min(len(tweets) - 1, st.session_state.index + 1)

    tweet = tweets[st.session_state.index]
    display_tweet(tweet)

else:
    st.info("Please upload a JSON file to preview the dataset.")
