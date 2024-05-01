import sys
import heapq
import itertools
import random
from collections import defaultdict, Counter
import networkx as nx


# Step 1: Extract symbols from the KB --> parse it
# Step 2: Make a binary table --> binary tree
# Step 3: Loop over each sentence in the KB = {s1, s2, s3, etc}
# Step 4: Look for config in which KB is true
# Step 5: Check if the query is true in these configs
# Output: Yes (how many configurations is it true?) or No (nothing else here)
def TT():
    return True


# Forward chaining
def FC():
    return True


# Backward chaining
def BC():
    return True


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 assign2.py <filename> <search_method>")
        return

    filename = sys.argv[1]
    search_method = sys.argv[2]

    search_methods = {
        'FC': FC,
        'TT': TT,
        'BC': BC
    }

    method_function = search_methods.get(search_method)
    if method_function:
        result = method_function()
        print(result)  # You need to decide what to print here
    else:
        print("Invalid method function")


if __name__ == "__main__":
    main()