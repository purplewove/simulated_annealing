from numpy import matrix, genfromtxt
from numpy.random import permutation, random_integers, random
from math import e
'''
Created on Oct 22, 2015

@author: templetonc
'''
class TSP():
    def __init__(self, *args):
        self.data_source = args[0]
        self.distance_matrix = self.read_data(self.data_source)
        assert (len (self.distance_matrix.shape)) == 2
        assert self.distance_matrix.shape[0] == self.distance_matrix.shape[1]
        
    def read_data(self, data_source):
        return genfromtxt(data_source)

    def __len__(self):
        return int(self.distance_matrix.shape[0])

    def __getitem__(self, tup):
        x, y = tup
        return self.distance_matrix[x][y]

    def __repr__(self):
        return "TSP(%s)" % str(self.data_source)

    def __str__(self):
        return str(self.distance_matrix)

class Annealer():
    def __init__(self, initial_temperature, cooling_steps, cooling_fraction, steps_per_temp):
        self.temperature = initial_temperature
        self.cooling_steps = cooling_steps
        self.cooling_fraction = cooling_fraction
        self.steps_per_temp = steps_per_temp
        self.solution = []
        self.tsp_instance = None
    
    def set_problem(self, tsp_instance):
        self.tsp = tsp_instance
        
    
    def solve(self):
        counter = 0
        solution = self.initialize_solution()
        current_value = self.solution_cost(solution)
        for _ in range(self.cooling_steps):
            self.temperature *= self.cooling_fraction
            start_value = current_value
            for _ in range(self.steps_per_temp):
                #print counter
                counter += 1
                while True:
                    i1 = self.random_index()
                    i2 = self.random_index()
                    if i1 != i2:
                        break
                flip = self.random_float()
                delta, solution = self.transition(i1, i2, solution)
                merit = self.calculate_merit(delta, current_value)
                #print merit
                if (delta < 0):
                    #print ("delta is less than 0")
                    current_value = current_value + delta
                else: 
                    if merit > flip:
                        print ("delta is greater than zero and merit is greater than flip")
                        print "merit = %s, flip = %s, temp = %s" % (merit, flip, self.temperature)
                        current_value = current_value + delta
                    else: 
                        print ("delta is greater than zero and merit is LESS than flip")
                        print "merit = %s, flip = %s, temp = %s" % (merit, flip, self.temperature)
                        self.transition(i2, i1, solution)
            #why? restore the temperature
            if current_value < start_value:
                self.temperature = self.temperature/self.cooling_fraction
        return current_value, solution            
    
    def initialize_solution(self):
        solution = permutation(len(self.tsp))
        return solution
    
    def solution_cost(self, solution):
        assert len(solution) == len(self.tsp)
        cost = 0
        for i in range(len(self.tsp) - 1):
            cost += self.tsp[solution[i], solution[i+1]]
        return cost
            
    def random_index(self):
        return random_integers(len(self.tsp)) - 1
    
    def random_float(self):
        return random()
     
    def transition(self, i1, i2, solution):
        subtract = self.neighbor_cost(i1, solution) + self.neighbor_cost(i2, solution)
        solution = self.swap(i1, i2, solution)
        add = self.neighbor_cost(i1, solution) + self.neighbor_cost(i2, solution) 
        delta = add - subtract
        return delta, solution
       
    def neighbor_cost(self, i, solution):
        if i == 0:
            cost = self.tsp[solution[i], solution[i + 1]]
        elif i == len(self.tsp) - 1:
            cost = self.tsp[solution[i - 1], solution[i]]
        else: 
            cost = self.tsp[solution[i - 1], solution[i]] + self.tsp[solution[i], solution[i + 1]]
        return cost
    
    def calculate_merit(self, delta, current_value): #divide delta by current value?
        exponent = float(-delta)/float(current_value)/self.temperature
        try:
            merit = e**exponent 
        except OverflowError as err:
            print err.message
            print "exponent = %s, delta = %s, self.temperature = %s" % (exponent, delta, self.temperature)
        else:
            return merit
    
    def swap(self, i1, i2, solution):
        solution[i1], solution[i2] = solution[i2], solution[i1]
        return solution
        
if __name__ == '__main__':
    init_temp = .01
    cooling_steps = 1000
    cooling_fraction = .99
    steps_per_temp = 1000
    annealer = Annealer (init_temp, cooling_steps, cooling_fraction, steps_per_temp)      
    tsp = TSP("..\\att\\att48_d.txt")
    annealer.set_problem(tsp)
    
    #best_tour = [1, 8, 38, 31, 44, 18, 7, 28, 6, 37, 19, 27, 17, 43, 30, 36, 46, 33, 20, 47, 21, 32, 39, 48, 5, 42, 24, 10, 45, 35, 4, 26, 2, 29, 34, 41, 16, 22, 3, 23, 14, 25, 13, 11, 12, 15, 40, 9]
    #best_tour_adjusted = [n - 1 for n in best_tour]
    #assert len(best_tour) == 48
    #print ("cost of best tour is: %s" % str(annealer.solution_cost(best_tour_adjusted) + tsp[8, 0]))  
    cost, path = annealer.solve()
    print "cost = %s, path = %s" % (cost, path)
    
    
    