import re
import itertools
import sys

def evaluate_clause(clause, assignment):
    if "=>" in clause:
        antecedent, consequent = map(str.strip, clause.split("=>"))
        antecedent_parts = [part.strip() for part in antecedent.split('&')]
        antecedent_value = all(assignment.get(p, False) for p in antecedent_parts)
        consequent_value = assignment.get(consequent, False)
        result = not antecedent_value or consequent_value
        return result
    else:
        return assignment.get(clause.strip(), False)
    

def TT(kb, query):
    symbols = set()
    kb_symbols = sorted(set().union(*(re.findall(r'\b[A-Za-z]+\b', clause) for clause in kb)))
    query_symbols = sorted(set(re.findall(r'\b[A-Za-z]+\b', query)))
    symbols = sorted(set(kb_symbols + query_symbols))
    
    truth_table = generate_truth_table(symbols)
    symbol_list = list(symbols)
    
    valid_models = 0
    
    for assignment_values in truth_table:
        assignment = dict(zip(symbol_list, assignment_values))
        kb_truth_values = [evaluate_clause(clause, assignment) for clause in kb]
        
        if all(kb_truth_values):
            valid_models += 1
            query_truth_value = evaluate_clause(query, assignment)
            
            if query_truth_value:
                return f"YES: {valid_models}"
    else:
        return "NO"

def parse_input(filename):
    with open(filename, 'r') as file:
        content = file.read()
    tell, ask = content.split("ASK")
    tell = tell.replace("TELL\n", "").split(";")
    ask = ask.strip()
    return [clause.strip() for clause in tell if clause.strip()], ask

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 iengine.py <filename> <search_method>")
        return

    filename = sys.argv[1]
    search_method = sys.argv[2]

    search_methods = {
        'TT': TT
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
