import pandas as pd
import numpy as np
import random
import itertools
import pdb
import matplotlib.pyplot as plt
import progressbar
import math
import time
from joblib import Parallel, delayed

class GibbsSampler:
	def __init__(self, data_frame, parsedquery, table_matching, steps):
		"""
        Parameters
        --------------------
            parsedquery         --  List of Dictionary. 
            						Each dictionary for each conj of UCQ; 
            						key:table (predicate), values: variables associated with that predicate
            data                --  Panda DataFrame.
            iter_max            --  int, maximum iteration steps
            table_matching      --  List of dictionary.
            						Each dictionary for each conj of UCQ;
            						key:pseudo-table name (pseudo-predicate), values:table name (predicate)
            world               --  Dictionary, each tuple status in one sampling world. 
            						key: table (predicate), values: np.array, tuple sampling status (0,1)


        """
		self.parsedquery = parsedquery #{'Q':['x2'],'R':['x1','y1']}#,'P':['x1'],'R1':['x2','y2']
		self.data = data_frame
		self.iter_max = steps
		self.table_matching = table_matching
		self.world = {key:np.ones(self.data.tables_df[key].shape[0],dtype = int)for key in self.data.tables_df.keys()} #Initial world, set to 1 for all tuples

	def sampling(self,prob):
			return np.random.binomial(1, prob)

	def check_world(self, query, conj_index):
		#Description: Check World SAT for each conj in one world
		#Return: True or False
		for key in self.table_matching[conj_index].keys():
			value = self.table_matching[conj_index][key]
			if value != key:
				self.data.tables_df[key] = self.data.tables_df[value].copy()
				self.world[key] = self.world[value].copy()

		for key in query.keys():
			tmp = dict(zip(list(self.data.tables_df[key].columns.values),query[key]))
			self.data.tables_df[key] = self.data.tables_df[key].rename(index=str, columns=tmp)

		joint = []
		#matched_table = self.table_matching[conj_index][list(query)[0]]
		active_list= (np.where(self.world[list(query)[0]]==1)[0])
		joint.append(self.data.tables_df[list(query)[0]].iloc[active_list,:-1])
		
		for key in query.keys():
			tmp = []
			#matched_table = self.table_matching[conj_index][key]
			active_list= (np.where(self.world[key]==1)[0])
			tmp.append(self.data.tables_df[key].iloc[active_list,:-1])
			intersect = []
			non_intersect = []
			# print("joint", joint)
			for i in range(len(joint)):
				get_intersect = set(query[key]).intersection(joint[i].columns.values)
				if bool(get_intersect):
					intersect.append((get_intersect, i))
				else:
					non_intersect.append(i)
			if len(intersect)!=0:
				for inter_col, index in intersect:
					#active_list= (np.where(self.world[matched_table]==1)[0])
					# print("inter", list(inter_col))
					# print(self.data.tables_df[matched_table].iloc[active_list,:-1])
					# print("inter_col", inter_col)
					# print("tmp")
					# print(tmp[0])
					# print("index",index)
					# print("joint", joint[index])
					tmp[0] = pd.merge(joint[index],tmp[0],on = list(inter_col),how = 'inner')
					
			if len(non_intersect)!=0:
				#pdb.set_trace()
				for j in non_intersect:
					tmp.append(joint[j])
			joint = tmp
		# print("last",joint)
		# print("world",self.world)
		for i in joint:
			if i.empty:
				return False
		
		return True	

	def Gibbs(self):
		#Description: Gibbs sampling
		#Return: Approximate inference for one query
		#update_count = 0 #Sampling update count. 1 update_count: a single tuple sampling
		iter_count = 1 #Iteration count. 1 iter_count: sampling for all tuples 
		sat_num = 0 # Satisfied world count. Checked for each update_count
		convergence = []
		bar = progressbar.ProgressBar(maxval=1, widgets=[progressbar.Bar('=', '[', ']'), ' ',progressbar.Percentage()])
		bar.start()
		start_time = time.time()
		#pre_evaluation = True
		query_table = set(table for _ in self.table_matching for table in _.values())
		while iter_count < self.iter_max:
			for table in query_table: 
				num_tuples = self.data.tables_df[table].shape[0]
				# for index in range(num_tuples):
				# 	self.world[table][index] = self.sampling(self.data.tables_df[table].iloc[index,-1])
				self.world[table] = Parallel(n_jobs = 2)(delayed(self.sampling)(self.data.tables_df[table].iloc[index,-1]) for index in range(num_tuples))
				#print(self.world)
			conj_index = 0 #Index of each conj in one UCQ
			#flag = 0
			for one_conj in self.parsedquery: #Check world SAT for each conj
				if self.check_world(one_conj, conj_index):
					sat_num = sat_num + 1
					#pre_evaluation = True
					#flag = 1
					break
				conj_index = conj_index + 1
			#if flag == 0:
				#pre_evaluation = False
			#update_count = update_count + 1
			convergence.append(sat_num/iter_count)
			iter_count = iter_count + 1
			bar.update(iter_count/self.iter_max)
		bar.finish()
		end_time = time.time()
		print(end_time - start_time)
		return sat_num / iter_count, convergence

def view_convergence(convergence):
	#Description: Plot convergence rate
	num = len(convergence)
	if math.sqrt(num).is_integer():
		row = int(math.sqrt(num))
		col = row
	else:
		row = int(math.sqrt(num)) + 1
		col = row

	if row == 1:
		plt.plot(convergence[0])
	else:
		fig, axs = plt.subplots(row, col)
		for ax, query in zip(axs.flat, convergence):
			ax.plot(query)
	plt.show()

def run_Gibbs(PD, steps = 300):
	#Description: Gibbs-Sampling pre-processing for queries
	#Output: Prob of each UCQ
	print("Start Gibbs-Sampling approximation")
	convergence = []
	query_index = 0
	for one_query in PD.queries:
		query_index = query_index + 1
		one_query_ = []
		table_list_one_query = [] 
		for one_conj in one_query:
		    one_conj_ = {}
		    var_count = {}  
		    table_list_one_conj = {}
		    for predicate in one_conj:
		        if predicate.name not in list(one_conj_.keys()):
		        	table_list_one_conj[predicate.name] = predicate.name
		        	name = predicate.name
		        	one_conj_[name] = []
		        	var_count[predicate.name] = 1
		        else:
		        	name = predicate.name + str(var_count[predicate.name] + 1)
		        	one_conj_[name]=[]
		        	table_list_one_conj[name] = predicate.name
		        	var_count[predicate.name] = var_count[predicate.name] + 1
		        for variable in predicate.variables:
		        	one_conj_[name].append(variable.name)
		    one_query_ .append(one_conj_)
		    table_list_one_query.append(table_list_one_conj)

		#Gibbs approximation
		gibbs = GibbsSampler(PD, one_query_, table_list_one_query, steps)
		prob, prob_stream = gibbs.Gibbs()
		convergence.append(prob_stream)
		print("Gibbs sampling approximation -- #%d query: " % query_index, prob)
	print('Done')
	
	view_convergence(convergence)
	

	


	