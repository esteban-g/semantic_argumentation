import clingo

def create_rule(literal_str):
  """Creates a new rule from a literal string in Clingo.

  Args:
    literal_str: A string representing the literal (e.g., "happy(person)").

  Returns:
    A clingo.Rule object containing the created rule.
  """
  # Use parse_term instead of parse_literal
  term = clingo.parse_term(literal_str)
  # Ensure the term is a literal before creating the rule
  if not isinstance(term, clingo.Literal):
    raise ValueError(f"Invalid literal format: {literal_str}")

  # Create an empty body (no conditions)
  body = []
  return clingo.Rule(head=term, body=body)

# Example usage
rule_str = "smokes(person) :- addicted(person)."
new_rule = create_rule(rule_str)

# Print or use the new_rule object in your Clingo program
print(new_rule)  # Output: smokes(person) <- addicted(person).