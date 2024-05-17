import clingo

ctl = clingo.Control()
ctl.add("base", [], "g:- f. c :- not d.")
ctl.ground([("base", [])])

# get the symbolic atoms object
atoms = ctl.symbolic_atoms

# iterate over all atoms
for atom in atoms:
    # print the atom and its truth value
    print(atom.symbol, atom.is_fact, atom.is_external)