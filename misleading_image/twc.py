import requests
from PIL import Image

class TweetWithContext:
    def __init__(self, text: str, image_path_or_url: str, community_note: str, id: str = None):
        """
        A class representing a tweet with its text, image path, and community note.

        Args:
            text (str): The tweet's text content.
            image_path (str): The file path to the tweet's image or a URL to download the image from.
            community_note (str): The community note text associated with the tweet.
        """
        self.text = text
        self.image: Image = self.download_image_to_PIL(image_path_or_url) if image_path_or_url.startswith("http") else self.load_image_to_PIL(image_path_or_url)
        self.community_note = community_note
        self.id = id

    @staticmethod
    def download_image_to_PIL(image_url: str):
        """
        Download the image from the URL and convert it to a PIL Image object.
        """
        # print(f"Downloading image from {image_url}...") 
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image from {image_url}: {e}")
            return None
        return Image.open(response.raw)

    @staticmethod
    def load_image_to_PIL(image_path: str):
        """
        Load the image from the file path and convert it to a PIL Image object.
        """
        return Image.open(image_path)


    def __repr__(self):
        return (f"TweetWithContext(text='{self.text[:30]}...', "
                f"image_path='{self.image_path}', "
                f"community_note='{self.community_note[:30]}...')")

    def to_dict(self):
        """
        Convert the tweet object to a dictionary.
        """
        return {
            "text": self.text,
            "image_path": self.image_path,
            "community_note": self.community_note,
        }
