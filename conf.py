
class VariablesMissing (Exception):
  def __init__ (self, variables):
    self.variables = set(variables)
  def __str__ (self):
    return 'Variable(s) missing: {:s}'.format(', '.join(self.variables))


def load_vars (expected_vars, filename):
  loaded = {}

  for line in open(filename, 'r'):
    var, _, value = line.rstrip('\r\n').partition(': ')
    if var in expected_vars:
      loaded[var] = expected_vars[var](value)

  missing = set(expected_vars.keys()) - set(loaded.keys())
  if missing:
    raise VariablesMissing(missing)

  return loaded

