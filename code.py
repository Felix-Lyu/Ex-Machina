import re
import numpy as np
import tweepy
import csv
from tweepy import OAuthHandler
from textblob import TextBlob
import pandas as pd
import time

class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''

    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = '9RkYhudUQkKKHEuCwnU1WmKGt'
        consumer_secret = 'bkRl7MNNSzi2Hvg1bJUb3weakYw9Rlf9v35thqPLQ3YcViWCjA'
        access_token = '357276346-oIxMqGkzb82Vz7uE6cEKCX5l8HUKNwPmTVKAADNR'
        access_token_secret = 'fsph2QGPKvL8dDRRu97IgICqCdGNnf44cIkTXS2ctaaH2'

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count=10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q=query, count=count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count == 0:
                    # if tweet has retweets, ensure that it is appended only once
                    #   if parsed_tweet not in tweets:
                    #       tweets.append(parsed_tweet)
                    # else:
                    tweets.append(parsed_tweet)

            # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))

    # Twitter only allows access to a user's most recent 3240 tweets
    def get_user_tweets(self, username):
        # list that stores all the tweet texts of this user
        alltweets = []

        # make initial requests
        new_tweets = self.api.user_timeline(screen_name=username, count=200, tweet_mode='extended')
        print("Initial call: %s fetched" % (len(new_tweets)))

        # the id to start searching next time
        oldest = new_tweets[len(new_tweets) - 1].id - 1

        # append all the new tweet texts into alltweets
        for tweet in new_tweets:
            alltweets.append(tweet.full_text)

        # print(new_tweets[0])
        # print(new_tweets[0].full_text)
        # print(self.clean_tweet(new_tweets[0].full_text))
        # repeat the process until no more tweets can be fetched
        while (len(new_tweets) > 0):
            print("getting tweets before %s" % oldest)

            new_tweets = self.api.user_timeline(screen_name=username, count=200, max_id=oldest, tweet_mode='extended')

            if len(new_tweets) == 0:
                break

            for tweet in new_tweets:
                alltweets.append(tweet.full_text)

            # update the oldest id
            oldest = new_tweets[len(new_tweets) - 1].id - 1

            print("...%s tweets downloaded so far" % len(alltweets))

        print("Total fetched from user %s: %s" % (username, len(alltweets)))

        user_array = []

        for i in range(0, len(alltweets)):
            # our dictionary object for each tweet that holds all the necessary info
            parsed_tweet = {'text': alltweets[i],
                            'cleaned': self.clean_tweet(alltweets[i]),
                            'sentiment': 0,  #FIXME: currently a place holder
                            'user': username,
                            'mentioned': self.any_mention(alltweets[i], "Democrat.xlsx")}

            user_array.append(parsed_tweet)

        # writing everything into a csv file
        with open('AllTweets.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            for obj in user_array:
                writer.writerow([obj['text'], obj['cleaned'], obj['sentiment'], obj['user'],obj['mentioned']])

        return user_array

        # f = open("results", "wb")
        # for i in range(0, len(alltweets)):
        #     f.write(alltweets[i])
        #     # f.write('\n')
        # # f.writelines(alltweets)
        # f.close()

    def any_mention(self, text, target_file):
        found = ''
        df = pd.read_excel(target_file)
        for row in range(df.size):
            cur_target = df['name'][row][1:]
            if cur_target in text:
                if len(found) > 0:
                    found += ' '
                found += cur_target

        return found


def main():
    start_time = time.time()

    # creating object of TwitterClient Class
    api = TwitterClient()

    # api.any_mention('I hate @SenDougJones!!! Guys like @SenBrianSchatz should be sacked..', 'Democrat.xlsx')

    # create a file to hold all desired info
    with open('AllTweets.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Text", "Cleaned Text", "Sentiment", "User"])

    # read in twitter account names from Republican.xlsx（or Democrats.xlsx）
    df = pd.read_excel('Republican.xlsx')
    for row in range(df.size):
        username = df['name'][row][1:]
        api.get_user_tweets(username)



    print("--- %s seconds ---" % (time.time() - start_time))

    # calling function to get tweets
    # tweets = api.get_tweets(query='Donald Trump')

    # # picking positive tweets from tweets
    # ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # # percentage of positive tweets
    # print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets)))
    # # picking negative tweets from tweets
    # ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # # percentage of negative tweets
    # print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets)))
    # # percentage of neutral tweets
    # print("Neutral tweets percentage: {} %".format(100*(len(tweets)-len(ntweets)-len(ptweets))/len(tweets)))
    #
    # # printing first 5 positive tweets
    # print("\n\nPositive tweets:")
    # for tweet in ptweets[:10]:
    #     print(tweet['text'])
    #
    # # printing first 5 negative tweets
    # print("\n\nNegative tweets:")
    # for tweet in ntweets[:10]:
    #     print(tweet['text'])


if __name__ == "__main__":
    # calling main function
    main()