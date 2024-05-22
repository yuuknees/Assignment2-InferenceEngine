import re
import sys
import itertools
from collections import defaultdict, Counter
import networkx as nx

# Evaluate an expression considering conjunctions, disjunctions, negations, implications, and biconditionals
def evaluate_expression(expression, assignment):
    if '<=>' in expression:
        part1, part2 = expression.split('<=>')
        return evaluate_expression(part1.strip(), assignment) == evaluate_expression(part2.strip(), assignment)
    elif '=>' in expression:
        antecedent, consequent = expression.split('=>')
        antecedent_value = evaluate_expression(antecedent.strip(), assignment)
        return not antecedent_value or evaluate_expression(consequent.strip(), assignment)
    elif '||' in expression:
        return any(evaluate_expression(part.strip(), assignment) for part in expression.split('||'))
    elif '&' in expression:
        return all(evaluate_expression(part.strip(), assignment) for part in expression.split('&'))
    elif expression.startswith('~'):
        return not evaluate_expression(expression[1:].strip(), assignment)
    else:
        return assignment.get(expression, False)

# Evaluate the truth value of a clause based on the current assignment
def evaluate_clause(clause, assignment):
    return evaluate_expression(clause, assignment)

# Parse the input file to extract clauses and query
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
    return clauses, query

# Extract symbols from the knowledge base
def extract_symbols(knowledge_base):
    symbols = set()
    for statement in knowledge_base:
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
    models_where_kb_and_query_true = 0
    models_where_kb_true = 0

    for assignment_values in truth_table:
        assignment = dict(zip(symbol_list, assignment_values))
        kb_truth_values = [evaluate_clause(clause, assignment) for clause in kb]
        query_truth_value = evaluate_clause(query, assignment)
        if all(kb_truth_values):
            models_where_kb_true += 1
            if query_truth_value:
                models_where_kb_and_query_true += 1

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

    if inferred[query]:
        return f"YES: {', '.join(sorted(k for k, v in inferred.items() if v))}"
    return "NO"

# Backward Chaining Method
def BC(kb, query):
    agenda = [query]
    inferred = defaultdict(bool)
    relevant = set()

    while agenda:
        q = agenda.pop(0)
        if not inferred[q]:
            inferred[q] = True
            relevant.add(q)
            applicable_rules = []

            for clause in kb:
                if "=>" in clause:
                    antecedent, consequent = clause.split("=>")
                    consequent = consequent.strip()
                    if q == consequent:
                        applicable_rules.append((antecedent.strip(), consequent))

            for antecedent, consequent in applicable_rules:
                symbols = [s.strip() for s in re.split('&|\\|\\|', antecedent)]
                if all(inferred[s] for s in symbols):
                    continue
                else:
                    for symbol in symbols:
                        if not inferred[symbol]:
                            agenda.append(symbol)
                            relevant.add(symbol)

    if inferred[query]:
        return f"YES: {', '.join(sorted(relevant))}"
    return "NO"

def main():
    if len(sys.argv) != 3:
        print("Usage: python redo_3.py <filename> <search_method>")
        sys.exit(1)

    filename, search_method = sys.argv[1], sys.argv[2]
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
