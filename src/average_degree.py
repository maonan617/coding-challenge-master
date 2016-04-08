import json
import datetime
import itertools
import os
import sys

#input_dirpath = "../tweet_input"
#output_dirpath = "../tweet_output"

#if not os.path.isdir(input_dirpath):
#        os.makedirs(input_dirpath)

#if not os.path.isdir(output_dirpath):
#        os.makedirs(output_dirpath)

args = sys.argv[1:]

intput_filepath = args[0]
output_filepath = args[1]


fin=open(intput_filepath,'r')
fout= open(output_filepath,'w')




tweets = fin.readlines()
timeWin = list()
hashdict = dict()#{hashtag:latest createTime}
edgedict = dict()#{edge:latest createTime}
degree = 0

for tweet in tweets:
	tmpdic = json.loads(tweet)
	hashtags = list() 
	edges = list()
	if ('created_at' not in tmpdic.keys()) or ('entities' not in tmpdic.keys()):
		fout.write('%.2f \n'%degree)
		continue #ignore the imcomplete tweet
	createTime = tmpdic['created_at']
	createTime = datetime.datetime.strptime(createTime,'%a %b %d %H:%M:%S +0000 %Y') #read timestamp
	for text in tmpdic['entities']['hashtags']:
		hashtags.append(text['text'])
	hashtags=list(set(hashtags)) #get unduplicated hashtag list
	edges = list(itertools.permutations(hashtags,2))
	
	if timeWin == []: #read the first tweet and calculate the average degree
		timeWin.append((createTime,hashtags))
		for hashtag in hashtags:
			hashdict[hashtag] = createTime
		
		for edge in edges:
			edgedict[edge] = createTime
		if len(hashdict.keys()) == 0: degree=0
		else:degree = len(edgedict.keys())/float(len(hashdict.keys()))
		fout.write('%.2f \n'%degree)
		continue
		
	upper = max(timeWin)[0]
	#condition1: new timestamp is greater than the upper bound of present time window
	#add new tweet and delete the one before the new lower bound	
	
	if  createTime > upper: 

		timeWin.append((createTime,hashtags)) 
		for tag in hashtags:
			hashdict[tag] = createTime
		for edge in edges:
			edgedict[edge] = createTime
		
		lower = createTime-datetime.timedelta(seconds=60)
		for time,hashtags in timeWin:#remove tweet that fell out of the time window
			if time < lower: 
				timeWin.remove((time,hashtags))
		for hashtag in hashdict.keys(): 
			
			if hashdict[hashtag] < lower:
				del hashdict[hashtag]
		for edge in edgedict.keys(): 
			if edgedict[edge] < lower:
				del edgedict[edge]	

	#condition2: new timestamp is less than upper bound of present time window and located in 60s window
	#add new tweet information 
	elif (upper-createTime).seconds <= 60:
		timeWin.append((createTime,hashtags)) 	
		for tag in hashtags:
			hashdict[tag] = createTime
		for edge in edges:
			edgedict[edge] = createTime
	
	#calculate average degree
	if len(hashdict.keys()) == 0: degree=0
	else:degree = len(edgedict.keys())/float(len(hashdict.keys()))
	#output and write the result
	fout.write('%.2f \n'%degree)
