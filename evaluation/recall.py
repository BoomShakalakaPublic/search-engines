#recall
#input: (set<relevant_docs>,list<top doc_id>) for one query and one system
#output: recall table
from __future__ import division
from constants import f_flags
import os

def recall(relevant,docs,path):
	ans=[]
	count_relevant=len(relevant)
	count_cur=0
	file_handle = os.open(path, f_flags)
	with os.fdopen(file_handle, 'w') as f:
		for doc in docs:
			if doc in relevant:
				count_cur+=1
				f.write("R\t")
			else:
				f.write("N\t")
			ans.append(count_cur/count_relevant)
			f.write(str(count_cur/count_relevant)+'\n')
	return ans