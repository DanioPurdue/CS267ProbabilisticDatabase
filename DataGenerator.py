import numpy as np

class DataGenerator:
    def __init__(self, n):
        self.n = n # number of data points you need
        self.generateTuples()

    def generateTuples(self):
        print("\n\ngenerating random data\n\n")
        """
        P, Q and R tables and they are similar to the input given in the examples
        P(x), Q(x), R(x, y)

        """
        # name of the table
        with open("test_table1.txt", "w") as file:
            file.write("P\n")
            for i in range(self.n):
                rand_val = np.random.rand(1)
                file.write(str(i) + "," + str(round(rand_val[0], 3))+"\n")

        with open("test_table2.txt", "w") as file:
            file.write("Q\n")
            for i in range(self.n):
                rand_val = np.random.rand(1)
                file.write(str(i) + "," + str(round(rand_val[0], 3))+"\n")

        with open("test_table3.txt", "w") as file:
            file.write("R\n")
            for j in range(self.n):
                for i in range(self.n):
                    if (i + j) % 3 == 0 or (i + j) % 4 == 0:
                        rand_val = np.random.rand(1)
                        file.write(str(i) + "," + str(j) + "," + str(round(rand_val[0], 3))+"\n")
                    
        with open("test_table4.txt", "w") as file:
            file.write("T\n")
            for j in range(self.n):
                for i in range(self.n):
                    if (i + j) % 3 == 1 or (i + j) % 4 == 0:
                        rand_val = np.random.rand(1)
                        file.write(str(i) + "," + str(j) + "," + str(round(rand_val[0], 3))+"\n")
        print("Done!")






if __name__ == "__main__":
    num_step = 500 #<--------change this n value
    print("Generate data points of size: " + str(num_step))
    DataGenerator(num_step)