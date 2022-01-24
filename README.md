# Retrieve Tweet replies

This Python script pulls all direct replies to a specified Tweet, extracts user [mentions](https://help.twitter.com/en/using-twitter/mentions-and-replies) from the replies, and returns a list of usernames ordered by most to least frequently mentioned in the replies.

This script uses v2 of the Twitter API, and more specifically:
* [Search Tweets](https://developer.twitter.com/en/docs/twitter-api/tweets/search/introduction)
* [Tweets lookup](https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/introduction)

## Requirements 

* Twitter developer account.
* Developer Project and App with access to the v2 full-archive search endpoint: [GET /2/tweets/search/all](https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all).

You can read more about getting access to all of the above in [Twitter's developer docs](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api).

## Authentication & set up

Rename `.env_example` to `.env` and add the credentials for your developer App in between the `""`.
```
TWITTER_CONSUMER_KEY=""
TWITTER_CONSUMER_SECRET=""
TWITTER_ACCESS_TOKEN=""
TWITTER_ACCESS_TOKEN_SECRET=""
TWITTER_BEARER_TOKEN=""
```
Don't forget to add `.env` to your `.gitignore` file to keep your credentials secure. 

## Running the script 

```
$ python3 replies.py -t <TWEET-ID>
```

|Flags|   |   |   |
|---|---|---|---|
|`-t`|Tweet ID|Required|ID of the Tweet for which you want to pull data.|
|`-h`|Help|Optional|View a list of available flags and a description for each of these.|
|`-s`|Start time|Optional|The oldest UTC timestamp from which the replies will be provided. Format: YYYY-MM-DDTHH:mm:ssZ; for example: 2021-12-04T01:30:00Z. If unspecified, will default to returning replies from up to 30 days ago.|
|`-e`|End time|Optional|The newest, most recent UTC timestamp to which the replies will be provided. Format: YYYY-MM-DDTHH:mm:ssZ; for example: 2021-12-04T01:30:00Z. If unspecified, will default to [now - 30 seconds].|
|   |   |   |   |

Run the following command to see a list of available flags: 
```
$ python3 replies.py -h
```

## Output

### Returned in the command line interface
* Ordered dictionary containing: a list of all usernames present in the replies and the number of times each username was mentioned. Note: the username who authored the original Tweet is not included.
* Number of replies to the Tweet.
* Number of usernames mentioned in these replies.
* Total request count made to the Search API to get these replies. 

### Returned in a new file
* `replies.txt` containing a list of Tweet IDs for the replies.
