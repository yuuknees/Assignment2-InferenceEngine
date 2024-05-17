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
    
    # print("Parsed clauses:", clauses)
    # print("Parsed query:", query)
    return clauses, query



def TT(kb, query):
    symbols = sorted(set(re.findall(r'\b[A-Za-z]+\b', ' '.join(kb) + ' ' + query)))
    truth_table = list(itertools.product([False, True], repeat=len(symbols)))
    symbol_list = list(symbols)
    #print("Symbols:", symbols)  # Verify the extracted symbols

    models_where_kb_and_query_true = 0
    models_where_kb_true = 0

    for assignment_values in truth_table:
        assignment = dict(zip(symbol_list, assignment_values))
        kb_truth_values = [evaluate_clause(clause, assignment) for clause in kb]
        query_truth_value = evaluate_clause(query, assignment)
        # Add this print statement to see the results for each model
        # print(f"Assignment: {assignment}, KB Truths: {kb_truth_values}, Query: {query_truth_value}")

        if all(kb_truth_values):
            models_where_kb_true += 1
            if query_truth_value:
                models_where_kb_and_query_true += 1

    #print(f"Models where KB is true: {models_where_kb_true}, Models where both KB and Query are true: {models_where_kb_and_query_true}")
    if models_where_kb_true > 0 and models_where_kb_and_query_true == models_where_kb_true:
        return f"YES: {models_where_kb_and_query_true}"
    else:
        return "NO"
    

def FC(kb, query):
    agenda = []
    inferred = defaultdict(bool)
    count = Counter()

    for clause in kb:
        if "=>" not in clause:
            agenda.append(clause.strip())
            inferred[clause.strip()] = True

    implications = []
    for clause in kb:
        if "=>" in clause:
            antecedent, consequent = clause.split("=>")
            antecedent = frozenset(map(str.strip, antecedent.strip().split('&')))
            consequent = consequent.strip()
            implications.append((antecedent, consequent))
            count[(antecedent, consequent)] = len(antecedent)

    while agenda:
        p = agenda.pop(0)
        for antecedent, consequent in implications:
            if p in antecedent:
                count[(antecedent, consequent)] -= 1
                if count[(antecedent, consequent)] == 0:
                    if not inferred[consequent]:
                        inferred[consequent] = True
                        agenda.append(consequent)

    # After agenda is empty, we check if the query was inferred
    if inferred[query]:
        return f"YES: {', '.join(sorted(k for k, v in inferred.items() if v))}"
    return "NO"


'''
    ~ Backward chaining pseudocode ~
    function backwardChaining(query, knowledgeBase):
        if query is true:
            return true
        for rule in knowledgeBase:
            if rule.conclusion == query:
                if backwardChaining(rule.antecedent, knowledgeBase):
                    return true
        return false
'''
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
                # If all symbols in the premise are already inferred, return true
                if all(symbol in inferred and inferred[symbol] for symbol in premise.split("&")):
                    return True  # The query is proven true
                else:
                    agenda.append(premise)  # Add the premise to the agenda
    # Step 3: If the loop completes without returning true, the query cannot be proven true
    return False
    
def main():
    if len(sys.argv) != 3:
        print("Usage: python redo_3.py <filename> <search_method>")
        sys.exit(1)

    filename, search_method = sys.argv[1], sys.argv[2]
    # print(f"Running with filename: {filename} and method: {search_method}")
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
