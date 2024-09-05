from fastapi import FastAPI
from tweeterpy import TweeterPy
from tweeterpy import config
from tweeterpy.util import RateLimitError, Tweet, User
from configparser import ConfigParser
import time, random
import csv


config = ConfigParser()
config.read('config.ini')
twitter = TweeterPy()

# login if required
# twitter.login(config['X']['username'], config['X']['password'])
twitter.generate_session("8a514c564589755b7724d1decbc1f3568a1efa22")

app = FastAPI()

def get_data(tweet, count):
    # Tweet_count, Username, Text, Created At, Retweets, Likes, Mentions, Sensitive
    res_list = [count, tweet.screen_name, tweet.full_text, tweet.created_at, tweet.quote_count, tweet.favorite_count, tweet.user_mentions, tweet.possibly_sensitive]

    # Convert list to a dictionary
    res_dict = {
        "count": res_list[0],
        "screen_name": res_list[1],
        "full_text": res_list[2],
        "created_at": res_list[3],
        "quote_count": res_list[4],
        "favorite_count": res_list[5],
        "user_mentions": res_list[6],
        "possibly_sensitive": res_list[7]
    }

    return res_dict, res_list

def get_tweets(username):
    MAX_TWEETS = 10
    user_tweets = []
    tweet_count  = 0
    has_more = True
    cursor = None
    while has_more:
        try:
            response = None
            response = twitter.get_user_tweets(username, end_cursor=cursor, total=MAX_TWEETS)
            for i in range(len(response['data'])):
                tweet = response['data'][i] 
                if tweet.get('entryId') != None and tweet.get('entryId').startswith('tweet-'):
                    user_tweets.append(response['data'][i])
                    tweet_count += 1

                    time.sleep(random.uniform(0.2, 0.5))

                    if tweet_count > MAX_TWEETS:
                        break

            break

            has_more = response.get('has_next_page')
            api_rate_limits = response.get('api_rate_limit')
            limit_exhausted = api_rate_limits.get('rate_limit_exhausted')
            if has_more:
                cursor = response.get('cursor_endpoint')
                time.sleep(random.uniform(7, 10))
            if limit_exhausted:
                raise RateLimitError
        except Exception as error:
            print(error)
            break

    result = []
    
    with open('tweets.csv', 'w', encoding="utf-8") as file:
        writer = csv.writer(file)
        for count, tweet in enumerate(user_tweets):
            data_dict, data_list = get_data(Tweet(tweet), count)
            result.append(data_dict)
            writer.writerow(data_list)

    return result


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/get_data/{user_id}")
def read_item(user_id: str):
    return get_tweets(user_id)


# Check Configuration docs for the available settings.
# config.PROXY = {"http":"127.0.0.1","https":"127.0.0.1"}
# config.TIMEOUT = 10

# MAX_TWEETS = 10








