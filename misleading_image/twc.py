class TweetWithContext:
    def __init__(self, text: str, image_path: str, community_note: str):
        """
        A class representing a tweet with its text, image path, and community note.

        Args:
            text (str): The tweet's text content.
            image_path (str): The file path to the tweet's image.
            community_note (str): The community note text associated with the tweet.
        """
        self.text = text
        self.image_path = image_path
        self.community_note = community_note

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
