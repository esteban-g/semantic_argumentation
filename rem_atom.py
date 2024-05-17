import clingo

def remove_non_head_atoms(program):
    # Create a Control object
    ctl = clingo.Control()

    # Add the rules from the program
    for rule in program:
        head, body = rule
        ctl.add("base", [], f"{head} :- {body}.")

    # Ground the program
    ctl.ground([("base", [])])

    # Collect the head atoms
    head_atoms = set()
    body_atoms = set()
    for model in ctl.solve(yield_=True):
        for atom in model.symbols(shown=True):
            print('atom.name:',atom.name)
            if atom.name == "base" and atom.positive:
                head_atoms.add(atom.arguments[0])

    # Remove non-head atoms
    new_program = []
    for rule in program:
        head, body = rule
        if head in head_atoms:
            new_program.append(rule)
        
    return new_program

# Example usage
if __name__ == "__main__":
    program = [
        ("p", "q"),
        ("q", "not c"),
        ("t", "not u"),
    ]

    updated_program = remove_non_head_atoms(program)
    for rule in updated_program:
        print(f"{rule[0]} :- {rule[1]}")
