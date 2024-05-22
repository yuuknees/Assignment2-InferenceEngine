import sys
import itertools
from collections import defaultdict, Counter
import networkx as nx
import re


# Step 1: Extract symbols from the KB --> parse it
# Step 2: Make a binary table --> binary tree
# Step 3: Loop over each sentence in the KB = {s1, s2, s3, etc}
# Step 4: Look for config in which KB is true
# Step 5: Check if the query is true in these configs
# Output: Yes (how many configurations is it true?) or No (nothing else here)

def evaluate_clause(clause, assignment):
    # Evaluate a single clause based on the truth assignment
    # Returns True if the clause is true under the assignment, otherwise False
    if '=>' in clause:  # Implication
        antecedent, consequent = clause.split('=>')
        antecedent = antecedent.strip()
        consequent = consequent.strip()
        if antecedent not in assignment:
            return True  # Implication is vacuously true if antecedent is not in assignment
        return not assignment[antecedent] or assignment.get(consequent, False)
    elif '&' in clause:  # Conjunction
        symbols = [symbol.strip() for symbol in clause.split('&')]
        return all(assignment.get(symbol, False) for symbol in symbols)
    else:  # Single proposition
        prop = clause.strip()
        return assignment.get(prop, False)


def TT(kb, query):
    # Extract symbols mentioned in KB clauses and the query
    symbols = set()
    kb_symbols = sorted(set().union(*(clause.split() for clause in kb)))
    query_symbols = sorted(set(query.split()))
    symbols = sorted(set(kb_symbols + query_symbols))

    # Generate all possible combinations of truth values for symbols
    truth_table = list(itertools.product([False, True], repeat=len(symbols)))
    symbol_list = list(symbols)

    # Initialize variables for counting models and checking entailment
    models = 0

    # Check truth table
    for assignment_values in truth_table:
        assignment = dict(zip(symbol_list, assignment_values))

        # Evaluate each clause in the KB
        kb_truth_values = [evaluate_clause(clause, assignment) for clause in kb]

        # Check if all KB clauses are true under the current assignment
        if all(kb_truth_values):
            # Increment model count if KB is true under current assignment
            models += 1
            # Evaluate the query under the current assignment
            query_truth_value = evaluate_clause(query, assignment)

            # If the query is true under the current assignment, return YES and the number of models
            if query_truth_value:
                return f"YES: {models}"
    else:
        return "NO"


# Forward chaining - fix: BAD BAD BAD BADDD
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


# Backward chaining - fix: only prints out one
def BC(kb, query):
    inferred = defaultdict(bool)  # Stores whether a symbol is inferred
    agenda = [query]  # Initialize the agenda with the query

    # Step 1: Main loop
    while agenda:
        q = agenda.pop(0)  # Get the first symbol from the agenda
        if q not in inferred or not inferred[q]:  # If q is not already inferred
            inferred[q] = True
            # Step 2: Find premises that entail q
            premises = [clause.split("=>")[0].strip() for clause in kb if "=>" in clause and q == clause.split("=>")[1].strip()]
            for premise in premises:
                # If all symbols in the premise are already inferred, add the premise to the agenda
                if all(symbol in inferred and inferred[symbol] for symbol in premise.split("&")):
                    agenda.append(premise)
    # Step 3: Generate the result based on inferred symbols
    inferred_symbols = [symbol for symbol in inferred.keys() if inferred[symbol]]
    return inferred_symbols


def parse_TT(filename):
    with open(filename, 'r') as file:
        content = file.read().strip()

    # Find TELL and ASK blocks
    tell_index = content.index("TELL") + len("TELL")
    ask_index = content.index("ASK")
    
    # Extract and process clauses from TELL block
    clauses_text = content[tell_index:ask_index].strip()
    clauses = [clause.strip().replace(" ", "") for clause in clauses_text.split(';') if clause.strip()]
    
    # Extract the query from ASK block
    query = content[ask_index + len("ASK"):].strip()
    
    return clauses, query

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
