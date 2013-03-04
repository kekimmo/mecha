
class VariablesMissing (Exception):
  def __init__ (self, var_names):
    self.var_names = var_names
  def __str__ (self):
    return 'Variable(s) missing: {:s}'.format(', '.join(self.var_names))


def load_vars (expected_vars, filename):
  loaded = {}
  missing = list(expected_vars.keys())

  for line in open(filename, 'r'):
    var, _, value = line.rstrip('\r\n').partition(': ')
    if var in expected_vars:
      loaded[var] = expected_vars[var](value)
      try:
        missing.remove(var)
      except ValueError:
        pass

  if missing:
    raise VariablesMissing(missing)

  return loaded

