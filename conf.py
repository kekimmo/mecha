
def load_vars (expected_vars, filename):
  loaded = {}

  for line in open(filename, 'r'):
    var, _, value = line.rstrip('\r\n').partition(': ')
    if var in expected_vars:
      loaded[var] = expected_vars[var](value)

  for var in expected_vars:
    if var not in loaded:
      loaded[var] = None

  return loaded

