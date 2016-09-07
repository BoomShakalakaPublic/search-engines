#Parse and tokenize each article and generate a	text file per article that contains only the title and	plain textual content of the  article. Ignore/remove  ALL markup notation (HTML tags), URLs,  references to images, tables, formulas, and navigational components.	
 
import os
import re
import string
import sys
from bs4 import BeautifulSoup,Comment
import nltk


bracket_re=re.compile('\[[0-9]*?\]')
edit_re=re.compile('\[edit\]')
char_re=re.compile('[0-9a-zA-Z]')

f_flags = os.O_CREAT | os.O_EXCL | os.O_RDWR

def saveFile(filePath,info):
	#if file already exits, remove the old version
	if os.path.exists(filePath):
		os.remove(filePath)
	file_handle = os.open(filePath, f_flags)
	with os.fdopen(file_handle, 'w') as f:
			f.write(info)
			f.close()

def parse(f):
	page=f.read()
	soup=BeautifulSoup(page,"lxml")

	#extract <h*>  <p> <table> in div "content"
	tags=set([x.name for x in soup.find_all(re.compile('h\d'))])
	tags.add('p')
	tags.add('table')	
	soup=soup.find_all('div',id="content",role="main")[0]
	for s in soup.find_all('table',re.compile('.*?navbox.*?$')):
		s.extract()
	content=soup.find_all(tags)
	text='\n'.join([line.get_text() for line in content])

	
	#remove []
	text=bracket_re.sub("",text)
	text=edit_re.sub("",text)

	exclude=set(string.punctuation)
	exclude.remove('-')
	exclude.remove('.')
	exclude.remove(',')
	exclude.remove('+')
	for p in exclude:
		text=text.replace(p," ")
	#tokenize
	#nltk.download() tokenizers/punkt
	tokens=nltk.word_tokenize(text)
	tokens=filter(lambda t: char_re.search(t), tokens)
	#remove star
	tokens=[t.replace("*","").replace("\'","").lower() for t in tokens]


	#get filename
	title=soup.find('h1',id="firstHeading").get_text()
	title="".join(title.split())
	if not os.path.exists("docs"):
		os.mkdir("docs")
	filePath="docs/"+title+".txt"
	saveFile(filePath," ".join(tokens).encode('utf-8'))




#reading files
fileList=os.listdir("html")
print "File list readed. Starting processing:"
count=0
for page in fileList:
	with open("html/"+page) as f:
		count+=1
		sys.stdout.write("\rProgress: %d / 1000.   " % (count,))
		sys.stdout.flush()
		parse(f)

print "\n Complete."

