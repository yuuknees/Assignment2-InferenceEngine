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

def parse_truthTable(filename):
    with open(filename, 'r') as file:
        content = file.read()
        kb_match = re.search()
        query_match = re.search()

        if kb_match and query_match:
            kb = kb_match.group(1).strip()
            query = query_match.group(1).strip()

            clauses = [clause.strip() for clause in kb.splitx(';') if clause.strip()]
            return clauses, query
        else:
            raise ValueError("the file is no good.")


def evaulate_clause(clause, model):
    antecedents, consequent = parse_clause(clause)
    antecedents_values = [model[symbol] for symbol in antecedents if  symbol in model]
    if all (antecedents_values):
        return model.get(consequent, True)
    return True

def TT(knowledge_base, query):
    """Checks the truth table for a given knowledge base and query"""

    symbols = set()
    for clause in knowledge_base:
        print(f"soemthing {symbols}")
        antecedents, consequent = parse_clause(clause)
        symbols.update(antecedents)
        symbols.add(consequent)

    #generate all possible combinations of true or false for the given number of symbols 
    truth_table = list(itertools.product([False, True], repeat=len(symbols)))
    symbol_list = list(symbols)

    valid_models = 0
    for model in truth_table:
        model_dict = dict(zip(symbol_list, model))
        print(f"model_dict is:{model_dict}")
        print("end for model")
        if all (evaulate_clause(clause, model_dict) for clause in knowledge_base):
            valid_models += 1
            if model_dict.get(query, False):
                continue

            if valid_models > 0:
                return f"yES: {valid_models}"
            
            else:
                return "nO"

def parse_clause(clause):
    pass

# if __name__ == "__main__":
#     method = sys.argv[1]
#     filename = sys.argv[2]
#     TT_knowledge_base, TT_query = parse_truthTable(filename)
#     print(f"TT{TT_knowledge_base}")
#     print({TT_query})
#     # FC_knowledge_base, FC_query = parse_FC(filename)


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
            clauses, query = parse_truthTable(filename)
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