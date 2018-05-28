import urllib.request, urllib.parse, urllib.error,urllib.request,urllib.error,urllib.parse
import json, re, datetime, sys
import config
import http.cookiejar
from pymongo import MongoClient
from pyquery import PyQuery
from bson.objectid import ObjectId

#CAUTION! change the settings depending on news or sarcsm
client = MongoClient(config.MONGODB['hostname'], config.MONGODB['port'])
db = client[config.MONGODB['db']]
#news
#collection = db[config.MONGODB['collection_news']]
#sarcasm
#collection = db[config.MONGODB['collection_sarcasm']]
#abusive
#collection = db[config.MONGODB['collection_sarcasm_en']]
#normal
collection = db[config.MONGODB['collection_sarcasm_es']]

# '#sarcasmopuro','#sarcastico','#sarcastica'
#KEYWORDS = ['#sarcasmo','#sarcasmopuro','#sarcastica',"#sarcastico"]  # Keyword to track ( multiple keywords separated by a comma)
#KEYWORDS = ['#mejorsuicidate','#robasoxigeno', '#tomacloro', '#matatemejor', '#dateuntiro', '#suicidate', '#suicidateya',
#			'#cortate','#daspena','#dasasco','#cortatelasvenas', '#pinchelooser', '#quepenamedas']
KEYWORDS = ['sarcasmo', 'sarcastico']
#KEYWORDS = ['el','la']
#KEYWORDS = ['the']
#LANGUAGES = ['es']

WANTED_KEYS = [
	'tweetid_str',
	'text',
	'created_at',
	'in_reply_to_status_id_str',
	'in_reply_to_user_id_str']  # Wanted keys to store in the database

#newspaper accounts in spanish
ACCOUNTS = ['cnnbrk','nypost','bbcbreking','bbcnews','guardian','independent','telegraph',
			'nytimesworld','bbcworld','bbcnews','latimes', 'nbcnews','cbsnews','dwnews','un',
			'afp','forbes']
#ACCOUNTS = ['CNNEE', 'el_pais', 'bbcmundo', 'ELTIEMPO', 'elespectador', 'prensa_libre', 'elsiglogt',
 			# 'dw_espanol', 'nytimeses', 'cnnbrk', 'el_pais', 'bbcmundo', 'ELTIEMPO', 'elespectador',
 			# 'prensa_libre', 'elsiglogt', 'dw_espanol', 'nytimeses', 'AP_noticias', 'AFPespanol',
 			# 'abc_es', 'europapress', 'EFEnoticias']

# write tweet to db
def post_tweet_to_db(tweet,):
	try:
		if collection.find({"tweetid_str" : tweet['tweetid_str']}).count() == 0:
			collection.insert(tweet)
		else:
			duplicatedTweets+=1
	except:
	#	print("Insertion error")
		pass
	return True

