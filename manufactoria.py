
_cmds = set('j jrb jgy w'.split())
_argc = dict(j=1, jrb=2, jgy=2, w=2)

def parse_code(lines):
	labels = {}
	first = None
	for line in lines:
		line = line.split('#', 1)[0].strip()
		if not line:
			continue
		label, cmd, *args = line.split()

		assert cmd in _cmds, 'Unknown command: %r' % (cmd, )
		assert len(args) >= _argc[cmd], 'Command %r needs at least %d argument(s), got %d' % (cmd, _argc[cmd], len(args))

		if not first:
			first = label

		if cmd == 'w':
			assert args[0].replace('R', '').replace('B', '').replace('Y', '').replace('G', '') == ''

		if cmd in 'jrb jgy'.split() and len(args) == 2:
			args.append('REJECT')

		labels[label] = (cmd, args)

	for label, (cmd, args) in labels.items():
		check = args[1:] if cmd == 'w' else args
		for item in check:
			assert item in 'ACCEPT REJECT ASSERT'.split() or item in labels, 'Unknown target: %r' % (item, )

	labels[None] = first

	return labels

def print_tape(tape, inplace = False):
	if inplace:
		start, end = '\r\x1b[K', ''
	else:
		start, end = '', '\n'
	print(start + ''.join(dict(R='\x1b[1;31mR\x1b[m', B='\x1b[1;34mB\x1b[m', Y='\x1b[1;33mY\x1b[m', G='\x1b[1;32mG\x1b[m')[item] for item in tape), end = end)

def simulate(labels, data):
	tape = list(data.upper())

	inplace = True

	print_tape(tape, inplace)
	if inplace: print()

	ptr = labels[None]
	while True:
		if ptr in 'ACCEPT REJECT ASSERT'.split():
			print_tape(tape, inplace)
			if inplace: print()
			print(ptr)
			print()
			return ''.join(tape), ptr
		cmd, args = labels[ptr]
		print_tape(tape, inplace)
		if not inplace: print(ptr, cmd, *args)
		if cmd == 'j':
			ptr = args[0]
		elif cmd in 'jrb jgy'.split():
			check = cmd[1:].upper()
			try:
				item = tape[0]
			except IndexError:
				item = 'N'
			if item in check:
				tape.pop(0)
			ptr = args[check.find(item)]
		elif cmd == 'w':
			tape.extend(list(args[0]))
			ptr = args[1]
		time.sleep(0.025)

import time
import sys

cfn, dfn = sys.argv[1:]
print('Using', cfn, 'for code and', dfn, 'for data')

labels = parse_code(open(cfn))
for line in open(dfn):
	line = line.split('#', 1)[0].strip()
	if not line:
		continue
	tape_in, _tape_out, _status = line.split()
	tape_out, status = simulate(labels, tape_in)
	if _tape_out != '*':
		assert tape_out in _tape_out.split('|')
	assert status == _status

