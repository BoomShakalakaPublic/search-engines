#
import os

search_result_dir="search result"
eval_result_dir="evaluation"
pre_table_dir=eval_result_dir+"/precision"
recall_table_dir=eval_result_dir+"/recall"
f_flags = os.O_CREAT | os.O_EXCL | os.O_RDWR