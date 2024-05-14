import re
import sys
import itertools
from collections import defaultdict, Counter
import networkx as nx

def evaluate_clause(clause, assignment):
    if "=>" in clause:
        # Splitting the clause into antecedent (left of '=>') and consequent (right of '=>')
        antecedent, consequent = map(str.strip, clause.split("=>"))
        # Evaluating the antecedent:
        # - Split by '&' to handle multiple conditions joined by logical AND
        # - Check if each condition (proposition) is True in the current assignment
        antecedent_value = all(assignment.get(p.strip(), True) for p in antecedent.split('&'))
        # Implication logic:
        # - If antecedent is False, implication is True
        # - If antecedent is True, check the value of the consequent
        return not antecedent_value or assignment.get(consequent.strip(), True)
    else:
        # Directly return the truth value of the proposition for facts
        return assignment.get(clause.strip(), True)

def parse_input(filename):
    with open(filename, 'r') as file:
        content = file.read().split('ASK')
        
    if len(content) < 2:
        print("Error: Incorrect file format. 'ASK' section not found.")
        sys.exit(1)
        
    kb_section = content[0].strip()
    if 'TELL' not in kb_section:
        print("Error: Incorrect file format. 'TELL' section not found.")
        sys.exit(1)
        
    kb_raw = kb_section.split('TELL')[1].strip()
    query = content[1].strip()
    clauses = [clause.strip() for clause in kb_raw.split(';') if clause.strip()]
    
    print("Parsed clauses:", clauses)
    print("Parsed query:", query)
    return clauses, query



def TT(kb, query):
    symbols = sorted(set(re.findall(r'\b[A-Za-z]+\b', ' '.join(kb) + ' ' + query)))
    truth_table = list(itertools.product([False, True], repeat=len(symbols)))
    symbol_list = list(symbols)
    print("Symbols:", symbols)  # Verify the extracted symbols

    models_where_kb_and_query_true = 0
    models_where_kb_true = 0

    for assignment_values in truth_table:
        assignment = dict(zip(symbol_list, assignment_values))
        kb_truth_values = [evaluate_clause(clause, assignment) for clause in kb]
        query_truth_value = evaluate_clause(query, assignment)
        # Add this print statement to see the results for each model
        print(f"Assignment: {assignment}, KB Truths: {kb_truth_values}, Query: {query_truth_value}")

        if all(kb_truth_values):
            models_where_kb_true += 1
            if query_truth_value:
                models_where_kb_and_query_true += 1

    print(f"Models where KB is true: {models_where_kb_true}, Models where both KB and Query are true: {models_where_kb_and_query_true}")
    if models_where_kb_true > 0 and models_where_kb_and_query_true == models_where_kb_true:
        return f"YES: {models_where_kb_and_query_true}"
    else:
        return "NO"


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
    
def main():
    if len(sys.argv) != 3:
        print("Usage: python redo_3.py <filename> <search_method>")
        sys.exit(1)

    filename, search_method = sys.argv[1], sys.argv[2]
    print(f"Running with filename: {filename} and method: {search_method}")
    clauses, query = parse_input(filename)

    if search_method == 'TT':
        result = TT(clauses, query)
        print(result)
    elif search_method == 'FC':
        result = FC(clauses, query)
        print(result)
    elif search_method == 'BC':
        result = FC(clauses, query)
        print(result)
    else:
        print("Invalid search method")

if __name__ == "__main__":
    main()