class TwitterCrawler:

	bufferLength = 100
	keywordSearch = 0
	accountSearch = 0
	maxTweets  = 0
	language = "en"
	queryUrl = None
	mode = "na"
	duplicatedTweets=0

	tweet = {}

	def __init__(self,maxTweets,language,mode,keywordSearch=0,accountSearch=0,refreshCursor=''):
		self.bufferLength = 100
		self.maxTweets = maxTweets
		self.language = language
		self.keywordSearch = keywordSearch
		self.accountSearch = accountSearch
		self.mode = mode
		self.lastRefreshCursor=refreshCursor

	def crawlTweets(self):
		receiveBuffer = None
		refreshCursor = ''
		results = []
		resultsAux = []
		cookieJar = http.cookiejar.CookieJar()
		active = True

		while active:
			json = self.getJsonReponse(refreshCursor, cookieJar)
			if len(json['items_html'].strip()) == 0:
				break
			self.lastRefreshCursor=refreshCursor
			refreshCursor = json['min_position']			
			tweets = PyQuery(json['items_html'])('div.js-stream-tweet')
			
			if len(tweets) == 0:
				break
			
			for tweetItem in tweets:
				tweetPQ = PyQuery(tweetItem)
				tweet = {}
				text = re.sub(r"\s+", " ", tweetPQ("p.js-tweet-text").text().replace('# ', '#').replace('@ ', '@'));
				timestamp = tweetPQ("small.time span.js-short-timestamp").attr("data-time");
				tweetid_str = tweetPQ.attr("data-tweet-id");
				twitter_is_reply_to = tweetPQ("div.js-stream-tweet").attr("data-is-reply-to")
				in_reply_to_user_id_str = tweetPQ("div.ReplyingToContextBelowAuthor a.js-user-profile-link").attr("data-user-id")
				in_reply_to_status_id_str = tweetPQ("div.js-stream-tweet").attr("data-conversation-id")

				#get links
				twitter_links = []
				for link in tweetPQ("a"):
					try:
						twitter_links.append((link.attrib["data-expanded-url"]))
					except KeyError:
						pass
				
				#assign to tweet
				try:
					timestamp = datetime.datetime.fromtimestamp(int(timestamp))
				except TypeError:
					print("Type Error in timestamp")
					continue #skip non timestamped element

				tweet["tweetid_str"] = tweetid_str
				tweet["text"] = text
				tweet["created_at"] = timestamp.strftime('%a %b %d %H:%M:%S +0000 %Y')
				#tweet.urls = ",".join(urls)

				if(twitter_is_reply_to == "true"):
					tweet["in_reply_to_status_id_str"] = in_reply_to_status_id_str
					tweet["in_reply_to_user_id_str"] = in_reply_to_user_id_str

				else:
					tweet["in_reply_to_status_id_str"] = None
					tweet["in_reply_to_user_id_str"] = None
				
				#filter out links and tweets shorter than 3 words
				if not twitter_links and len(text.split(' '))>3:
					results.append(tweet)
					resultsAux.append(tweet)
					#commment out later 
					post_tweet_to_db(tweet)


				
				if receiveBuffer and len(resultsAux) >= self.bufferLength:
					receiveBuffer(resultsAux)
					resultsAux = []
				
				if self.maxTweets > 0 and len(results) >= self.maxTweets:
					active = False
					break
		
		if receiveBuffer and len(resultsAux) > 0:
			receiveBuffer(resultsAux)
		print("lastRefreshCursor: " + self.lastRefreshCursor)
		#print("duplicated Tweets: " + self.duplicatedTweets)
		return results

	def getURL(self,refreshCursor):
		if self.mode=="account":
			accountString = 'from:' + ' OR from:'.join(self.accountSearch)
			url = "https://twitter.com/i/search/timeline?f=realtime&q=%s&src=typd&%smax_position=%s"
			urlGetData = ''
			urlGetData += ' ' + accountString
			urlLang = 'lang=' + self.language + '&'
			url = url % (urllib.parse.quote(urlGetData), urlLang, refreshCursor)
			#print(refreshCursor)
			#print(url)
			return url
		elif self.mode == "keyword":
			keywordSearchString=' OR '.join(self.keywordSearch)
			url = "https://twitter.com/i/search/timeline?f=realtime&q=%s&src=typd&%smax_position=%s"
			urlGetData = ''
			urlGetData += ' ' + keywordSearchString
			urlLang = 'lang=' + self.language + '&'
			url = url % (urllib.parse.quote(urlGetData), urlLang, refreshCursor)
			#print (refreshCursor)
			return url
		else:
			raise ValueError('Mode for URL search provided is not correct')
	
	def getJsonReponse(self, refreshCursor, cookieJar):

		url=self.getURL(refreshCursor)

		headers = [
			('Host', "twitter.com"),
			('User-Agent', "GoogleChrome/58.0 (Windows NT 6.1; Win64; x64)"),
			('Accept', "application/json, text/javascript, */*; q=0.01"),
			('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
			('X-Requested-With', "XMLHttpRequest"),
			('Referer', url),
			('Connection', "keep-alive")
		]

		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
		opener.addheaders = headers

		try:
			response = opener.open(url)
			jsonResponse = response.read()
		except:
			print("Unexpected error:", sys.exc_info()[0])
			sys.exit()
			return
		
		dataJson = json.loads(jsonResponse.decode())

		#print(dataJson)
		
		return dataJson		

if __name__ == '__main__':

	print(" Hi")

#get tweets from keywords
	#refreshCursor='TWEET-4837069245-1000861142250553345-BD1UO2FFu9QAAAAAAAAVfAAAAAcAAABWKAACAQECAAAAAAACAAgIAABAAACAQAgAAAABACBQAAAQAAIAAAEAgAAAAAQAAAAIQAAoiQgAAAAAECBUAAAAgAAAAAACAAAAAAABAAAgAAAAIAAAgICAAAAIAAABBBAAAAAAABAgACAAEMAAAAAAABIBEAgAAAAEAAAAIgBAAgAQAAAAAAAAABAAAAAAAAAAAAIEAAIAAAgAAgAAAAASAEAhAABAAAAAgAAIQAASAIAQMAAAABAACEACBADAAAgACAwAAAAAAAAAAAAAAAAAAIwAIAUCAEAAAAAAQAAAAACAAIIAAAAAQAEJAAAAAIAAAAAAACAEAAAAgAAQAAAAAAgAACAAAUAAEAAAAAhAAAAAAAABAgEAAgEAEIAAAAAAQIAAAAhCAAAABEAAAAAAAAAAAAAAAAAAAAAAQBAAAAEEAEAAEQAAEAAAQJAAAIAEBAAAgAAAAgAAAEAAgKQQAAAAAAAAgABAQBAAAIBAAAAAAAAAIAADhACCAAABAAAQAgAAAAAAAAAAAAAAAUAEAAAIAAAAABAQCAAUAEEAAACAAEABBIAAAAQAAEAAAAAAAAAAAEABAAQIAACAAEQAAACAAUgAgIAAAIAAQAgQAAAAAAwCAAAAAAAAQAAECAAAABiAAAgAAAAIFAAAAAABAACAAIAAAAAABCQAEAAAAAAAAAAAAAEAAAAABAAAACABCAAAIAAAAUIMAAwAAAAAAAAAAAAAAAAAABAQIAAABAAAQAAABACIAAAAAAAIAgACCAAAAIAAAAAABAAAAAhBAAAAAAAACAAAIAAAAAJACAAAAEIAAAAAAAQACAAAAAAAgAAAAAAAAAAABABCCAIgAAAAIAgAAABCAAAABAAAAAAAAAhAAEAIABAAQgUAAAAGAAAAAACEAAAAABAAAAIIAA==-T-0-54'
	#tweets = TwitterCrawler(maxTweets=100000000,language="es",keywordSearch=KEYWORDS,mode="keyword",refreshCursor=refreshCursor).crawlTweets()
	tweets = TwitterCrawler(maxTweets=100000000,language="es",keywordSearch=KEYWORDS,mode="keyword").crawlTweets()
	print("Done")


#get tweets from accounts
##with refresh cursor
	#refreshCursor="TWEET-1963033-1000398402482356226-BD1UO2FFu9QAAAAAAAAVfAAAAAcAAABWCJQEREUAAxqo4IMYAgAEIKASBEQFlJAMG4SgABJSIQuAVAJVAIMEokAworgRG4AFAAQIAgQlUPAAACBGpqAAAABEIghopgEEYEEILCAwiBQARcBQaCVAlFJ2qQAmDgQCVGoCIkAiAGBSECwABAIQIGAREBCgoIAAA5gJKoYgi4CgjiIAEyAQggBAGEAkASAAAAQAgSAglCljkSPiohAGkABIEBAgYEsABwAAwASchkAZQAAQDCgAIQIbkSAGBIIkKBADKxEFCIGBQBBugBIkgADIEAgwUgaJwYXE6AADAMtgiBwAAgqhQRAhBAQIsSgJBoWQAWEwILEEQW5oDLIAQAgAgQIghAgk0gQBIpFEBAkAIEBERQgsIAAoEyKQgFMUQOAExBCAACwktBCFAmEAAQABAABAZEOaQDIUCIujAhAQwCADiKwACKABJgYAAEAAAQRACBgAVAhAgQMCCYwYKFA0mqyBhCtAJEBxAAIBgUCHgAEIwQIQiTFQRCjEIRgBCEJIIIAhEBACrAIgkIEYJCwkgAYEQicCCABAAGAPAAAAQAgQghANCAiACAIhBCUBSGAAACCQGSCiaQiEJZEFIBACANACJEAQiQGAQIoGATwQIgBgpAAACLAJqwEjJAQQUIAgMAkBAOSkAEgJTQV1gQExAIuEgoFDMRABQgCgAQIkkGI3EYAJAAXAESCsjUIrgcECAACMEQIoIhAKiEZQChQLAABArAYKiAACxIgAiAQyQEckqhEEm0BACQAIEAQSEQABCAUQCggBgVCIAkQAAEgBAkAASwBYqAABglmIfEKgDAEDEAAYBITBmIiBXMECSIGFwCMAIYgcCgUBBAAEEhJgghA8CAAIoACCVtDCIAAMAZiDDIgQSEAAACCHAAYWAB1WEJAEUEACQEQRIgPUgg==-T-0-2661"
	#tweets = TwitterCrawler(maxTweets=500000,language="es",accountSearch=ACCOUNTS,mode="account",refreshCursor=refreshCursor).crawlTweets()
	#tweets = TwitterCrawler(maxTweets=500000,language="en",accountSearch=ACCOUNTS,mode="account").crawlTweets()
	#print("Done")