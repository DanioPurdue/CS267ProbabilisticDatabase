import copy
from itertools import combinations
from Variable import Variable
from Predicate import Predicate


class Lift:
    def __init__(self, database):
#         self.cache = []
        self.database = database

        
    def printQuery(self, query):
        print("=====================================")
        for clause in query:
            for pred in clause:
                print(pred)
            print("")
    
    
    def findInTable(self,tableName,variables):
        """
        Find the probability of a variable tuple in a table, -1 if not found
 
        Parameters
        --------------------
            tablename         --  String, Name of the table
            variables         --  Tuple of name of ground variables(atom), (e.g. ("1","2"))
 
        Returns
        --------------------
            p       --  the probability of a variable tuple in a table, 
                        -1 if not found in table,
                        -400 if table does not exist
        """
        
        if tableName not in self.database:
            return -400
        table = self.database[tableName]
        if variables not in table:
            return 0    ##return 0
        else:
            return table[variables]
   
                    
    def Step0(self, query):
        """
        Step 0 of Lifted Inference Algorithm 
 
        Parameters
        --------------------
 
        Returns
        --------------------
            p           --  the probability of a variable tuple in a table, 
                        -1 if not applicable,
                        -400 if query is empty
        """
        if not query:
            return -400
        if len(query) == 1 and len(query[0]) == 1:
            predicate = query[0][0]
            if all([var.atom for var in predicate.variables]):
                parameter = tuple([var.name for var in predicate.variables])
                # tuple of variables in predicate
                p = self.findInTable(predicate.name,parameter)
                if predicate.negation:
                    return 1-p
                return p
        return -1

    def getRelationalSymbols(self, q):
        """
        Take a query, return the set of all its relational symbols (predicate names and non-atom variable names)
        """
        
        rs = []
        for clause in q:
            for pred in clause:
                rs.append(pred.name)
                for var in pred.variables:
                    if not var.atom:
                        rs.append(var.name)
        return set(rs)
    
    def isIndependent(self,q1,q2):
        """
        Parameters
        --------------------
            q1         --  the first query, [][]
            q2         --  the second query, [][]
 
        Returns
        --------------------
            True       -- if q1 and q2 are independent
            False      -- if not
        """
        rs_1 = self.getRelationalSymbols(q1)
        rs_2 = self.getRelationalSymbols(q2)
        return len(rs_1 & rs_2) == 0
    
    def find_common_predicate(self, query):
        if len(query) == 1:
            return -1
        sets = []
        for cq in query:
            sets.append(set([predicate.name for predicate in cq]))
        and_sets = sets[0]
        for set_ in sets[1:]:
            and_sets = and_sets & set_
        if not len(and_sets) == 0:
            return list(and_sets)[0]
        return -1  
    
    def change_variables(self, query, common_predicate_name):
        new_query = copy.deepcopy(query)
        variables_names = [chr(i) for i in range(97, 123)]
        for id_c, cq in enumerate(query):
            for predicate in cq:
                if predicate.name == common_predicate_name:
                    standard_names = [variable.name for variable in predicate.variables]
            for id_p, predicate in enumerate(cq):
                if not predicate.name == common_predicate_name:
                    for id_v, variable in enumerate(predicate.variables):
                        if variable.name in standard_names:
                            index = standard_names.index(variable.name)
                            if index > 25:
                                print("wrong index")
                            else:
                                new_query[id_c][id_p].variables[id_v].name = variables_names[index]
        variables = []
        for i in range(len(standard_names)):
            variables.append(Variable(variables_names[i]))
        s1 = Predicate(common_predicate_name,variables)
        query1 = [[s1]]
        query2 = []
        for id_c, cq in enumerate(new_query):
            query2.append([])
            for predicate in cq:
                if not predicate.name == common_predicate_name:
                    query2[id_c].append(predicate)
        return query1, query2
    
    def convert_to_and_form(self, querys, separator):
        sepa_values = []
        for query in querys:
            for cq in query:
                for predicate in cq:
                    for id_v, variable in enumerate(predicate.variables):
                        if variable.name == separator:
                            table = self.database[predicate.name]
                            tuples = table.keys()
                            for tuple_ in tuples:
                                if not tuple_[id_v] in sepa_values:
                                    sepa_values.append(tuple_[id_v])  
        result = 1
        for value in sepa_values:
            infer_result = 1
            for query in querys:
                temp_query = []
                for id_c, cq in enumerate(query):
                    temp_query.append([])
                    for id_p, predicate in enumerate(cq):
                        temp_query[id_c].append(copy.deepcopy(predicate))
                        for id_v, variable in enumerate(predicate.variables):
                            if variable.name == separator:
                                temp_query[id_c][id_p].variables[id_v].name = value
                                temp_query[id_c][id_p].variables[id_v].atom = True
                infer_result = infer_result * self.infer(temp_query)
            result = result*(1-infer_result)
        return 1-result
    
    def Step1(self, query):
        common_predicate_name = self.find_common_predicate(query)
        if not common_predicate_name == -1:
            query1,  query2 = self.change_variables(query, common_predicate_name)
            if self.isIndependent(query1, query2):
                return self.infer(query1)*self.infer(query2)
            else:
                temp_query = [[]]
                for query in [query1, query2]:
                    for cq in query:
                        for predicate in cq:
                            temp_query[0].append(copy.deepcopy(predicate))
                separator = self.find_separator(temp_query)
                if separator != -1:
                    result = self.convert_to_and_form([query1, query2], separator)
                    return result
                else:
                    return -1 
        else:
            return -1
        
    
    def Step2(self,query):
        """
        Step 2 of the Lifted Inference Algorithm
        
        Parameters
        --------------------
            query         --  the query to evaluate
 
        Returns
        --------------------
            p       -- the probability of query if there is decomposable conjunction
                    -- -1 if fails
        """
        if len(query) != 1:
            return -1
        m = len(query[0])
        for i in range(1,m):
            q1 = [query[0][:i]]
            q2 = [query[0][i:]]
            if self.isIndependent(q1,q2):
                return self.infer(q1) * self.infer(q2)
        return -1
    
    
    def equalQ(self,q1,q2):
        if len(q1) != len(q2):
            return False
        for c1,c2 in zip(q1,q2):
            if len(c1) != len(c2):
                return False
            for p1,p2 in zip(c1,c2):
                if p1.name != p2.name or len(p1.variables) != len(p2.variables):
                    return False
                for v1,v2 in zip(p1.variables,p2.variables):
                    if v1.name != v2.name:
                        return False
        return True
    
    def existInCache(self,q):
        return any([self.equalQ(q,q2) for q2 in self.cache])
    
    def sep_cq(self,query):
        query_union = []
        predicate1 = query[0][0]
        var_names = [variable.name for variable in predicate1.variables]
        query_union.append([var_names,[predicate1]])
        for id_p,predicate in enumerate(query[0][1:]):
            var_names = [variable.name for variable in predicate.variables]
            length = len(query_union)
            for id_u in range(length):
                union = query_union[id_u]
                key = union[0]
                if len(set(var_names) & set(key)) == 0:
                    if id_u!=length-1:
                        continue
                    else:
                        query_union.append([var_names, [predicate]]) 
                else:
                    new_key = var_names if len(var_names)>len(key) else key
                    query_union[id_u][1].append(predicate)
                    query_union[id_u][0] = new_key
        keys = []
        query_union_new = []
        for id_u, union in enumerate(query_union):
            if union[0] in keys:
                idx = keys.index(union[0])
                for q in union[1]:
                    print(q.name)
                    if not q.name in [predicate.name for predicate in query_union_new[idx]]: 
                        query_union_new[idx].append(q)
            else:
                keys.append(union[0])
                query_union_new.append(union[1])            
        querys = [[union] for union in query_union_new]
        return querys 

    def sep_dq(self,query):
        query_union = []
        predicate1 = query[0]
        var_names = [variable.name for variable in predicate1[0].variables]
        query_union.append([var_names,[predicate1]])
        for id_p,predicate in enumerate(query[1:]):
            var_names = [variable.name for variable in predicate[0].variables]
            length = len(query_union)
            for id_u in range(length):
                union = query_union[id_u]
                key = union[0]
                if len(set(var_names) & set(key)) == 0:
                    if id_u!=length-1:
                        continue
                    else:
                        query_union.append([var_names, [predicate]]) 
                else:
                    new_key = var_names if len(var_names)>len(key) else key
                    query_union[id_u][1].append(predicate)
                    query_union[id_u][0] = new_key
        querys = [union[1] for union in query_union] 
        return querys 
          
        
    def queryUnion(self, querys):
        """
        Step 2 of the Lifted Inference Algorithm
        
        Parameters
        --------------------
            querys         --  an array of single clause querys
 
        Returns
        --------------------
            rtn            --  the query which is the union of all input clauses
        """
        rtn = []
        for q in querys:
            clause = q[0]
            rtn.append(clause)
        return rtn
    
    def Step3(self, query):
        # Only operates on CQ
        if len(query) > 1:
            return -1
        
