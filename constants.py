from json import load

configuration = (lambda f: load(open(f, 'r')))('../config.json')
inp = configuration['Settings']['inputconfig']

consts = (lambda f: {co: c[co] for c in load(open(f, 'r')).values() for co in c})(f'../data/inputs_config_{inp}.json')

globals().update(consts | configuration['Preliminary estimations'])
del consts
del inp
del configuration