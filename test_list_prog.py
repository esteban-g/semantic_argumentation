from clingo import Control

def list_atoms(program):
  """
  This function takes a logic program string and lists all its atoms.
  """
  ctl = Control()
  ctl.load(program)  # Use load instead of add

  # Use Clingox for iterating over symbolic atoms efficiently
  from clingox import SymbolicAtomIter

  # Iterate over all positive and negative atoms
  for positive in [True, False]:
    for atom in SymbolicAtomIter(ctl.program, name="", arity=0, positive=positive):
      print(atom)

# Example usage
program = """
  happy(bird).
  sings(canary).
  canary :- bird.

  # Negative literal
  :- unhappy(X).
"""

list_atoms(program)