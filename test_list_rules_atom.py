import clingo

def main(prg):
    # Add your program rules here (e.g., prg.add("p", "{a;b;c}."))
    # Ground the program
    prg.ground([("p", [])])

    # Iterate over the symbolic atoms
    for atom in prg.symbolic_atoms:
        if atom.is_fact:
            # Handle facts (e.g., atom is a fact)
            print(f"Fact: {atom.symbol}")
        elif atom.is_rule:
            # Handle rules (e.g., atom is part of a rule)
            rule = atom.rule
            head = rule.head
            body = rule.body
            print(f"Rule: {head} :- {body}")

if __name__ == "__main__":
    prg = clingo.Control()
    main(prg)