
def implication(p, q):
    return (not p) or q

def count_models():
    count = 0
    for p2 in [False, True]:
        for p3 in [False, True]:
            for p1 in [False, True]:
                result1 = implication(p2, p3)
                result2 = implication(p3, p1)
                if result1 and result2:
                    count += 1
    return count

def truth_table():
    print("P2 | P3 | P1 | P2 => P3 | P3 => P1")
    print("------------------------------------")
    for p2 in [False, True]:
        for p3 in [False, True]:
            for p1 in [False, True]:
                result1 = implication(p2, p3)
                result2 = implication(p3, p1)
                print(f"{int(p2)}  | {int(p3)}  | {int(p1)}  |    {int(result1)}     |     {int(result2)}")

if __name__ == "__main__":
    truth_table()
    num_models = count_models()
    if num_models > 0:
        print(f"\nYES: {num_models}")
    else:
        print("\nNO")