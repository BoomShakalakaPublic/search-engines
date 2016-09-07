#Focus crawling. Breadth first crawling, key word "solar"

import requests
import re
import urlparse
import os
import string
import sets
import time
import sys
import shutil
import threading
import Queue

#Global variables
crawl_depth=5
# Matches href="" attribute
link_re = re.compile(r'href="(.*?)"')
pureText_re = re.compile(r'<.*?>')
result_url=list()
counts = 0
counts_total = 0
processed_url = set([])
wait=False
queue=Queue.Queue()
#create result files
#if result files already exit, remove the old files
#result.txt
flags = os.O_CREAT | os.O_EXCL | os.O_RDWR
if os.path.exists("result_2-a.txt"):
	os.remove("result_2-a.txt")
urlList_fh = os.open("result_2-a.txt", flags)
urlList=os.fdopen(urlList_fh,'w')
#html's
if os.path.exists("html_2-a"):
	shutil.rmtree("html_2-a")
os.makedirs("html_2-a")

#locks for global result 
lock_resultURL = threading.Lock()
lock_counts = threading.Lock()
lock_queue = threading.Lock()
lock_processedURL = threading.Lock()

#store crawled information into files
def saveFile(filePath,info):
	#if file already exits, remove the old version
	if os.path.exists(filePath):
		os.remove(filePath)
	file_handle = os.open(filePath, flags)
	with os.fdopen(file_handle, 'w') as f:
			f.write(info)
			f.close()
#page class. status : "white"--this page need to be crawled; "grey"--this page need to be opened to determine if need to be crawled
class page:
	def __init__(self, url,depth,status):
		self.url=url
		self.depth=depth
		self.status=status
def process_page(p,keyword):
	global result_url
	global processed_url
	global queue
	global counts
	global counts_total
	counts_total+=1
	try:
		r=requests.get(p.url)
	except requests.exceptions.RequestException as e:
		print "\nCan't connect to "+p.url+'\n'
		return
	#if a page's status is grey,check its content
	if p.status=="grey":
		#remove all tags before looking for keywords
		if keyword.lower() in pureText_re.sub("",r.text.encode('utf-8').lower())  :
			p.status="white"

	#crawl the page if it is "white"
	if(p.status=="white"):
		#store current page into directory "html_2-a"
		#naming stored file by url.path+parameter('/' is repalced by '++')
		lock_resultURL.acquire()
		if(len(result_url)>=1000):
			lock_resultURL.release()
			return
		purl=urlparse.urlparse(p.url)
		result_url.append(p.url)
		filename = purl.path+purl.params+".html"
		filename=string.replace(filename,'/','++')
		filePath="html_2-a/"+filename
		saveFile(filePath,r.text.encode('utf-8'))
		lock_counts.acquire()
		counts+=1
		lock_counts.release()
		lock_resultURL.release()
		if (p.depth<crawl_depth): 
			t=threading.Thread(target=process_links,args=(p,r,keyword))
			t.start()

		#progress indicator
		sys.stdout.write("\r%d pages have been stored. %d have been crawled totally. Current depth: %d. "  % (counts,counts_total,p.depth))
		sys.stdout.flush()

def process_links(p,r,keyword):
	global result_url
	global processed_url
	global queue
	#find child page's urls if not reach depth limit
	lock_resultURL.acquire()
	lock_queue.acquire()

	#read all links in current page
	links = link_re.findall(r.text)

	for link in links:
		par=urlparse.urlparse(link)
		#only add links start with /wiki/ and don't contain : to a list for latter iteration
		if "/wiki/" in par.path and (par.netloc=="") and not ":" in par.path: 
			#if # is in the link, only keep the part before
			if(link.find("#")>0):
				link=link[:link.find("#")]
			complete_path="http://en.wikipedia.org"+link
			lock_processedURL.acquire()


			#if the url didn't appeared before
			if complete_path not in processed_url : 
				processed_url.add(complete_path)

				p_tmp=page(complete_path,p.depth+1,"grey")
				if keyword.lower() in link.lower():
					p_tmp.status="white"					
				queue.put(p_tmp)


			lock_processedURL.release()
	lock_resultURL.release()
	lock_queue.release()	

def crawl(url,keyword):
	global counts
	global result_url
	global queue



	start_page=page(url,1,"white")
	processed_url.add(url)
	queue.put(start_page)
	while (not queue.empty() ) and len(result_url)<1000:
		p=queue.get()
		t=threading.Thread(target=process_page,args=(p,keyword))
		t.start()
		time.sleep(1)


			
			
print "Crawl start:\n"						
crawl('http://en.wikipedia.org/wiki/Sustainable_energy',"solar")
while(threading.active_count()>1):
	time.sleep(3)
for item in result_url:
	urlList.write(item+'\n')
urlList.close()
print "\n Crawl completed."
