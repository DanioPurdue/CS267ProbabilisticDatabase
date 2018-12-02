import pandas as pd
import numpy as np
import random
import itertools
import pdb
import matplotlib.pyplot as plt
import progressbar
import math

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

	def var_state(self, var, query, conj_index):
		#Descritpion: Retrive state of a variable from tuples with status 1 
		#Return: A set of states
		state = set()
		table_list = []
		for key in query.keys():
			if var in query[key]:
				matched_table = self.table_matching[conj_index][key]
				table_list.append((matched_table,query[key].index(var)))
		for table,var_index in table_list:
			state_list = self.data.tables_df[table].values[:,var_index].astype(int).tolist()
			for _ in range(len(state_list)):
				if self.world[table][_] == 1:
					state.add(state_list[_])
		return state

	def check_single_state(self, single_state, query, conj_index):
		#Description: Check World SAT of a single_state 
		#Return: True or False
		predicate_sat = [0 for _ in range(len(query.keys()))]
		for table in query.keys():
			temp = [single_state[var] for var in query[table]]
			matched_table = self.table_matching[conj_index][table]
			num_tuples = self.data.tables_df[matched_table].values.shape[0]
			for index in range(num_tuples):
				if self.world[matched_table][index] == 1:
					if (list(self.data.tables_df[matched_table].values[index][0:-1])==temp):
						predicate_sat[list(query.keys()).index(table)] = 1
						break
				else:
					continue
		return all(predicate_sat)


	def check_world(self, query, conj_index):
		#Description: Check World SAT for each conj in one world
		#Return: True or False
		
		flag = [] 
		for key in query.keys():
			matched_table = self.table_matching[conj_index][key]
			if any(self.world[matched_table]) == False: # If any table has all 0 prob, return False
				return False
			if all(self.world[matched_table]) == True:
				flag.append(True)
		if all(flag) & len(flag)!=0: #If all tables has 1 prob, return True
			return True
		
		var_state = {} 
		var_names=set(var for _ in query.values() for var in _) #Get variable names of the query/conj
		for var in var_names:
			var_state[var] = self.var_state(var, query, conj_index) #Retrieve state of each variable from tuples with status 1

		all_combi = list(itertools.product(*var_state.values())) #Retrieve all possible variable state combinations 
		for each in all_combi:
			sat = self.check_single_state(dict(zip(var_names, each)), query, conj_index) #Check SAT of each possible state
			if sat == True:
				return True
		return False


	def Gibbs(self):
		#Description: Gibbs sampling
		#Return: Approximate inference for one query
		update_count = 0 #Sampling update count. 1 update_count: a single tuple sampling
		iter_count = 0 #Iteration count. 1 iter_count: sampling for all tuples 
		sat_num = 0 # Satisfied world count. Checked for each update_count
		convergence = []
		bar = progressbar.ProgressBar(maxval=1, widgets=[progressbar.Bar('=', '[', ']'), ' ',progressbar.Percentage()])
		bar.start()
		while iter_count < self.iter_max:
			query_table = set(table for _ in self.table_matching for table in _.values())
			for table in query_table: 
				num_tuples = self.data.tables_df[table].shape[0]
				for index in range(num_tuples):
					self.world[table][index] = self.sampling(self.data.tables_df[table].values[index,-1])
					conj_index = 0 #Index of each conj in one UCQ
					for one_conj in self.parsedquery: #Check world SAT for each conj
						if self.check_world(one_conj, conj_index):
							sat_num = sat_num + 1
							break
						conj_index = conj_index + 1
					update_count = update_count + 1
					convergence.append(sat_num/update_count)
			iter_count = iter_count + 1
			bar.update(iter_count/self.iter_max)
		bar.finish()
		
		return sat_num / update_count, convergence


def view_convergence(convergence):
	#Description: Plot convergence rate
	num = len(convergence)
	if math.sqrt(num).is_integer():
		row = int(math.sqrt(num))
		col = row
	else:
		row = int(math.sqrt(num)) + 1
		col = row
	fig, axs = plt.subplots(row, col)

	for ax, query in zip(axs.flatten(), convergence):
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

	


	