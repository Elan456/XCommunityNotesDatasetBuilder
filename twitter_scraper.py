import asyncio
from twscrape import API, AccountsPool, gather


def get_accounts(accounts_str):
    # Reading from accounts.csv where the info is seperated by colons, not commas
    accounts = []
    for account in accounts_str.split(","):
        values = [v.strip() for v in account.split(":")]
        accounts.append(values)

    return accounts


def format_tweets(tweets):
    formatted_tweets = []
    for tweet in tweets:
        mentions = []
        for mention in tweet.mentionedUsers:
            mentions.append(mention.username)

        coordinates = [None, None]
        if tweet.coordinates is not None:
            coordinates = [tweet.coordinates.longitude, tweet.coordinates.latitude]

        links = []
        for link in tweet.links:
            links.append(link.url)

        image_urls = []
        for photo in tweet.media.photos:
            image_urls.append(photo.url)
        # for video in tweet.media.videos:
        #     video_urls.append(video.thumbnailUrl)

        links = []
        for link in tweet.links:
            links.append(link.url)

        place = tweet.place.fullName if tweet.place is not None else "NA"

        formatted_tweet = {
            "id": tweet.id,
            "text": tweet.rawContent,
            "date": tweet.date,
            "author_id": tweet.user.id,
            "author_name": tweet.user.username,
            "retweets": tweet.retweetCount,
            "lang": tweet.lang,
            "mentions": mentions,
            "hashtags": tweet.hashtags,
            "coordinates": coordinates,
            "place": place,
            "url": tweet.url,
            "image_urls": image_urls,
            "links": links,
        }
        formatted_tweets.append(formatted_tweet)

    return formatted_tweets


async def a_grab_tweets(keywords, tweet_count, must_have_images, start, end, **kwargs):
    # Setting up the accounts pool
    pool = AccountsPool()
    for account in get_accounts(kwargs["twitter.accounts"]):
        await pool.add_account(*account)

    # Logging in to all new accounts
    # yield ProgressUpdate(0, "Logging in to Twitter accounts...")
    await pool.login_all()

    print("Logged in to Twitter accounts")

    # Creating an API object
    api = API(pool)

    # Search API (latest tab)
    query = keywords[:]

    if start is not None:
        query += f" since:{start}"
    if end is not None:
        query += f" until:{end}"
    if must_have_images:
        query += " filter:images"

    # yield ProgressUpdate(0, "Searching for tweets...")
    generator = api.search(query, limit=tweet_count)
    tweets = await gather(generator)
    # yield ProgressUpdate(1, "Formatting tweets...")

    formatted_tweets = format_tweets(tweets)
    # yield formatted_tweets
    return formatted_tweets


async def get_tweet_by_id(tweet_id, twitter_accounts=None):
    """
    Given a tweet ID, returns the tweet's content in a dictionary format.
    If no Twitter accounts str is provided, it will be loaded from the `accounts.txt` file.
    """

    if twitter_accounts is None:
        with open("accounts.txt", "r") as f:
            twitter_accounts = f.read()

    # Setting up the accounts pool
    pool = AccountsPool()
    for account in get_accounts(twitter_accounts):
        await pool.add_account(*account)

    # Logging in to all new accounts
    await pool.login_all()

    # Creating an API object
    api = API(pool)

    tweet = await api.tweet_details(tweet_id)
    print(tweet)

    return tweet



if __name__ == "__main__":
    # Example usage of getting a tweet by ID
    tweet_id = "1687169266754158592"
    tweet = asyncio.run(get_tweet_by_id(tweet_id))
    