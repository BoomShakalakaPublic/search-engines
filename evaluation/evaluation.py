#evaluation: precision&recall, map, mrr, p@k(5,20)
from __future__ import division
import os
from precision import precision
from recall import recall
from constants import search_result_dir,eval_result_dir,f_flags,pre_table_dir,recall_table_dir


def checkDup(path):
	if os.path.exists(path):
		os.remove(path)

def makeDir(path):
	if not os.path.exists(path):
		os.makedirs(path)


makeDir(pre_table_dir)
makeDir(recall_table_dir)


#read relevant judement
relevant={}
rele_file="cacm.rel"
with open(rele_file) as f_rele:
	content=f_rele.readlines()
	for entry in content:
		item=entry.split()
		q_id=item[0]
		doc_id=item[2]
		if q_id not in relevant:
			relevant[q_id]=set([])
		relevant[q_id].add(doc_id)




fileList=os.listdir(search_result_dir)
for fileName in fileList:
	with open(search_result_dir+"/"+fileName) as f:
		#query-top 100 docs
		results={}
		#read search result
		content=f.readlines()
		content=[x for x in content if x!="\n"]
		tmp=content[0].split()
		system=tmp[5]
		print system
		for l in content:
			if not l:
				continue
			rank_entry=l.split()
			q_id=rank_entry[0]
			doc_id=rank_entry[2]
			if q_id not in results:
				results[q_id]=[]
			results[q_id].append(doc_id)
		#initiate tables' files	
		pre_file=eval_result_dir+"/"+system+" precision"+".txt"
		recall_file=eval_result_dir+"/"+system+" recall"+".txt"
		checkDup(pre_file)
		checkDup(recall_file)
		fh_pre = os.open(pre_file, f_flags)
		fh_recall=os.open(recall_file,f_flags)
		fd_pre=os.fdopen(fh_pre, 'w')
		fd_recall=os.fdopen(fh_recall,'w')

		validQ_Count=len(results)
		p_dir=pre_table_dir+'/'+system
		makeDir(p_dir)

		#precision&map&p@k
		sum_ap=0
		sum_p5=0
		sum_p20=0
		for q in results:
			rele_set=set([])
			if q in relevant:
				rele_set=relevant[q]
			#if there is no relevant documents for current query, exclude it 
			else:
				validQ_Count-=1
				continue
			table_path=p_dir+'/Q'+q+".txt"
			checkDup(table_path)
			[precision_table,ap]=precision(rele_set,results[q],table_path)
			sum_p5+=precision_table[4]
			sum_p20+=precision_table[19]
			sum_ap+=ap
			fd_pre.write(q)
			for x in precision_table:
				fd_pre.write("\t"+str(x))
			fd_pre.write('\n')
		fd_pre.close()
		AP5=sum_p5/validQ_Count
		AP20=sum_p20/validQ_Count
		MAP=sum_ap/validQ_Count
		
		#recall&mrr
		sum_rr=0
		r_dir=recall_table_dir+'/'+system
		makeDir(r_dir)
		for q in results:
			rele_set=set([])
			if q in relevant:
				rele_set=relevant[q]
			else:
				continue
			table_path=r_dir+'/Q'+q+".txt"
			checkDup(table_path)
			recall_table=recall(rele_set,results[q],table_path)
			rank=1
			while rank<=len(recall_table) and recall_table[rank-1]==0:
				rank+=1
			if rank<=len(recall_table):
				sum_rr+=1/rank
			fd_recall.write(q)
			for x in recall_table:
				fd_recall.write("\t"+str(x))
			fd_recall.write('\n')
		fd_recall.close()
		MRR=sum_rr/validQ_Count
		print "MAP=",MAP,"AP@K5=",AP5,"AP@K20=",AP20,"MRR=",MRR



			



