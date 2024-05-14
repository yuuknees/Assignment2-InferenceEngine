import sys
import itertools
from collections import defaultdict, Counter

def evaluate_clause(clause, assignment):
    if '=>' in clause:
        antecedent, consequent = map(str.strip, clause.split('=>'))
        if antecedent not in assignment:
            return True
        return not assignment[antecedent] or assignment.get(consequent, False)
    elif '&' in clause:
        symbols = map(str.strip, clause.split('&'))
        return all(assignment.get(symbol, False) for symbol in symbols)
    else:
        prop = clause.strip()
        return assignment.get(prop, False)

def TT(kb, query):
    symbols = sorted(set().union(*(clause.split() for clause in kb)))
    truth_table = list(itertools.product([False, True], repeat=len(symbols)))
    symbol_list = list(symbols)
    models = 0

    for assignment_values in truth_table:
        assignment = dict(zip(symbol_list, assignment_values))
        kb_truth_values = [evaluate_clause(clause, assignment) for clause in kb]

        if all(kb_truth_values):
            models += 1
            query_truth_value = evaluate_clause(query, assignment)
            if query_truth_value:
                return f"YES: {models}"
    else:
        return "NO"

def FC(kb, query):
    inferred = defaultdict(bool)
    count = Counter()
    agenda = [symbol for symbol in kb if "=>" not in symbol and evaluate_clause(symbol, {})]

    while agenda:
        p = agenda.pop(0)
        if p == query:
            inferred_symbols = [symbol for symbol in inferred.keys() if inferred[symbol]]
            return "YES: " + ", ".join(inferred_symbols)
        if not inferred[p]:
            inferred[p] = True
            for clause in kb:
                if "=>" in clause and p in clause.split("=>")[0]:
                    count[clause] += 1
                    if count[clause] == clause.split("=>")[0].count(" ") + 1:
                        q = clause.split("=>")[1].strip()
                        agenda.append(q)
                        inferred[q] = True

    return "NO"

def BC(kb, query):
    inferred = defaultdict(bool)
    agenda = [query]

    while agenda:
        q = agenda.pop(0)
        if q not in inferred or not inferred[q]:
            inferred[q] = True
            premises = [clause.split("=>")[0].strip() for clause in kb if "=>" in clause and q == clause.split("=>")[1].strip()]
            for premise in premises:
                if all(symbol in inferred and inferred[symbol] for symbol in premise.split("&")):
                    agenda.append(premise)

    inferred_symbols = [symbol for symbol in inferred.keys() if inferred[symbol]]
    return inferred_symbols

def parse_input(filename):
    with open(filename, 'r') as file:
        content = file.read().strip()

    tell_index = content.index("TELL") + len("TELL")
    ask_index = content.index("ASK")
    
    clauses_text = content[tell_index:ask_index].strip()
    clauses = [clause.strip() for clause in clauses_text.split(';') if clause.strip()]
    
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
            clauses, query = parse_input(filename)
            result = method_function(clauses, query)
            print(result)
        except ValueError as e:
            print("Error:", e)
    else:
        print("Invalid method function")

if __name__ == "__main__":
    main()
