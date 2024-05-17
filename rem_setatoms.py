import clingo

def remove_atoms(program: str, atoms_to_remove: set[str]) -> str:
    # Create a Control object
    ctl = clingo.Control()

    # Add the program to the control
    ctl.add("base", [], program)

    # Ground the program
    ctl.ground([("base", [])])

    # Remove the specified atoms
    for atom in atoms_to_remove:
        ctl.assign_external(clingo.Function(atom), False)

    # Solve the program
    ctl.solve()

    # Retrieve the modified program
    modified_program = ctl.symbolic_atoms

    # Convert the modified program to a string
    modified_program_str = "\n".join(str(atom) for atom in modified_program)

    return modified_program_str

# Example usage
program_to_modify = """
    p(a).
    q(b).
    r(c).
"""

atoms_to_remove = {"q(b)", "r(c)"}

modified_program = remove_atoms(program_to_modify, atoms_to_remove)
for atom in modified_program:
    print(atom.symbol)
    print(modified_program)
