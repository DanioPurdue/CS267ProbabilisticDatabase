import sys
import numpy as np
import pandas as pd
from Variable import Variable
from Predicate import Predicate
import GibbsSampling
from Lift import Lift 
from datetime import datetime


# Load read the
class TableLoader:
    """
        Description: given the name of the table, the table is loaded into a dataframe,
        but it can also be converted the a dictionary of dictionary for one table.
        dataframe is the main form of of the representations for the liftable inference algorithm.
        All the tables are represented as a dictionary of dataframes
    """
    def loadTable(self, path):
        # load the table and convert it to the dataframe
        df = pd.read_csv(path, skiprows=1, sep=',', header=None)
        file = open(path, "r")
        df.name = file.readline().strip('\n')
        file.close()
        names = []
        for i in range(len(df.columns) - 1):
            names.append('var' + str(i + 1))
        names.append('Pr')
        df.columns = names
        return df

    def dataFrameToDictTable(self, df):
        # convert the pandas dataframe into a a list [table name, dict()]
        table = dict()
        table_name = df.name
        # this function is for gibbs sampler
        for one_row in df.itertuples():
            names = [one_row[idx] for idx in range(1, len(one_row) - 1)]
            table[tuple(names)] = one_row[-1]
        return [table_name, table]

    def dataFrameToStringDictTable(self, df):
        # convert the pandas dataframe into a a list [table name, dict()]
        table = dict()
        table_name = df.name
        # this function is for gibbs sampler
        for one_row in df.itertuples():
            names = [str(one_row[idx]) for idx in range(1, len(one_row) - 1)]
            table[tuple(names)] = one_row[-1]
        return [table_name, table]
    
    def getAllVariables(self, df):
        # this function is for gibbs sampler
        table_name = df.name
        rand_vars_list = []
        for one_row in df.itertuples():
            names = [str(one_row[idx]) for idx in range(len(one_row) - 1)]
            prob = one_row[-1]
            rand_vars_list.append(randomVar(df.name, names, prob))
        return rand_vars_list
   
class QueryParser:
    """
        Description: parsed the raw string input
        Query to the designated form for the lifted inference algorithm
    """
    def parseString(self, query_str):
        """
        :param query_str: string - the input string
        :return: res_query: a list of conjunctive queries, and each conjunctive queries
        """
        res_query = list()
        conj_list = query_str.strip().split("||")
        for conj_query in conj_list:
            # print("pre " + conj_query)
            res_query.append(self.conjuncQueryParser(conj_query.strip()))
            # print("end =========")
        return res_query

    def conjuncQueryParser(self, conj_query):
        # Description: get the tables for each conjunctive query
        # return: a list of predicates object
        conj_list = list()
        i = 0
        str_len = len(conj_query)
        while i < str_len:
            if conj_query[i].isupper():
                one_table = ""
                while conj_query[i] != ")":
                    one_table += conj_query[i]
                    i = i + 1
                one_table += conj_query[i]
                conj_list.append(one_table)
            i += 1
        # print("processed:" + str(conj_list))
        return [self.predicateParser(one_pred_str) for one_pred_str in conj_list]

    def predicateParser(self, one_pred_str):
        left_idx = one_pred_str.find('(')
        right_idx = one_pred_str.find(')')
        pred_name = one_pred_str[0:left_idx];
        var_strs = one_pred_str[left_idx + 1: right_idx].strip().split(',')
        variables = [Variable(one_var.strip()) for one_var in var_strs]
        return Predicate(pred_name, variables)

class randomVar:
    def __init__(self, table_name, var_names, prob):
        """
        randomVar object: each object is a tuple in the database

        Parameters
        --------------------
            tablename         --  String, Name of the table
            var_name          --  tuple of string, names of each variables
            prob              --  float, probabiliy associated with that tuple

        """
        self.table_name = table_name
        self.var_names = var_names
        self.prob = prob

    def getNames(self):
        return self.var_names

    def getTableName(self):
        return self.table_name

    def sample(self):
        return np.random.binomial(1, self.prob);

class ProbaDatabase:
    def __init__(self):
        self.query_file_path = None
        self.tables_path = []
        self.tables_df = dict() #tables in dataframe Form
        self.tables_dicts = dict()
        self.queries = []
        self.hard_query_idxs = []
        self.raw_query_strs = []

    def loadTablesAndQueries(self):
        """
        this function call queryParser and TableLoader, and this function is called
        in the main()
        """

        # load all the tables into the pandas dataframe
        tableLoader = TableLoader()
        for table_path in self.tables_path:
            df = tableLoader.loadTable(table_path)
            self.tables_df[df.name] = df
            table_name, one_dict = tableLoader.dataFrameToStringDictTable(df)
            self.tables_dicts[table_name] = one_dict

        # load all the queries
        queryParser = QueryParser()
        with open(self.query_file_path, "r") as file:
            one_line = file.readline()
            while one_line:
                q_str = one_line.strip("\n")
                print("query string: " + q_str)
                self.raw_query_strs.append(q_str)
                self.queries.append(queryParser.parseString(q_str))
                one_line = file.readline()

if __name__ == "__main__":
    PD = ProbaDatabase()
    options = sys.argv[1:]
    idx = 0
    """ Parsing Input """
    while idx < len(options):
        one_entry = options[idx]
        if options[idx] == "--table":
            idx += 1
            PD.tables_path.append(options[idx])
        elif options[idx] == "--query":
            idx += 1
            PD.query_file_path = options[idx]
        else:
            print("invalid input")
        idx = idx + 1
    PD.loadTablesAndQueries()
    DB = PD.tables_dicts
    

    lift = Lift(DB)
    query_idx = 0
    for q in PD.queries:
        start=datetime.now()
        print("Solving Query: ")
        lift.printQuery(q)
        p = lift.infer(q)
        print("p = ", p)
        print("Execution time: ",datetime.now() - start)
        print("=================================\n\n")
        if p == -999:
            PD.hard_query_idxs.append(query_idx)
        query_idx += 1
    
    if len(PD.hard_query_idxs) != 0:
        print("The query file contains %d hard queries." % len(PD.hard_query_idxs))
        num_steps = 1000
        print("Number of steps for each sample: " + str(num_steps))
        GibbsSampling.run_Gibbs(PD,num_steps) #Optional positional keyword: steps = # of steps

