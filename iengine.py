import re
import sys
import itertools
from collections import defaultdict, Counter
import networkx as nx

# Evaluate an expression 
def evaluate_expression(expression, assignment):
    # Biconditionals
    if '<=>' in expression:
        part1, part2 = expression.split('<=>')
        return evaluate_expression(part1.strip(), assignment) == evaluate_expression(part2.strip(), assignment)
    # Implications
    elif '=>' in expression:
        antecedent, consequent = expression.split('=>')
        antecedent_value = evaluate_expression(antecedent.strip(), assignment)
        return not antecedent_value or evaluate_expression(consequent.strip(), assignment)
    # Disjunctions
    elif '||' in expression:
        return any(evaluate_expression(part.strip(), assignment) for part in expression.split('||'))
    # Conjunctions
    elif '&' in expression:
        return all(evaluate_expression(part.strip(), assignment) for part in expression.split('&'))
    # Negations
    elif expression.startswith('~'):
        return not evaluate_expression(expression[1:].strip(), assignment)
    else:
        # Directly return the truth value of the proposition for facts
        return assignment.get(expression, False)

# Evaluate the truth value of a clause based on the current assignment
def evaluate_clause(clause, assignment):
    return evaluate_expression(clause, assignment)

# Parse the input file to extract clauses and query
def parse_input(filename):
    # Read the content of the file and split the sections based on 'ASK'
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
    
    #print("Parsed clauses:", clauses) #Debug uncomment to see the parsed clauses
    #print("Parsed query:", query) #Debug uncomment to see the parsed clauses and query
    return clauses, query

# Extract symbols from the knowledge base
def extract_symbols(knowledge_base):
    symbols = set()
    for statement in knowledge_base:
        # Removes all spaces and divides the statement into a list of parts separated by any of the given logical operators
        parts = re.split('=>|<=>|&|\\|\\|', statement.replace(' ', ''))
        for part in parts:
            if part.startswith('~'):
                part = part[1:]
            symbols.add(part.strip())
    return symbols


# Truth Table Method
def TT(kb, query):
    symbols = sorted(extract_symbols(kb + [query]))
    truth_table = list(itertools.product([False, True], repeat=len(symbols)))
    symbol_list = list(symbols)
     #print("Symbols:", symbols)  # Debug verify the extracted symbols
    
    models_where_kb_and_query_true = 0
    models_where_kb_true = 0

    for assignment_values in truth_table:
        assignment = dict(zip(symbol_list, assignment_values))
        kb_truth_values = [evaluate_clause(clause, assignment) for clause in kb]
        query_truth_value = evaluate_clause(query, assignment)
        # print(f"Assignment: {assignment}, KB Truths: {kb_truth_values}, Query: {query_truth_value}") #Debug to see the results for each model
 
        if all(kb_truth_values):
            models_where_kb_true += 1
            if query_truth_value:
                models_where_kb_and_query_true += 1

    #print(f"Models where KB is true: {models_where_kb_true}, Models where both KB and Query are true: {models_where_kb_and_query_true}") #Debug to see the final counts
    if models_where_kb_true > 0 and models_where_kb_and_query_true == models_where_kb_true:
        return f"YES: {models_where_kb_and_query_true}"
    else:
        return "NO"

# Forward Chaining Method
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

# Backward Chaining Method
def BC(kb, query):
    # Initialize inferred symbols and relevant symbols
    agenda = [query]
    inferred = defaultdict(bool)
    relevant = set()

    while agenda:
        q = agenda.pop(0)
        #print(f"Processing query: {q}") #Debug uncomment to see the query being processed
        if not inferred[q]:
            inferred[q] = True
            relevant.add(q)
            applicable_rules = []

            # Identify rules where q is the consequent
            for clause in kb:
                if "=>" in clause:
                    antecedent, consequent = clause.split("=>")
                    consequent = consequent.strip()
                    if q == consequent:
                        applicable_rules.append((antecedent.strip(), consequent))
            # print(f"Applicable rules for {q}: {applicable_rules}") # Debug uncomment to see the applicable rules

            # Check if all antecedents of the applicable rules are inferred
            for antecedent, consequent in applicable_rules:
                symbols = [s.strip() for s in re.split('&|\\|\\|', antecedent)]
                if all(inferred[s] for s in symbols):
                    #print(f"All antecedents of {antecedent} are inferred.") # Debug uncomment to see the antecedents
                    continue
                else:
                    for symbol in symbols:
                        if not inferred[symbol]:
                            agenda.append(symbol)
                            relevant.add(symbol)
                            #print(f"Adding {symbol} to agenda.") # Debug uncomment to see the symbol being added to agenda
                     
    #After agenda is empty, we check if the query was inferred
    if inferred[query]:
        return f"YES: {', '.join(sorted(relevant))}"
    return "NO"

def main():
    if len(sys.argv) != 3:
        print("Usage: python redo_3.py <filename> <search_method>")
        sys.exit(1)

    filename, search_method = sys.argv[1], sys.argv[2]
    # print(f"Running with filename: {filename} and method: {search_method}") # Debug uncomment to see the filename and search method
    clauses, query = parse_input(filename)

    if search_method == 'TT':
        result = TT(clauses, query)
        print(result)
    elif search_method == 'FC':
        result = FC(clauses, query)
        print(result)
    elif search_method == 'BC':
        result = BC(clauses, query)
        print(result)
    else:
        print("Invalid search method")

if __name__ == "__main__":
    main()