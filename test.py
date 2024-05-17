import clingo

from clingox.backend import SymbolicBackend
from clingox.program import Program,ProgramObserver
ctl = clingo.Control()
prg = Program()
ctl.register_observer(ProgramObserver(prg))

a = clingo.Function("j")
b = clingo.Function("b")
c = clingo.Function("c")



with ctl.backend() as backend:
            symbolic_backend = SymbolicBackend(backend)
            symbolic_backend.add_rule([a], [b], [c])
            atom_b = backend.add_atom(b)
            backend.add_rule([atom_b])
prg.add_to_backend
for rule in prg.rules:
    print("Answer: {}".format(rule))

ctl.solve(on_model=lambda m: print("Answer: {}".format(m)))