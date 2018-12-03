class Lift:
    def __init__(self, database):
#         self.query = query
        self.database = database
        # predicate[][] query, [CNF1, CNF2,...]
        # dict{name: dataframe} database
    
    def convertCNF(self, query):
        """
        Convert UCQ to CNF
        """
        for CQ in query:
            for pred in CQ:
                pred.negation = True
                for var in pred.variables:
                    var.quantifier = "forall"
        
    def printQuery(self, query):
        for clause in query:
            for pred in clause:
                print(pred)
            print("")
        print("=====================================")
    
    def findInTable(self,table,variables): # str tableName; str_tuple variables
        """
        Find the probability of a variable tuple in a table, -1 if not found
 
        Parameters
        --------------------
            table             --  DataFrame, the table of the predicate
            variables         --  Tuple of name of ground variables(atom), (e.g. ("1","2"))
 
        Returns
        --------------------
            p       --  the probability of a variable tuple in a table, 
                        -1 if not found in table,
                        -400 if table does not exist
        """
        q_str = []
        for i in range(len(variables)):
            s = "var"+str(i+1)+" == "+variables[i]
            q_str.append(s)
        q_str = (" & ").join(q_str)
        print("query string: ", q_str)
        t = table.query(q_str)
        print("after query: ")
        print(t["1"])
        return t["1"].Pr

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
        pred_list_1 = [pred.name for cnf in q1 for pred in cnf]
        pred_list_2 = [pred.name for cnf in q2 for pred in cnf]
        return len(set(pred_list_1) & set(pred_list_2)) == 0
    
    def Step3(self,query):
        """
        Step 3 of the Lifted Inference Algorithm
        
        Parameters
        --------------------
            query         --  the query to evaluate
 
        Returns
        --------------------
            p       -- the probability of query if there is decomposable disjunction
                    -- -1 if fails
        """
        m = len(query)
        if m <= 1:
            return -1
        for i in range(1,m):
            q1 = query[:i]
            q2 = query[i:]
            if self.isIndependent(q1,q2):
                return (1-self.infer(q1)) * (1-self.infer(q2))
        return -1
    
    def find_separator(self,query):
        variables_at = dict()
        if len(query) != 1:
            print("not conjunction query")
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
        if all([variable.quantifier == "universal" for variable in variables]):
            result = 1
            for sepa_value in sepa_values:
                temp_query = [[]]
                for id_p, predicate in enumerate(predicates):
                    temp_query[0].append(predicate)
                    for id_v, variable in enumerate(predicate.variables):
                        if variable.name == separator:
                            temp_query[0][id_p].variables[id_v].name = sepa_value
                            temp_query[0][id_p].variables[id_v].atom = True
                result = result * self.infer(temp_query)
            return result
        elif all([variable.quantifier == "exist" for variable in variables]):
            result = 1
            temp_query = [[]]
            for id_p, predicate in enumerate(predicates):
                temp_query[0].append(predicate)
                for id_v, variable in enumerate(predicate.variables):
                    if variable.name == separator:
                        for sepa_value in sepa_values:
                            temp_query[0][id_p].variables[id_v].name = sepa_value
                            temp_query[0][id_p].variables[id_v].atom = True
                            temp_query[0][id_p].variables[id_v].quantifier = "universal"
                            result = result * (1 - self.infer(temp_query))
            return 1 - result                  
            
                    
    def step0(self, query):
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
            table = self.database[predicate.name]
            if all([var.atom for var in predicate.variables]):
                parameter = tuple([var.name for var in predicate.variables])
                # tuple of variables in predicate
                p = self.findInTable(table, parameter)
                return p
        return -1
    
    def Step4(self, query):
        if not query:
            return -400
#         flag, q = separa_inde(query)
#         if flag:
#             return self.infer(q[0])*self.infer(q[1])
#         else:
#             return -1
        return -1
            
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
#         flag_0 = self.Step0(query)
#         if flag_0 == -400:
#             print("not query")
#         elif flag_0 == -1:
#             flag_4 = self.Step4(query)
#             if flag_4 == -400:
#                 print("not query")
#             elif flag_4 == -1:
#                 flag_5 = self.Step5(query)
#                 if flag_5 == -400:
#                     print("not query")
#                 elif flag_5 == -1:
#                     print("fail")
#                     return -1
#                 else:
#                     return flag_5
#             else:
#                 return flag_4
#         else:
#             return flag_0
        
        p = self.step0(query)
        print (query)
        if p != -1:
            print ('step 0: ', p)
            return p
        p = self.Step3(query)
        if p != -1:
            print ('step 3: ', p)
            return p
        p = self.Step5(query)
        if p != -1:
            print ('step 5: ', p)
            return p
        return -999

