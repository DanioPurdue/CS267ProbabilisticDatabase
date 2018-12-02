class Predicate:
    def __init__(self, name, variables,negation = False):
        """
        Predicate class.
 
        Attributes
        --------------------
            name              --  Name of the table which the predicate corresponds to
            variables         --  Array of variable objects
            negation          --  Whether the predicate is negated or not
        """
        self.name = name
        self.variables = variables
        self.negation = negation

    def __str__(self):
        var_list = [str(one_var) for one_var in self.variables]
        negation = "~" if self.negation else ""
        return str(negation) + " " + self.name + str(var_list)