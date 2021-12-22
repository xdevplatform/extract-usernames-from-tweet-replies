import os
import sys
import argparse
import requests
import time

from collections import Counter
from dotenv import load_dotenv

load_dotenv(verbose=True)  # Throws error if no .env file is found

consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

# Argparse for CLI options. Run `python3 replies.py -h` to see the list of arguments.
parser = argparse.ArgumentParser()
parser.add_argument(
    "-t",
    "--tweet_id",
    required=True,
    help="ID of the Tweet for which you want to pull replies",
)
parser.add_argument(
    "-s",
    "--start_time",
    help="The oldest UTC timestamp from which the replies will be provided. Format: YYYY-MM-DDTHH:mm:ssZ; for example: 2021-12-04T01:30:00Z. If unspecified, will default to returning replies from up to 30 days ago.",
)
parser.add_argument(
    "-e",
    "--end_time",
    help="The newest, most recent UTC timestamp to which the replies will be provided. Format: YYYY-MM-DDTHH:mm:ssZ; for example: 2021-12-04T01:30:00Z. If unspecified, will default to [now - 30 seconds].",
)
args = parser.parse_args()


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FullArchiveSearchPython"
    return r


def get_parameters():
    params = {
        "query": f"conversation_id:{args.tweet_id}",
        "tweet.fields": "in_reply_to_user_id,author_id,conversation_id,entities",
        "max_results": "500",
    }
    if args.start_time:
        params.update(start_time=args.start_time)
    if args.end_time:
        params.update(end_time=args.end_time)

    return (params, args.tweet_id)


def get_replies(parameters):

    replies = []

    search_url = "https://api.twitter.com/2/tweets/search/all"
    request_count = 0

    while True:
        response = requests.request(
            "GET", search_url, auth=bearer_oauth, params=parameters
        )
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        response_payload = response.json()
        meta = response_payload["meta"]
        if meta["result_count"] == 0:
            sys.exit("No replies to analyze")
        for reply in response_payload["data"]:
            replies.append(reply)
        request_count += 1
        if "next_token" not in meta:
            break
        next_token = meta["next_token"]
        parameters.update(next_token=next_token)
        time.sleep(1)

    return replies, request_count


def get_author(tweet_id):
    tweet_lookup_url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    parameters = {
        "tweet.fields": "author_id",
        "expansions": "author_id",
        "user.fields": "username",
    }

    response = requests.request(
        "GET", tweet_lookup_url, auth=bearer_oauth, params=parameters
    )

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    response_payload = response.json()
    author_id = response_payload["data"]["author_id"]
    for user in response_payload["includes"]["users"]:
        author_username = user["username"]

    return (author_id, author_username)


def get_usernames(author_id, replies):
    usernames = []
    replies_ids = []

    for reply in replies:
        # Only include Tweets that are in direct reply to the original Tweet
        if reply["in_reply_to_user_id"] == author_id:
            for mention in reply["entities"]["mentions"]:
                usernames.append(mention["username"])
            replies_ids.append(reply["id"])

    return usernames, replies_ids


def count_and_sort(usernames, author_username):

    ordered_usernames = Counter(usernames)

    # Remove mentions of original author from results
    ordered_usernames.pop(f"{author_username}")

    return ordered_usernames


def results(ordered_usernames, replies_ids, request_count):

    with open("replies.txt", "w") as output:
        output.write(str(replies_ids))

    print("============================")
    print(ordered_usernames)
    print("============================")
    print("* Number of direct replies to original Tweet:", len(replies_ids))
    print("* Number of usernames mentioned:", len(ordered_usernames))
    print("* Total request count:", request_count)
    print("============================")


if __name__ == "__main__":
    parameters, original_tweet_id = get_parameters()
    replies, request_count = get_replies(parameters)
    author_id, author_username = get_author(original_tweet_id)
    usernames, replies_ids = get_usernames(author_id, replies)
    ordered_usernames = count_and_sort(usernames, author_username)
    results(ordered_usernames, replies_ids, request_count)
