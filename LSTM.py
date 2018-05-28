import pandas as pd
import numpy as np

from pymongo import MongoClient
from Preprocessing import config
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
# from keras.preprocessing.text import Tokenizer
# from keras.preprocessing.sequence import pad_sequences
# from keras.models import Sequential
# from keras.layers import Dense, Embedding, LSTM, SpatialDropout1D
# from keras.utils.np_utils import to_categorical
collection_name='news_and_sarcasm'

client = MongoClient(config.MONGODB['hostname'], config.MONGODB['port'])
db = client[config.MONGODB['db']]
collection = db[config.MONGODB[collection_name]]

def getDatasetsFromMongoDB():
	''' mongodb to pandas dataframe, export to csv and return'''
	results=collection.find()
	#strip and reshuflle
	df =  pd.DataFrame(list(results))
	df=df[['label','text']]
	df=df.reindex(np.random.permutation(df.index))
	filename=collection_name+'.csv'
	df.to_csv(filename,encoding='utf-8-sig')
	return df

def getDatasetsFromCsv():
	'''import csv and return it'''
	df=pd.read_csv('sarcasm_and_news_dataset.csv')
	df=df.reindex(np.random.permutation(df.index))
	return df[['label','text']]


if __name__ == '__main__':

	#Embedding layer parameters
	max_features=2000
	embedding_dim=128
	lstm_out=196
	batch_size=32

	print("getting datasets...")

	#data=getDatasetsFromCsv()
	data=getDatasetsFromMongoDB()
	print(data)
	train,test = train_test_split(data,test_size=0.1)

	# #tokenize
	# tokenizer = Tokenizer(num_words=max_features, split=' ')
	# tokenizer.fit_on_texts(data['text'].values)
	# X = tokenizer.texts_to_sequences(data['text'].values)
	# X = pad_sequences(X)

	# #build model
	# model = Sequential()
	# model.add(Embedding(max_features, embedding_dim,imput_length=X.shape[1]))
	# model.add(SpatialDropout1D(0.4))
	# model.add(LSTM(lstm_out, dropout=0.2,recurrent_dropout=0.2))
	# model.add(Dense(2,activation='softmax'))
	# model.compile(loss='categorical_crossentropy', optimizer='adam',metrics=['accuracy'])
	# print(model.summary())

	#training
	# Y= pd.get_dummies(data['label']).values
	# X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size=0.33, 
	# 	random_state=42)
	# print(X_train.shape,Y_train.shape)
	# print(X_test.shape,Y_test.shape)

	# model.fit(X_train, Y_train, epochs = 7, batch_size=batch_size, verbose=2)