#precision
#input: (set<relevant_docs>,list<top doc_id>) for one query and one system
#output: <list> (precision table,average precision)
from __future__ import division
from constants import f_flags
import os

def precision(relevant,docs,path):
	ans=[]
	count_all=0
	count_relevant=0
	sum_pre=0.0
	file_handle = os.open(path, f_flags)
	with os.fdopen(file_handle, 'w') as f:
		for doc in docs:
			count_all+=1
			pre=count_relevant/count_all
			if doc in relevant:
				count_relevant+=1
				pre=count_relevant/count_all
				sum_pre+=pre
				f.write("R\t")
			else:
				f.write("N\t")
			ans.append(pre)
			f.write(str(pre)+'\n')
	avr_pre=0
	if count_relevant!=0:
		avr_pre=sum_pre/count_relevant

	return [ans,avr_pre]