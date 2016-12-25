#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import numpy as np
from time import perf_counter

Item = namedtuple("Item", ['index', 'value', 'weight', 'density'])

def lin_relax_est(items, value, capacity):
    """
    Assumes list is sorted into value/weight density.
    """
    # Get optimistic estimate of optimal value by relaxing selection variable
    # to be in range 0 <= xi <=1
    estimate = value
    for item in items:
        if capacity <= 0:
            break
        v = item.value * min(capacity/float(item.weight), 1)
        estimate = estimate + v
        capacity = capacity - item.weight

    return estimate

def binary_search(items, capacity):
    # Sort items by value density
    sorted_items = sorted(items, key=lambda x: x[3], reverse=True)

    branch_stack = []

    # Set up first branch
    b = {'chosen_items': [],
         'index': 0,
         'value': 0,
         'capacity': capacity,
         'estimate': 0}

    # Set first branch as the best branch
    best_branch = b

    # Push first branch onto stack
    branch_stack.append(b)

    # Iterate over all the branches in the stack, popping off the last one
    # and working on it until we reach the final item.
    while len(branch_stack) > 0:
        # Pop off a branch to work on from the stack
        working_branch = branch_stack.pop()

        # Check first if the working stack's estimate is less than the
        # best stack's value. If it is, we can skip this branch
        if working_branch['estimate'] < best_branch['value']:
            continue

        start_index = working_branch['index']
        for index, item in enumerate(sorted_items[start_index:]):
            real_index = index + start_index
            value = working_branch['value']
            capacity = working_branch['capacity']
            current_items = working_branch['chosen_items'][:]
            # If we can fit the item in run the estimate with it
            if item.weight <= capacity:
                v_true = value + item.value
                c_true = capacity - item.weight
                
                # Only compute the estimate if this isn't the last node
                if real_index < len(sorted_items)-1:
                    e_true = lin_relax_est(sorted_items[real_index+1:],
                                           v_true, c_true)
                    # if the estimate is worse than the best value
                    #acheived so far, ignore this branch
                    if e_true < best_branch['value']:
                        continue

                working_branch['chosen_items'].append(item.index)
                working_branch['index'] = real_index
                working_branch['value'] = v_true
                working_branch['capacity'] = c_true
            else:
                continue

            # If this isn't the last node, un the estimate without the item
            if real_index < len(sorted_items)-1:
                e_false = lin_relax_est(sorted_items[real_index+1:],
                                        value, capacity)
       
                # Create a branch node for not choosing the item,
                # if its estimate is greater than the best value
                # and current working value
                if (e_false >= best_branch['value'] and
                    e_false >= working_branch['value']):
                    branch_stack.append({'chosen_items': current_items,
                                         'index': real_index+1,
                                         'value': value,
                                         'capacity': capacity,
                                         'estimate': e_false})

            # Update the best branch
            if best_branch['value'] < working_branch['value']:
                best_branch = working_branch

    # Fill out the coursera taken items list
    taken = np.zeros(len(items))
    for i in best_branch['chosen_items']:
        taken[i] = 1

    return (best_branch['value'], [int(x) for x in taken])

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
    return (value, [int(x) for x in decision_list])

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
        value = int(parts[0])
        weight = int(parts[1])
        density = float(value) / float(weight)
        items.append(Item(i-1, value, weight, density))
    

    # Make the decision whether to use dynamic programming or binary search
    #estimated_dp_mem_mb = ((len(items) * float(capacity) * 8)/1000000)
    estimated_dp_mem_mb = 8000
    if estimated_dp_mem_mb < 4000:
        #t1 = perf_counter()
        value, taken = dynamic_programming(items, capacity)
        #t2 = perf_counter()
        #dp_time = t2-t1
    else:
        #t1 = perf_counter()
        value, taken = binary_search(items, capacity)
        #t2 = perf_counter()
        #bs_time = t2-t1

    #print('dp_time='+str(dp_time)+' bs_time='+str(bs_time))

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
    output_data += ' '.join(map(str, taken))
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


