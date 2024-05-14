import re
import itertools
import sys

# Function to parse the input file
def parse_TT(filename):
    with open(filename, 'r') as file:
        content = file.read().strip()

    try:
        tell_index = content.index("TELL") + len("TELL")
        ask_index = content.index("ASK")
    except ValueError:
        raise ValueError("File must contain 'TELL' and 'ASK' sections")

    # Extract and process clauses from TELL block
    clauses_text = content[tell_index:ask_index].strip()
    clauses = [clause.strip() for clause in clauses_text.split(';') if clause.strip()]

    # Extract the query from ASK block
    query = content[ask_index + len("ASK"):].strip()

    return clauses, query

# Function to evaluate a clause based on an assignment
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

# Function to generate all possible truth assignments for a given set of symbols
def generate_truth_table(symbols):
    return list(itertools.product([False, True], repeat=len(symbols)))

# Truth Table Algorithm (TT)
def TT(kb, query):
    # Extract all unique symbols
    symbols = set()
    kb_symbols = sorted(set().union(*(re.findall(r'\b[A-Za-z]+\b', clause) for clause in kb)))
    query_symbols = sorted(set(re.findall(r'\b[A-Za-z]+\b', query)))
    symbols = sorted(set(kb_symbols + query_symbols))

    # Generate all possible truth assignments
    truth_table = generate_truth_table(symbols)
    symbol_list = list(symbols)

    valid_models = 0

    for assignment_values in truth_table:
        assignment = dict(zip(symbol_list, assignment_values))
        kb_truth_values = [evaluate_clause(clause, assignment) for clause in kb]

        # Check if all KB clauses are true under this assignment
        if all(kb_truth_values):
            query_truth_value = evaluate_clause(query, assignment)
            
            # Print debugging information
            print(f"Assignment: {assignment}")
            print(f"KB Truth Values: {kb_truth_values}")
            print(f"Query Truth Value: {query_truth_value}\n")

            # Check if the query is true under this assignment
            if query_truth_value:
                valid_models += 1

    return f"YES: {valid_models}" if valid_models > 0 else "NO"


# Main function to handle command-line arguments and execute the appropriate method
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
            clauses, query = parse_TT(filename)
            result = method_function(clauses, query)
            print(result)
        except ValueError as e:
            print("Error:", e)
    else:
        print("Invalid method function")

if __name__ == "__main__":
    main()
