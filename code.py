import re
import numpy as np
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 

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
		consumer_secret ='bkRl7MNNSzi2Hvg1bJUb3weakYw9Rlf9v35thqPLQ3YcViWCjA'
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
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

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

	def get_tweets(self, query, count = 10): 
		''' 
		Main function to fetch tweets and parse them. 
		'''
		# empty list to store parsed tweets 
		tweets = [] 

		try: 
			# call twitter api to fetch tweets 
			fetched_tweets = self.api.search(q = query, count = count) 

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
				#	if parsed_tweet not in tweets: 
				#		tweets.append(parsed_tweet) 
				#else: 
					tweets.append(parsed_tweet) 

			# return parsed tweets 
			return tweets 

		except tweepy.TweepError as e: 
			# print error (if any) 
			print("Error : " + str(e)) 

        def get_user_tweets(self, username, count):
                #Twitter only allows access to a user's most recent 3240 tweets

                alltweets=[]

                number_of_tweets = count
                
                #make initial requests
                new_tweets = self.api.user_timeline(screen_name = username,count = 1)
                print("total new: ")
                print(len(new_tweets))

                oldest = new_tweets[len(new_tweets)-1].id - 1
                print("yes")

                for tweet in new_tweets:
                    alltweets.append(tweet.text.encode("utf-8"))

                for i in range (0, number_of_tweets):
                    print("getting tweets before %s", oldest)

                    new_tweets = self.api.user_timeline(screen_name = username, max_id = oldest)
                   
                    if len(new_tweets) == 0:
                        break

                    for tweet in new_tweets:
                        alltweets.append((tweet.text).encode("utf-8"))

                    oldest = new_tweets[len(new_tweets)-1].id - 1

                    print("...%s tweets downloaded so far", len(alltweets))
                
                print("Total fetched from user %s", username)
                print(len(alltweets))
                print(alltweets[0])
                
                f = open("results","wb")
                f.writelines(alltweets)
                f.close()

                #for i in alltweets:
                #   print(i)


def main(): 
	# creating object of TwitterClient Class 
	api = TwitterClient() 
	
        api.get_user_tweets("realdonaldtrump", 200)

        # calling function to get tweets 
	tweets = api.get_tweets(query = 'Donald Trump', count = 200) 

	# picking positive tweets from tweets 
	ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
	# percentage of positive tweets 
	print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets))) 
	# picking negative tweets from tweets 
	ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 
	# percentage of negative tweets 
	print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))) 
	# percentage of neutral tweets 
        print("Neutral tweets percentage: {} %".format(100*(len(tweets)-len(ntweets)-len(ptweets))/len(tweets))) 

	# printing first 5 positive tweets 
	print("\n\nPositive tweets:") 
	for tweet in ptweets[:10]: 
		print(tweet['text']) 

	# printing first 5 negative tweets 
	print("\n\nNegative tweets:") 
	for tweet in ntweets[:10]: 
		print(tweet['text'])



        #print("\n\n\n\n")
        #api.get_user_tweets("realdonaldtrump", 200)

if __name__ == "__main__": 
	# calling main function 
	main() 
