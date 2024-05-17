import re
import sys
import itertools
from collections import defaultdict, Counter

def evaluate_clause(clause, assignment):
    if "=>" in clause:
        antecedent, consequent = map(str.strip, clause.split("=>"))
        antecedent_value = all(assignment.get(p.strip(), True) for p in antecedent.split('&'))
        return not antecedent_value or assignment.get(consequent.strip(), True)
    else:
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

def BC(kb, query):
    inferred = defaultdict(bool)

    def backward_chain(q):
        if inferred[q]:
            return True

        for clause in kb:
            if "=>" in clause:
                antecedent, consequent = clause.split("=>")
                antecedent = antecedent.strip().split('&')
                consequent = consequent.strip()

                if consequent == q:
                    if all(backward_chain(a.strip()) for a in antecedent):
                        inferred[q] = True
                        return True

        if q in kb and "=>" not in q:
            inferred[q] = True
            return True

        return False

    result = backward_chain(query)
    return f"YES: {query}" if result else "NO"

def main():
    if len(sys.argv) != 3:
        print("Usage: python redo.py <filename> <search_method>")
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
