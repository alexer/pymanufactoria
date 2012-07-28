"""
Convert manufactoria save data to (really unreadable) "assembly"
"""
import re

def next_coord(slots, p, d):
	x, y = p
	xd, yd, dd = [(-1, 0, 'h'), (0, -1, 'v'), (1, 0, 'h'), (0, 1, 'v')][d]
	nx, ny = (x + xd, y + yd)
	if (nx, ny) == (12, 13):
		return 'ACCEPT'
	slot = slots.get((nx, ny))
	if not slot:
		return 'REJECT'
	if slot[0] == 'i':
		return '%d-%d-%s' % (nx, ny, dd)
	return '%d-%d' % (nx, ny)

def parse_savedata(data):
	slots = {}
	for item in data.split(';'):
		if not item: continue
		t, x, y, d = re.match('([cipqbrgy])(\\d+):(\\d+)f(\d+)', item).groups()
		slots[int(x), int(y)] = (t, int(d))
	return slots

def save2scr(slots):
	labels = {}
	for p, (t, d) in slots.items():
		ps = '%d-%d' % p
		if t in 'brgy':
			cmd = 'w'
			args = [t.upper(), next_coord(slots, p, d)]
			labels[ps] = (cmd, args)
		elif t in 'pq':
			cmd = dict(p='jrb', q='jgy')[t]
			d3 = d % 4
			d1 = (d - 1) % 4
			d2 = (d + 1) % 4
			if d >= 4:
				d1, d2 = d2, d1
			labels[ps] = (cmd, [next_coord(slots, p, d1), next_coord(slots, p, d2), next_coord(slots, p, d3)])
		elif t == 'c':
			cmd = 'j'
			args = [next_coord(slots, p, d)]
			labels[ps] = (cmd, args)
		elif t == 'i':
			td, bd = d//2, [1, 3, 0, 2][d % 4]
			dt, db = 'hv'[td % 2], 'hv'[bd % 2]
			labels[ps + '-' + dt] = ('j', [next_coord(slots, p, td)])
			labels[ps + '-' + db] = ('j', [next_coord(slots, p, bd)])
		else:
			raise 'Unknown element: ' + repr(t)
	return labels

import sys

data = sys.argv[1]
slots = parse_savedata(data)
labels = save2scr(slots)

# Print labels, with start position first
for label, (cmd, args) in sorted(labels.items(), key = lambda x: x[0] not in ('12-2', '12-2-v')):
	print(label, cmd, *args)

