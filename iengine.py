import sys
import heapq
import itertools
import random
from collections import defaultdict, Counter
import networkx as nx
import re


# Step 1: Extract symbols from the KB --> parse it
# Step 2: Make a binary table --> binary tree
# Step 3: Loop over each sentence in the KB = {s1, s2, s3, etc}
# Step 4: Look for config in which KB is true
# Step 5: Check if the query is true in these configs
# Output: Yes (how many configurations is it true?) or No (nothing else here)

# class KnowledgeBase:
#     def __init__(self):
#         self.clauses = set()
#         self.rules = []


def evaluate_clause(clause, assignment):
    if "=>" in clause:
        antecedent, consequent = clause.split("=>")
        return not antecedent.strip() or (antecedent.strip() and assignment.get(antecedent.strip(), False)) == assignment.get(consequent.strip(), False)
    else:
        return clause.strip() and assignment.get(clause.strip(), False)


def TT(kb, query):
    # Extract symbols mentioned in KB clauses and the query
    kb_symbols = sorted(set().union(*(re.findall(r'\b[A-Za-z]+\b', clause) for clause in kb)))
    query_symbols = sorted(set(re.findall(r'\b[A-Za-z]+\b', query)))
    symbols = sorted(set(kb_symbols + query_symbols))

    # Generate all possible combinations of truth values for symbols
    truth_assignments = itertools.product([False, True], repeat=len(symbols))

    # Initialize variables for counting models and checking entailment
    models = 0

    # Check truth table
    for assignment_values in truth_assignments:
        assignment = dict(zip(symbols, assignment_values))

        # Evaluate each clause in the KB
        kb_truth_values = [evaluate_clause(clause, assignment) for clause in kb]

        # Check if all KB clauses are true under the current assignment
        if all(kb_truth_values):
            # Increment model count if KB is true under current assignment
            models += 1
            # # Evaluate the query under the current assignment
            query_truth_value = evaluate_clause(query, assignment)

            # If the query is true under the current assignment, return YES and the number of models
            if query_truth_value:
                return f"YES: {models}"
    else:
        return "NO"


# Forward chaining
def FC(kb, query):
    inferred = defaultdict(bool)  # Stores whether a symbol is inferred
    count = Counter()  # Counts how many premises of each rule are satisfied

    # Step 1: Initialize agenda with symbols known to be true
    agenda = [symbol for symbol in kb if "=>" not in symbol and evaluate_clause(symbol, {})]

    # Step 2: Main loop
    while agenda:
        p = agenda.pop(0)  # Get the first symbol from the agenda
        if p == query:  # If the query is inferred, return YES
            inferred_symbols = [symbol for symbol in inferred.keys() if inferred[symbol]]
            return "YES: " + ", ".join(inferred_symbols)
        if not inferred[p]:  # If the symbol is not already inferred
            inferred[p] = True
            # Step 3: For each implication containing p in the premise
            for clause in kb:
                if "=>" in clause and p in clause.split("=>")[0]:
                    count[clause] += 1
                    # If all premises are satisfied, infer the consequent
                    if count[clause] == clause.split("=>")[0].count(" ") + 1:
                        q = clause.split("=>")[1].strip()
                        agenda.append(q)
                        inferred[q] = True  # Mark the consequent as inferred

    return "NO"  # If the query cannot be inferred





# Backward chaining
def BC():
    return True

# # #load text file
# def load_file(filename):
#     with open(filename, 'r') as f:
#         lines = f.readlines()   
#     return lines


def parse_TT(filename):
    with open(filename, 'r') as file:
        content = file.read()

    # Extract the kb and query
    match = re.search(r"TELL\s+(.*?)(;|$)", content, re.DOTALL)
    query_match = re.search(r"ASK\s+(.*)", content)
    
    if match and query_match:
        kb = match.group(1).strip().split(';')
        query = query_match.group(1).strip()

        # Process the knowledge base to split into individual clauses
        clauses = [clause.strip() for clause in kb if clause.strip()]
        return clauses, query
    else:
        raise ValueError("The file format is incorrect or the content is missing")

#jenn's code section
def parse_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()   

    kb = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("ASK"):
            kb.append(line)
        elif line.startswith("ASK"):
            query = line.split(" ")[1]

    return kb, query


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 iengine.py <filename> <search_method>")
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
        try:
            clauses, query = parse_TT(filename)
            result = method_function(clauses, query)
            if search_method == 'TT':
                if 'YES' in result:
                    print(result)
                else:
                    print("NO")
            else:
                if result:
                    print("YES:", ", ".join(result))
                else:
                    print("NO")
        except ValueError as e:
            print("Error:", e)
    else:
        print("Invalid method function")

if __name__ == "__main__":
    main()
