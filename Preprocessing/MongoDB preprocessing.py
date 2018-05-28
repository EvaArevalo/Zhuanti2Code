from pymongo import MongoClient
from pyquery import PyQuery
import json, re, datetime, sys
from bson.objectid import ObjectId
import bson
import config
import re, string
#connect to mongodb
##CAUTION! change the settings depending on news or sarcsm
client = MongoClient(config.MONGODB['hostname'], config.MONGODB['port'])
db = client[config.MONGODB['db']]
#set to approp db
collection = 'collection_normal_es'

UNWANTEDKEYS =['sarcasmo','sarcastica','sarcastico','sarcasmopuro','ojosenblanco']

#remove links, pics, mentions and hashtags
def preProcessing():
	results=db[config.MONGODB[collection]].find()
	for item in results:
		#print (item['text'])
		text=item['text']
		flag = False

		#strip links
		text = re.sub('http\S+', '<link>', text)
		#strip pics
		text = re.sub('pic.twitter.com\S+', ' <pic>', text)
		#strip mentions
		text = re.sub('@[ ]{0,1}\S+', '<mention>', text)
		#strip tailing hashtags
		oldtext=text
		text = re.sub('#[ ]{0,1}\w+$', '<hashtags>', text)
		text = re.sub('#[ ]{0,1}\w+[ ]{0,2}<pic>', '<hashtags> <pic>', text)
		while(oldtext!=text):
			oldtext=text
			text = re.sub('#[ ]{0,1}\w+[ ]{0,1}<hashtags>', '<hashtags>', text)
			text = re.sub('#[ ]{0,1}\w+[ ]{0,1,2}<pic>', '<hashtags> <pic>', text)
		#strip remaining hashtag marks
		text = re.sub('#', '', text)

		#replace in db
		if(text!=item['text']):
			#print("ORIGINAL: "+ item['text'])
			#print("REGCORR: "+ text)
			db[config.MONGODB[collection]].update(
				{"tweetid_str":item['tweetid_str']},
				{ "$set" : {"text":text}}
				)    

		for unwantedkey in UNWANTEDKEYS:
			if unwantedkey in item['text']:
				print(item["tweetid_str"])
				print(item["text"])

#remove tweets smaller than 4
def removingSmalltweets():
	results=db[config.MONGODB[collection]].find()
	count=0
	for item in results:
		if len(item['text'].split()) <4:
			count+=1
			print(item['text'])
			print(item['tweetid_str'])
	print(count)

if __name__ == '__main__':

	preProcessing()
	#removingSmalltweets()


#ã

#  drop duplicates   
#  	var duplicates = [];
#     db.collection.aggregate([
#       { $match: { 
#         tweetid_str: { "$ne": '' }  
#       }},
#       { $group: { 
#         _id: { tweetid_str: "$tweetid_str"},
#         dups: { "$addToSet": "$_id" }, 
#         count: { "$sum": 1 } 
#       }}, 
#       { $match: { 
#         count: { "$gt": 1 }    
#       }}
#     ]).result          
#     .forEach(function(doc) {doc.dups.shift(); doc.dups.forEach( function(dupId){ duplicates.push(dupId);   
# } )})

#     printjson(duplicates);     
 
#     db.collection.remove({_id:{$in:duplicates}})