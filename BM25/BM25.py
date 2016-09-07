#
import json
import os
from operator import itemgetter
from math import log

#load inverted index
index={}
print "Loading index file..."
with open("index_1.json", 'rb') as fp:
	index = json.load(fp)
print "Loading complete."

#query set
q1="global warming potential"
q2="green power renewable energy"
q3="solar energy california"
q4="light bulb bulbs alternative alternatives"
Q=[q1,q2,q3,q4]

#document length, average document length
doc_len={}
total_len=0
fileList=os.listdir("docs")
for doc in fileList:
	with open("docs/"+doc,'rb') as f:
		text=f.read()
		doc_name=doc.replace(".txt","")
		dl=len(text.split())
		doc_len[doc_name]=dl
		total_len+=dl
avdl=float(total_len)/1000.0

f_flags = os.O_CREAT | os.O_EXCL | os.O_RDWR
def saveRank(filePath,score,q_id):
	#if file already exits, remove the old version
	if os.path.exists(filePath):
		os.remove(filePath)
	file_handle = os.open(filePath, f_flags)
	with os.fdopen(file_handle, 'w') as fp:
	    for i in range(len(score)):
	    	fp.write(q_id+" Q0 "+score[i][0].encode('utf-8')+" "+str(i+1)+" "+str(score[i][1])+" BM25"+'\n')


k1=1.2
k2=100
b=0.75
for i in range(len(Q)):

	BM25=[]
	q=Q[i]
	print "Processing query "+str(i+1)+": "+ q
	terms=q.split()
	#the document set that contain the terms in given query
	doc_set=set([])
	for t in terms:
		for x in index[t]:
			doc_set.add(x[0])
	#compute BM25 score for each document 
	for doc in doc_set:
		dl=doc_len[doc.encode('utf-8')]

		K=1.2*((1-0.75)+0.75*dl/avdl)
		score=0
		for t in terms:
			n=0
			if t in index:
				n=len(index[t])
			else:
				continue
			f=0
			for x in index[t]:
				if x[0]==doc:
					f=x[1]
					break
			#q=1 for every term
			tmp=1/((n+0.5)/(1000-n+0.5))
			if tmp>0:
				score+=log(tmp)*(k1+1)*f/(K+f)*(k2+1)/(k2+1)

		
		BM25.append([doc,score])
	BM25=sorted(BM25,key=itemgetter(1),reverse=True)
	fileName="Q"+str(i+1)+"BM25.txt"
	saveRank(fileName,BM25[:100],"Q"+str(i+1))

print "Complete!"
