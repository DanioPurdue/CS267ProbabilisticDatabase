class Variable:
    def __init__(self, name, atom = False):
        """
        Predicate class.
 
        Attributes
        --------------------
            name              --  Name of the variable (e.g. "x1", "1")
            quantifier        --  "exist" or "forall"
            atom              --  Whether the variable is a ground atom
        """
        
        self.name = name
        self.quantifier = "exist"
        self.atom = atom

    def __str__(self):
        atom = "(atom)" if self.atom else ""
        return str(self.quantifier) + " " + str(self.name) + " " + atom