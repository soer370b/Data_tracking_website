import ast
f = '4'
print(type(f))
L = ["hello", "3", "3.64", "-1"]

if type(f).__name__ == "str":
    print("hey")
else:
    print('ikke hey')
def tryeval(val):
  try:
    val = ast.literal_eval(val)
  except ValueError:
    pass
  return val

# print [tryeval(x) for x in L]
g = tryeval(f)
print(type(g))

if type(g).__name__ == "str":
    print("hey")
else:
    print('ikke hey')
