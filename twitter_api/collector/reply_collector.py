from .base_collector import TwitterCollector

class ReplyTwitterCollector(TwitterCollector):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def get_replies_from_keywords(self, or_keywords, and_keywords):
        """
        Will find replies that have any of the or_keywords or all of the and_keywords
        """

        if not or_keywords and not and_keywords:
            raise ValueError("Must provide at least one keyword")
        
        if or_keywords and and_keywords:
            raise ValueError("Can only provide one type of keyword, or or and")
        
        ...  # TODO: Implement this method