#-*- coding: utf-8 -*-
import os
import time
from tqdm import tqdm
import time

def load_data(path):
	ans=[]
	if path.split(".")[-1]=="xls":                    
		from xlrd import open_workbook
		import xlwt
		workbook=open_workbook(path)
		sheet=workbook.sheet_by_index(0)
		for i in range(1,sheet.nrows):
			temp=sheet.row_values(i)[1].split(";")[:-1]
			if len(temp)==0: continue
			temp=[j.split(":")[0] for j in temp]
			temp=list(set(temp))
			temp.sort()
			ans.append(temp)
	elif path.split(".")[-1]=="csv":
		import csv
		with open(path,"r") as f:
			reader=csv.reader(f)
			for row in reader:
				row=list(set(row))
				row.sort()
				ans.append(row)
	return ans

def save_rule(rule,path):
	with open(path,"w") as f:
		f.write("index  confidence"+"   rules\n")
		index=1
		for item in rule:
			s=" {:<4d}  {:.3f}        {}=>{}\n".format(index,item[2],str(list(item[0])),str(list(item[1])))
			index+=1
			f.write(s)
		f.close()
	print("result saved,path is:{}".format(path))

class Apriori():
	def create_c1(self,dataset):
		c1=set()
		for i in dataset:
			for j in i:
				item = frozenset([j])
				c1.add(item)
		return c1

	def create_ck(self,Lk_1,size):
		Ck = set()
		l = len(Lk_1)
		lk_list = list(Lk_1)
		for i in range(l):
			for j in range(i+1, l):
				l1 = list(lk_list[i])
				l2 = list(lk_list[j])
				l1.sort()
				l2.sort()
				if l1[0:size-2] == l2[0:size-2]:
					Ck_item = lk_list[i] | lk_list[j]
					if self.has_infrequent_subset(Ck_item, Lk_1):
						Ck.add(Ck_item)
		return Ck

	def has_infrequent_subset(self,Ck_item, Lk_1):
		for item in Ck_item: 
			sub_Ck = Ck_item - frozenset([item])
			if sub_Ck not in Lk_1:
				return False
		return True

	def generate_lk_by_ck(self,data_set,ck,min_support,support_data):
		item_count={}
		Lk = set()
		for t in tqdm(data_set):
			for item in ck:
				if item.issubset(t):
					if item not in item_count:
						item_count[item] = 1
					else:
						item_count[item] += 1
		t_num = float(len(data_set))
		for item in item_count:
			if item_count[item] >= min_support:
				Lk.add(item)
				support_data[item] = item_count[item]
		return Lk
		

	def generate_L(self,data_set, min_support):
		support_data = {} 
		C1 = self.create_c1(data_set)
		L1 = self.generate_lk_by_ck(data_set, C1, min_support, support_data)
		Lksub1 = L1.copy()
		L = []
		L.append(Lksub1)
		i=2
		while(True):
			Ci = self.create_ck(Lksub1, i) 
			Li = self.generate_lk_by_ck(data_set, Ci, min_support, support_data)
			if len(Li)==0:break
			Lksub1 = Li.copy() 
			L.append(Lksub1)
			i+=1
		for i in range(len(L)):
			print("frequent item {}：{}".format(i+1,len(L[i])))
		return L, support_data

	def generate_R(self,dataset, min_support, min_conf):
		L,support_data=self.generate_L(dataset,min_support)
		rule_list = []
		sub_set_list = []
		for i in range(0, len(L)):
			for freq_set in L[i]:
				for sub_set in sub_set_list:
					if sub_set.issubset(freq_set):
						conf = support_data[freq_set] / support_data[freq_set - sub_set]
						big_rule = (freq_set - sub_set, sub_set, conf)
						if conf >= min_conf and big_rule not in rule_list:
							rule_list.append(big_rule)
				sub_set_list.append(freq_set)
		rule_list = sorted(rule_list,key=lambda x:(x[2]),reverse=True)
		return rule_list
    
def find_exec_time():
    return time.time()

if __name__=="__main__":
    
    filename="food basket.csv"
    min_support=15
    min_conf=0.7
    current_path=os.getcwd()
    if not os.path.exists(current_path+"/log"):
        os.mkdir("log")
    path=current_path+"/dataset/"+filename
    save_path=current_path+"/log/"+filename.split(".")[0]+"_apriori.txt"
    data=load_data(path)
    start_time = time.time()
    apriori=Apriori()
    rule_list=apriori.generate_R(data,min_support,min_conf)
    save_rule(rule_list,save_path)
    print("--- %s execution time in seconds ---" % (time.time() - start_time))

# 	filename="food basket.csv"
# 	min_support=10
# 	min_conf=0.7
# 	size=5

# 	current_path=os.getcwd()
# 	if not os.path.exists(current_path+"/log"):
# 		os.mkdir("log")
# 	path=current_path+"/dataset/"+filename
# 	save_path=current_path+"/log/"+filename.split(".")[0]+"_apriori.txt"
    

# 	data=load_data(path)
# 	apriori=Apriori()
# 	rule_list=apriori.generate_R(data,min_support,min_conf)
# 	save_rule(rule_list,save_path)
#     #print("--- %s execution time in seconds ---" % (time.time() - start_time))
