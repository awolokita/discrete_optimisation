#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import numpy as np

Item = namedtuple("Item", ['index', 'value', 'weight'])



def dynamic_programming(items, capacity):
    """
    Table is of form:
      j
    k 0 . . N-1
    0
    1
    . 
    .
    K

    where k is remaining capacity and j is the item number
    """
    # Initialise the DP table
    table = np.zeros((capacity+1, len(items)+1))
    
    # Iterate over Item list
    for item in items:
        j = item.index+1
	# Initialise the current item column as the previous one
        table[:,j] = table[:,j-1]

        # Check if the item even fits with 100% capacity.
        # If not, that column is the same as the previous one.
        if item.weight > capacity:
            continue

        for k in range(0, capacity+1):
            # Check if this item fits at this k capacity
            if item.weight > k:
                continue

            # Check if the previous value in the left column is the same or
            # better
            val = item.value + table[k-item.weight,j-1]
            if val > table[k,j-1]:
                table[k,j] = val
    
    # Traceback optimal solution
    j = len(items)
    k = capacity
    decision_list = np.zeros(len(items))
    value = table[k,j]
    while j > 0:
        # Check if we have chosen this item
        if table[k,j] > table [k,j-1]:
            decision_list[j-1] = 1
            k = k - items[j-1].weight
        j = j-1

    #print(table)
    return (value, decision_list)


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1])))

    value, taken = dynamic_programming(items, capacity)

    # a trivial greedy algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    #value = 0
    #weight = 0
    #taken = [0]*len(items)


#    for item in items:
#        if weight + item.weight <= capacity:
#            taken[item.index] = 1
#            value += item.value
#            weight += item.weight
    
    # prepare the solution in the specified output format
    output_data = str(int(value)) + ' ' + str(1) + '\n'
    output_data += ' '.join(map(str, [int(x) for x in taken]))
    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')


