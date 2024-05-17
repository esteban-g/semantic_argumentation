import clingo
from clingox.backends import SymbolicBackend

def create_symbolic_rule(ctl, literal_str):
  """Creates a new rule with a symbolic literal in Clingox.

  Args:
    ctl: A clingo.Control object.
    literal_str: A string representing the literal (e.g., "happy(person)").

  Returns:
    A list containing the rule head (symbolic atom).
  """
  literal = clingo.parse_literal(literal_str)
  with SymbolicBackend(ctl.backend()) as symbolic_backend:
    # Convert the literal to a symbolic atom
    head = symbolic_backend.convert_literal(literal)
    return [head]

# Example usage
ctl = clingo.Control()
# ... (rest of your Clingox code)
rule_head = create_symbolic_rule(ctl, "teaches(Alice, Math)")

# You can now use rule_head (symbolic atom) in your Clingox logic