class Lift:
    def __init__(self, database):
#         self.query = query
        self.database = database
        # predicate[][] query, [CNF1, CNF2,...]
        # dict{name: dataframe} database
    
        
    def printQuery(self, query):
        for clause in query:
            for pred in clause:
                print(pred)
            print("")
        print("=====================================")
    
    
    def findInTable(self,tableName,variables): # str tableName; str_tuple variables
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
        if len(variables)==1:
            variables = variables[0]
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
            return -400
        m = len(query[0])
        for i in range(1,m):
            q1 = query[:m]
            q2 = query[m:]
            if self.isIndependent(q1,q2):
                return 1 - (1-self.infer(q1)) * (1-self.infer(q2))
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
        
        if all([variable.quantifier == "exist" for variable in variables]):
            result = 1
            for sepa_value in sepa_values:
                temp_query = [[]]
                for id_p, predicate in enumerate(predicates):
                    temp_query[0].append(copy.deepcopy(predicate))
                    for id_v, variable in enumerate(predicate.variables):
                        if variable.name == separator:
                                temp_query[0][id_p].variables[id_v].name = sepa_value
                                temp_query[0][id_p].variables[id_v].atom = True
                                temp_query[0][id_p].variables[id_v].quantifier = "universal"
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
        
        p = self.Step0(query)
        if p != -1:
            print ('step 0: ', p)
            return p
        p = self.Step2(query)
        if p != -1:
            print ('step 2: ', p)
            return p
        p = self.Step5(query)
        if p != -1:
            print ('step 5: ', p)
            return p
        return -999