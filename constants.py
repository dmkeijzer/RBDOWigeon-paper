from json import load

consts = (lambda f: {co: c[co] for c in load(open(f, 'r')).values() for co in c})('inputs.json')

globals().update(consts)
del consts