#         if self.existInCache(query):
#             return -1
        
#         self.cache.append(query)     
        querys = self.sep_cq(query)
        m = len(querys)
        if len(querys) == 1:
            return -1
        
        rst = 0
        nums = [x for x in range(m)]
        for i in range(m):
            for comb in combinations(nums,i+1):
                print(comb)
                q = [querys[j][0] for j in comb]
                print(self.infer(q))
                rst += (-1)**(len(comb)+1) * self.infer(q)
        return rst
    
    def Step4(self, query):
        """
        Step 4 of the Lifted Inference Algorithm
        
        Parameters
        --------------------
            query         --  the query to evaluate
 
        Returns
        --------------------
            p       -- the probability of query if there is decomposable disjunction
                    -- -1 if fails
        """
        if not query:
            return -1
        m = len(query)
        if m < 2:
            return -1
        for i in range(1,m):
            q1 = query[:i]
            q2 = query[i:]
            if self.isIndependent(q1,q2):
                rst = 1 - (1-self.infer(q1)) * (1-self.infer(q2))
                return rst
        return -1
    
    
    
    def find_separator(self,query):
        variables_at = dict()
        if len(query) != 1:
            print("not conjunction query in Step5")
            return -1
        predicates = [predicate for predicate in query[0]]
        for predicate in predicates:
            for variable in predicate.variables:
                if variable.atom == True:
                    continue
                if variable.name not in variables_at.keys():
                    variables_at[variable.name] = []
                variables_at[variable.name].append(predicate.name)
        for key in variables_at:
            if len(variables_at[key]) == len(predicates):
                return key
        print("no separator")
        return -1
           
    def convert_to_uni(self, query, separator):
        if len(query) != 1:
            self.printQuery(query)
            print("not conjunction query")
            return -1
        predicates = [predicate for predicate in query[0]] 
        sepa_values = []
        for predicate in predicates:
            for id_v, variable in enumerate(predicate.variables):
                if variable.name == separator:
                    table = self.database[predicate.name]
                    tuples = table.keys()
                    for tuple_ in tuples:
                        if not tuple_[id_v] in sepa_values:
                            sepa_values.append(tuple_[id_v])  
        variables = []
        for predicate in predicates:
            for variable in predicate.variables:
                if (not variable in variables) and (variable.atom == False):
                    variables.append(variable)               
        
        result = 1
        for sepa_value in sepa_values:
            temp_query = [[]]
            for id_p, predicate in enumerate(predicates):
                temp_query[0].append(copy.deepcopy(predicate))
                for id_v, variable in enumerate(predicate.variables):
                    if variable.name == separator:
                            temp_query[0][id_p].variables[id_v].name = sepa_value
                            temp_query[0][id_p].variables[id_v].atom = True
            result = result * (1 - self.infer(temp_query))
        return 1 - result                  
            


            
    def Step5(self, query):
        if not query:
            return -400
        separator = self.find_separator(query)
        if separator != -1:
            result = self.convert_to_uni(query, separator)
            return result
        else:
            return -1
            
    def infer(self, query):
        p = self.Step0(query)
        if p != -1:
#             print ('step 0: ', p)
            return p
        
        p = self.Step1(query)
        if p != -1:
#             print ('step 1: ', p)
            return p
        
        p = self.Step2(query)
        if p != -1:
#             print ('step 2: ', p)
            return p
        
        p = self.Step3(query)
        if p != -1:
#             print ('step 3: ', p)
            return p
        
        p = self.Step4(query)
        if p != -1:
#             print ('step 4: ', p)
            return p
        
        p = self.Step5(query)
        if p != -1:
#             print ('step 5: ', p)
            return p
        print("Not liftable")
        return -999