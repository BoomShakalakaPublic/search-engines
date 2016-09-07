
import json
import os
import sys
import threading
import time
from nltk.util import ngrams


f_flags = os.O_CREAT | os.O_EXCL | os.O_RDWR

# N for n-gram
N=3
#index file name
index_file="index_"+str(N)+".json"
#progress indicator
count=0
lock_count=threading.Lock()
#index
ind={}
lock_ind=threading.Lock()



def index(id,content):
	global ind
	global count
	terms=set(content)
	lock_ind.acquire()
	for t in terms:
		if t not in ind:
			ind[t]=[]
		# [docId, tf]
		ind[t].append([id,content.count(t)])
	lock_ind.release()
	lock_count.acquire()
	count+=1
	sys.stdout.write("\rProgress: %d / 1000.   " % (count,))
	sys.stdout.flush()
	lock_count.release()



def saveIndex(filePath,data):
	#if file already exits, remove the old version
	if os.path.exists(filePath):
		os.remove(filePath)
	file_handle = os.open(filePath, f_flags)
	with os.fdopen(file_handle, 'w') as fp:
	    json.dump(data, fp)




fileList=os.listdir("docs")	
print "Start index:"
count=0
for doc in fileList:
	with open("docs/"+doc)as f:

		content=f.read().split()
		context=[]
		for g in ngrams(content,N):
			#combine ngrams into a string
			context.append(" ".join(g))
		t=threading.Thread(target=index,args=(doc.replace(".txt",""),context))
		t.start()

while(threading.active_count()>1):
	time.sleep(1)
print "Saving index..."
saveIndex(index_file,ind)
print "Complete"


